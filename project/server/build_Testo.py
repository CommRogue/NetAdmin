import os
import sys

import client_builder

options = [
            '..\\client\\source\\main.py',
            f'--distpath=build',
            '--onefile',
            '--noconsole', 
            '--add-binary=lib_bin\\turbojpeg-bin\\turbojpeg.dll;.',
            '--hidden-import=win32com.client',
            '--hidden-import=win32api',
            '--hidden-import=win32con',
            '--hidden-import=win32timezone',
            f"--paths={os.path.join(sys.path[0], '../shared')}",
]

#'--runtime-tmpdir=.',

client_builder.build(options)