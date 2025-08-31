# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec file for the decoupled OneClick Launcher
#
# This creates a standalone executable with minimal dependencies
# for patch and launch functionality only.
#

block_cipher = None

a = Analysis(
    ['standalone_patch_and_launch.py'],
    pathex=[],
    binaries=[],
    datas=[('run_patch_client/run_ptch_client.exe', 'run_patch_client')],
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
    name='oneclick_launcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    single_file=True,
    destdir='dist'
)