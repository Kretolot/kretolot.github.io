#!/usr/bin/env python3
"""
Choinka ASCII 3D w OKNIE (pygame): gęsta choinka, świecące lampki, gwiazda z poświatą,
śnieg, spadające prezenty, napis i licznik statystyk.

Instalacja:    py -m pip install pygame
Uruchomienie:  py choinka_okno.py

Sterowanie:
    ESC / zamknięcie okna - wyjście
    F11                   - pełny ekran
    SPACJA                - pauza
    +  /  -               - większe / mniejsze znaki
    R                     - start od nowa
    S                     - zrzut ekranu (PNG obok skryptu)
Okno można dowolnie skalować myszką.
Nagrywanie rolki: Win+G (Xbox Game Bar) albo OBS.
"""
import math
import os
import random
import sys
import time

try:
    import pygame
except ImportError:
    print("Brak biblioteki pygame. Zainstaluj ją poleceniem:")
    print("    py -m pip install pygame")
    print("(jeśli to nie zadziała: py -m pip install pygame-ce)")
    try:
        input("Naciśnij Enter, aby zamknąć...")
    except EOFError:
        pass
    sys.exit(1)

# ------------------------------------------------------------------ ustawienia
CAPTION = "MERRY CHRISTMAS"     # możesz zmienić, np. "WESOLYCH SWIAT"
N_GIFTS = 9
FIRST_GIFT = 1.0
GIFT_GAP = 0.9
HOLD = 9.0                      # ile sekund pokazać komplet, zanim zacznie od nowa
FALL_TIME = 0.9
SPIN = 0.55                     # prędkość obrotu (rad/s)
N_LIGHTS = 170
N_FLAKES = 300
FPS_TARGET = 30
WINDOW_SIZE = (1000, 900)
BASE_FONT = 15

TAU = 2 * math.pi
TILT = 0.20
CT, ST = math.cos(TILT), math.sin(TILT)

DARK_CH = ".:'`,"
MID_CH = "vxo%&"
BRIGHT_CH = "WXS#@"
DARK_COL = (22, 22, 28, 23, 22)
MID_COL = (28, 34, 34, 40, 28)
BRIGHT_COL = (40, 46, 82, 118, 46)
LIGHT_COLS = (196, 226, 39, 201, 231, 208, 46, 214)


def pal(n):
    """Indeks 0-255 (paleta xterm) -> RGB."""
    if n < 16:
        base = [(0, 0, 0), (205, 0, 0), (0, 205, 0), (205, 205, 0), (0, 0, 238),
                (205, 0, 205), (0, 205, 205), (229, 229, 229), (127, 127, 127),
                (255, 0, 0), (0, 255, 0), (255, 255, 0), (92, 92, 255),
                (255, 0, 255), (0, 255, 255), (255, 255, 255)]
        return base[n]
    if n < 232:
        n -= 16
        r, g, b = n // 36, (n // 6) % 6, n % 6
        f = lambda v: 0 if v == 0 else 55 + 40 * v
        return (f(r), f(g), f(b))
    v = 8 + 10 * (n - 232)
    return (v, v, v)


# ------------------------------------------------------------------ geometria sceny
TIERS = []
for _k in range(6):
    TIERS.append((2.95 - _k * 0.43, 0.8 + _k * 0.95, 1.6))   # (promień, z start, wysokość)
TREE_TOP = 0.8 + 5 * 0.95 + 1.6
STAR_Z = TREE_TOP + 0.25


def radius_at(z):
    best = 0.0
    for R, z0, h in TIERS:
        if z0 <= z <= z0 + h:
            best = max(best, R * (1 - (z - z0) / h))
    return best


def point_in_poly(px, py, poly):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi + 1e-12) + xi:
            inside = not inside
        j = i
    return inside


_scene_cache = {}


def build_scene(sc):
    key = round(sc * 2) / 2
    if key in _scene_cache:
        return _scene_cache[key]
    rnd = random.Random(11)
    dens = 4.0 * key * key

    tree = []
    for R, z0, h in TIERS:
        area = math.pi * R * math.hypot(R, h)
        for _ in range(int(area * dens)):
            f = 1 - math.sqrt(rnd.random())
            r = R * (1 - f)
            a = rnd.random() * TAU
            b = rnd.random() * 0.55
            if f > 0.8:
                b += 0.25
            if f < 0.12:
                b -= 0.25
            tree.append((r * math.cos(a), r * math.sin(a), z0 + f * h,
                         a, b, rnd.randrange(5)))

    trunk = []
    for _ in range(int(260 * key)):
        a = rnd.random() * TAU
        trunk.append((0.32 * math.cos(a), 0.32 * math.sin(a), rnd.random() * 0.85,
                      rnd.choice("#H8"), rnd.choice((94, 130, 94, 95))))

    lights = []
    areas = [math.pi * R * math.hypot(R, h) for R, z0, h in TIERS]
    for _ in range(N_LIGHTS):
        R, z0, h = rnd.choices(TIERS, weights=areas)[0]
        f = rnd.uniform(0.04, 0.8)
        r = R * (1 - f) * 1.06 + 0.03
        a = rnd.random() * TAU
        lights.append((r * math.cos(a), r * math.sin(a), z0 + f * h,
                       rnd.random() * TAU, rnd.choice(LIGHT_COLS), rnd.choice("O@0o")))

    garland = []
    n = int(150 * key)
    for s in range(n):
        f = s / n
        z = 0.95 + f * 5.7
        r = radius_at(z) + 0.10
        if r < 0.15:
            continue
        a = f * TAU * 8
        garland.append((r * math.cos(a), r * math.sin(a), z,
                        '=' if s % 3 else '~', 220 if s % 2 else 178))

    verts = []
    for i in range(10):
        rad = 0.62 if i % 2 == 0 else 0.26
        ang = math.pi / 2 + i * TAU / 10
        verts.append((rad * math.cos(ang), rad * math.sin(ang)))
    star = []
    step = 0.045
    gx = -0.65
    while gx <= 0.65:
        gy = -0.65
        while gy <= 0.65:
            if point_in_poly(gx, gy, verts):
                star.append((gx, 0.0, STAR_Z + gy))
                star.append((0.0, gx, STAR_Z + gy))
            gy += step
        gx += step

    N = max(7, int(key * 1.7))
    local = []
    for a in range(N + 1):
        for b in range(N + 1):
            u, v = a / N - 0.5, b / N - 0.5
            par = (a + b) % 2
            cross = abs(u) < 0.11 or abs(v) < 0.11
            local.append((u, v, 1.0, cross, par))
            side = abs(u) < 0.11
            w = v + 0.5
            local.append((u, -0.5, w, side, par))
            local.append((u, 0.5, w, side, par))
            local.append((-0.5, u, w, side, par))
            local.append((0.5, u, w, side, par))
    for s in (-1, 1):
        local += [(0.20 * s, 0, 1.12, True, 0), (0.12 * s, 0, 1.22, True, 1),
                  (0, 0.20 * s, 1.12, True, 0), (0, 0.12 * s, 1.22, True, 1)]
    local += [(0, 0, 1.15, True, 1), (0, 0, 1.30, True, 0)]

    gifts = []
    body_cols = [27, 196, 34, 129, 208, 39, 160, 205, 178]
    rib_cols = [231, 220, 220, 231, 231, 220, 231, 220, 196]
    order = [0, 5, 2, 7, 4, 1, 8, 3, 6]
    for i in range(N_GIFTS):
        slot = order[i % len(order)]
        a = TAU * slot / N_GIFTS + rnd.uniform(-0.12, 0.12)
        r = rnd.uniform(3.7, 4.8)
        gifts.append(dict(cx=r * math.cos(a), cy=r * math.sin(a),
                          size=rnd.uniform(0.55, 0.9), yaw=rnd.uniform(0, TAU),
                          body=body_cols[i % len(body_cols)],
                          rib=rib_cols[i % len(rib_cols)],
                          t0=FIRST_GIFT + i * GIFT_GAP))

    flakes = [(rnd.random(), rnd.random(), rnd.uniform(0.35, 1.3),
               rnd.random() * TAU, rnd.randrange(3)) for _ in range(N_FLAKES)]

    scene = dict(tree=tree, trunk=trunk, lights=lights, garland=garland,
                 star=star, local=local, gifts=gifts, flakes=flakes)
    _scene_cache[key] = scene
    return scene


def bounce(p):
    n1, d1 = 7.5625, 2.75
    if p < 1 / d1:
        return n1 * p * p
    if p < 2 / d1:
        p -= 1.5 / d1
        return n1 * p * p + 0.75
    if p < 2.5 / d1:
        p -= 2.25 / d1
        return n1 * p * p + 0.9375
    p -= 2.625 / d1
    return n1 * p * p + 0.984375


def put_text(buf, W, row, col, text, color):
    for j, ch in enumerate(text):
        c = col + j
        if ch != ' ' and 0 <= c < W:
            buf[row * W + c] = (ch, color)


# ------------------------------------------------------------------ obliczanie klatki
def compute_frame(t, W, H, aspect, fps, show_hint):
    """Zwraca siatkę znaków (lista (znak, kolor) lub None) + dane do poświaty."""
    top, bottom = 1, H - 6
    area = bottom - top
    sc = max(1.2, min(area / 9.4, W / (10.5 * aspect)))
    S = build_scene(sc)

    sxs = aspect * sc
    base_row = bottom - 1.0 * sc
    mid = W / 2.0
    ang = t * SPIN
    ca, sa = math.cos(ang), math.sin(ang)

    N = W * H
    buf = [None] * N
    zb = [-1e9] * N
    tw = [None] * N

    # śnieżne pole
    horizon = int(top + 0.60 * area)
    for r in range(horizon, min(H, bottom + 5)):
        depth = (r - horizon) / max(1, bottom + 5 - horizon)
        mod = 9 - int(depth * 5)
        for c in range(W):
            h = (c * 7 + r * 13) % mod
            if h == 0:
                buf[r * W + c] = (':', 60 if depth < 0.5 else 67)
            elif h == 3 and depth > 0.25:
                buf[r * W + c] = ('.', 103)
            elif (c * 5 + r * 11 + int(t * 2)) % 97 == 0:
                buf[r * W + c] = ('+', 153)

    top_lim = H - 5

    def plot(x, y, z, ch, col, bias=0.0):
        xr = x * ca - y * sa
        yr = x * sa + y * ca
        sx = int(mid + xr * sxs)
        sy = int(base_row - (z * CT - yr * ST) * sc)
        if 0 <= sx < W and 1 <= sy < top_lim:
            i = sy * W + sx
            d = yr * CT + z * ST + bias
            if d > zb[i]:
                zb[i] = d
                buf[i] = (ch, col)
                tw[i] = None
                return i
        return -1

    for pt in S['tree']:
        x, y, z = pt[0], pt[1], pt[2]
        yr = x * sa + y * ca
        sx = int(mid + (x * ca - y * sa) * sxs)
        sy = int(base_row - (z * CT - yr * ST) * sc)
        if 0 <= sx < W and 1 <= sy < top_lim:
            i = sy * W + sx
            d = yr * CT + z * ST
            if d > zb[i]:
                zb[i] = d
                tw[i] = pt

    for x, y, z, ch, col in S['trunk']:
        plot(x, y, z, ch, col)
    for x, y, z, ch, col in S['garland']:
        plot(x, y, z, ch, col, 0.05)

    light_cells = {}
    for x, y, z, ph, col, ch in S['lights']:
        s = math.sin(t * 4.0 + ph)
        if s > 0.75:
            i = plot(x, y, z, ch, 231, 0.1)
            gl = (col, 1.0)
        elif s > -0.25:
            i = plot(x, y, z, ch, col, 0.1)
            gl = (col, 0.6)
        else:
            i = plot(x, y, z, 'o', 238, 0.05)
            gl = None
        if i >= 0 and gl:
            light_cells[i] = (buf[i], gl)

    star_col = 226 if math.sin(t * 5) > -0.3 else 229
    for x, y, z in S['star']:
        plot(x, y, z, '#', star_col, 0.3)

    total = FIRST_GIFT + N_GIFTS * GIFT_GAP + HOLD
    tt = t % total
    local = S['local']
    for g in S['gifts']:
        if tt < g['t0']:
            continue
        p = min(1.0, (tt - g['t0']) / FALL_TIME)
        zoff = 7.0 * (1 - bounce(p))
        s = g['size'] * min(1.0, 0.35 + p * 3)
        cy_, sy_ = math.cos(g['yaw']), math.sin(g['yaw'])
        cx, cy = g['cx'], g['cy']
        body, rib = g['body'], g['rib']
        for lx, ly, lz, isr, par in local:
            x = (lx * cy_ - ly * sy_) * s + cx
            y = (lx * sy_ + ly * cy_) * s + cy
            z = lz * s + zoff
            if isr:
                plot(x, y, z, '=' if par else '+', rib, 0.02)
            else:
                plot(x, y, z, 'X' if par else '#', body, 0.0)

    frame_k = int(t * 10)
    for i in range(N):
        pt = tw[i]
        if pt is None:
            continue
        a, b, k = pt[3], pt[4], pt[5]
        L = b * 0.65 + 0.35 * (0.5 + 0.5 * math.sin(a + ang + 0.9))
        if (i * 7 + frame_k * 13) % 83 == 0:
            buf[i] = ('*', 231)
        elif L < 0.28:
            buf[i] = (DARK_CH[k], DARK_COL[k])
        elif L < 0.58:
            buf[i] = (MID_CH[k], MID_COL[k])
        else:
            buf[i] = (BRIGHT_CH[k], BRIGHT_COL[k])

    # promienie gwiazdy
    scx = int(mid)
    scy = int(base_row - STAR_Z * CT * sc)
    reach = int(1.7 * sc * aspect)
    for dx in range(2, reach):
        col = 136 if dx < reach * 0.4 else (94 if dx < reach * 0.75 else 58)
        for sgn in (-1, 1):
            c = scx + sgn * dx
            if 0 <= c < W and 1 <= scy < H and zb[scy * W + c] < -1e8:
                buf[scy * W + c] = ('-', col)
    for dy in range(1, int(1.9 * sc)):
        col = 136 if dy < sc * 0.7 else 94
        r = scy - dy
        if 1 <= r < H and zb[r * W + scx] < -1e8:
            buf[r * W + scx] = ('|', col)
    for dd in range(2, int(sc * 1.1)):
        for sx_, sy_, chd in ((1, -1, '/'), (-1, -1, '\\')):
            c, r = scx + sx_ * dd * 2, scy + sy_ * dd
            if 0 <= c < W and 1 <= r < H and zb[r * W + c] < -1e8:
                buf[r * W + c] = (chd, 94)

    # śnieg
    for nx, ny, spd, ph, layer in S['flakes']:
        c = int(nx * W + 2 * math.sin(t * 1.3 + ph)) % W
        r = int((ny * H + t * spd * H * 0.10)) % H
        i = r * W + c
        if zb[i] < -1e8 and 0 <= r < H - 5:
            if layer == 0:
                buf[i] = ('.', 244)
            elif layer == 1:
                buf[i] = ('+', 250)
            else:
                buf[i] = ('*' if spd > 0.9 else '+', 255)

    letters = sum(1 for c in buf if c is not None)

    # napis
    spaced = ' '.join(CAPTION)
    pal_cap = (196, 40, 226, 231, 39)
    c0 = (W - len(spaced)) // 2
    row = H - 5
    for j, ch in enumerate(spaced):
        if 0 <= c0 + j < W:
            if ch != ' ':
                buf[row * W + c0 + j] = (ch, pal_cap[(j // 2 + int(t * 2)) % len(pal_cap)])
            else:
                buf[row * W + c0 + j] = None

    # HUD
    put_text(buf, W, 0, W - 10, f"t {t:5.2f}s", 214)
    put_text(buf, W, H - 3, 2, f"rotation {math.degrees(ang) % 360:6.2f}°", 244)
    put_text(buf, W, H - 2, 2, f"lights   {N_LIGHTS}", 244)
    put_text(buf, W, H - 1, 2, f"letters  {letters:,}", 244)
    r_txt = f"running · {fps:.0f} fps"
    put_text(buf, W, H - 1, W - len(r_txt) - 2, r_txt, 108)
    if show_hint:
        hint = "ESC wyjscie  ·  F11 pelny ekran  ·  SPACJA pauza  ·  +/- rozmiar  ·  S zrzut"
        put_text(buf, W, H - 2, (W - len(hint)) // 2, hint, 240)

    # poświata lampek (tylko te, które nadal są widoczne)
    glows = []
    for i, (cell, gl) in light_cells.items():
        if buf[i] == cell:
            glows.append((i % W, i // W, gl[0], gl[1]))

    return buf, dict(glows=glows, star=(scx, scy), star_col=star_col)


# ------------------------------------------------------------------ okno / rysowanie
def make_glow(color_rgb, radius):
    surf = pygame.Surface((radius * 2, radius * 2))
    surf.fill((0, 0, 0))
    for k in range(radius, 0, -1):
        a = (1 - k / radius) ** 2.2
        c = (int(color_rgb[0] * a * 0.75), int(color_rgb[1] * a * 0.75),
             int(color_rgb[2] * a * 0.75))
        pygame.draw.circle(surf, c, (radius, radius), k)
    return surf


def make_background(w, h):
    bg = pygame.Surface((w, h))
    for y in range(h):
        k = y / max(1, h - 1)
        c = (int(4 + 8 * (1 - k)), int(6 + 12 * (1 - k)), int(14 + 30 * (1 - k) ** 1.5))
        pygame.draw.line(bg, c, (0, y), (w, y))
    return bg


def main():
    pygame.init()
    pygame.display.set_caption("Choinka ASCII 3D")
    flags = pygame.RESIZABLE
    screen = pygame.display.set_mode(WINDOW_SIZE, flags)
    clock = pygame.time.Clock()
    fullscreen = False
    font_mul = 1.0

    state = {}
    glyph_cache = {}
    glow_cache = {}
    rnd = random.Random(3)
    sky = [(rnd.random(), rnd.random() * 0.6, rnd.random() * TAU) for _ in range(90)]

    def setup():
        sw, sh = screen.get_size()
        size = int(BASE_FONT * font_mul * math.sqrt(max(1, sw * sh) / (WINDOW_SIZE[0] * WINDOW_SIZE[1])))
        size = max(8, min(60, size))
        font = pygame.font.SysFont("consolas,couriernew,dejavusansmono,menlo,monospace", size)
        state['font'] = font
        state['cw'] = max(4, font.size("M")[0])
        state['ch'] = max(6, font.get_height())
        state['W'] = max(40, sw // state['cw'])
        state['H'] = max(24, sh // state['ch'])
        state['ox'] = (sw - state['W'] * state['cw']) // 2
        state['oy'] = (sh - state['H'] * state['ch']) // 2
        state['bg'] = make_background(sw, sh)
        glyph_cache.clear()
        glow_cache.clear()

    def glyph(ch, col):
        key = (ch, col)
        g = glyph_cache.get(key)
        if g is None:
            g = state['font'].render(ch, True, pal(col))
            glyph_cache[key] = g
        return g

    def glow(col, radius):
        key = (col, radius)
        g = glow_cache.get(key)
        if g is None:
            g = make_glow(pal(col), radius)
            glow_cache[key] = g
        return g

    setup()
    anim_t = 0.0
    last = time.time()
    paused = False
    start_wall = time.time()
    running = True

    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.VIDEORESIZE:
                setup()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                elif ev.key == pygame.K_SPACE:
                    paused = not paused
                elif ev.key == pygame.K_r:
                    anim_t = 0.0
                    start_wall = time.time()
                elif ev.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    font_mul = min(2.5, font_mul * 1.12)
                    setup()
                elif ev.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    font_mul = max(0.5, font_mul / 1.12)
                    setup()
                elif ev.key == pygame.K_s:
                    name = f"choinka_{int(time.time())}.png"
                    pygame.image.save(screen, name)
                    print("Zapisano", name)
                elif ev.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode(WINDOW_SIZE, flags)
                    setup()

        now = time.time()
        if not paused:
            anim_t += now - last
        last = now

        cw, chh, W, H = state['cw'], state['ch'], state['W'], state['H']
        aspect = chh / cw
        show_hint = (now - start_wall) < 8
        buf, meta = compute_frame(anim_t, W, H, aspect, clock.get_fps() or FPS_TARGET, show_hint)

        sw, sh = screen.get_size()
        screen.blit(state['bg'], (0, 0))

        # migające gwiazdki na niebie
        for nx, ny, ph in sky:
            v = int(70 + 70 * math.sin(anim_t * 2 + ph))
            screen.set_at((int(nx * sw), int(ny * sh)), (v, v, v + 20))

        ox, oy = state['ox'], state['oy']

        # poświata (addytywna) pod znakami
        scx, scy = meta['star']
        pulse = 0.85 + 0.15 * math.sin(anim_t * 5)
        r_star = int(cw * 9 * pulse)
        g = glow(226, r_star)
        screen.blit(g, (ox + scx * cw + cw // 2 - r_star, oy + scy * chh - r_star),
                    special_flags=pygame.BLEND_RGB_ADD)
        r_l = int(cw * 3.2)
        for c, r, col, strength in meta['glows']:
            gg = glow(col, r_l)
            if strength < 1.0:
                screen.blit(gg, (ox + c * cw + cw // 2 - r_l, oy + r * chh + chh // 2 - r_l),
                            special_flags=pygame.BLEND_RGB_ADD)
            else:
                screen.blit(gg, (ox + c * cw + cw // 2 - r_l, oy + r * chh + chh // 2 - r_l),
                            special_flags=pygame.BLEND_RGB_ADD)
                screen.blit(gg, (ox + c * cw + cw // 2 - r_l, oy + r * chh + chh // 2 - r_l),
                            special_flags=pygame.BLEND_RGB_ADD)

        # znaki
        blits = []
        for i, cell in enumerate(buf):
            if cell is not None:
                blits.append((glyph(cell[0], cell[1]),
                              (ox + (i % W) * cw, oy + (i // W) * chh)))
        screen.blits(blits, False)

        pygame.display.flip()
        clock.tick(FPS_TARGET)

    pygame.quit()


if __name__ == "__main__":
    main()