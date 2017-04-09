# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['E:\\MyProject\\Python\\pattern\\TextureRecognize'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='TextureRecognize',
          debug=False,
          strip=False,
          upx=True,
          console=True , icon='icon.ico')

# Copy  assets files
from shutil import rmtree, copytree
rmtree('./dist/assets/', ignore_errors=True)
copytree('./assets/', './dist/assets/')
