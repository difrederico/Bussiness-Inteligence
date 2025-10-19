@echo off
echo.
echo 📱 COMPILADOR APK - LEITOR QR FISCAL
echo =====================================
echo.

REM Verifica se Python está disponível
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    echo 💡 Instale Python ou use py.exe
    echo.
    echo 🚀 ALTERNATIVAS:
    echo 1. GitHub Codespaces - replit.com
    echo 2. WSL: wsl --install
    echo 3. Docker Desktop
    echo.
    pause
    exit /b 1
)

REM Verifica se buildozer está instalado
buildozer --version >nul 2>&1
if errorlevel 1 (
    echo 📦 Instalando buildozer...
    pip install buildozer
)

echo ✅ Iniciando compilação APK...
echo ⏱️ Isso pode demorar 15-30 minutos...
echo.

REM Compila o APK
buildozer android debug

REM Verifica se APK foi criado
if exist "bin\*.apk" (
    echo.
    echo 🎉 APK CRIADO COM SUCESSO!
    echo 📁 Localização: bin\
    
    REM Copia APK para local fácil
    for %%f in (bin\*.apk) do (
        copy "%%f" "LeitorQR_Fiscal.apk"
        echo 📋 Cópia criada: LeitorQR_Fiscal.apk
    )
    
    echo.
    echo 📱 PRÓXIMOS PASSOS:
    echo 1. Transfira LeitorQR_Fiscal.apk para o celular
    echo 2. Ative "Fontes Desconhecidas" no Android
    echo 3. Instale o APK
    echo 4. Permita acesso à câmera
    echo.
) else (
    echo.
    echo ❌ APK não foi criado
    echo 💡 ALTERNATIVAS RÁPIDAS:
    echo.
    echo 🌐 ONLINE (Mais Fácil):
    echo - Replit.com: Importe projeto e execute buildozer
    echo - GitHub Codespaces: Compile na nuvem
    echo.
    echo 🐧 WSL (Windows):
    echo - wsl --install
    echo - sudo apt install buildozer
    echo - buildozer android debug
    echo.
    echo 🐳 DOCKER:
    echo - docker run --rm -v "%cd%":/app kivy/buildozer android debug
    echo.
)

echo 📋 Veja INSTALACAO_CELULAR.md para mais detalhes
pause