"""Build script — create a standalone DomainTool.exe using PyInstaller.

Usage:
    pip install pyinstaller pillow   # one-time setup
    python build.py                  # creates dist/DomainTool.exe

The script will:
    1. Generate icon.ico from the V-letter design (requires Pillow)
    2. Run PyInstaller to create a single-file EXE
"""

import subprocess
import sys
import os

_DIR = os.path.dirname(os.path.abspath(__file__))
_ICO_PATH = os.path.join(_DIR, 'icon.ico')


def generate_ico():
    """Generate icon.ico using Pillow."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("[!] Pillow not installed. Run: pip install pillow")
        print("    Building without custom icon...")
        return None

    sizes = [16, 32, 48, 64, 128, 256]
    images = []
    for sz in sizes:
        img = Image.new('RGBA', (sz, sz), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # Rounded rectangle background
        r = max(2, sz // 6)
        draw.rounded_rectangle([0, 0, sz - 1, sz - 1], radius=r, fill='#3a8fc9')
        # V shape as polygon
        m = int(sz * 0.18)
        sw = max(2, int(sz * 0.13))
        points = [
            (m, m),                         # top-left outer
            (m + sw, m),                    # top-left inner
            (sz // 2, sz - m - sw // 2),    # bottom center inner
            (sz - m - sw, m),               # top-right inner
            (sz - m, m),                    # top-right outer
            (sz // 2, sz - m),              # bottom center outer
        ]
        draw.polygon(points, fill='white')
        images.append(img)

    images[0].save(_ICO_PATH, format='ICO',
                   sizes=[(s, s) for s in sizes])
    print(f"[+] Generated {_ICO_PATH}")
    return _ICO_PATH


def build_exe():
    """Run PyInstaller to create DomainTool.exe."""
    ico = generate_ico()

    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--windowed',
        '--name=DomainTool',
        '--add-data', f'lang.py{os.pathsep}.',
        '--add-data', f'icon.py{os.pathsep}.',
        '--clean',
    ]
    if ico and os.path.exists(ico):
        cmd.extend(['--icon', ico])

    cmd.append('main.py')

    print(f"[*] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=_DIR)

    if result.returncode == 0:
        exe = os.path.join(_DIR, 'dist', 'DomainTool.exe')
        print(f"\n[+] Build successful!")
        print(f"    EXE: {exe}")
        print(f"    Size: {os.path.getsize(exe) / 1024 / 1024:.1f} MB")
    else:
        print(f"\n[!] Build failed with code {result.returncode}")
        print("    Make sure PyInstaller is installed: pip install pyinstaller")
        sys.exit(1)


if __name__ == '__main__':
    build_exe()
