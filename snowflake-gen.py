import adsk.core, adsk.fusion, traceback

# https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-CB1A2357-C8CD-474D-921E-992CA3621D04
# the code is the same as this above example (I think) but is not working

radius = 4
depth = 1

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

        circle_profile = sketch_1.profiles.item(0)

        extrude1 = extrudes.addSimple(circle_profile, depth, adsk.fusion.FeatureOperations.NewBodyFeatureOperation) 

        body1 = extrude1.bodies.item(0)

        body1.name = "body name test"

        ui.messageBox('Snowflake base created successfully.')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
