#!/bin/bash

# Script de Build - Leitor de Cupons Fiscais Android
# Automação do processo de compilação com Buildozer

echo "🚀 === LEITOR DE CUPONS FISCAIS - BUILD ANDROID ==="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log_info() {
    echo -e "${BLUE}ℹ️  INFO:${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅ SUCCESS:${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠️  WARNING:${NC} $1"
}

log_error() {
    echo -e "${RED}❌ ERROR:${NC} $1"
}

# Verifica dependências
check_dependencies() {
    log_info "Verificando dependências..."
    
    # Verifica Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 não encontrado. Instale Python 3.8+"
        exit 1
    fi
    
    # Verifica Buildozer
    if ! command -v buildozer &> /dev/null; then
        log_warning "Buildozer não encontrado. Instalando..."
        pip install buildozer
        if [ $? -ne 0 ]; then
            log_error "Falha ao instalar Buildozer"
            exit 1
        fi
    fi
    
    log_success "Dependências verificadas"
}

# Limpa builds anteriores
clean_build() {
    log_info "Limpando builds anteriores..."
    
    if [ -d ".buildozer" ]; then
        rm -rf .buildozer
        log_success "Cache buildozer limpo"
    fi
    
    if [ -d "bin" ]; then
        rm -rf bin
        log_success "Diretório bin limpo"
    fi
}

# Build debug APK
build_debug() {
    log_info "Iniciando build DEBUG..."
    
    buildozer android debug
    
    if [ $? -eq 0 ]; then
        log_success "Build DEBUG concluído com sucesso!"
        
        # Verifica se APK foi gerado
        if [ -f "bin/qrreader-1.0.0-arm64-v8a-debug.apk" ]; then
            APK_SIZE=$(du -h bin/qrreader-1.0.0-arm64-v8a-debug.apk | cut -f1)
            log_success "APK gerado: bin/qrreader-1.0.0-arm64-v8a-debug.apk (${APK_SIZE})"
        else
            log_warning "APK não encontrado no local esperado. Verifique pasta bin/"
        fi
    else
        log_error "Falha no build DEBUG"
        exit 1
    fi
}

# Build release APK
build_release() {
    log_info "Iniciando build RELEASE..."
    
    buildozer android release
    
    if [ $? -eq 0 ]; then
        log_success "Build RELEASE concluído com sucesso!"
        
        # Verifica se APK foi gerado
        if [ -f "bin/qrreader-1.0.0-arm64-v8a-release-unsigned.apk" ]; then
            APK_SIZE=$(du -h bin/qrreader-1.0.0-arm64-v8a-release-unsigned.apk | cut -f1)
            log_success "APK gerado: bin/qrreader-1.0.0-arm64-v8a-release-unsigned.apk (${APK_SIZE})"
            log_warning "APK não assinado. Use jarsigner para produção."
        else
            log_warning "APK não encontrado no local esperado. Verifique pasta bin/"
        fi
    else
        log_error "Falha no build RELEASE"
        exit 1
    fi
}

# Deploy no dispositivo
deploy_apk() {
    log_info "Instalando APK no dispositivo..."
    
    # Verifica ADB
    if ! command -v adb &> /dev/null; then
        log_error "ADB não encontrado. Instale Android SDK Platform Tools"
        exit 1
    fi
    
    # Verifica dispositivos conectados
    DEVICES=$(adb devices | grep -w "device" | wc -l)
    if [ $DEVICES -eq 0 ]; then
        log_error "Nenhum dispositivo Android conectado"
        log_info "Conecte um dispositivo via USB e ative Depuração USB"
        exit 1
    fi
    
    log_success "$DEVICES dispositivo(s) conectado(s)"
    
    # Instala APK mais recente
    if [ -f "bin/qrreader-1.0.0-arm64-v8a-debug.apk" ]; then
        log_info "Instalando APK debug..."
        adb install -r bin/qrreader-1.0.0-arm64-v8a-debug.apk
        
        if [ $? -eq 0 ]; then
            log_success "APK instalado com sucesso!"
            log_info "Iniciando aplicação..."
            adb shell monkey -p com.business.qrreader -c android.intent.category.LAUNCHER 1
        else
            log_error "Falha na instalação do APK"
        fi
    else
        log_error "APK não encontrado. Execute build primeiro."
    fi
}

# Logs em tempo real
show_logs() {
    log_info "Mostrando logs em tempo real (Ctrl+C para sair)..."
    log_info "Filtrando logs do Python/Kivy..."
    
    adb logcat | grep -E "(python|kivy|QRReader)"
}

# Menu principal
show_menu() {
    echo ""
    echo "📋 Escolha uma opção:"
    echo "1) 🧹 Limpar builds anteriores"
    echo "2) 🔨 Build DEBUG"
    echo "3) 📦 Build RELEASE"
    echo "4) 📱 Deploy no dispositivo"
    echo "5) 📊 Mostrar logs"
    echo "6) 🔄 Build completo (limpar + debug + deploy)"
    echo "0) ❌ Sair"
    echo ""
    read -p "Opção: " choice
}

# Função principal
main() {
    echo "Versão: 1.0.0"
    echo "Autor: Business Solutions"
    echo ""
    
    check_dependencies
    
    while true; do
        show_menu
        
        case $choice in
            1)
                clean_build
                ;;
            2)
                build_debug
                ;;
            3)
                build_release
                ;;
            4)
                deploy_apk
                ;;
            5)
                show_logs
                ;;
            6)
                log_info "Iniciando build completo..."
                clean_build
                sleep 2
                build_debug
                sleep 2
                deploy_apk
                ;;
            0)
                log_success "Saindo..."
                exit 0
                ;;
            *)
                log_error "Opção inválida: $choice"
                ;;
        esac
        
        echo ""
        read -p "Pressione Enter para continuar..."
    done
}

# Executa função principal
main