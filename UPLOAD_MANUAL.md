# 🚀 UPLOAD MANUAL PARA GITHUB - PASSO A PASSO

## ✅ VOCÊ PRECISA FAZER ISSO:

### 1️⃣ **Abrir GitHub no Navegador**
- Acesse: https://github.com/difrederico/Bussiness-Inteligence
- Clique em "v2-android" (pasta)

### 2️⃣ **Criar a Pasta .github/workflows**
- Clique "Add file" → "Create new file"
- Nome do arquivo: `.github/workflows/build.yml`
- Cole o conteúdo abaixo ↓

### 3️⃣ **Conteúdo do Arquivo build.yml**
```yaml
name: Build Android APK

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install system dependencies
      run: |
        sudo apt update
        sudo apt install -y git zip unzip openjdk-17-jdk autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
        sudo apt install -y build-essential libltdl-dev libffi-dev libssl-dev python3-dev
    
    - name: Install Python dependencies
      run: |
        pip install --upgrade pip
        pip install buildozer
        pip install kivy opencv-python pyzbar numpy
    
    - name: Build APK with Buildozer
      run: |
        cd v2-android
        buildozer android debug
    
    - name: Upload APK artifact
      uses: actions/upload-artifact@v3
      with:
        name: LeitorQR-Fiscal-APK
        path: v2-android/bin/*.apk
        
    - name: Create Release
      if: github.ref == 'refs/heads/main'
      uses: softprops/action-gh-release@v1
      with:
        tag_name: v1.0.${{ github.run_number }}
        name: Leitor QR Fiscal v1.0.${{ github.run_number }}
        files: v2-android/bin/*.apk
        body: |
          🚀 **Leitor QR Fiscal - Versão Android**
          
          📱 **APK Pronto para Instalação**
          
          **Como Instalar:**
          1. Baixe o arquivo APK
          2. Ative "Fontes Desconhecidas" no Android
          3. Instale o APK
          4. Permita acesso à câmera
          
          **Funcionalidades:**
          ✅ Leitura de QR Codes fiscais
          ✅ Validação de chaves de acesso
          ✅ Histórico de leituras
          ✅ Exportação CSV
          ✅ Interface mobile otimizada
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 4️⃣ **Salvar Arquivo**
- Clique "Commit new file"
- Mensagem: "Adicionar GitHub Actions para APK"

### 5️⃣ **Verificar Compilação**
- Vá em: **Actions** (aba do repositório)
- Aguarde "Build Android APK" aparecer
- Status: 🟡 Rodando → 🟢 Concluído

### 6️⃣ **Baixar APK**
- **Opção 1**: Aba "Releases" → Download direto
- **Opção 2**: Actions → Workflow concluído → Artifacts

---

## 📱 **RESULTADO FINAL**

Após 10-15 minutos você terá:
- ✅ APK compilado automaticamente
- ✅ Download disponível no GitHub
- ✅ Pronto para instalar no Android

**🎯 FAÇA ISSO AGORA E ME AVISE QUANDO TERMINAR!** 🚀