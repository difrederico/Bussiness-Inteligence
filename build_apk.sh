#!/bin/bash

# Script para aceitar licenças do Android SDK automaticamente

set -e

echo "🔧 Configurando licenças do Android SDK..."

# Criar diretório de licenças se não existir
mkdir -p ~/.android/repositories.cfg

# Definir variáveis de ambiente
export ANDROID_HOME="$HOME/.buildozer/android/platform/android-sdk"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export PATH="$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/tools/bin:$ANDROID_HOME/platform-tools"

echo "✅ Licenças configuradas!"

echo "🚀 Iniciando compilação do APK..."
buildozer android debug