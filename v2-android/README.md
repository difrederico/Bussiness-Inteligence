# 📱 Leitor de Cupons Fiscais - Android

**🚀 APK PRONTO PARA DOWNLOAD! 🚀**

[![Build Android APK](https://github.com/usuario/leitor-qr-fiscal/actions/workflows/build.yml/badge.svg)](https://github.com/usuario/leitor-qr-fiscal/actions/workflows/build.yml)

## 📱 **[BAIXAR APK AQUI](https://github.com/usuario/leitor-qr-fiscal/releases/latest)** 

---

## 🚀 Instalação Rápida no Android

### 1️⃣ **Baixar APK**
- Clique no link acima
- Baixe `LeitorQR-Fiscal.apk`

### 2️⃣ **Preparar Celular**
```
Configurações → Segurança → Fontes Desconhecidas → ATIVAR
```

### 3️⃣ **Instalar**
1. Abra o APK baixado
2. Toque "Instalar"
3. Confirme "Instalar mesmo assim"

### 4️⃣ **Configurar Permissões**
```
Configurações → Apps → Leitor QR Fiscal → Permissões
✅ Câmera: Permitir
✅ Armazenamento: Permitir
```

---

## 📋 Descrição

Aplicação móvel desenvolvida em **Kivy** para Android que permite:

✅ **Leitura de QR codes** de cupons fiscais via câmera  
✅ **Upload de imagens** com QR codes da galeria  
✅ **Validação automática** das chaves de acesso fiscais  
✅ **Armazenamento seguro** das chaves lidas  
✅ **Exportação CSV** dos dados coletados  
✅ **Interface otimizada** para dispositivos móveis  

---

## 🔧 Funcionalidades

### 📷 Detecção Avançada
- **3 modos de detecção**: Simples, Melhorado, Agressivo
- **15+ técnicas** de processamento de imagem
- **Otimização mobile** para melhor performance
- **Suporte rotação** e diferentes escalas

### 📊 Gerenciamento de Dados
- **Armazenamento local** em JSON
- **Busca e filtros** nas chaves salvas
- **Validação DV** das chaves de acesso
- **Detecção de duplicatas** automática

### 📤 Exportação
- **Formato CSV** padronizado
- **Separador ponto-vírgula** (Excel BR)
- **Encoding UTF-8** com BOM
- **Salva na pasta Downloads**

---

## 📱 Requisitos Android

- **Android 5.0+** (API 21)
- **Câmera** com permissão
- **Armazenamento** com permissão
- **4GB RAM** recomendado

---

## 🚀 Instalação

### Método 1: APK Pré-compilado
```bash
# Baixe o APK e instale diretamente
adb install qrreader-1.0.0.apk
```

### Método 2: Compilação com Buildozer
```bash
# Instale buildozer
pip install buildozer

# Clone o projeto
git clone [repo]
cd v2-android

# Compile para Android
buildozer android debug

# Instale no dispositivo conectado
buildozer android deploy run
```

---

## 📚 Dependências

### Python Packages
- **kivy**: Framework UI móvel
- **kivymd**: Material Design
- **opencv-python**: Processamento de imagem
- **pyzbar**: Decodificação QR
- **numpy**: Computação numérica
- **pillow**: Manipulação de imagem
- **plyer**: APIs nativas Android

### Android Permissions
- `CAMERA`: Acesso à câmera
- `WRITE_EXTERNAL_STORAGE`: Salvar arquivos
- `READ_EXTERNAL_STORAGE`: Ler arquivos  
- `INTERNET`: Atualizações (opcional)

---

## 🎯 Como Usar

### 1. **Leitura por Câmera**
- Abra o app
- Toque em "📷 Iniciar Câmera"
- Aponte para o QR code do cupom
- Aguarde a detecção automática

### 2. **Leitura por Upload**
- Toque em "📤 Upload"
- Selecione imagem da galeria
- Aguarde o processamento

### 3. **Gerenciar Chaves**
- Visualize lista de cupons lidos
- Use 📋 para copiar chaves
- Busque por texto específico
- Exporte dados em CSV

### 4. **Configurações**
- **Modo**: Simples/Melhorado/Agressivo
- **Debug**: Logs detalhados
- **Performance**: Monitoramento FPS

---

## 🔍 Algoritmos de Detecção

### 🟢 Simples
- Detecção direta sem pré-processamento
- **Mais rápido**, menor precisão
- Ideal para QR codes nítidos

### 🟡 Melhorado (Padrão)
- Equalização de histograma
- Threshold adaptativo
- Filtro bilateral
- **Balanceado** velocidade/precisão

### 🔴 Agressivo
- Múltiplas escalas (0.8x, 1.2x, 1.5x)
- Rotações (-15°, -10°, +10°, +15°)
- **Máxima precisão** para casos difíceis
- Mais lento, ideal para imagens borradas

---

## 📊 Estrutura de Dados

### Chave Fiscal Salva
```json
{
  "key": "35200114200166000166550010000000046176777681",
  "timestamp": 1640995200.0
}
```

### Arquivo CSV Exportado
```csv
Chave_Fiscal;Data_Leitura;Hora_Leitura
35200114200166000166550010000000046176777681;31/12/2021;18:00:00
```

---

## 🛠️ Desenvolvimento

### Estrutura do Projeto
```
v2-android/
├── main.py              # Aplicação principal
├── buildozer.spec       # Configuração Android
├── README.md           # Documentação
└── assets/             # Recursos (ícones, etc)
```

### Logs e Debug
```python
# Ativar debug no app
self.debug_switch.active = True

# Logs no Android
adb logcat | grep python
```

### Testes Locais
```bash
# Executar no desktop (testes)
python main.py

# Testar dependências
python -c "import cv2, pyzbar, numpy, kivy"
```

---

## 🔄 Diferenças da Versão Desktop

| Funcionalidade | Desktop | Android |
|---|---|---|
| **Framework** | Tkinter | Kivy |
| **Interface** | Janelas | Touch/Mobile |
| **Câmera** | OpenCV VideoCapture | Kivy Camera |
| **Audio** | pygame | Plyer notifications |
| **Arquivos** | tkinter.filedialog | Android Storage |
| **Clipboard** | tkinter/pyperclip | Android ClipboardManager |

---

## ⚡ Performance

### Otimizações Mobile
- **FPS limitado**: 10 FPS para economia de bateria
- **Cooldown**: 2s entre detecções sucessivas
- **Técnicas reduzidas**: Apenas as mais eficientes
- **Resolução adaptativa**: Redimensiona frames grandes

### Monitoramento
- **FPS em tempo real** no debug
- **Contador de frames** processados
- **Tempo de resposta** das detecções

---

## 🐛 Troubleshooting

### Problemas Comuns

**❌ Câmera não funciona**
```bash
# Verificar permissões
adb shell pm grant com.business.qrreader android.permission.CAMERA
```

**❌ QR não detecta**
- Teste modo "Agressivo"
- Melhore iluminação
- Aproxime/afaste câmera
- Tente upload de imagem

**❌ Exportação falha**
```bash
# Verificar permissão storage
adb shell pm grant com.business.qrreader android.permission.WRITE_EXTERNAL_STORAGE
```

**❌ App trava/lento**
- Feche outros apps
- Reinicie dispositivo
- Use modo "Simples"
- Verifique RAM disponível

---

## 🔮 Próximas Versões

### v1.1
- [ ] Tema escuro/claro
- [ ] Sincronização cloud
- [ ] Histórico por data
- [ ] Estatísticas avançadas

### v1.2
- [ ] OCR texto cupons
- [ ] Categorização automática
- [ ] Relatórios PDF
- [ ] Widget home screen

---

## 📄 Licença

**MIT License** - Uso livre para fins comerciais e pessoais

---

## 👨‍💻 Desenvolvedor

**Projeto criado para otimização de processos fiscais empresariais**

🔗 **Baseado na versão desktop** com funcionalidades equivalentes  
📱 **Otimizado para dispositivos móveis** Android  
⚡ **Performance e usabilidade** aprimoradas para touch  

---

*Versão Android 1.0.0 - Desenvolvido com ❤️ em Python + Kivy*