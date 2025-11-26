import adsk.core, adsk.fusion, traceback

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

        # ---- PARAMETER ----
        params = design.userParameters
        size_param = params.add(
            'snowflakeSize',
            adsk.core.ValueInput.createByString('4 in'),
            'in',
            'Size of the snowflake base shape'
        )
        
        # ---- SKETCH ----
        sketch = root.sketches.add(root.xYConstructionPlane)
        sketch.name = 'Snowflake Base Sketch'

        # Circle
        circles = sketch.sketchCurves.sketchCircles
        circles.addByCenterRadius(
            adsk.core.Point3D.create(0,0,0),
            size_param.value
        )

        ui.messageBox('Snowflake base created successfully.')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
