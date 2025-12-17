import adsk.core, adsk.fusion, traceback, tempfile
import math
import random

# https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-CB1A2357-C8CD-474D-921E-992CA3621D04
# https://forums.autodesk.com/t5/fusion-api-and-scripts-forum/thin-extrude-an-open-profile-via-api/td-p/11566052
# https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-536A4E7D-AA90-4ACB-9378-009993C59FF2
# note: MAKE SURE DIMENSION INPUTS ARE VALUEINPUTS

arm_length_input = 5

arm_depth = 0.1
arm_width = 0.2

# hole_offset = 0.15

class SnowflakeLine:
    def __init__(self, p1x, p1y, p2x, p2y):
        self.p1x = p1x
        self.p1y = p1y
        self.p2x = p2x
        self.p2y = p2y

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

        # geometry
        origin = adsk.core.Point3D.create(0,0,0)
        x_axis: adsk.core.Base = root.xConstructionAxis
        y_axis: adsk.core.Base = root.yConstructionAxis
        z_axis: adsk.core.Base = root.zConstructionAxis
        XY_plane: adsk.core.Base = root.xYConstructionPlane
        XZ_plane: adsk.core.Base = root.xZConstructionPlane
        YZ_plane: adsk.core.Base = root.yZConstructionPlane

        # features:
        extrudeFeatures = root.features.extrudeFeatures
        cirPatternFeatures = root.features.circularPatternFeatures

        # operations:
        join_operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        cut_operation = adsk.fusion.FeatureOperations.CutFeatureOperation

        working_plane = XY_plane
            
        def mountingHole(
            center_distance: int = 0, 
            direction: adsk.core.Base = y_axis, 
            plane: adsk.core.Base = XY_plane,
            reinforcement_radius: int = .15,
            hole_radius: int = 0.06,
            reinforcement_depth: int = 0.1
            ):

            if direction == x_axis and plane != YZ_plane:
                hole_x = center_distance
            else:
                hole_x = 0
            
            if direction == y_axis and plane != XZ_plane:
                hole_y = center_distance
            else:
                hole_y = 0
            
            if direction == z_axis and plane != XY_plane:
                hole_z = center_distance
            else:
                hole_z = 0

            hole_center = adsk.core.Point3D.create(hole_x, hole_y, hole_z) #make into inputs

            reinforcement_sketch = root.sketches.add(plane)
            reinforcement_sketch.name = "mounting hole reinforcement"

            reinforcementSketchCircles = reinforcement_sketch.sketchCurves.sketchCircles

            reinforcementSketchCircles.addByCenterRadius(hole_center, .15)

            reinforcement_extrude = extrudeFeatures.addSimple(reinforcement_sketch.profiles.item(0), adsk.core.ValueInput.createByReal(reinforcement_depth), join_operation)

            hole_sketch = root.sketches.add(plane)
            hole_sketch.name = "hanger hole sketch"

            holeSketchCircles = hole_sketch.sketchCurves.sketchCircles

            holeSketchCircles.addByCenterRadius(hole_center, hole_radius)

            cut_distance = adsk.core.ValueInput.createByString("1 in")

            hole_extrude = extrudeFeatures.addSimple(hole_sketch.profiles.item(0), cut_distance, cut_operation)

        def openProfileThinExtrude(profile_collection, input_width: float, input_depth: float):

            ext_input = extrudeFeatures.createInput(profile_collection, join_operation)

            wallLocation = adsk.fusion.ThinExtrudeWallLocation.Center
            width = adsk.core.ValueInput.createByReal(input_width)
            depth = adsk.core.ValueInput.createByReal(input_depth)
            distance_extent = adsk.fusion.DistanceExtentDefinition.create(depth)
            direction = adsk.fusion.ExtentDirections.PositiveExtentDirection
            ext_input.setOneSideExtent(distance_extent, direction)
            ext_input.setThinExtrude(wallLocation, width)

            # Create the feature.
            extrusion = extrudeFeatures.add(ext_input)
            return extrusion

        def cirPattern(input_entities, pattern_num: int, axis: adsk.core.Base):

            cirPatternInput = cirPatternFeatures.createInput(input_entities, axis)
            cirPatternInput.quantity = adsk.core.ValueInput.createByReal(pattern_num)
            cirPatternInput.totalAngle = adsk.core.ValueInput.createByString('360 deg')
            cirPatternInput.isSymmetric = False
        
            cir_pattern = cirPatternFeatures.add(cirPatternInput)

            return cir_pattern
        
        arm_sketch = root.sketches.add(working_plane)
        arm_sketch.name = "snowflake arm sketch"

        arm_sketch_lines = arm_sketch.sketchCurves.sketchLines

        arm_line_collection = adsk.core.ObjectCollection.create()

        for snowflake_line in snowflake_lines:
            p1 = adsk.core.Point3D.create(snowflake_line.p1x, snowflake_line.p1y, 0)
            p2 = adsk.core.Point3D.create(snowflake_line.p2x, snowflake_line.p2y, 0)
            new_line = arm_sketch_lines.addByTwoPoints(p1, p2)

        arm_profile_collection = adsk.core.ObjectCollection.create()

        for line in arm_sketch_lines:
            arm_line_collection.add(line)
            profile = root.createOpenProfile(line)
            arm_profile_collection.add(profile)
    
        arm_extrusion = openProfileThinExtrude(arm_profile_collection, arm_width, arm_depth)

        arm_bodies = arm_extrusion.bodies

        cirPatternInputEntities = adsk.core.ObjectCollection.create()

        for body in arm_bodies: # 1 for now
            cirPatternInputEntities.add(body)

        cirPattern(cirPatternInputEntities, 6, z_axis)

        join_sketch = root.sketches.add(working_plane)
        join_sketch.name = 'join sketch'
        join_sketch_circles = join_sketch.sketchCurves.sketchCircles
        join_sketch_circles.addByCenterRadius(origin, 0.0625)

        join_extrude_distance = adsk.core.ValueInput.createByString("0.001 in")
        join_circle_profile = join_sketch.profiles.item(0)
        join_extrude = extrudeFeatures.addSimple(join_circle_profile, join_extrude_distance, join_operation)    


        snowflake_body = join_extrude.bodies.item(0)
        snowflake_body.name = "snowflake body"
        
        # hole:
        hole_offset = 0.15
        mounting_hole_distance = arm_length_input - hole_offset
        mountingHole(center_distance=mounting_hole_distance, direction=y_axis, plane = working_plane, reinforcement_radius = 0.15, hole_radius= 0.06)

        ui.messageBox('Snowflake base created successfully.')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))