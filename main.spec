# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py','.\\ui\CSGO_UI.py','Process.py','.\\ui\\KeyEdit_UI.py','CSGOLUAKeyListener.py','EditKeysLua.py','tool.py'],
    pathex=['G:\\python\\PythonGuns\\python-guns\\CSGO_LUA'],
    binaries=[],
    datas=[('G:\\python\\PythonGuns\\python-guns\\CSGO_LUA\\_internal\\LUA','LUA'),
    ('G:\\python\\PythonGuns\\python-guns\\CSGO_LUA\\_internal\\config.json'),
    ('G:\\python\\PythonGuns\\python-guns\\CSGO_LUA\\_internal\\info.html'),
    ('G:\\python\\PythonGuns\\python-guns\\CSGO_LUA\\ico','ico')],
    hiddenimports=['G:\\python\\PythonGuns\\python-guns\\CSGO_LUA'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)


pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    icon='G:\\python\\PythonGuns\\python-guns\\CSGO_LUA\\ico\\GHUB.ico',
    exclude_binaries=True,
    name='GHUB',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    onefile=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GHUB',
    icon='G:\\python\\PythonGuns\\python-guns\\CSGO_LUA\\ico\\GHUB.ico',
)
