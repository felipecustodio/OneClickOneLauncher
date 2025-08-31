# -*- mode: python ; coding: utf-8 -*-
#
# DEPRECATED: This PyInstaller spec file is deprecated.
# 
# Please use the new decoupled version:
# oneclick_launcher/standalone.spec
#
# The new version creates a much smaller executable (~7MB vs ~50MB)
# and doesn't depend on the full OneLauncher package.
#

block_cipher = None

a = Analysis(
    ['patch_and_launch.py'],
    pathex=[],
    binaries=[],
    datas=[('src/run_patch_client/run_ptch_client.exe', 'run_patch_client')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='patch_and_launch',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    single_file=True,
    destdir='dist'
)
