# PyInstaller spec for Focus Timer (onedir build, faster launch than onefile).
# Build with: pyinstaller packaging/focus-timer.spec
# (run from the repository root so relative paths resolve correctly)

a = Analysis(
    ["../src/main.py"],
    pathex=["."],
    datas=[
        ("../src/assets/alarm.wav", "src/assets"),
        ("../src/presentation/styles.qss", "src/presentation"),
    ],
    hiddenimports=[],
    hookspath=[],
    excludes=[],
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="focus-timer",
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name="focus-timer",
)
