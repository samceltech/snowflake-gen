import adsk.core, adsk.fusion, traceback, tempfile
import math
import random

# from snowflake_algorithm import generate

# https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-CB1A2357-C8CD-474D-921E-992CA3621D04
# the code is the same as this above example (I think) but is not working

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

        extrudes = root.features.extrudeFeatures

        # ---- PARAMETER ----
        # params = design.userParameters
        # size_param = params.add(
        #     'snowflakeSize',
        #     adsk.core.ValueInput.createByString('4 in'),
        #     'in',
        #     'Size of the snowflake base shape'
        # )
        
        # ---- SKETCH ----

        # messing with lines
        # note: for some reason VScode isn't autofilling/recognizing sketchLines
        sketch_2 = root.sketches.add(root.xYConstructionPlane)
        sketch_2.name = "snowflake base sketch 2"

        sketch2Lines = sketch_2.sketchCurves.sketchLines

        line_collection = adsk.core.ObjectCollection.create()

        for snowflake_line in snowflake_lines:
            p1 = adsk.core.Point3D.create(snowflake_line.p1x, snowflake_line.p1y, 0)
            p2 = adsk.core.Point3D.create(snowflake_line.p2x, snowflake_line.p2y, 0)
            new_line = sketch2Lines.addByTwoPoints(p1, p2)

        # # https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-536A4E7D-AA90-4ACB-9378-009993C59FF2
        # # Have the profile selected.
        filter =  adsk.core.SelectionCommandInput.SketchCurves
        # curve = ui.selectEntity('Select a profile', filter).entity

        profile_collection = adsk.core.ObjectCollection.create()

        for line in sketch2Lines:
            line_collection.add(line)
            profile = root.createOpenProfile(line)
            profile_collection.add(profile)
            
    
        # Define the required input.
        extrudeFeatures = root.features.extrudeFeatures
        operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        input = extrudeFeatures.createInput(profile_collection, operation)
        wallLocation = adsk.fusion.ThinExtrudeWallLocation.Center
        wallThickness = adsk.core.ValueInput.createByString("2 mm")
        distance = adsk.core.ValueInput.createByString("1 mm")
        distance_extent = adsk.fusion.DistanceExtentDefinition.create(distance)
        direction = adsk.fusion.ExtentDirections.PositiveExtentDirection
        isFullLength = True
        input.setOneSideExtent(distance_extent, direction)
        input.setThinExtrude(wallLocation, wallThickness)

        # Create the feature.
        extrudeFeature = extrudeFeatures.add(input)

        extrude_bodies = extrudeFeature.bodies

        # https://forums.autodesk.com/t5/fusion-api-and-scripts-forum/thin-extrude-an-open-profile-via-api/td-p/11566052

        cirPatternInputEntities = adsk.core.ObjectCollection.create()

        for body in extrude_bodies: # 1 for now
            cirPatternInputEntities.add(body)

        cirPatternFeatures = root.features.circularPatternFeatures

        z_axis: adsk.core.Base = root.zConstructionAxis
        
        cirPatternInput = cirPatternFeatures.createInput(cirPatternInputEntities, z_axis)

        cirPatternInput.quantity = adsk.core.ValueInput.createByReal(6)
        cirPatternInput.totalAngle = adsk.core.ValueInput.createByString('360 deg')
        cirPatternInput.isSymmetric = False
        
        cir_pattern = cirPatternFeatures.add(cirPatternInput)

        pattern_bodies = cir_pattern.bodies

        tool_bodies = adsk.core.ObjectCollection.create()

        target_added = False

        for body in pattern_bodies:
            if target_added == False:
                target_body = body #put the first one as the target ... I guess
            if target_added == True:
                tool_bodies.add(body)

        sketch_1 = root.sketches.add(root.xYConstructionPlane)
        sketch_1.name = 'Snowflake Base Sketch'
        sketchCircles = sketch_1.sketchCurves.sketchCircles

        sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(0,0,0),
            # size_param.value
            radius
        )

        #looks like this does cm by default. createbyreal probabaly easier to use overall
        extrude_distance = adsk.core.ValueInput.createByString("0.001 in")

        circle_profile = sketch_1.profiles.item(0)

        # note: MAKE SURE DIMENSION INPUTS ARE VALUEINPUTS
        extrude1 = extrudes.addSimple(circle_profile, extrude_distance, adsk.fusion.FeatureOperations.JoinFeatureOperation)    

        body1 = extrude1.bodies.item(0)

        body1.name = "snowflake body"

        hole_distance = arm_length_input - hole_offset

        hole_center = adsk.core.Point3D.create(0, hole_distance, 0)

        reinforcement_sketch = root.sketches.add(root.xYConstructionPlane)
        reinforcement_sketch.name = "mounting hole reinforcement"

        reinforcementSketchCircles = reinforcement_sketch.sketchCurves.sketchCircles

        reinforcementSketchCircles.addByCenterRadius(hole_center, .15)

        reinforcement_extrude = extrudes.addSimple(reinforcement_sketch.profiles.item(0), adsk.core.ValueInput.createByReal(0.1), adsk.fusion.FeatureOperations.JoinFeatureOperation)

        hole_sketch = root.sketches.add(root.xYConstructionPlane)
        hole_sketch.name = "hanger hole sketch"

        holeSketchCircles = hole_sketch.sketchCurves.sketchCircles

        holeSketchCircles.addByCenterRadius(hole_center, 0.06)

        hole_distance = adsk.core.ValueInput.createByString("1 in")

        hole_extrude = extrudes.addSimple(hole_sketch.profiles.item(0), hole_distance, adsk.fusion.FeatureOperations.CutFeatureOperation)

        ## INCLUDING THIS MAKES IT NOT RUN AT ALL??
        ## tmp_dir = tempfile.gettempdir()

        # comp = root

        # stl_options = export_manager.createSTLExportOptions(comp, "C:\Users\samso\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\Scripts\snowflake-gen\export_test\comp.stl")

        # export = export_manager.execute(stl_options)

        ui.messageBox('Snowflake base created successfully.')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))