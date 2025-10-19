@echo off
REM Script de Build - Leitor de Cupons Fiscais Android (Windows)
REM Automação do processo de compilação com Buildozer

title Leitor de Cupons Fiscais - Build Android

echo.
echo 🚀 === LEITOR DE CUPONS FISCAIS - BUILD ANDROID ===
echo.
echo Versão: 1.0.0
echo Autor: Business Solutions
echo.

REM Cores para Windows (usando echo com códigos ANSI)
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "NC=[0m"

:check_dependencies
echo %BLUE%ℹ️  INFO:%NC% Verificando dependências...

REM Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%❌ ERROR:%NC% Python não encontrado. Instale Python 3.8+
    pause
    exit /b 1
)

REM Verifica Buildozer
buildozer --version >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%⚠️  WARNING:%NC% Buildozer não encontrado. Instalando...
    pip install buildozer
    if errorlevel 1 (
        echo %RED%❌ ERROR:%NC% Falha ao instalar Buildozer
        pause
        exit /b 1
    )
)

echo %GREEN%✅ SUCCESS:%NC% Dependências verificadas
echo.

:menu
echo.
echo 📋 Escolha uma opção:
echo 1) 🧹 Limpar builds anteriores
echo 2) 🔨 Build DEBUG
echo 3) 📦 Build RELEASE  
echo 4) 📱 Deploy no dispositivo
echo 5) 📊 Mostrar logs
echo 6) 🔄 Build completo (limpar + debug + deploy)
echo 0) ❌ Sair
echo.
set /p choice="Opção: "

if "%choice%"=="1" goto clean_build
if "%choice%"=="2" goto build_debug
if "%choice%"=="3" goto build_release
if "%choice%"=="4" goto deploy_apk
if "%choice%"=="5" goto show_logs
if "%choice%"=="6" goto full_build
if "%choice%"=="0" goto exit_script

echo %RED%❌ ERROR:%NC% Opção inválida: %choice%
goto menu

:clean_build
echo %BLUE%ℹ️  INFO:%NC% Limpando builds anteriores...

if exist ".buildozer" (
    rmdir /s /q ".buildozer"
    echo %GREEN%✅ SUCCESS:%NC% Cache buildozer limpo
)

if exist "bin" (
    rmdir /s /q "bin"
    echo %GREEN%✅ SUCCESS:%NC% Diretório bin limpo
)

echo.
pause
goto menu

:build_debug
echo %BLUE%ℹ️  INFO:%NC% Iniciando build DEBUG...
echo.

buildozer android debug

if errorlevel 1 (
    echo %RED%❌ ERROR:%NC% Falha no build DEBUG
    pause
    goto menu
)

echo %GREEN%✅ SUCCESS:%NC% Build DEBUG concluído com sucesso!

REM Verifica se APK foi gerado
if exist "bin\qrreader-1.0.0-arm64-v8a-debug.apk" (
    for %%A in ("bin\qrreader-1.0.0-arm64-v8a-debug.apk") do (
        echo %GREEN%✅ SUCCESS:%NC% APK gerado: bin\qrreader-1.0.0-arm64-v8a-debug.apk ^(%%~zA bytes^)
    )
) else (
    echo %YELLOW%⚠️  WARNING:%NC% APK não encontrado no local esperado. Verifique pasta bin\
)

echo.
pause
goto menu

:build_release
echo %BLUE%ℹ️  INFO:%NC% Iniciando build RELEASE...
echo.

buildozer android release

if errorlevel 1 (
    echo %RED%❌ ERROR:%NC% Falha no build RELEASE
    pause
    goto menu
)

echo %GREEN%✅ SUCCESS:%NC% Build RELEASE concluído com sucesso!

REM Verifica se APK foi gerado
if exist "bin\qrreader-1.0.0-arm64-v8a-release-unsigned.apk" (
    for %%A in ("bin\qrreader-1.0.0-arm64-v8a-release-unsigned.apk") do (
        echo %GREEN%✅ SUCCESS:%NC% APK gerado: bin\qrreader-1.0.0-arm64-v8a-release-unsigned.apk ^(%%~zA bytes^)
    )
    echo %YELLOW%⚠️  WARNING:%NC% APK não assinado. Use jarsigner para produção.
) else (
    echo %YELLOW%⚠️  WARNING:%NC% APK não encontrado no local esperado. Verifique pasta bin\
)

echo.
pause
goto menu

:deploy_apk
echo %BLUE%ℹ️  INFO:%NC% Instalando APK no dispositivo...

REM Verifica ADB
adb version >nul 2>&1
if errorlevel 1 (
    echo %RED%❌ ERROR:%NC% ADB não encontrado. Instale Android SDK Platform Tools
    pause
    goto menu
)

REM Verifica dispositivos conectados
for /f %%i in ('adb devices ^| find /c "device"') do set device_count=%%i
set /a device_count=device_count-1

if %device_count% LEQ 0 (
    echo %RED%❌ ERROR:%NC% Nenhum dispositivo Android conectado
    echo %BLUE%ℹ️  INFO:%NC% Conecte um dispositivo via USB e ative Depuração USB
    pause
    goto menu
)

echo %GREEN%✅ SUCCESS:%NC% %device_count% dispositivo^(s^) conectado^(s^)

REM Instala APK mais recente
if exist "bin\qrreader-1.0.0-arm64-v8a-debug.apk" (
    echo %BLUE%ℹ️  INFO:%NC% Instalando APK debug...
    adb install -r "bin\qrreader-1.0.0-arm64-v8a-debug.apk"
    
    if errorlevel 1 (
        echo %RED%❌ ERROR:%NC% Falha na instalação do APK
        pause
        goto menu
    )
    
    echo %GREEN%✅ SUCCESS:%NC% APK instalado com sucesso!
    echo %BLUE%ℹ️  INFO:%NC% Iniciando aplicação...
    adb shell monkey -p com.business.qrreader -c android.intent.category.LAUNCHER 1
) else (
    echo %RED%❌ ERROR:%NC% APK não encontrado. Execute build primeiro.
)

echo.
pause
goto menu

:show_logs
echo %BLUE%ℹ️  INFO:%NC% Mostrando logs em tempo real ^(Ctrl+C para sair^)...
echo %BLUE%ℹ️  INFO:%NC% Filtrando logs do Python/Kivy...
echo.

adb logcat | findstr /i "python kivy QRReader"

echo.
pause
goto menu

:full_build
echo %BLUE%ℹ️  INFO:%NC% Iniciando build completo...
echo.

REM Limpar
call :clean_build

echo.
echo Aguardando 3 segundos...
timeout /t 3 /nobreak >nul

REM Build debug
call :build_debug

echo.
echo Aguardando 3 segundos...
timeout /t 3 /nobreak >nul

REM Deploy
call :deploy_apk

echo.
echo %GREEN%✅ SUCCESS:%NC% Build completo finalizado!
pause
goto menu

:exit_script
echo %GREEN%✅ SUCCESS:%NC% Saindo...
exit /b 0