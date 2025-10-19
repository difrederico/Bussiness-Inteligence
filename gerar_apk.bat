@echo off
echo.
echo 🚀 GERADOR DE APK AUTOMÁTICO
echo ===========================
echo.
echo Este script vai:
echo 1. Preparar o projeto para GitHub
echo 2. Subir para o repositório
echo 3. Gerar APK automaticamente
echo 4. Disponibilizar download
echo.

set /p confirm="Continuar? (s/n): "
if /i not "%confirm%"=="s" exit /b

echo.
echo 📁 Preparando arquivos...

REM Cria .gitignore se não existir
if not exist ".gitignore" (
    echo # Buildozer files > .gitignore
    echo .buildozer/ >> .gitignore
    echo bin/ >> .gitignore
    echo __pycache__/ >> .gitignore
    echo *.pyc >> .gitignore
    echo .vscode/ >> .gitignore
    echo *.log >> .gitignore
)

echo ✅ Arquivos preparados

echo.
echo 📋 PRÓXIMOS PASSOS MANUAIS:
echo.
echo 1. Crie um repositório no GitHub:
echo    - Acesse github.com
echo    - Clique "New repository"
echo    - Nome: leitor-qr-fiscal
echo    - Público ou Privado
echo    - NÃO adicione README, .gitignore ou licença
echo.
echo 2. Execute estes comandos no terminal:
echo.
echo    git init
echo    git add .
echo    git commit -m "Leitor QR Fiscal Android - Primeira versão"
echo    git branch -M main
echo    git remote add origin https://github.com/SEU_USUARIO/leitor-qr-fiscal.git
echo    git push -u origin main
echo.
echo 3. O GitHub Actions irá compilar automaticamente!
echo.
echo 4. Em 10-15 minutos, baixe o APK em:
echo    https://github.com/SEU_USUARIO/leitor-qr-fiscal/releases
echo.

pause

echo.
echo 🔄 Quer que eu tente automatizar?
set /p auto="Tentar git automaticamente? (s/n): "
if /i not "%auto%"=="s" goto :manual

echo.
echo 📋 Insira a URL do seu repositório GitHub:
set /p repo_url="URL (ex: https://github.com/usuario/leitor-qr-fiscal.git): "

if "%repo_url%"=="" (
    echo ❌ URL não informada
    goto :manual
)

echo.
echo 🚀 Executando git...

git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git não instalado! Baixe em: https://git-scm.com
    goto :manual
)

git init
if errorlevel 1 goto :git_error

git add .
if errorlevel 1 goto :git_error

git commit -m "Leitor QR Fiscal Android - Primeira versão"
if errorlevel 1 goto :git_error

git branch -M main
if errorlevel 1 goto :git_error

git remote add origin "%repo_url%"
if errorlevel 1 goto :git_error

echo.
echo 📤 Fazendo upload... (pode pedir login GitHub)
git push -u origin main
if errorlevel 1 goto :git_error

echo.
echo 🎉 SUCESSO! Projeto enviado para GitHub!
echo.
echo 📱 O APK será compilado automaticamente em:
echo %repo_url%/actions
echo.
echo 📥 Download do APK em 10-15 minutos:
echo %repo_url%/releases
echo.
goto :end

:git_error
echo.
echo ❌ Erro no git. Tente manualmente:
goto :manual

:manual
echo.
echo 💡 COMANDOS MANUAIS:
echo.
echo git init
echo git add .
echo git commit -m "Leitor QR Fiscal Android"
echo git branch -M main
echo git remote add origin SUA_URL_AQUI
echo git push -u origin main
echo.

:end
echo 📋 Documentação completa em: README.md
echo 🎯 Guia de instalação em: INSTALACAO_CELULAR.md
echo.
pause