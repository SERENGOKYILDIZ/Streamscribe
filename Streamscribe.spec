# -*- mode: python ; coding: utf-8 -*-
"""
StreamScribe v2.1.1 PyInstaller Specification File
STANDALONE BUILD - Works on computers without Python or other tools
Optimized build configuration with proper icon and metadata
Updated for v2.1.1 with progress bar stabilization and 403 error fixes
"""

import os
from pathlib import Path

# Get current directory
current_dir = Path.cwd()

# Icon path - use the high-quality favicon.ico
icon_path = current_dir / 'logo' / 'favicon.ico'

# Ensure icon exists
if not icon_path.exists():
    print(f"Warning: Icon not found at {icon_path}")
    icon_path = None

a = Analysis(
    ['main.py'],
    pathex=[str(current_dir)],
    binaries=[],
    datas=[
        ('ffmpeg', 'ffmpeg'),           # Built-in FFmpeg binaries
        ('logo', 'logo'),               # Application icons
        ('config.py', '.'),             # Configuration
        ('logger.py', '.'),             # Logging system
        ('error_handler.py', '.'),      # Error handling
        ('utils.py', '.'),              # Utility functions
        ('gui.py', '.'),                # GUI interface
        ('downloader.py', '.')          # Download engine
    ],
    hiddenimports=[
        # Core GUI and UI
        'customtkinter',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.scrolledtext',
        
        # Image processing
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL.ImageFilter',
        'PIL.ImageEnhance',
        
        # Network and HTTP
        'requests',
        'requests.adapters',
        'requests.auth',
        'requests.cookies',
        'requests.exceptions',
        'requests.models',
        'requests.sessions',
        'requests.structures',
        'requests.utils',
        'urllib3',
        'urllib3.util',
        'urllib3.exceptions',
        'urllib3.connection',
        'urllib3.connectionpool',
        'urllib3.poolmanager',
        'urllib3.response',
        'urllib3.filepost',
        'urllib3.fields',
        'urllib3.contrib',
        'urllib3.contrib.pyopenssl',
        'urllib3.contrib.socks',
        
        # YouTube downloading
        'yt_dlp',
        'yt_dlp.extractor',
        'yt_dlp.downloader',
        'yt_dlp.postprocessor',
        'yt_dlp.utils',
        'yt_dlp.compat',
        
        # System and utilities
        'threading',
        'logging',
        'pathlib',
        'json',
        'time',
        'subprocess',
        'platform',
        'os',
        'sys',
        'shutil',
        'tempfile',
        'webbrowser',
        'queue',
        'collections',
        'functools',
        'inspect',
        'traceback',
        'weakref',
        'gc',
        
        # Security and certificates
        'certifi',
        'charset_normalizer',
        'idna',
        'cryptography',
        'ssl',
        'hashlib',
        'hmac',
        
        # Data processing
        'base64',
        'binascii',
        'codecs',
        'encodings',
        'locale',
        're',
        'string',
        'unicodedata',
        
        # Additional dependencies
        'mutagen',
        'brotli',
        'secretstorage',
        'curl_cffi',
        'darkdetect',
        'packaging',
        'setuptools',
        'wheel',
        'importlib_metadata',
        'zipp',
        'tomli',
        'pycparser',
        'cffi',
        'six',
        'pyparsing',
        'markupsafe',
        'jinja2',
        'click',
        'itsdangerous',
        'werkzeug',
        'flask',
        
        # New v2.1 features and fixes
        'datetime',  # For playlist folder naming
        'html',      # For title cleaning
        'unicodedata', # For title normalization
        'argparse',  # For command line arguments
        'getattr',   # For safe attribute access
        'hasattr',   # For attribute checking
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude heavy ML/AI libraries (not needed for basic functionality)
        'torch', 'torchaudio', 'whisper', 'moviepy', 'numpy', 'numba', 
        'llvmlite', 'tensorflow', 'keras', 'scikit-learn', 'pandas',
        'matplotlib', 'seaborn', 'plotly', 'bokeh', 'dash', 'streamlit',
        
        # Exclude development and testing tools
        'tkinter.test', 'unittest', 'test', 'tests', 'pytest', 'nose',
        'coverage', 'pylint', 'flake8', 'black', 'isort', 'mypy',
        
        # Exclude documentation and examples
        'docutils', 'sphinx', 'pydoc', 'doctest', 'pdb', 'ipdb',
        
        # Exclude Jupyter and notebook tools
        'jupyter', 'notebook', 'ipython', 'ipykernel', 'nbconvert'
    ],
    noarchive=False,
    optimize=1,  # Reduced optimization for better compatibility
)

pyz = PYZ(a.pure, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Streamscribe_v2.1.1_Standalone',  # Standalone version name
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress executable
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_path) if icon_path else None,  # Set application icon
    version_file=None,  # Could add version info file later
)
