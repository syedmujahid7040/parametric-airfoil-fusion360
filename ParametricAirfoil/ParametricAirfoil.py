# Parametric Airfoil by Syed Mujahid - Autodesk Fusion add-in
# https://github.com/syedmujahid7040/parametric-airfoil-fusion360
#
# Creates an airfoil sketch that is driven by user parameters (chord and trailing-edge thickness).
# Every spline point is dimensioned with an expression, so changing the chord in
# MODIFY > Change Parameters resizes the airfoil - and everything built on it - live.
# The blunt trailing edge is closed with a line, so the profile always extrudes / lofts.
#
# MIT License - Copyright (c) 2026 Syed Mujahid

import os
import re
import traceback

import adsk.core
import adsk.fusion

from . import airfoil_core as core

CMD_ID = 'SyedMujahid_ParametricAirfoil'
CMD_NAME = 'Parametric Airfoil'
CMD_TOOLTIP = ('Parametric Airfoil by Syed Mujahid\n\n'
               'Create an airfoil sketch whose chord and trailing-edge thickness are user parameters. '
               'Pick Clark Y, NACA 0009 or any .dat file, choose a plane, and change the chord any time '
               'in Change Parameters.')
PANEL_ID = 'SolidCreatePanel'                 # SOLID > CREATE (an existing panel, as Autodesk asks)
OLD_PANEL_IDS = ['SolidScriptsAddinsPanel']   # where version 1.0.0 placed the button
IMPORT_ITEM = 'Import .dat file...'
HELP_URL = 'https://github.com/syedmujahid7040/parametric-airfoil-fusion360#how-to-use'
PRIVACY_URL = 'https://github.com/syedmujahid7040/parametric-airfoil-fusion360/blob/main/PRIVACY.md'
HERE = os.path.dirname(os.path.abspath(__file__))
RESOURCES = os.path.join(HERE, 'resources', 'ParametricAirfoil')

_app = None
_ui = None
_handlers = []
_state = {'dat_path': '', 'dat_name': ''}


# ================================================================================================
# Add-in entry points
def run(context):
    global _app, _ui
    try:
        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        cmd_def = _ui.commandDefinitions.itemById(CMD_ID)
        if cmd_def:
            cmd_def.deleteMe()
        cmd_def = _ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_TOOLTIP, RESOURCES)
        try:
            cmd_def.toolClipFilename = os.path.join(RESOURCES, 'toolclip.png')
        except Exception:
            pass

        on_created = CommandCreatedHandler()
        cmd_def.commandCreated.add(on_created)
        _handlers.append(on_created)

        for old_id in OLD_PANEL_IDS:
            old = _ui.allToolbarPanels.itemById(old_id)
            if old and old.controls.itemById(CMD_ID):
                old.controls.itemById(CMD_ID).deleteMe()

        panel = _ui.allToolbarPanels.itemById(PANEL_ID)
        if panel and not panel.controls.itemById(CMD_ID):
            ctrl = panel.controls.addCommand(cmd_def)
            ctrl.isPromotedByDefault = True       # icon shown directly on the SOLID > CREATE toolbar
            ctrl.isPromoted = True

        if not context.get('IsApplicationStartup', True):
            # started manually from Scripts and Add-Ins: tell the user where the button is
            _ui.messageBox('Parametric Airfoil is ready.\n\nFind it in the DESIGN workspace under\n'
                           'SOLID > CREATE > Parametric Airfoil.', CMD_NAME)
    except Exception:
        if _ui:
            _ui.messageBox('Parametric Airfoil failed to start:\n' + traceback.format_exc())


def stop(context):
    try:
        for pid in [PANEL_ID] + OLD_PANEL_IDS:
            panel = _ui.allToolbarPanels.itemById(pid)
            ctrl = panel.controls.itemById(CMD_ID) if panel else None
            if ctrl:
                ctrl.deleteMe()
        cmd_def = _ui.commandDefinitions.itemById(CMD_ID)
        if cmd_def:
            cmd_def.deleteMe()
        _handlers.clear()
    except Exception:
        if _ui:
            _ui.messageBox('Parametric Airfoil failed to stop:\n' + traceback.format_exc())


# ================================================================================================
# Dialog
def _design():
    return adsk.fusion.Design.cast(_app.activeProduct)


def _unique_sketch_name(comp, base):
    name, k = base, 2
    while comp.sketches.itemByName(name) is not None:
        name = '%s_%d' % (base, k)
        k += 1
    return name


def _default_param_value(design, name, fallback_cm):
    p = design.userParameters.itemByName(name) if design else None
    return p.value if p else fallback_cm


class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def notify(self, args):
        try:
            design = _design()
            if design is None:
                _ui.messageBox('Open a design in the DESIGN workspace first.', CMD_NAME)
                return
            cmd = args.command
            cmd.setDialogInitialSize(380, 420)
            inputs = cmd.commandInputs

            dd = inputs.addDropDownCommandInput('airfoil', 'Airfoil', adsk.core.DropDownStyles.TextListDropDownStyle)
            for i, name in enumerate(core.BUILTIN.keys()):
                dd.listItems.add(name, i == 0, '')
            dd.listItems.add(IMPORT_ITEM, False, '')
            dd.tooltip = 'Built-in airfoils, or any Selig / Lednicer .dat file (e.g. from the UIUC airfoil database).'

            browse = inputs.addBoolValueInput('browse', 'Choose .dat file', False, '', False)
            browse.isVisible = False
            info = inputs.addTextBoxCommandInput('datinfo', 'File', 'No file chosen', 2, True)
            info.isVisible = False

            sel = inputs.addSelectionInput('plane', 'Plane', 'Select a construction plane or planar face')
            sel.addSelectionFilter('ConstructionPlanes')
            sel.addSelectionFilter('PlanarFaces')
            sel.setSelectionLimits(1, 1)
            sel.tooltip = 'The airfoil is drawn on this plane with its leading edge at the sketch origin.'

            chord_name = inputs.addStringValueInput('chordname', 'Chord parameter', 'RootChord')
            chord_name.tooltip = 'Name of the user parameter that drives the chord. Use a new name (e.g. TailChord) for a second airfoil.'
            inputs.addValueInput('chord', 'Chord length', 'mm',
                                 adsk.core.ValueInput.createByReal(_default_param_value(design, 'RootChord', 20.0)))

            te_name = inputs.addStringValueInput('tename', 'TE parameter', 'TE_Thk')
            te_name.tooltip = 'Name of the user parameter for the blunt trailing-edge thickness.'
            te = inputs.addValueInput('te', 'Trailing-edge thickness', 'mm',
                                      adsk.core.ValueInput.createByReal(_default_param_value(design, 'TE_Thk', 0.1)))
            te.tooltip = 'Keep at 0.5 mm or more; about 1 mm prints well.'

            res = inputs.addIntegerSpinnerCommandInput('points', 'Points per surface', 15, 61, 1, 25)
            res.tooltip = 'Spline points on each of the upper and lower surfaces (25 is plenty for most wings).'

            look = inputs.addBoolValueInput('lookat', 'Look at airfoil', True, '', True)
            look.tooltip = 'Turn the view to face the sketch plane, so the airfoil is shown flat with the leading edge on the left.'

            inputs.addTextBoxCommandInput(
                'note', '',
                '<i>If a parameter with that name already exists it is reused (its current value wins), '
                'so several sketches can share one chord.</i>', 3, True)
            inputs.addTextBoxCommandInput(
                'credit', '',
                '<small>Parametric Airfoil by Syed Mujahid &nbsp;·&nbsp; '
                '<a href="%s">Help</a> &nbsp;·&nbsp; <a href="%s">Privacy policy</a></small>' % (HELP_URL, PRIVACY_URL),
                1, True)

            for h, ev in ((ExecuteHandler(), cmd.execute),
                          (InputChangedHandler(), cmd.inputChanged),
                          (ValidateHandler(), cmd.validateInputs)):
                ev.add(h)
                _handlers.append(h)
        except Exception:
            _ui.messageBox('Failed:\n' + traceback.format_exc())


def _pick_dat_file(inputs):
    dlg = _ui.createFileDialog()
    dlg.title = 'Choose an airfoil .dat file'
    dlg.filter = 'Airfoil coordinates (*.dat;*.txt;*.csv);;All files (*.*)'
    if dlg.showOpen() != adsk.core.DialogResults.DialogOK:
        return
    path = dlg.filename
    try:
        with open(path, 'r', errors='replace') as f:
            name, X, YU, YL = core.dat_stations(f.read(), 25)
        core.check_stations(X, YU, YL)
        _state['dat_path'], _state['dat_name'] = path, name
        inputs.itemById('datinfo').text = '%s\n%s' % (name, os.path.basename(path))
    except core.AirfoilError as e:
        _state['dat_path'] = ''
        inputs.itemById('datinfo').text = 'Could not read file: %s' % e


class InputChangedHandler(adsk.core.InputChangedEventHandler):
    def notify(self, args):
        try:
            inputs = args.inputs
            changed = args.input
            if changed.id == 'airfoil':
                is_dat = changed.selectedItem.name == IMPORT_ITEM
                inputs.itemById('browse').isVisible = is_dat
                inputs.itemById('datinfo').isVisible = is_dat
                if is_dat and not _state['dat_path']:
                    _pick_dat_file(inputs)
            elif changed.id == 'browse':
                _pick_dat_file(inputs)
            elif changed.id in ('chordname', 'tename'):
                # show the existing parameter's value so the user sees what will be used
                design = _design()
                p = design.userParameters.itemByName(changed.value.strip())
                if p:
                    inputs.itemById('chord' if changed.id == 'chordname' else 'te').value = p.value
        except Exception:
            pass


_NAME_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


class ValidateHandler(adsk.core.ValidateInputsEventHandler):
    def notify(self, args):
        try:
            inputs = args.inputs
            cn = inputs.itemById('chordname').value.strip()
            tn = inputs.itemById('tename').value.strip()
            ok = bool(_NAME_RE.match(cn)) and bool(_NAME_RE.match(tn)) and cn != tn
            ok = ok and inputs.itemById('chord').value > 0.01 and inputs.itemById('te').value > 0.001
            if inputs.itemById('airfoil').selectedItem.name == IMPORT_ITEM:
                ok = ok and bool(_state['dat_path'])
            args.areInputsValid = ok
        except Exception:
            args.areInputsValid = False


class ExecuteHandler(adsk.core.CommandEventHandler):
    def notify(self, args):
        try:
            inputs = args.command.commandInputs
            choice = inputs.itemById('airfoil').selectedItem.name
            n = inputs.itemById('points').value
            if choice == IMPORT_ITEM:
                with open(_state['dat_path'], 'r', errors='replace') as f:
                    label, X, YU, YL = core.dat_stations(f.read(), n)
            else:
                label = choice
                X, YU, YL = core.builtin_stations(choice, n)
            core.check_stations(X, YU, YL)

            msg = build_airfoil(
                plane=inputs.itemById('plane').selection(0).entity,
                label=label, X=X, YU=YU, YL=YL,
                chord_name=inputs.itemById('chordname').value.strip(),
                chord_cm=inputs.itemById('chord').value,
                te_name=inputs.itemById('tename').value.strip(),
                te_cm=inputs.itemById('te').value,
                look_at=inputs.itemById('lookat').value)
            _ui.messageBox(msg, CMD_NAME)
        except core.AirfoilError as e:
            _ui.messageBox('Airfoil data problem: %s' % e, CMD_NAME)
        except Exception:
            _ui.messageBox('Failed:\n' + traceback.format_exc(), CMD_NAME)


# ================================================================================================
# Geometry
def _ensure_param(design, name, value_cm, comment):
    p = design.userParameters.itemByName(name)
    if p is None:
        p = design.userParameters.add(name, adsk.core.ValueInput.createByReal(value_cm), 'mm', comment)
        return p, True
    return p, False


def _resolve_plane(entity, design):
    """Return (component, planar entity) to sketch on, handling planes/faces picked inside an occurrence."""
    occ = getattr(entity, 'assemblyContext', None)
    native = entity.nativeObject if occ else entity
    if occ:
        return occ.component, native
    if native.objectType == adsk.fusion.ConstructionPlane.classType():
        comp = native.component
    else:
        comp = native.body.parentComponent
    return comp, native


def _world_up():
    """World 'up' as set in Fusion preferences (Z-up or Y-up)."""
    try:
        o = _app.preferences.generalPreferences.defaultModelingOrientation
        if o == adsk.core.DefaultModelingOrientations.YUpModelingOrientation:
            return adsk.core.Vector3D.create(0, 1, 0)
    except Exception:
        pass
    return adsk.core.Vector3D.create(0, 0, 1)


def _sketch_to_world(sk):
    """Matrix from sketch space to world space (includes the occurrence transform for sub-components)."""
    m = sk.transform.copy()
    design = _design()
    comp = sk.parentComponent
    if comp != design.rootComponent:
        occs = design.rootComponent.allOccurrencesByComponent(comp)
        if occs.count:
            m.transformBy(occs.item(0).transform2)
    return m


def _orientation(sk):
    """Pick the in-sketch chord direction c and thickness direction t (each one of +/-X, +/-Y of the sketch)
    so the airfoil sits upright in the world: thickness along world up, chord horizontal and pointing
    toward +X (or +Y / +Z when the plane contains no X direction).
    Returns ((cx, cy), (tx, ty)) as 2D unit vectors in sketch space."""
    m = _sketch_to_world(sk)
    axes = []
    for v2 in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        v = adsk.core.Vector3D.create(v2[0], v2[1], 0)
        v.transformBy(m)
        v.normalize()
        axes.append((v2, v))
    up = _world_up()
    t2, tv = max(axes, key=lambda a: a[1].dotProduct(up))
    if tv.dotProduct(up) < 0.5:
        # plane faces up (a "top" plane): there is no up direction in it - keep the sketch's own axes
        return (1, 0), (0, 1)
    cands = [a for a in axes if abs(a[0][0] * t2[0] + a[0][1] * t2[1]) == 0]   # perpendicular to t
    prefs = [adsk.core.Vector3D.create(1, 0, 0), adsk.core.Vector3D.create(0, 1, 0), adsk.core.Vector3D.create(0, 0, 1)]
    for pref in prefs:
        best = max(cands, key=lambda a: a[1].dotProduct(pref))
        if best[1].dotProduct(pref) > 0.5:
            return best[0], t2
    return cands[0][0], t2


def _p2(c, t, along_c, along_t):
    """Sketch point at (along_c, along_t) in the airfoil's own (chord, thickness) axes."""
    return adsk.core.Point3D.create(c[0] * along_c + t[0] * along_t, c[1] * along_c + t[1] * along_t, 0)


def look_at_sketch(sk, chord, c, t):
    """Turn the camera to face the airfoil: thickness direction up, chord to the right (leading edge
    on the left), orthographic, framed on the airfoil."""
    m = _sketch_to_world(sk)
    o = _p2(c, t, 0.5 * chord, 0)
    o.transformBy(m)
    cw = adsk.core.Vector3D.create(c[0], c[1], 0); cw.transformBy(m); cw.normalize()
    tw = adsk.core.Vector3D.create(t[0], t[1], 0); tw.transformBy(m); tw.normalize()
    d = cw.crossProduct(tw)                            # eye direction that puts chord on screen-right
    d.normalize()
    d.scaleBy(4 * chord)
    eye = o.copy()
    eye.translateBy(d)
    vp = _app.activeViewport
    cam = vp.camera
    cam.isSmoothTransition = True
    cam.cameraType = adsk.core.CameraTypes.OrthographicCameraType
    cam.target = o
    cam.eye = eye
    cam.upVector = tw
    cam.isFitView = False
    cam.viewExtents = 0.75 * chord                     # frame the airfoil itself, not the whole model
    vp.camera = cam
    vp.refresh()


def build_airfoil(plane, label, X, YU, YL, chord_name, chord_cm, te_name, te_cm, look_at=True):
    design = _design()
    comp, plane_ent = _resolve_plane(plane, design)

    chord_p, chord_new = _ensure_param(design, chord_name, chord_cm, 'Airfoil chord - change this to resize the airfoil')
    te_p, te_new = _ensure_param(design, te_name, te_cm, 'Trailing-edge thickness (keep >= 0.5 mm)')
    chord, te = chord_p.value, te_p.value            # Fusion works in cm internally

    rows = core.point_rows(X, YU, YL)
    le_index = len(X) - 1
    last = len(rows) - 1

    safe = re.sub(r'[^A-Za-z0-9_]+', '_', label).strip('_') or 'Airfoil'
    sk = comp.sketches.add(plane_ent)
    sk.name = _unique_sketch_name(comp, 'Airfoil_%s_%s' % (safe, chord_name))

    # chord / thickness directions inside the sketch, so the airfoil is upright in the world
    c, t = _orientation(sk)
    H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    V = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    chord_dir = H if c[0] != 0 else V                # dimension orientation along the chord
    thick_dir = V if c[0] != 0 else H                # ... and across it

    try:
        sk.isComputeDeferred = True
    except Exception:
        pass
    try:
        pts = adsk.core.ObjectCollection.create()
        for row in rows:
            x, y = core.point_xy(row, chord, te)
            pts.add(_p2(c, t, x, y))
        spline = sk.sketchCurves.sketchFittedSplines.add(pts)
        fps = spline.fitPoints
        if fps.count != len(rows):
            raise RuntimeError('Expected %d fit points but Fusion returned %d' % (len(rows), fps.count))

        origin = sk.originPoint
        dims = sk.sketchDimensions
        cons = sk.geometricConstraints

        # Reference point one chord "below" the origin (against the thickness direction). Thickness
        # dimensions are measured from here so they are always positive, even where a cambered lower
        # surface rises above the chord line.
        ref_line = sk.sketchCurves.sketchLines.addByTwoPoints(origin, _p2(c, t, 0, -chord))
        ref_line.isConstruction = True
        if thick_dir == V:
            cons.addVertical(ref_line)
        else:
            cons.addHorizontal(ref_line)
        ref = ref_line.endSketchPoint
        d = dims.addDistanceDimension(origin, ref, thick_dir, _p2(c, t, -0.3 * chord, -0.5 * chord))
        d.parameter.expression = chord_name

        for i, row in enumerate(rows):
            fp = fps.item(i)
            if i == le_index:
                cons.addCoincident(fp, origin)
                continue
            x, y = core.point_xy(row, chord, te)
            h_expr, v_expr = core.expressions(row, chord_name, te_name)
            dh = dims.addDistanceDimension(origin, fp, chord_dir, _p2(c, t, x, -0.6 * chord))
            dh.parameter.expression = h_expr
            dv = dims.addDistanceDimension(ref, fp, thick_dir, _p2(c, t, -0.15 * chord, y))
            dv.parameter.expression = v_expr

        # close the blunt trailing edge so the profile is always a single closed region
        sk.sketchCurves.sketchLines.addByTwoPoints(fps.item(0), fps.item(last))
    finally:
        try:
            sk.isComputeDeferred = False
        except Exception:
            pass
    try:
        sk.areDimensionsShown = False                # ~100 dimensions would clutter the canvas
    except Exception:
        pass
    if look_at:
        try:
            look_at_sketch(sk, chord, c, t)
        except Exception:
            pass                                     # the view is a convenience; never fail the command

    def pinfo(p, new):
        return '%s = %s%s' % (p.name, p.expression, '' if new else '  (existing parameter reused)')

    return ('Airfoil "%s" created in sketch "%s".\n\n'
            'Closed profiles: %d (should be 1)\n'
            '%s\n%s\n\n'
            'To resize: MODIFY > Change Parameters and edit %s.' %
            (label, sk.name, sk.profiles.count, pinfo(chord_p, chord_new), pinfo(te_p, te_new), chord_name))
