"""Text for the Autodesk Design and Make Marketplace submission form, with length checks.
Run: python tools/marketplace_fields.py  -> writes dist/MARKETPLACE_FORM.txt and dist/Help.html
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = 'https://github.com/syedmujahid7040/parametric-airfoil-fusion360'
PRIVACY = REPO + '/blob/main/PRIVACY.md'

FIELDS = [
    ('App Name', 50, 'Parametric Airfoil by Syed Mujahid'),

    ('App Short Description', 200,
     'Create airfoil sketches you can resize at any time. Clark Y, NACA 0009 or any .dat file, with chord and '
     'trailing-edge thickness as Fusion user parameters. Always a closed profile.'),

    ('App Description', 4000, f"""Airfoil importers draw a spline from a .dat file and leave you with a dead shape. You can't change the chord later, the profile often won't close for Extrude or Loft, and once a wing is built on it, even the Scale feature fails.

Parametric Airfoil builds the airfoil as a fully parameter-driven sketch instead. Every spline point is dimensioned with an expression of two user parameters: the chord (for example RootChord) and the trailing-edge thickness (TE_Thk). Change the chord at any time in Modify > Change Parameters, and the airfoil and every feature built on it update.

Features:
- Three airfoil sources: Clark Y, NACA 0009, or import any Selig or Lednicer .dat file (for example from the UIUC Airfoil Database)
- Chord and trailing-edge thickness are user parameters that appear in the Parameters dialog
- Blunt trailing edge closed with a line, so the profile always extrudes and lofts
- Sketch on any construction plane or planar face. The airfoil is placed upright (chord horizontal, upper surface up) and the view turns to face it
- Use different parameter names (RootChord, TipChord, TailChord) to build tapered wings and tails that stay editable
- Accurate import: cosine-spaced resampling that also handles highly cambered airfoils
- Button in SOLID > CREATE

How to use:
1. In the DESIGN workspace click SOLID > CREATE > Parametric Airfoil.
2. Choose Clark Y, NACA 0009, or Import .dat file.
3. Select a plane.
4. Enter the chord parameter name and length (for example RootChord = 280 mm) and the trailing-edge thickness (1 mm recommended).
5. Click OK, then Extrude or Loft the profile.
6. To resize later: MODIFY > Change Parameters, edit RootChord.

Built by Syed Mujahid while designing a VTOL UAV from scratch. Free and open source (MIT license).

Source code and documentation: {REPO}
Privacy policy (the add-in collects no data): {PRIVACY}"""),

    ('Publisher Privacy Policy', None, PRIVACY),

    ('App Version - Version Number', None, '1.0.0'),

    ('App Version - Version Description', None,
     'First release. Clark Y and NACA 0009 built in, plus import of any Selig or Lednicer .dat file. Chord and '
     'trailing-edge thickness driven by user parameters; closed profile with a blunt trailing edge; placed upright '
     'on any plane; button in SOLID > CREATE.'),

    ('Video link (Autodesk Screencast or YouTube)', None,
     'Upload brag.mp4 to YouTube (Public or Unlisted) and paste its link here. Leave empty if you skip the video.'),

    ('General Usage Instructions', None, """Parametric Airfoil adds a Parametric Airfoil button to SOLID > CREATE in the DESIGN workspace.

1. Click SOLID > CREATE > Parametric Airfoil.
2. Airfoil: choose Clark Y (wings), NACA 0009 (tails, symmetric) or Import .dat file (any Selig or Lednicer coordinate file).
3. Plane: select an origin plane, construction plane or planar face. The leading edge is placed on the sketch origin, with the chord horizontal and the upper surface facing up.
4. Chord parameter / Chord length: the user parameter that drives the chord, for example RootChord = 280 mm. If a parameter with that name already exists it is reused, so several sketches can share one chord.
5. TE parameter / Trailing-edge thickness: blunt trailing-edge thickness, for example TE_Thk = 1 mm.
6. Click OK. A closed airfoil profile is created; extrude or loft it as usual.
7. To resize the airfoil and everything built on it: MODIFY > Change Parameters, edit RootChord.

Tip: for a tapered wing, create the root airfoil with RootChord and the tip airfoil on an offset plane with TipChord, then Loft between them. Both chords stay editable."""),

    ('Installation/Uninstallation', 1000,
     'The installer copies Parametric Airfoil into the Autodesk ApplicationPlugins folder, and it loads '
     'automatically when Fusion starts. The button appears in the DESIGN workspace under SOLID > CREATE.\n\n'
     'To uninstall, uninstall it from the Autodesk App Manager, or with Windows Settings > Apps if installed '
     'with the Autodesk installer. You can also stop it in Fusion under UTILITIES > ADD-INS > Scripts and '
     'Add-Ins. Sketches and user parameters already created stay in your designs; delete them like any other '
     'feature.'),

    ('Support Information', 1000,
     f'Support is provided by the author, Syed Mujahid, through GitHub. Report bugs, ask questions or request '
     f'new airfoils by opening an issue at <a href="{REPO}/issues">{REPO}/issues</a>. '
     f'Most issues get a reply within a few days. Documentation: <a href="{REPO}">{REPO}</a>'),

    ('Additional Information', 2000,
     f'Free and open source (MIT license). Source code: <a href="{REPO}">{REPO}</a><br>'
     f'Privacy: the add-in collects no data and never connects to the internet. '
     f'<a href="{PRIVACY}">Privacy policy</a><br>'
     'Supported .dat formats: Selig (TE > upper > LE > lower > TE) and Lednicer (point counts, then upper and '
     'lower surfaces), as used by the UIUC Airfoil Coordinates Database.<br>'
     'Each surface is resampled to 15-61 cosine-spaced points (25 by default). The sketch is fully dimensioned '
     'from the chord and trailing-edge parameters, so it updates live when either changes.'),

    ('Known Issues', 1000,
     'Each airfoil uses about 100 driving dimensions, so creating a sketch takes a few seconds and dimensions are '
     'hidden by default. Very large chord changes (for example 10x) can take a moment to recompute. If a plane '
     'faces straight up (top view), the airfoil is drawn in the sketch\'s own X/Y directions.'),

    ('Learn More Url', None, REPO),
]

HELP_HTML = """<!doctype html><html><head><meta charset="utf-8"><title>Parametric Airfoil by Syed Mujahid - Help</title>
<style>body{font-family:Segoe UI,Arial,sans-serif;max-width:760px;margin:32px auto;padding:0 16px;line-height:1.55;color:#222}
h1{font-size:26px}h2{font-size:19px;margin-top:28px}code{background:#f2f2f2;padding:1px 4px;border-radius:3px}</style></head><body>
<h1>Parametric Airfoil by Syed Mujahid</h1>
<p>A free Autodesk Fusion add-in that creates airfoil sketches driven by user parameters, so you can change the chord at any time.</p>
<h2>How to use</h2><pre style="white-space:pre-wrap;font-family:inherit">{usage}</pre>
<h2>Install / uninstall</h2><p>{install}</p>
<h2>Support</h2><p>{support}</p>
<h2>More information</h2><p>{additional}</p>
<h2>Known issues</h2><p>{known}</p>
<p><a href="{repo}">{repo}</a> &middot; <a href="{privacy}">Privacy policy</a> &middot; MIT License &copy; 2026 Syed Mujahid</p>
</body></html>"""


def main():
    os.makedirs(os.path.join(ROOT, 'dist'), exist_ok=True)
    out = ['AUTODESK MARKETPLACE FORM - Parametric Airfoil by Syed Mujahid',
           'Copy each block into the field with the same name.', '']
    ok = True
    for name, limit, text in FIELDS:
        n = len(text)
        flag = ''
        if limit and n > limit:
            ok = False
            flag = '  <-- TOO LONG'
        lim = f' (limit {limit}, used {n})' if limit else ''
        out += ['=' * 70, f'{name}{lim}{flag}', '=' * 70, text, '']
    files = ['=' * 70, 'FILES', '=' * 70,
             'App File: ParametricAirfoil-Marketplace-1.0.0.zip (add-in bundle + Help.html)',
             'App Icon: icon-120.png (120 x 120)',
             'App Screenshots: 1-dialog.jpg, 2-airfoil-sketch.jpg, 3-extruded-wing.jpg, 4-change-parameters.jpg, '
             '5-resized-wing.jpg (each under 2 MB)']
    out += files
    with open(os.path.join(ROOT, 'dist', 'MARKETPLACE_FORM.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')
    d = {k: v for k, _, v in FIELDS}
    html = HELP_HTML
    for k, v in (('usage', d['General Usage Instructions']), ('install', d['Installation/Uninstallation']),
                 ('support', d['Support Information']), ('additional', d['Additional Information']),
                 ('known', d['Known Issues']), ('repo', REPO), ('privacy', PRIVACY)):
        html = html.replace('{' + k + '}', v)
    with open(os.path.join(ROOT, 'dist', 'Help.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    for name, limit, text in FIELDS:
        print(f'{len(text):5d} / {limit or "-":>5}  {name}')
    print('ALL WITHIN LIMITS' if ok else 'SOME FIELDS TOO LONG')


if __name__ == '__main__':
    main()
