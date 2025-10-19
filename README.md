# 📱 Leitor de Cupons Fiscais - Android Completo

Aplicativo Android completo para leitura e gerenciamento de cupons fiscais brasileiros com todas as funcionalidades essenciais do app desktop original.

## ✨ Funcionalidades Principais

### 📝 Entrada de Dados
- **Digitação manual** de chaves fiscais (44 dígitos)
- **Validação automática** com algoritmo de dígito verificador brasileiro
- **Limpeza** de caracteres não numéricos
- **Interface touch-friendly** otimizada para Android

### 📷 Leitura de QR Codes
- **Câmera em tempo real** com auto-detecção
- **Captura manual** de imagens
- **Auto scan** contínuo para leitura rápida
- **Upload de imagens** com QR codes existentes
- **Detecção avançada** quando bibliotecas disponíveis

### 💾 Gerenciamento de Dados
- **Armazenamento local** em JSON
- **Lista organizada** por data (mais recentes primeiro)
- **Busca em tempo real** nas chaves salvas
- **Prevenção de duplicatas** automática
- **Contador de chaves** em tempo real

### 📤 Exportação e Compartilhamento
- **Exportação CSV** com timestamp completo
- **Cópia para clipboard** individual
- **Exclusão seletiva** com confirmação
- **Limpeza geral** com proteção

### 🔄 Modo Batch
- **Leitura rápida** sem popups
- **Contador de lote** em tempo real
- **Ideal para inventários** e coletas massivas
- **Toggle simples** liga/desliga

### ⚙️ Configurações e Status
- **Status das bibliotecas** em tempo real
- **Instruções de instalação** de dependências
- **Estatísticas de uso** 
- **Interface accordion** organizada

## 🛠️ Dependências

### ✅ Básicas (Incluídas)
- **Python 3** - Runtime principal
- **Kivy 2.3.0** - Framework de interface
- **JSON** - Persistência de dados
- **CSV** - Exportação de dados
- **RE** - Validação de padrões

### 📦 Opcionais (Funcionalidade Avançada)
- **OpenCV** - Processamento avançado de imagem
- **pyzbar** - Decodificação otimizada de QR codes
- **PIL** - Manipulação de imagens

```bash
# Para funcionalidade completa
pip install opencv-python pyzbar pillow

# No Android/Termux
pkg install python-opencv zbar
pip install pyzbar pillow
```

## 📱 Build para Android

### 1. Preparar Ambiente
```bash
# Instalar buildozer
pip install buildozer

# Verificar dependências (Linux/macOS)
buildozer android debug
```

### 2. Build APK
```bash
# Build debug
buildozer android debug

# Build release
buildozer android release
```

### 3. Instalar no Dispositivo
```bash
# Via ADB
adb install bin/leitorqr-*-debug.apk

# Via transferência de arquivo
# Copie o APK para o dispositivo e instale
```

## 📋 Uso da Aplicação

### Validação Manual
1. Digite ou cole uma chave fiscal de 44 dígitos
2. Toque em "✅ Validar Chave"
3. Chave válida será automaticamente salva

### Leitura por QR Code
1. Toque em "📷 Câmera QR Code"
2. Posicione o QR code na tela
3. Use "🔄 Auto Scan" para detecção contínua
4. Ou "📸 Capturar QR" para captura manual

### Upload de Imagem
1. Toque em "🖼️ Upload Imagem"
2. Selecione arquivo com QR code
3. Aguarde processamento automático

### Gerenciar Chaves Salvas
1. Acesse seção "💾 Chaves Salvas"
2. Use busca para filtrar
3. Copie, exclua ou exporte conforme necessário

### Modo Batch
1. Ative o switch "Batch" na seção de chaves
2. Leia múltiplos QR codes rapidamente
3. Contador mostra progresso em tempo real

### Exportar Dados
1. Toque em "📤 Exportar CSV"
2. Arquivo será salvo no armazenamento do dispositivo
3. Inclui todas as chaves com timestamps

## 🔧 Configuração Avançada

### Arquivo buildozer.spec
```ini
[app]
title = Leitor de Cupons Fiscais
package.name = leitorqr
package.domain = com.business.fiscal
source.main = main_android_completo.py

# Permissões necessárias
android.permissions = INTERNET,CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Arquitetura alvo
android.archs = arm64-v8a

# APIs suportadas
android.minapi = 21
android.api = 30
```

## 📊 Validação de Chaves Fiscais

O app implementa o algoritmo oficial brasileiro para validação de chaves de acesso:

1. **Formato**: 44 dígitos numéricos
2. **Estrutura**: 43 dígitos + 2 dígitos verificadores
3. **Algoritmo**: Módulo 11 com pesos específicos
4. **Conformidade**: Totalmente compatível com padrão nacional

## 🚀 Melhorias em Relação à Versão Simplificada

### Interface
- ✅ **Accordion organizado** por funcionalidades
- ✅ **ScrollView** para listas longas
- ✅ **Feedback visual** em todas as ações
- ✅ **Cores contextuais** (verde/vermelho/laranja)

### Funcionalidades
- ✅ **Câmera com auto-scan** contínuo
- ✅ **Upload de imagens** com seletor
- ✅ **Busca em tempo real** nas chaves
- ✅ **Modo batch** para leitura massiva
- ✅ **Exportação CSV** completa

### Dados
- ✅ **Timestamps precisos** em cada chave
- ✅ **Prevenção de duplicatas** inteligente
- ✅ **Persistência robusta** com tratamento de erros
- ✅ **Estrutura JSON** organizada

### UX/UI
- ✅ **Touch-friendly** para dispositivos móveis
- ✅ **Mensagens claras** e informativas
- ✅ **Confirmações** para ações destrutivas
- ✅ **Status em tempo real** de bibliotecas

## 🔄 Compatibilidade

### Android
- **API 21+** (Android 5.0+)
- **ARM64** e **ARMv7** suportados
- **Permissões** granulares apropriadas
- **AndroidX** habilitado

### Bibliotecas
- **Graceful degradation** - funciona sem dependências opcionais
- **Detecção automática** de capacidades
- **Instruções integradas** para instalação

## 📈 Roadmap Futuro

- [ ] **Sincronização em nuvem** 
- [ ] **Relatórios avançados** com gráficos
- [ ] **API REST** para integração
- [ ] **Notificações push** 
- [ ] **Modo offline** aprimorado
- [ ] **Backup/restore** automático

## 🐛 Troubleshooting

### Câmera não funciona
- Verifique permissões no Android
- Instale kivy[base] completo
- Reinicie o aplicativo

### QR codes não são detectados
- Instale opencv-python e pyzbar
- Verifique iluminação adequada
- Use modo manual se auto-scan falhar

### Exportação falha
- Verifique permissões de armazenamento
- Libere espaço no dispositivo
- Tente exportar com menos chaves

## 📞 Suporte

Para suporte técnico ou relato de bugs:
- 📧 Email: suporte@exemplo.com
- 🐛 Issues: GitHub repository
- 📱 Versão do app: 2.0
- 🤖 Android: API 21-30

---

**© 2024 Mercado em Números - Leitor de Cupons Fiscais v2.0**