@echo off
REM Script para build do Leitor de Cupons Fiscais - Versão Completa (Windows)
REM Uso: build_completo.bat [debug|release|clean|install|info|check]

setlocal enabledelayedexpansion

set "APP_NAME=Leitor de Cupons Fiscais - Completo"
set "PACKAGE_NAME=leitorqr"
set "VERSION=2.0"
set "BUILDOZER_SPEC=buildozer_completo.spec"
set "MAIN_FILE=main_android_completo.py"

REM Função para log com cores (limitado no Windows CMD)
:log
echo [BUILD] %~1
goto :eof

:success
echo [SUCCESS] %~1
goto :eof

:warning
echo [WARNING] %~1
goto :eof

:error
echo [ERROR] %~1
exit /b 1

REM Verifica se buildozer está instalado
:check_buildozer
buildozer version >nul 2>&1
if errorlevel 1 (
    call :error "Buildozer não encontrado. Instale com: pip install buildozer"
)
call :success "Buildozer encontrado"
goto :eof

REM Verifica arquivos necessários
:check_files
call :log "Verificando arquivos necessários..."

if not exist "%MAIN_FILE%" (
    call :error "Arquivo principal não encontrado: %MAIN_FILE%"
)

if not exist "%BUILDOZER_SPEC%" (
    call :error "Arquivo de configuração não encontrado: %BUILDOZER_SPEC%"
)

call :success "Todos os arquivos necessários encontrados"
goto :eof

REM Prepara ambiente de build
:prepare_build
call :log "Preparando ambiente de build..."

REM Faz backup do buildozer.spec existente
if exist "buildozer.spec" (
    call :log "Fazendo backup do buildozer.spec existente..."
    for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
    set "backup_name=buildozer.spec.backup.!dt:~0,14!"
    move "buildozer.spec" "!backup_name!" >nul
)

copy "%BUILDOZER_SPEC%" "buildozer.spec" >nul
call :success "Configuração aplicada: %BUILDOZER_SPEC% -> buildozer.spec"
goto :eof

REM Limpa builds anteriores
:clean_build
call :log "Limpando builds anteriores..."

if exist ".buildozer" (
    call :log "Removendo diretório .buildozer..."
    rmdir /s /q ".buildozer" >nul 2>&1
)

if exist "bin" (
    call :log "Removendo diretório bin..."
    rmdir /s /q "bin" >nul 2>&1
)

if exist "buildozer.spec" (
    call :log "Removendo buildozer.spec temporário..."
    del "buildozer.spec" >nul 2>&1
)

call :success "Limpeza concluída"
goto :eof

REM Build debug
:build_debug
call :log "Iniciando build DEBUG do %APP_NAME% v%VERSION%..."

call :prepare_build

call :log "Executando buildozer android debug..."
buildozer android debug

if exist "bin\%PACKAGE_NAME%-%VERSION%-debug.apk" (
    call :success "Build DEBUG concluído com sucesso!"
    call :log "APK gerado: bin\%PACKAGE_NAME%-%VERSION%-debug.apk"
) else (
    call :error "Build falhou - APK não encontrado"
)
goto :eof

REM Build release  
:build_release
call :log "Iniciando build RELEASE do %APP_NAME% v%VERSION%..."

call :prepare_build

call :log "Executando buildozer android release..."
buildozer android release

if exist "bin\%PACKAGE_NAME%-%VERSION%-release-unsigned.apk" (
    call :success "Build RELEASE concluído com sucesso!"
    call :log "APK gerado: bin\%PACKAGE_NAME%-%VERSION%-release-unsigned.apk"
    call :warning "ATENÇÃO: APK não está assinado. Para produção, assine com jarsigner."
) else (
    call :error "Build falhou - APK não encontrado"
)
goto :eof

REM Instala APK no dispositivo
:install_apk
call :log "Procurando APKs para instalação..."

set "APK_FILE="

REM Procura APK mais recente (simplificado para Windows)
if exist "bin\*release*.apk" (
    for %%f in (bin\*release*.apk) do set "APK_FILE=%%f"
    call :log "Encontrado APK release: !APK_FILE!"
) else if exist "bin\*debug.apk" (
    for %%f in (bin\*debug.apk) do set "APK_FILE=%%f"
    call :log "Encontrado APK debug: !APK_FILE!"
) else (
    call :error "Nenhum APK encontrado. Execute build primeiro."
)

REM Verifica se ADB está disponível
adb version >nul 2>&1
if errorlevel 1 (
    call :error "ADB não encontrado. Instale Android SDK Platform Tools."
)

REM Verifica dispositivos conectados
call :log "Verificando dispositivos Android conectados..."
adb devices | find "device" >nul
if errorlevel 1 (
    call :error "Nenhum dispositivo Android conectado. Conecte um dispositivo e habilite depuração USB."
)

call :log "Dispositivos encontrados:"
adb devices

REM Instala APK
call :log "Instalando APK: !APK_FILE!"
adb install -r "!APK_FILE!"
if errorlevel 1 (
    call :error "Falha na instalação do APK"
) else (
    call :success "App instalado com sucesso!"
    call :log "Inicie o app no dispositivo: %APP_NAME%"
)
goto :eof

REM Mostra informações do projeto
:show_info
call :log "=== INFORMAÇÕES DO PROJETO ==="
call :log "Nome: %APP_NAME%"
call :log "Pacote: %PACKAGE_NAME%"
call :log "Versão: %VERSION%"
call :log "Arquivo principal: %MAIN_FILE%"
call :log "Configuração: %BUILDOZER_SPEC%"
echo.
call :log "Funcionalidades incluídas:"
call :log "  ✅ Validação de chaves fiscais"
call :log "  ✅ Câmera com auto-scan"
call :log "  ✅ Upload de imagens"
call :log "  ✅ Armazenamento local" 
call :log "  ✅ Exportação CSV"
call :log "  ✅ Modo batch"
call :log "  ✅ Busca em tempo real"
echo.
call :log "Dependências opcionais:"
call :log "  📦 opencv-python (processamento avançado)"
call :log "  📦 pyzbar (decodificação QR otimizada)"
echo.
call :log "Compatibilidade:"
call :log "  🤖 Android API 21+ (Android 5.0+)"
call :log "  📱 ARM64 e ARMv7"
call :log "  🔐 Permissões: CAMERA, STORAGE"
goto :eof

REM Mostra modo de uso
:show_usage
echo Uso: %~nx0 [comando]
echo.
echo Comandos disponíveis:
echo   debug     - Build APK debug
echo   release   - Build APK release
echo   clean     - Limpa builds anteriores
echo   install   - Instala APK no dispositivo
echo   info      - Mostra informações do projeto
echo   check     - Verifica ambiente de desenvolvimento
echo.
echo Exemplos:
echo   %~nx0 debug           # Build para desenvolvimento
echo   %~nx0 release         # Build para produção
echo   %~nx0 clean           # Limpa builds anteriores
echo   %~nx0 install         # Instala APK mais recente
goto :eof

REM Verifica ambiente
:check_environment
call :log "=== VERIFICAÇÃO DO AMBIENTE ==="

call :check_buildozer
call :check_files

call :log "Verificando Python..."
python --version >nul 2>&1
if errorlevel 1 (
    python3 --version >nul 2>&1
    if errorlevel 1 (
        call :error "Python não encontrado"
    ) else (
        call :success "Python 3 encontrado"
    )
) else (
    call :success "Python encontrado"
)

call :log "Verificando pip..."
pip --version >nul 2>&1
if errorlevel 1 (
    call :warning "pip não encontrado"
) else (
    call :success "pip encontrado"
)

call :log "Verificando Java..."
java -version >nul 2>&1
if errorlevel 1 (
    call :warning "Java não encontrado"
) else (
    call :success "Java encontrado"
)

adb version >nul 2>&1
if errorlevel 1 (
    call :warning "ADB não encontrado - instalação manual será necessária"
) else (
    call :success "ADB encontrado"
)

call :success "Verificação do ambiente concluída"
goto :eof

REM Função principal
:main
if "%1"=="" (
    call :show_info
    echo.
    call :show_usage
    exit /b 0
)

:process_args
if "%1"=="" goto :end_args

if /i "%1"=="debug" (
    call :build_debug
) else if /i "%1"=="release" (
    call :build_release  
) else if /i "%1"=="clean" (
    call :clean_build
) else if /i "%1"=="install" (
    call :install_apk
) else if /i "%1"=="info" (
    call :show_info
) else if /i "%1"=="check" (
    call :check_environment
) else if /i "%1"=="help" (
    call :show_usage
) else if /i "%1"=="--help" (
    call :show_usage
) else if /i "%1"=="-h" (
    call :show_usage
) else (
    call :error "Comando desconhecido: %1"
)

shift
goto :process_args

:end_args
exit /b 0

REM Chama função principal
call :main %*