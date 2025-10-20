[app]
# (str) Título do app  
title = Leitor QR Fiscal

# (str) Nome do pacote
package.name = leitorqr

# (str) Domínio do pacote
package.domain = com.business

# (str) Arquivo principal - APENAS main.py
source.main = main.py

# (str) Diretório de código fonte 
source.dir = .

# (list) EXTENSÕES PERMITIDAS - Extremamente restritivo
source.include_exts = py

# (list) ARQUIVOS ESPECÍFICOS PERMITIDOS - Lista branca
source.include_patterns = main.py

# (list) EXCLUSÕES AGRESSIVAS - Lista negra
source.exclude_exts = pyc,pyo,bak,tmp,log,old
source.exclude_dirs = tests,test,__pycache__,.git,.github,.buildozer,bin,dist,backup,old
source.exclude_patterns = test_*,*_test*,*_backup*,*_old*,*_bak*,*_complex*,*_moderno*,*_novo*,android_*,build_*,deploy_*,quick_*,*.log,*.tmp

# (str) Versão
version = 1.0

# (str) Versão do app (usada internamente)
version.regex = __version__ = ['"]([^'"]*)['"]
version.filename = %(source.dir)s/main.py

# (list) Dependências Python - MÍNIMAS
requirements = python3,kivy==2.1.0,pillow

# (list) Permissões Android - Essenciais apenas
android.permissions = INTERNET,CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# (int) Target Android API - Compatível
android.api = 28

# (int) Minimum API - Amplo suporte
android.minapi = 21

# (str) NDK - Estável e testado
android.ndk = 21b

# (str) Bootstrap - SDL2 padrão
p4a.bootstrap = sdl2

# (str) Orientação
orientation = portrait

# (bool) Fullscreen
fullscreen = 0

# (str) Ícone do app
#icon.filename = %(source.dir)s/data/icon.png

# (str) Presplash
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Arquiteturas suportadas - ARM apenas
android.archs = armeabi-v7a

# (bool) Aceitar licença SDK automaticamente
android.accept_sdk_license = True

# (str) Tema Android
android.theme = "@android:style/Theme.NoTitleBar"

# (str) Entry point
android.entrypoint = org.kivy.android.PythonActivity

# (str) Gradle dependencies - Mínimas
android.gradle_dependencies = 

# (str) Java build tool
android.gradle_repositories = 

# (list) Python for android (p4a) fork - Estável
#p4a.fork = kivy

# (str) python for android branch - Master estável
#p4a.branch = master

# (str) Nome da distribuição compilada
#p4a.dist_name = kivyapp

# (list) Whitelist de arquivos
#android.whitelist = 

# (str) Diretório onde o APK será criado
#android.outdir = %(source.dir)s/bin

[buildozer]
# (int) Log level (0 = apenas erros, 1 = info, 2 = debug)
log_level = 2

# (int) Exibir warnings quando executando como root
warn_on_root = 1