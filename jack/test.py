# generate_f3d_robust.py
import adsk.core, adsk.fusion, traceback, os, argparse, time

def get_design_from_document(doc, ui=None):
    # Preferred: get the Design product from the document's products collection
    try:
        products = doc.products
        design_prod = products.itemByProductType('DesignProductType')
        if design_prod:
            design = adsk.fusion.Design.cast(design_prod)
            if design:
                return design
    except:
        if ui:
            print("Warning: couldn't get design via doc.products.itemByProductType()")

    # Fallback: use app.activeProduct if it's a design
    try:
        app = adsk.core.Application.get()
        active = app.activeProduct
        design = adsk.fusion.Design.cast(active)
        if design:
            return design
    except:
        pass

    return None

def create_new_document(ui=None):
    app = adsk.core.Application.get()
    docs = app.documents
    # Documents.add currently expects at least the documentType (and visible in some API flavors)
    # We'll call with only the documentType and let the API accept defaults, but be ready to pass visible=True.
    try:
        doc = docs.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    except TypeError:
        # Some API variants require visible flag
        try:
            doc = docs.add(adsk.core.DocumentTypes.FusionDesignDocumentType, True)
        except TypeError:
            # Some variants require options as well — pass None for options if needed
            doc = docs.add(adsk.core.DocumentTypes.FusionDesignDocumentType, True, None)
    # Small delay to let Fusion initialize the new doc/product
    time.sleep(0.2)
    return doc

def create_circle_sketch(root_comp, size_in):
    dia_cm = size_in * 2.54
    sketch = root_comp.sketches.add(root_comp.xYConstructionPlane)
    sketch.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(0,0,0), dia_cm/2
    )
    return sketch

def create_square_sketch(root_comp, size_in):
    side_cm = size_in * 2.54
    h = side_cm / 2.0
    #sketch = root_comp.sketches.add(root_comp.xYConstructionPlane)
    construction_planes = root_comp.constructionPlanes
    xy_plane = construction_planes.item(0)   # Index 0 is ALWAYS the XY Plane
    print("HERE")
    sketch = root_comp.sketches.add(xy_plane, None)

    print("HERE1")
    lines = sketch.sketchCurves.sketchLines
    pts = [
        adsk.core.Point3D.create(-h, -h, 0),
        adsk.core.Point3D.create( h, -h, 0),
        adsk.core.Point3D.create( h,  h, 0),
        adsk.core.Point3D.create(-h,  h, 0)
    ]
    for i in range(4):
        lines.addByTwoPoints(pts[i], pts[(i+1)%4])
    return sketch

def save_document_as(doc, filepath):
    # For a new document you must use saveAs to set location/name (per docs).
    # Build SaveOptions if available, otherwise call saveAs with minimal args.
    try:
        saveOpts = adsk.core.SaveOptions.create()
    except:
        saveOpts = None
    # Document.saveAs exists in current API docs.
    # Provide isSavingAs flag via SaveOptions if supported; otherwise call simplest overload.
    if saveOpts:
        try:
            doc.saveAs(filepath, saveOpts)
            return True
        except:
            pass
    try:
        doc.saveAs(filepath)
        return True
    except Exception:
        return False

def run_main(circle=None, square=None, output='output.f3d'):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface


        # Create new document
        doc = create_new_document(ui)
        if not doc:
            print('Failed to create new document.')
            return

        # Get Design product from the doc (preferred) or app.activeProduct (fallback)
        design = get_design_from_document(doc, ui)
        if not design:
            print('Could not find a Design product in the new document.')
            return
        
        # new addition, for debugging reasons
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType


        # design.rootComponent is the correct way to access the root component.
        root = design.rootComponent
        if root is None:
            print('design.rootComponent is None. The design may not be initialized yet.')
            return
        print("About to Sketch")

        if circle:
            create_circle_sketch(root, circle)

        if square:
            create_square_sketch(root, square)

        ## Save file (for a brand new, never-saved document saveAs is required)
        #out_path = os.path.abspath(output)
        #ok = save_document_as(doc, out_path)
        #if ok:
        #    print(f'Saved: {out_path}')
        #else:
        #    print('Save failed. Check permissions and path.')

        export_mgr = design.exportManager

        out_path = os.path.abspath(output)

        opts = export_mgr.createFusionArchiveExportOptions(out_path)
        success = export_mgr.execute(opts)

        if success:
            print(f"Saved: {out_path}")
        else:
            print("Save failed.")


    except Exception as e:
        print(e)
        if ui:
            print('Error:\n{}'.format(traceback.format_exc()))
            pass
        else:
            print(traceback.format_exc())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--circle', type=float, help='circle diameter in inches')
    parser.add_argument('--square', type=float, help='square side in inches')
    parser.add_argument('--output', required=True, help='output .f3d filename')
    args = parser.parse_args()
    run_main(circle=args.circle, square=args.square, output=args.output)
