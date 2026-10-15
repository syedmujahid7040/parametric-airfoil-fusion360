"""Build release packages into dist/:
  - ParametricAirfoil-<ver>.zip          : the add-in folder, for GitHub releases / manual install
  - ParametricAirfoil.bundle-<ver>.zip   : Autodesk App Store bundle (PackageContents.xml + Contents/)
Run:  python tools/build_release.py
"""
import json
import os
import shutil
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'ParametricAirfoil')
DIST = os.path.join(ROOT, 'dist')
SKIP = {'__pycache__', '.DS_Store'}

with open(os.path.join(SRC, 'ParametricAirfoil.manifest')) as f:
    VERSION = json.load(f)['version']

PACKAGE_CONTENTS = '''<?xml version="1.0" encoding="utf-8"?>
<ApplicationPackage SchemaVersion="1.0" AutodeskProduct="Fusion" ProductType="Application"
    Name="Parametric Airfoil by Syed Mujahid"
    Description="Creates airfoil sketches (Clark Y, NACA 0009 or any .dat file) driven by chord and trailing-edge thickness user parameters."
    AppVersion="{v}" FriendlyVersion="{v}" Author="Syed Mujahid"
    ProductCode="{{63F4F930-A4C9-40B0-9E9B-7B6D42063BA0}}" UpgradeCode="{{CAC42C86-F68A-40DB-93D8-C4E2ADFB5335}}"
    OnlineDocumentation="https://github.com/syedmujahid7040/parametric-airfoil-fusion360">
  <CompanyDetails Name="Syed Mujahid" Url="https://github.com/syedmujahid7040" />
  <RuntimeRequirements OS="Win64|Mac" Platform="Fusion" />
  <Components Description="Parametric Airfoil add-in">
    <RuntimeRequirements OS="Win64|Mac" Platform="Fusion" />
    <ComponentEntry AppName="ParametricAirfoil" Version="{v}"
        ModuleName="./Contents/ParametricAirfoil/ParametricAirfoil.py"
        AppDescription="Parametric airfoil sketches for Fusion" LoadOnStartup="True" />
  </Components>
</ApplicationPackage>
'''


def add_tree(zf, folder, arc_root):
    for dirpath, dirnames, filenames in os.walk(folder):
        dirnames[:] = [d for d in dirnames if d not in SKIP]
        for fn in filenames:
            if fn in SKIP or fn.endswith('.pyc'):
                continue
            full = os.path.join(dirpath, fn)
            zf.write(full, os.path.join(arc_root, os.path.relpath(full, folder)))


def main():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)

    plain = os.path.join(DIST, 'ParametricAirfoil-%s.zip' % VERSION)
    with zipfile.ZipFile(plain, 'w', zipfile.ZIP_DEFLATED) as zf:
        add_tree(zf, SRC, 'ParametricAirfoil')
        zf.write(os.path.join(ROOT, 'LICENSE'), 'ParametricAirfoil/LICENSE')

    bundle = os.path.join(DIST, 'ParametricAirfoil.bundle-%s.zip' % VERSION)
    with zipfile.ZipFile(bundle, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('ParametricAirfoil.bundle/PackageContents.xml', PACKAGE_CONTENTS.format(v=VERSION))
        add_tree(zf, SRC, 'ParametricAirfoil.bundle/Contents/ParametricAirfoil')
        zf.write(os.path.join(ROOT, 'LICENSE'), 'ParametricAirfoil.bundle/Contents/ParametricAirfoil/LICENSE')

    for p in (plain, bundle):
        print(os.path.relpath(p, ROOT), os.path.getsize(p), 'bytes')


if __name__ == '__main__':
    main()
