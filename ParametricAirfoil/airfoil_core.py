# airfoil_core.py - geometry for Parametric Airfoil by Syed Mujahid
# Pure Python (no Fusion imports) so it can be unit-tested outside Fusion.
#
# Every airfoil, built-in or imported, ends up as a list of "stations": cosine-spaced chord
# positions x (0..1) with an upper and a lower surface height (fractions of chord, signed, +up).
# The original trailing-edge gap is removed so both surfaces meet at (1, 0); the blunt trailing
# edge is added back later from the TE thickness parameter.

import math

# ----------------------------------------------------------------------------------------------
# Built-in airfoils: 25 cosine stations, upper/lower half-thickness (AL is positive downwards).
_X25 = [0.0000000, 0.0042776, 0.0170371, 0.0380602, 0.0669873, 0.1033233, 0.1464466, 0.1956193,
        0.2500000, 0.3086583, 0.3705905, 0.4347369, 0.5000000, 0.5652631, 0.6294095, 0.6913417,
        0.7500000, 0.8043807, 0.8535534, 0.8966767, 0.9330127, 0.9619398, 0.9829629, 0.9957224,
        1.0000000]
_NACA0009 = [0.0000000, 0.0084928, 0.0164277, 0.0236848, 0.0301089, 0.0355342, 0.0398120, 0.0428352,
             0.0445556, 0.0449913, 0.0442236, 0.0423857, 0.0396461, 0.0361915, 0.0322120, 0.0278912,
             0.0234033, 0.0189129, 0.0145789, 0.0105567, 0.0069986, 0.0040491, 0.0018369, 0.0004650,
             0.0000000]
BUILTIN = {
    'Clark Y': (
        _X25,
        [0.0000000, 0.0092990, 0.0227143, 0.0380098, 0.0515579, 0.0639329, 0.0747517, 0.0832339,
         0.0883556, 0.0907350, 0.0913780, 0.0897028, 0.0855776, 0.0794469, 0.0715670, 0.0623982,
         0.0525773, 0.0425660, 0.0327891, 0.0236843, 0.0156464, 0.0089951, 0.0040447, 0.0010165,
         0.0000000],
        [0.0000000, 0.0108247, 0.0192750, 0.0241518, 0.0276393, 0.0294373, 0.0301838, 0.0296454,
         0.0280249, 0.0257959, 0.0234800, 0.0211035, 0.0186623, 0.0162253, 0.0138324, 0.0115206,
         0.0093311, 0.0073014, 0.0054660, 0.0038565, 0.0025003, 0.0014206, 0.0006360, 0.0001597,
         0.0000000]),
    'NACA 0009': (_X25, _NACA0009, _NACA0009),
}


class AirfoilError(Exception):
    pass


# ----------------------------------------------------------------------------------------------
def cosine_stations(n):
    """n stations from 0 to 1, clustered at both the leading and trailing edge."""
    return [0.5 * (1.0 - math.cos(math.pi * k / (n - 1))) for k in range(n)]


def _pchip(xs, ys, xq):
    """Monotone piecewise-cubic (Fritsch-Carlson) interpolation; no overshoot between points."""
    n = len(xs)
    h = [xs[i + 1] - xs[i] for i in range(n - 1)]
    d = [(ys[i + 1] - ys[i]) / h[i] for i in range(n - 1)]
    m = [0.0] * n
    if n == 2:
        m = [d[0], d[0]]
    else:
        for i in range(1, n - 1):
            if d[i - 1] * d[i] <= 0:
                m[i] = 0.0
            else:
                w1 = 2 * h[i] + h[i - 1]
                w2 = h[i] + 2 * h[i - 1]
                m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])

        def end(h0, h1, d0, d1):
            e = ((2 * h0 + h1) * d0 - h0 * d1) / (h0 + h1)
            if e * d0 <= 0:
                return 0.0
            if d0 * d1 <= 0 and abs(e) > 3 * abs(d0):
                return 3 * d0
            return e
        m[0] = end(h[0], h[1], d[0], d[1])
        m[-1] = end(h[-1], h[-2], d[-1], d[-2])

    out = []
    j = 0
    for x in xq:
        if x <= xs[0]:
            out.append(ys[0]); continue
        if x >= xs[-1]:
            out.append(ys[-1]); continue
        while not (xs[j] <= x <= xs[j + 1]):
            j = j + 1 if x > xs[j + 1] else max(j - 1, 0)
        t = (x - xs[j]) / h[j]
        t2, t3 = t * t, t * t * t
        out.append((2 * t3 - 3 * t2 + 1) * ys[j] + (t3 - 2 * t2 + t) * h[j] * m[j]
                   + (-2 * t3 + 3 * t2) * ys[j + 1] + (t3 - t2) * h[j] * m[j + 1])
    return out


def _resample(surface, n):
    """surface: [(x, y)] from LE (x=0) to TE (x=1). Interpolate y against sqrt(x), which removes the
    infinite slope at the round leading edge, then sample at n cosine stations."""
    s = [math.sqrt(max(x, 0.0)) for x, _ in surface]
    y = [p[1] for p in surface]
    xq = cosine_stations(n)
    return _pchip(s, y, [math.sqrt(x) for x in xq])


def _clean_surface(pts):
    """Sort LE->TE, force start at (0,0), strictly increasing x, x normalised to end at 1, and the
    TE height removed linearly so the surface ends at (1, 0)."""
    pts = sorted(pts, key=lambda p: p[0])
    out = [(0.0, 0.0)]
    for x, y in pts:
        if x <= out[-1][0] + 1e-7:
            continue
        out.append((x, y))
    if len(out) < 4:
        raise AirfoilError('Not enough points on one surface after cleaning the data.')
    xl, yl = out[-1]
    return [(x / xl, y - (x / xl) * yl) for x, y in out]


def _stations_from_surfaces(upper, lower, n):
    upper = _clean_surface(upper)
    lower = _clean_surface(lower)
    yu = _resample(upper, n)
    yl = _resample(lower, n)
    if sum(yu) < sum(yl):          # file listed the lower surface first
        yu, yl = yl, yu
    return cosine_stations(n), yu, yl


def builtin_stations(name, n=25):
    X, AU, AL = BUILTIN[name]
    upper = list(zip(X, AU))
    lower = list(zip(X, [-a for a in AL]))
    return _stations_from_surfaces(upper, lower, n)


# ----------------------------------------------------------------------------------------------
def parse_dat(text):
    """Parse a Selig or Lednicer .dat airfoil file. Returns (name, upper, lower) where each surface is
    a list of (x, y) from leading edge to trailing edge, normalised so the LE is at (0,0) and the
    TE midpoint is at (1,0) (de-rotated and scaled)."""
    name = ''
    pairs = []
    for raw in text.splitlines():
        line = raw.replace(',', ' ').replace('\t', ' ').strip()
        if not line:
            pairs.append(None)                      # blank line - separates Lednicer surfaces
            continue
        tok = line.split()
        try:
            a, b = float(tok[0]), float(tok[1])
        except (ValueError, IndexError):
            if not pairs and not name:
                name = line
            continue
        pairs.append((a, b))

    first = next((p for p in pairs if p is not None), None)
    if first is None:
        raise AirfoilError('No coordinates found in the file.')

    pts = [p for p in pairs if p is not None]
    if first[0] > 1.5 and first[1] > 1.5 and float(first[0]).is_integer() and float(first[1]).is_integer():
        # Lednicer: counts, then upper LE->TE, then lower LE->TE
        nu, nl = int(first[0]), int(first[1])
        body = pts[1:]
        if len(body) < nu + nl:
            raise AirfoilError('Lednicer file says %d + %d points but has %d.' % (nu, nl, len(body)))
        upper, lower = body[:nu], body[nu:nu + nl]
    else:
        # Selig: TE -> upper -> LE -> lower -> TE
        if len(pts) < 8:
            raise AirfoilError('Too few points in the file (%d).' % len(pts))
        tx, ty = (pts[0][0] + pts[-1][0]) / 2.0, (pts[0][1] + pts[-1][1]) / 2.0
        near0 = min(range(len(pts)), key=lambda i: pts[i][0] ** 2 + pts[i][1] ** 2)
        if math.hypot(*pts[near0]) < 2e-3 and abs(tx - 1.0) < 0.01 and abs(ty) < 0.01:
            # already normalised (the usual case, e.g. UIUC files): keep the file's own chord line
            le = near0
        else:
            # leading edge = the point farthest from the trailing-edge midpoint
            le = max(range(len(pts)), key=lambda i: (pts[i][0] - tx) ** 2 + (pts[i][1] - ty) ** 2)
        upper = list(reversed(pts[:le + 1]))
        lower = pts[le:]

    le_pt = upper[0] if upper[0][0] <= lower[0][0] else lower[0]
    te_pt = ((upper[-1][0] + lower[-1][0]) / 2.0, (upper[-1][1] + lower[-1][1]) / 2.0)
    dx, dy = te_pt[0] - le_pt[0], te_pt[1] - le_pt[1]
    c = math.hypot(dx, dy)
    if c < 1e-9:
        raise AirfoilError('Leading and trailing edge coincide - is this an airfoil file?')
    ca, sa = dx / c, dy / c

    def norm(p):
        x, y = p[0] - le_pt[0], p[1] - le_pt[1]
        return ((x * ca + y * sa) / c, (-x * sa + y * ca) / c)

    return name or 'Imported airfoil', [norm(p) for p in upper], [norm(p) for p in lower]


def dat_stations(text, n=25):
    name, upper, lower = parse_dat(text)
    X, YU, YL = _stations_from_surfaces(upper, lower, n)
    return name, X, YU, YL


# ----------------------------------------------------------------------------------------------
def check_stations(X, YU, YL):
    """Raise if the surfaces cross (upper below lower) anywhere between LE and TE."""
    for i in range(1, len(X) - 1):
        if YU[i] - YL[i] <= 0:
            raise AirfoilError('Upper and lower surfaces cross at x/c = %.3f.' % X[i])


def point_rows(X, YU, YL):
    """Ordered spline points: upper TE -> LE -> lower TE.
    Each row is (x, y, side) with y signed (fraction of chord) and side +1 upper / -1 lower / 0 LE."""
    n = len(X) - 1
    rows = [(X[i], YU[i], +1) for i in range(n, 0, -1)]
    rows.append((0.0, 0.0, 0))
    rows += [(X[i], YL[i], -1) for i in range(1, n + 1)]
    return rows


def point_xy(row, chord, te):
    """Actual sketch coordinates for a row, chord and TE thickness (any consistent unit)."""
    x, y, side = row
    return x * chord, chord * y + side * te * 0.5 * x


def expressions(row, chord_name, te_name):
    """Dimension expressions for one non-LE point.
    Horizontal: distance from the sketch origin  = chord * x.
    Vertical:   distance from a reference point placed one chord BELOW the origin
                = chord * (1 + y) +/- TE/2 * x.
    Measuring from a point below the airfoil keeps every vertical dimension positive, so cambered
    airfoils whose lower surface rises above the chord line never produce a zero/flipped dimension."""
    x, y, side = row
    h = chord_name if x > 0.999999 else '%s * %.7f' % (chord_name, x)
    k = 1.0 + y
    te_k = 0.5 * x
    v = '%s * %.7f' % (chord_name, k)
    if side > 0:
        v += ' + %s * %.7f' % (te_name, te_k)
    else:
        v += ' - %s * %.7f' % (te_name, te_k)
    return h, v
