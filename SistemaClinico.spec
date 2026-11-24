# -*- mode: python ; coding: utf-8 -*-
# SistemaClinico.spec
# Generado para: registro_clinico v1.1.0
# PyInstaller spec con hidden imports completos para Firebase, PyQt6, cryptography, reportlab

import os
BASE = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    [os.path.join(BASE, 'main.py')],
    pathex=[BASE],
    binaries=[],
    datas=[
        (os.path.join(BASE, 'styles'), 'styles'),
        (os.path.join(BASE, 'data'),   'data'),
    ],
    hiddenimports=[
        # PyQt6
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtPrintSupport',
        # Firebase Admin SDK
        'firebase_admin',
        'firebase_admin.auth',
        'firebase_admin.firestore',
        'firebase_admin.credentials',
        'firebase_admin.exceptions',
        # Google Cloud / gRPC
        'google.cloud.firestore',
        'google.cloud.firestore_v1',
        'google.auth',
        'google.auth.credentials',
        'google.auth.transport.requests',
        'google.auth.transport.grpc',
        'google.oauth2',
        'google.oauth2.credentials',
        'google.oauth2.service_account',
        'grpc',
        'grpc._channel',
        'grpc.experimental',
        # Pyrebase4
        'pyrebase',
        'pyrebase4',
        'requests',
        'requests.adapters',
        'urllib3',
        # Cryptography
        'cryptography',
        'cryptography.fernet',
        'cryptography.hazmat',
        'cryptography.hazmat.primitives',
        'cryptography.hazmat.backends',
        # ReportLab
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.pdfgen.canvas',
        'reportlab.lib',
        'reportlab.lib.pagesizes',
        'reportlab.lib.styles',
        'reportlab.lib.units',
        'reportlab.platypus',
        # SQLite / stdlib
        'sqlite3',
        '_sqlite3',
        'json',
        'hashlib',
        'base64',
        'threading',
        'queue',
        'logging',
        'datetime',
        'pathlib',
        'shutil',
        'zipfile',
        'configparser',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas', 'scipy'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SistemaClinico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(BASE, 'data', 'app_icon.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SistemaClinico',
)
