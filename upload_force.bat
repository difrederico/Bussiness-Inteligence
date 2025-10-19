@echo off
echo 🚀 FORÇANDO UPLOAD PARA GITHUB...
echo ================================

cd /d "c:\Users\ACER\Desktop\bussines\v2-android"

REM Verificar se estamos no diretório correto
echo Diretório atual:
cd

REM Remover .git se existir para recomeçar limpo
if exist ".git" (
    echo Removendo .git anterior...
    rmdir /s /q .git
)

echo.
echo ✅ Inicializando Git...
git init
if errorlevel 1 (
    echo ❌ Erro ao inicializar Git
    pause
    exit /b 1
)

echo ✅ Configurando usuário Git...
git config user.name "Federico Lemes Rosa"
git config user.email "difrederico@users.noreply.github.com"

echo ✅ Configurando branch main...
git branch -M main

echo ✅ Listando arquivos para adicionar...
dir

echo ✅ Adicionando todos os arquivos...
git add .
if errorlevel 1 (
    echo ❌ Erro ao adicionar arquivos
    pause
    exit /b 1
)

echo ✅ Verificando status...
git status

echo ✅ Fazendo commit...
git commit -m "Leitor QR Fiscal Android - Upload inicial"
if errorlevel 1 (
    echo ❌ Erro no commit
    pause
    exit /b 1
)

echo ✅ Adicionando repositório remoto...
git remote add origin https://github.com/difrederico/leitor-qr-fiscal-android.git
if errorlevel 1 (
    echo ℹ️ Repositório remoto já existe, continuando...
)

echo ✅ Fazendo push...
git push -u origin main --force
if errorlevel 1 (
    echo ❌ Erro no push - pode precisar de autenticação
    echo ℹ️ Tente fazer login no GitHub ou usar token
    pause
    exit /b 1
)

echo.
echo 🎉 SUCESSO! Arquivos enviados para GitHub!
echo.
echo 📱 Acesse: https://github.com/difrederico/leitor-qr-fiscal-android
echo.
pause