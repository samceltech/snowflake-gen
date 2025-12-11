import adsk.core, adsk.fusion, traceback, tempfile

# https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-CB1A2357-C8CD-474D-921E-992CA3621D04
# the code is the same as this above example (I think) but is not working

radius = 4
depth = 1
depth_cm = 1 * 2.54

# [[[x, y]]] or some other coordinate, doesn't matter

class SnowflakeLine:
    def __init__(self, p1x, p1y, p2x, p2y):
        self.p1x = p1x
        self.p1y = p1y
        self.p2x = p2x
        self.p2y = p2y

snowflake_lines = [SnowflakeLine(0,0,5,0),SnowflakeLine(2,0,3,2), SnowflakeLine(2,0,3,-2), SnowflakeLine(5,0,6,1), SnowflakeLine(5,0,6,-1)]

# test_line_coords = [[[0,0], [1,0]], [[1,0],[2,1]]]

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        ui.messageBox('Snowflake Script Running...')

        design = app.activeProduct
        if not isinstance(design, adsk.fusion.Design):
            ui.messageBox('Please switch to Design workspace first.')
            return
        
        export_manager = design.exportManager

        root = design.rootComponent

        extrudes = root.features.extrudeFeatures

        # surface_feats = root.features.surfaceFeatures

        """ I think this broke because we are trying to create a parameter
        (like a fusion variable kinda) that already exists, and we need to
        reset it or delete it before making it again or it breaks.
        Probably not necessary for this program anyway"""
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

        #we will need to make an algorithm to spit out a bunch of points, then put them all into point3D.create()
        # p1 = adsk.core.Point3D.create(0, 0, 0)
        # p2 = adsk.core.Point3D.create(5, 0, 0)

        # test_line = sketch2Lines.addByTwoPoints(p1, p2) # eventually will be for every line in the shape

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
        operation = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        input = extrudeFeatures.createInput(profile_collection, operation)
        wallLocation = adsk.fusion.ThinExtrudeWallLocation.Center
        wallThickness = adsk.core.ValueInput.createByString("0.125 in")
        distance = adsk.core.ValueInput.createByString("0.0625 in")
        isFullLength = True
        input.setSymmetricExtent(distance, isFullLength)
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

        # msg = str(type(tool_bodies)) # collection as is required
        # msg2 = str(type(target_body)) #brepbody as is required

        # ui.messageBox(msg) 
        # ui.messageBox(msg2)

        # Define the required inputs and create te combine feature.

        # targetBody = ui.selectEntity('Select a body', 'Bodies').entity

        combineFeatures = root.features.combineFeatures

        combine_input: adsk.fusion.CombineFeatureInput = combineFeatures.createInput(target_body, tool_bodies)
        combine_input.isNewComponent = False
        combine_input.isKeepToolBodies = False
        combine_input.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        # combineFeature = combineFeatures.add(combine_input) #hmm, still breaking

        ## INCLUDING THIS MAKES IT NOT RUN AT ALL??
        ## tmp_dir = tempfile.gettempdir()

        # comp = root

        # stl_options = export_manager.createSTLExportOptions(comp, "C:\Users\samso\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\Scripts\snowflake-gen\export_test\comp.stl")

        # export = export_manager.execute(stl_options)

        ui.messageBox('Snowflake base created successfully.')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))





        """
        CIRCLES

        # sketch_1 = root.sketches.add(root.xYConstructionPlane)
        # sketch_1.name = 'Snowflake Base Sketch'
        # sketchCircles = sketch_1.sketchCurves.sketchCircles

        # sketchCircles.addByCenterRadius(
        #     adsk.core.Point3D.create(0,0,0),
        #     # size_param.value
        #     radius
        # )

        # # distance = adsk.core.ValueInput.createByString("1 in")

        # #looks like this does cm by default. createbyreal probabaly easier to use overall
        # extrude_distance = adsk.core.ValueInput.createByReal(depth_cm)

        # circle_profile = sketch_1.profiles.item(0)

        # # chatgpt's way (works too): 
        # # ext_input = extrudes.createInput(circle_profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        # # ext_input.setDistanceExtent(False, distance)
        # # extrude1 = extrudes.add(ext_input)

        # # note: MAKE SURE DIMENSION INPUTS ARE VALUEINPUTS
        # extrude1 = extrudes.addSimple(circle_profile, extrude_distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)    

        body1 = extrude1.bodies.item(0)

        body1.name = "body name test"

        
        """