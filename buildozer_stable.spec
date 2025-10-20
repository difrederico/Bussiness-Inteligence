[app]
# (str) Título do app
title = Leitor de Cupons Fiscais

# (str) Nome do pacote
package.name = leitorqrfiscal

# (str) Domínio do pacote (usado para Android/iOS packaging)
package.domain = com.business

# (str) Arquivo principal do app
source.main = main.py

# (list) Diretório de código fonte onde os arquivos Python são encontrados
source.dir = .

# (list) Padrões de arquivos para incluir
source.include_exts = py,png,jpg,kv,atlas,json

# (str) Versão da aplicação
version = 2.1

# 🔧 REQUIREMENTS CORRIGIDOS - VERSÃO ESTÁVEL
# ✅ Apenas dependências com recipes estáveis no p4a
# ❌ Removido opencv (causa falhas de build)
# ❌ Removido numpy (instável no p4a atual)
# ✅ Mantido pyjnius (essencial para APIs Android nativas)
requirements = python3,kivy==2.3.0,pillow,pyjnius,android

# (str) Requisitos garden (extensões Kivy)
garden_requirements = 

# 📱 COMPATIBILIDADE ANDROID ATUALIZADA
# ✅ APIs atualizadas para padrão 2024
# ✅ NDK compatível com GitHub Actions Ubuntu
# ✅ SDK estável e testado

# (str) Versões suportadas do Python
osx.python_version = 3

# 🎯 ANDROID APIS CORRIGIDAS
# ❌ android.api = 30 (muito antigo)
# ❌ android.sdk = 30 (obsoleto - causa erro!)
# ✅ Usando APIs mais recentes e estáveis

# (int) Android API mínima que a aplicação vai suportar
android.minapi = 21

# (int) Android API que a aplicação vai compilar (CORRIGIDO)
android.api = 33

# 🚫 REMOVIDO android.sdk - CAUSA ERRO FATAL
# Esta configuração está obsoleta e causa falha no build
# O buildozer detecta automaticamente a versão correta

# (str) Versão do Android NDK para usar (ATUALIZADA)
android.ndk = 25b

# (str) Diretório do Android NDK (auto detect)
android.ndk_path = 

# (str) Diretório do Android SDK (auto detect)
android.sdk_path = 

# (list) Padrões para ignorar durante packaging
source.exclude_dirs = tests, bin, venv, __pycache__, .buildozer, .git

# (list) Padrões de arquivos para excluir
source.exclude_patterns = license,images/*/*.jpg,*.pyc,*.pyo

# (str) Orientação da aplicação
orientation = portrait

# (bool) Indica se a aplicação deve ser fullscreen ou não
fullscreen = 0

# 🔐 PERMISSÕES ANDROID ESSENCIAIS
# ✅ Apenas as permissões realmente necessárias
# ✅ Compatível com Android 13+ (runtime permissions)
android.permissions = INTERNET,CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Arquitetura Android (OTIMIZADA)
# ✅ arm64-v8a: Mais comum e estável
# ❌ Removidas outras arqus para evitar problemas
android.archs = arm64-v8a

# (bool) Habilita AndroidX (ESSENCIAL para Android moderno)
android.enable_androidx = True

# 📦 BOOTSTRAP ESTÁVEL
# ✅ sdl2: Mais compatível com GitHub Actions
p4a.bootstrap = sdl2

# (bool) Aceitar licenças do SDK automaticamente
android.accept_sdk_license = True

# 🎨 RECURSOS VISUAIS (desabilitados para evitar problemas)
# icon.filename = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/presplash.png

[buildozer]
# (int) Log level (2 = debug completo para troubleshooting)
log_level = 2

# (int) Aviso quando executado como root
warn_on_root = 1