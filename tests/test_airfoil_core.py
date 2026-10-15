"""Offline tests for the airfoil geometry (no Fusion needed):  python tests/test_airfoil_core.py"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ParametricAirfoil'))
import airfoil_core as ac  # noqa: E402


def naca4_point(m, p, t, x, upper):
    yt = 5 * t * (0.2969 * math.sqrt(x) - 0.1260 * x - 0.3516 * x * x + 0.2843 * x ** 3 - 0.1015 * x ** 4)
    if p == 0:
        yc, dy = 0.0, 0.0
    elif x < p:
        yc, dy = m / p ** 2 * (2 * p * x - x * x), 2 * m / p ** 2 * (p - x)
    else:
        yc, dy = m / (1 - p) ** 2 * ((1 - 2 * p) + 2 * p * x - x * x), 2 * m / (1 - p) ** 2 * (p - x)
    th = math.atan(dy)
    s = 1 if upper else -1
    return x - s * yt * math.sin(th), yc + s * yt * math.cos(th)


def naca4(m, p, t, n=81):
    xs = [0.5 * (1 - math.cos(math.pi * i / (n - 1))) for i in range(n)]
    return [naca4_point(m, p, t, x, True) for x in xs], [naca4_point(m, p, t, x, False) for x in xs]


def exact_y(m, p, t, xt, upper):
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if naca4_point(m, p, t, mid, upper)[0] < xt:
            lo = mid
        else:
            hi = mid
    return naca4_point(m, p, t, lo, upper)[1]


def selig(U, L):
    return 'test\n' + '\n'.join('%.6f %.6f' % q for q in reversed(U)) + '\n' + '\n'.join('%.6f %.6f' % q for q in L[1:])


def lednicer(U, L):
    return ('test\n%d. %d.\n\n' % (len(U), len(L)) + '\n'.join('%.6f %.6f' % q for q in U) + '\n\n'
            + '\n'.join('%.6f %.6f' % q for q in L))


def max_err(m, p, t, X, YU, YL):
    U, L = naca4(m, p, t, 401)
    yu_te, yl_te = U[-1][1], L[-1][1]
    e = 0.0
    for i in range(1, len(X) - 1):
        e = max(e, abs(YU[i] - (exact_y(m, p, t, X[i], True) - X[i] * yu_te)),
                abs(YL[i] - (exact_y(m, p, t, X[i], False) - X[i] * yl_te)))
    return e


def test_builtins_unchanged():
    for name, (X, AU, AL) in ac.BUILTIN.items():
        Xs, YU, YL = ac.builtin_stations(name, 25)
        assert max(abs(a - b) for a, b in zip(AU, YU)) < 1e-6, name
        assert max(abs(a + b) for a, b in zip(AL, YL)) < 1e-6, name
        ac.check_stations(Xs, YU, YL)


def test_dat_accuracy():
    for (m, p, t) in [(0, 0, 0.12), (0.04, 0.4, 0.12), (0.02, 0.4, 0.15)]:
        U, L = naca4(m, p, t)
        for fmt, txt in (('selig', selig(U, L)), ('lednicer', lednicer(U, L))):
            _, X, YU, YL = ac.dat_stations(txt, 25)
            e = max_err(m, p, t, X, YU, YL)
            print('NACA %d%d%02d %-8s max error = %.5f chord' % (m * 100, p * 10, t * 100, fmt, e))
            assert e < 0.002, (m, p, t, fmt, e)


def test_expressions_match_geometry():
    U, L = naca4(0.09, 0.5, 0.12)            # strongly cambered: lower surface above chord line
    _, X, YU, YL = ac.dat_stations(selig(U, L), 40)
    for chord, te in ((280.0, 1.0), (50.0, 2.0)):
        for row in ac.point_rows(X, YU, YL):
            if row[2] == 0:
                continue
            h, v = ac.expressions(row, 'C', 'T')
            env = {'C': chord, 'T': te}
            hv, vv = eval(h, {}, env), eval(v, {}, env)
            px, py = ac.point_xy(row, chord, te)
            assert hv > 0 and vv > 0
            assert abs(hv - px) < 1e-4 and abs(vv - (py + chord)) < 1e-4


def test_bad_file():
    for txt in ('hello\nworld', '1 2\n3 4'):
        try:
            ac.dat_stations(txt)
        except ac.AirfoilError:
            continue
        raise AssertionError('expected AirfoilError')


if __name__ == '__main__':
    for name, fn in list(globals().items()):
        if name.startswith('test_'):
            fn()
            print('PASS', name)
