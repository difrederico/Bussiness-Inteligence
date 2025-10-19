[app]
# (str) Título do app
title = Leitor de Cupons Fiscais

# (str) Nome do pacote
package.name = leitorqr

# (str) Domínio do pacote (usado para Android/iOS packaging)
package.domain = com.business.fiscal

# (str) Arquivo principal do app
source.main = main_android_completo.py

# (list) Diretório de código fonte onde os arquivos Python são encontrados
source.dir = .

# (list) Padrões de arquivos para incluir
source.include_exts = py,png,jpg,kv,atlas,json

# (str) Versão da aplicação
version = 2.0

# (list) Requisitos da aplicação
requirements = python3,kivy==2.3.0,pyjnius,android

# (str) Requisitos opcionais (para funcionalidade completa)
# Para usar recursos avançados, instale separadamente:
# pip install opencv-python pyzbar

# (str) Versões suportadas do Python (padrão: 3.8,3.9,3.10,3.11)
osx.python_version = 3

# (int) Android API mínima que a aplicação vai suportar
android.minapi = 21

# (int) Android API que a aplicação vai compilar
android.api = 30

# (int) Android SDK para usar
android.sdk = 30

# (str) Versão do Android NDK para usar
android.ndk = 25b

# (str) Diretório do Android NDK (auto detect)
android.ndk_path = 

# (str) Diretório do Android SDK (auto detect)
android.sdk_path = 

# (list) Padrões para ignorar durante packaging
source.exclude_dirs = tests, bin, venv, __pycache__

# (list) Padrões de arquivos para excluir
source.exclude_patterns = license,images/*/*.jpg

# (str) Orientação da aplicação (landscape, portrait ou all)
orientation = portrait

# (bool) Indica se a aplicação deve ser fullscreen ou não
fullscreen = 0

# (list) Permissões
android.permissions = INTERNET,CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Alvo da arquitetura Android (arch arm64-v8a, armeabi-v7a, x86, x86_64)
android.archs = arm64-v8a

# (bool) Habilita AndroidX
android.enable_androidx = True

# (str) Bootstrap para usar (sdl2 é recomendado)
android.bootstrap = sdl2

# (bool) Aceitar licenças do SDK automaticamente
android.accept_sdk_license = True

# (str) Ícone da aplicação
icon.filename = %(source.dir)s/icon.png

# (str) Presplash da aplicação
presplash.filename = %(source.dir)s/presplash.png

[buildozer]
# (int) Log level (0 = apenas error, 1 = info, 2 = debug)
log_level = 2

# (int) Mostra saída completa do build
warn_on_root = 1