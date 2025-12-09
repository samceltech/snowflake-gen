import adsk.core, adsk.fusion, traceback

# https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-CB1A2357-C8CD-474D-921E-992CA3621D04
# the code is the same as this above example (I think) but is not working

radius = 4
depth = 1
depth_cm = 1 * 2.54

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
        sketch_1 = root.sketches.add(root.xYConstructionPlane)
        sketch_1.name = 'Snowflake Base Sketch'

        # Circle
        sketchCircles = sketch_1.sketchCurves.sketchCircles

        #add a circle of radius 4
        sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(0,0,0),
            # size_param.value
            radius
        )

        # distance = adsk.core.ValueInput.createByString("1 in")

        #looks like this does cm by default. createbyreal probabaly easier to use overall
        extrude_distance = adsk.core.ValueInput.createByReal(depth_cm)

        circle_profile = sketch_1.profiles.item(0)

        # chatgpt's way (works too): 
        # ext_input = extrudes.createInput(circle_profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        # ext_input.setDistanceExtent(False, distance)
        # extrude1 = extrudes.add(ext_input)

        # note: MAKE SURE DIMENSION INPUTS ARE VALUEINPUTS
        extrude1 = extrudes.addSimple(circle_profile, extrude_distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation) 
        
        body1 = extrude1.bodies.item(0)

        body1.name = "body name test"

        # messing with lines
        # note: for some reason VScode isn't autofilling/recognizing sketchLines
        sketch_2 = root.sketches.add(root.xYConstructionPlane)
        sketch_2.name = "snowflake base sketch 2"

        sketch2Lines = sketch_2.sketchCurves.sketchLines

        #we will need to make an algorithm to spit out a bunch of points, then put them all into point32.create()
        p1 = adsk.core.Point3D.create(0, 0, 0)
        p2 = adsk.core.Point3D.create(5, 0, 0)

        line = sketch2Lines.addByTwoPoints(p1, p2) # eventually will be for every line in the shape

        # # https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-536A4E7D-AA90-4ACB-9378-009993C59FF2
        # # Have the profile selected.
        filter =  adsk.core.SelectionCommandInput.SketchCurves
        curve = ui.selectEntity('Select a profile', filter).entity

        # Define the required input.
        extrudeFeatures = root.features.extrudeFeatures
        operation = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        input = extrudeFeatures.createInput(curve, operation)
        wallLocation = adsk.fusion.ThinExtrudeWallLocation.Center
        wallThickness = adsk.core.ValueInput.createByString("2 mm")
        input.setThinExtrude(wallLocation, wallThickness)
        distance = adsk.core.ValueInput.createByString("100 mm")
        isFullLength = True
        input.setSymmetricExtent(distance, isFullLength)

        # Create the feature.
        extrudeFeature = extrudeFeatures.add(input)

        # fix with this:
        # https://forums.autodesk.com/t5/fusion-api-and-scripts-forum/thin-extrude-an-open-profile-via-api/td-p/11566052


        ui.messageBox('Snowflake base created successfully.')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
