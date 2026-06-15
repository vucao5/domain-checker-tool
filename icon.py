"""V-letter icon generator for Domain Tool.

Creates a clean V icon using tkinter's PhotoImage — no external
dependencies (no PIL/Pillow needed at runtime).
"""

import tkinter as tk


def make_v_icon():
    """Create V-letter icon as PhotoImages. Call AFTER tk.Tk() is created.

    Returns a list of PhotoImage objects [48×48, 32×32, 16×16].
    """
    icons = []
    for sz in [48, 32, 16]:
        img = tk.PhotoImage(width=sz, height=sz)
        bg = '#3a8fc9'
        fg = '#ffffff'
        margin = max(2, int(sz * 0.17))
        stroke = max(2, sz * 0.14)
        v_top = margin
        v_bot = sz - margin
        v_h = max(1, v_bot - v_top - 1)

        for y in range(sz):
            row = []
            for x in range(sz):
                if y < v_top or y >= v_bot:
                    row.append(bg); continue
                p = (y - v_top) / v_h
                lx = margin + p * (sz / 2 - margin)
                rx = sz - 1 - margin - p * (sz / 2 - margin)
                half = stroke / 2
                if abs(x - lx) <= half or abs(x - rx) <= half:
                    row.append(fg)
                else:
                    row.append(bg)
            img.put('{' + ' '.join(row) + '}', to=(0, y))
        icons.append(img)
    return icons
