[app]
# Configuração básica da aplicação
title = Leitor QR Fiscal
package.name = leitorqr
package.domain = com.business

# Arquivo principal
source.main = main.py
source.dir = .

# Inclusões e exclusões - ULTRA RESTRITIVO
source.include_exts = py
source.exclude_exts = pyc,pyo,bak,tmp,log
source.exclude_dirs = tests,test,bin,dist,build,.git,.github,.buildozer,__pycache__,venv,.venv,node_modules
source.exclude_patterns = test_*,*_test*,*_backup*,*_old*,*_bak*,*_tmp*,*.log,*.tmp,README*,LICENSE*,*.md

# Versionamento
version = 1.0

# Dependências - MÍNIMAS e TESTADAS
requirements = python3,kivy==2.1.0,pillow

# Configurações Android
android.permissions = INTERNET,CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 28
android.minapi = 21
android.ndk = 21b
android.archs = armeabi-v7a
android.accept_sdk_license = True

# Configurações de interface
orientation = portrait
fullscreen = 0

# Bootstrap
p4a.bootstrap = sdl2

# Configurações avançadas
android.entrypoint = org.kivy.android.PythonActivity
android.theme = @android:style/Theme.NoTitleBar

[buildozer]
log_level = 2
warn_on_root = 1