# -*- mode: python ; coding: utf-8 -*-
import sys
sys.setrecursionlimit(1000000)
block_cipher = None


a = Analysis(['cli.py'],
             binaries=[],
             datas=[('Yesprit/data', 'Yesprit/data'), ('Yesprit/lib', 'Yesprit/lib'), ('Yesprit/resources','Yesprit/resources')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Yesprit',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True , icon='Yesprit/data/Yesprit.ico' )
