# Autodesk App Store submission – Parametric Airfoil by Syed Mujahid

Copy-paste text and checklist for the Autodesk App Store submission form.

## 1. Register as a publisher (one time)

1. Go to **https://apps.autodesk.com** and sign in with your Autodesk account (the same one you use for Fusion).
2. Open **Publisher Corner** (in the top-right account menu, or the "Publish" link in the page footer).
3. Fill in the publisher profile:
   - **Publisher name:** Syed Mujahid
   - **Website:** https://github.com/syedmujahid7040
   - **Support email:** your email
4. Read and accept the **Publisher Agreement**.
5. If you're unsure whether an Education (student) account can publish, email **appsubmissions@autodesk.com** before you start.

## 2. Create the app listing

| Field | Value |
|---|---|
| Product | Fusion |
| App name | Parametric Airfoil by Syed Mujahid |
| Price | Free |
| Version | 1.0.0 |
| OS | Windows, macOS |
| Language | English |
| Category | Modeling / Productivity |
| Upload | `dist/ParametricAirfoil.bundle-1.0.0.zip` (built by `python tools/build_release.py`) |
| Icon | `docs/icon.png` (512 × 512) |
| Support / docs URL | https://github.com/syedmujahid7040/parametric-airfoil-fusion360 |

### Short description (one line)

Create airfoil sketches you can resize at any time – chord and trailing edge are Fusion user parameters.

### Full description

Airfoil importers draw a spline from a .dat file – a dead shape. You can't change the chord later, the profile often won't close for Extrude or Loft, and once a wing is built on it, even the Scale feature fails.

Parametric Airfoil builds the airfoil as a fully parameter-driven sketch. Every spline point is dimensioned with an expression of two user parameters: the chord (for example RootChord) and the trailing-edge thickness (TE_Thk). Change the chord at any time in Modify > Change Parameters and the airfoil, and every feature built on it, updates.

Features:
• Three airfoil sources: Clark Y, NACA 0009, or import any Selig or Lednicer .dat file (e.g. from the UIUC Airfoil Database)
• Chord and trailing-edge thickness are user parameters that show up in the Parameters dialog
• Blunt trailing edge closed with a line – the profile always extrudes and lofts
• Sketch on any construction plane or planar face
• Use different parameter names (RootChord, TipChord, TailChord) to build tapered wings and tails that stay editable
• Accurate import: cosine-spaced resampling, works with highly cambered airfoils
• Free and open source (MIT)

Built by Syed Mujahid while designing a VTOL UAV from scratch.

### Quick-start / help page

1. In the DESIGN workspace click SOLID > CREATE > Parametric Airfoil (airfoil icon on the toolbar).
2. Choose Clark Y, NACA 0009, or Import .dat file....
3. Select a plane. The leading edge is placed on the sketch origin, chord along +X.
4. Enter the chord parameter name and chord length (e.g. RootChord = 280 mm) and the trailing-edge thickness (1 mm recommended).
5. Click OK, then Extrude or Loft the profile.
6. To resize: MODIFY > Change Parameters, edit RootChord.

Uninstall: UTILITIES > ADD-INS > Scripts and Add-Ins, stop the add-in, or uninstall it from the Autodesk App Store manager.

## 3. Screenshots to capture (1280 × 720 or larger)

1. The Parametric Airfoil dialog with Clark Y selected.
2. A finished airfoil sketch on a plane.
3. The Change Parameters dialog showing RootChord and TE_Thk.
4. The same wing before and after changing RootChord.
5. A tapered wing lofted between RootChord and TipChord airfoils.

## 4. Before submitting

- [ ] Add-in loads in under 0.005 s at startup (it only adds one button; geometry code runs on click)
- [ ] Button appears in the existing SOLID > CREATE panel, no new toolbar panel
- [ ] Tested on the current Fusion version on Windows (and Mac if available)
- [ ] Version number increased for every resubmission
