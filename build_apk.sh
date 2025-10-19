#!/bin/bash

# Script para aceitar licenças do Android SDK automaticamente

set -e

echo "🔧 Configurando licenças do Android SDK..."

# Criar diretório de licenças se não existir
mkdir -p ~/.android/repositories.cfg

# Limpar cache do buildozer para forçar download correto do NDK
echo "🧹 Limpando cache do buildozer..."
rm -rf ~/.buildozer/android/platform/android-ndk-r*

# Definir variáveis de ambiente
export ANDROID_HOME="$HOME/.buildozer/android/platform/android-sdk"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export PATH="$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/tools/bin:$ANDROID_HOME/platform-tools"

# Forçar o NDK correto
export ANDROIDNDK=""  # Limpar para forçar novo download

echo "✅ Configuração completa!"

echo "🚀 Iniciando compilação do APK com NDK 25b..."
buildozer android debug