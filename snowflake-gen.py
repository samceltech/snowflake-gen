import adsk.core, adsk.fusion, traceback, tempfile
import math
import random

# https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-CB1A2357-C8CD-474D-921E-992CA3621D04
# https://forums.autodesk.com/t5/fusion-api-and-scripts-forum/thin-extrude-an-open-profile-via-api/td-p/11566052
# https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-536A4E7D-AA90-4ACB-9378-009993C59FF2
# note: MAKE SURE DIMENSION INPUTS ARE VALUEINPUTS

radius = 0.0625
depth = 0.125
depth_cm = 1 * 2.54

arm_length_input = 5

hole_offset = 0.15

# [[[x, y]]] or some other coordinate, doesn't matter

class SnowflakeLine:
    def __init__(self, p1x, p1y, p2x, p2y):
        self.p1x = p1x
        self.p1y = p1y
        self.p2x = p2x
        self.p2y = p2y

# snowflake_lines = [SnowflakeLine(0,0,5,0),SnowflakeLine(2,0,3,2), SnowflakeLine(2,0,3,-2), SnowflakeLine(5,0,6,1), SnowflakeLine(5,0,6,-1)]

#fine, this way:
def generate(arm_length=arm_length_input, num_segments=24, base_branch_length=1.0, base_branch_probability=.8):
    """
    Generates a single snowflake arm that is perfectly symmetrical
    about the central axis. Sub‑branches become shorter and less common
    as they move outward.
    """

    segments = []
    main_points = [(0,0)]
    angle = 90  # straight upward

    # Build center spine
    for i in range(1, num_segments + 1):
        progress = i / num_segments
        seg_len = arm_length / num_segments

        prev = main_points[-1]
        dx = seg_len * math.cos(math.radians(angle))
        dy = seg_len * math.sin(math.radians(angle))
        new_pt = (prev[0] + dx, prev[1] + dy)
        main_points.append(new_pt)

        # Add main spine segment (center)
        segments.append((prev, new_pt))

    # Add symmetrical branches
    for i in range(1, num_segments):
        progress = i / num_segments

        # *Probability* decreases toward the tip
        branch_prob = base_branch_probability * (1 - progress)

        if random.random() < branch_prob:

            # *Branch length* also decreases toward the tip
            branch_length = base_branch_length * (1 - progress)

            origin = main_points[i]

            # Branch angles
            left_angle  = 90 + random.uniform(35, 65)
            right_angle = 90 - (left_angle - 90)  # perfect symmetry

            # Compute endpoints
            lx = origin[0] + branch_length * math.cos(math.radians(left_angle))
            ly = origin[1] + branch_length * math.sin(math.radians(left_angle))

            rx = origin[0] + branch_length * math.cos(math.radians(right_angle))
            ry = origin[1] + branch_length * math.sin(math.radians(right_angle))

            # Add branch segments
            segments.append((origin, (lx, ly)))
            segments.append((origin, (rx, ry)))

    return segments

snowflake_lines = []

input_lines = generate()

for input_line in input_lines:
    ipt_p1x = input_line[0][0]
    ipt_p1y = input_line[0][1]
    ipt_p2x = input_line[1][0]
    ipt_p2y = input_line[1][1]

    formatted_line = SnowflakeLine(ipt_p1x, ipt_p1y, ipt_p2x, ipt_p2y)

    snowflake_lines.append(formatted_line)

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        # ui.messageBox('Snowflake Script Running...')

        design = app.activeProduct
        if not isinstance(design, adsk.fusion.Design):
            ui.messageBox('Please switch to Design workspace first.')
            return
        
        export_manager = design.exportManager

        root = design.rootComponent

        origin = adsk.core.Point3D.create(0,0,0)
        z_axis: adsk.core.Base = root.zConstructionAxis

        # features:
        extrudeFeatures = root.features.extrudeFeatures
        cirPatternFeatures = root.features.circularPatternFeatures

        # operations:
        join_operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        cut_operation = adsk.fusion.FeatureOperations.CutFeatureOperation
            
        def mountingHole(): #does this even make sense to have be a function? thought this could help clean structure up

            hole_distance = arm_length_input - hole_offset
            hole_center = adsk.core.Point3D.create(0, hole_distance, 0) #make into inputs

            reinforcement_sketch = root.sketches.add(root.xYConstructionPlane)
            reinforcement_sketch.name = "mounting hole reinforcement"

            reinforcementSketchCircles = reinforcement_sketch.sketchCurves.sketchCircles

            reinforcementSketchCircles.addByCenterRadius(hole_center, .15)

            reinforcement_extrude = extrudeFeatures.addSimple(reinforcement_sketch.profiles.item(0), adsk.core.ValueInput.createByReal(0.1), adsk.fusion.FeatureOperations.JoinFeatureOperation)

            hole_sketch = root.sketches.add(root.xYConstructionPlane)
            hole_sketch.name = "hanger hole sketch"

            holeSketchCircles = hole_sketch.sketchCurves.sketchCircles

            holeSketchCircles.addByCenterRadius(hole_center, 0.06)

            hole_distance = adsk.core.ValueInput.createByString("1 in")

            hole_extrude = extrudeFeatures.addSimple(hole_sketch.profiles.item(0), hole_distance, cut_operation)

        def openProfileThinExtrude(profile_collection, width_str, depth_str):

            ext_input = extrudeFeatures.createInput(profile_collection, join_operation)

            wallLocation = adsk.fusion.ThinExtrudeWallLocation.Center
            width = adsk.core.ValueInput.createByString(width_str)
            depth = adsk.core.ValueInput.createByString(depth_str)
            distance_extent = adsk.fusion.DistanceExtentDefinition.create(depth)
            direction = adsk.fusion.ExtentDirections.PositiveExtentDirection
            ext_input.setOneSideExtent(distance_extent, direction)
            ext_input.setThinExtrude(wallLocation, width)

            # Create the feature.
            extrusion = extrudeFeatures.add(ext_input)
            return extrusion

        arm_sketch = root.sketches.add(root.xYConstructionPlane)
        arm_sketch.name = "snowflake arm sketch"

        arm_sketch_lines = arm_sketch.sketchCurves.sketchLines

        arm_line_collection = adsk.core.ObjectCollection.create()

        for snowflake_line in snowflake_lines:
            p1 = adsk.core.Point3D.create(snowflake_line.p1x, snowflake_line.p1y, 0)
            p2 = adsk.core.Point3D.create(snowflake_line.p2x, snowflake_line.p2y, 0)
            new_line = arm_sketch_lines.addByTwoPoints(p1, p2)

        filter =  adsk.core.SelectionCommandInput.SketchCurves

        arm_profile_collection = adsk.core.ObjectCollection.create()

        for line in arm_sketch_lines:
            arm_line_collection.add(line)
            profile = root.createOpenProfile(line)
            arm_profile_collection.add(profile)
    
        # Define the required input.

        arm_extrusion = openProfileThinExtrude(arm_profile_collection, "2 mm", "1 mm")

        arm_bodies = arm_extrusion.bodies

        cirPatternInputEntities = adsk.core.ObjectCollection.create()

        for body in arm_bodies: # 1 for now
            cirPatternInputEntities.add(body)
        
        cirPatternInput = cirPatternFeatures.createInput(cirPatternInputEntities, z_axis)

        cirPatternInput.quantity = adsk.core.ValueInput.createByReal(6)
        cirPatternInput.totalAngle = adsk.core.ValueInput.createByString('360 deg')
        cirPatternInput.isSymmetric = False
        
        cir_pattern = cirPatternFeatures.add(cirPatternInput)

        join_sketch = root.sketches.add(root.xYConstructionPlane)
        join_sketch.name = 'join sketch'
        join_sketch_circles = join_sketch.sketchCurves.sketchCircles

        join_sketch_circles.addByCenterRadius(origin, radius)

        #looks like this does cm by default. createbyreal probabaly easier to use overall
        join_extrude_distance = adsk.core.ValueInput.createByString("0.001 in")

        join_circle_profile = join_sketch.profiles.item(0)

        join_extrude = extrudeFeatures.addSimple(join_circle_profile, join_extrude_distance, join_operation)    

        snowflake_body = join_extrude.bodies.item(0)

        snowflake_body.name = "snowflake body"
        
        # hole:
        mountingHole()

        ui.messageBox('Snowflake base created successfully.')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))