@echo off
echo 🚀 SUBINDO PROJETO PARA GITHUB...
echo ==================================

REM Navegar para o projeto
cd /d "c:\Users\ACER\Desktop\bussines\v2-android"

REM Limpar qualquer configuração Git anterior
if exist ".git" rmdir /s /q .git

echo ✅ Inicializando repositório Git...
git init

echo ✅ Configurando branch main...
git branch -M main

echo ✅ Adicionando arquivos...
git add .

echo ✅ Fazendo primeiro commit...
git commit -m "Leitor QR Fiscal Android - Primeira versão com GitHub Actions"

echo ✅ Conectando ao repositório GitHub...
git remote add origin https://github.com/difrederico/leitor-qr-fiscal-android.git

echo ✅ Enviando para GitHub...
git push -u origin main

echo.
echo 🎉 CONCLUÍDO!
echo.
echo 📱 PRÓXIMOS PASSOS:
echo 1. Acesse: https://github.com/difrederico/leitor-qr-fiscal-android/actions
echo 2. Aguarde compilação (10-15 min)
echo 3. Baixe APK em: https://github.com/difrederico/leitor-qr-fiscal-android/releases
echo.
pause