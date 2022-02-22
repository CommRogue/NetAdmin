import PyInstaller.__main__
import os, sys

def build():
    PyInstaller.__main__.run([
        '..\\client\\main.py',
        '--onefile',
        '--runtime-tmpdir=.',
        '--add-binary=lib_bin\\turbojpeg-bin\\turbojpeg.dll;.',
        '--hidden-import=win32com.client',
        '--hidden-import=win32api',
        '--hidden-import=win32con',
        '--hidden-import=win32timezone',
        f"--paths={os.path.join(sys.path[0], '../shared')}",
    ])

build()