# Leitor de QR Code para extração de chaves de acesso (44 dígitos)
# Sistema avançado com visão computacional, detecção dinâmica e interface web
# CÓDIGO UNIFICADO: Combina leitura em tempo real e análise de upload de foto.

# === IMPORTAÇÕES E DEPENDÊNCIAS ===
import streamlit as st              # Framework web para criar a interface
from PIL import Image               # Biblioteca para manipulação de imagens
from pyzbar.pyzbar import decode   # Biblioteca para decodificação de QR Codes
import pandas as pd                 # Manipulação de dados e CSV
import os                          # Operações do sistema operacional
import cv2                         # OpenCV para visão computacional
import numpy as np                 # Operações matemáticas com arrays
import re                          # Expressões regulares para extração de dados
import time                        # Funções de tempo para auto-refresh
import csv                         # Para manipulação de CSV (usado no app.py original)

# Importação para acesso à câmera/webcam via WebRTC
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase

# === CONFIGURAÇÕES GLOBAIS ===

# Forçar as colunas do CSV a serem string (essencial para chaves de 44 dígitos)
CSV_DTYPE = {'Chave': str}

# Nome do arquivo onde as chaves são armazenadas
ARQUIVO_CHAVES = "chaves.csv"

# === FUNÇÃO PARA CONVERTER CHAVES EXISTENTES ===

def aplicar_mascara_chaves_existentes():
    """Aplica máscara de aspas simples em chaves que ainda não possuem"""
    if os.path.exists(ARQUIVO_CHAVES):
        try:
            # Lê o CSV garantindo que todas as chaves sejam STRING
            df = pd.read_csv(ARQUIVO_CHAVES, dtype=str, encoding='utf-8-sig')
            
            if 'Chave' in df.columns and not df.empty:
                # Verifica se existem chaves sem aspas simples
                chaves_sem_aspas = df[~df['Chave'].str.startswith("'", na=False)]
                
                if not chaves_sem_aspas.empty:
                    # Aplica máscara nas chaves que não têm aspas simples
                    df.loc[~df['Chave'].str.startswith("'", na=False), 'Chave'] = "'" + df.loc[~df['Chave'].str.startswith("'", na=False), 'Chave'].astype(str)
                    
                    # Força TODAS as colunas como string antes de salvar
                    df = df.astype(str)
                    
                    # Salva o CSV atualizado
                    df.to_csv(ARQUIVO_CHAVES, index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
                    
                    return len(chaves_sem_aspas)
            return 0
        except Exception:
            return 0
    return 0

# === FUNÇÕES DE PROCESSAMENTO E SALVAMENTO (Unificadas) ===

def extrair_chave(texto):
    """Extrai chave de acesso (44 dígitos) do texto do QR Code, com múltiplos padrões."""
    try:
        # Padrões comuns de URL de cupom fiscal (preservado do appscanner.py)
        if 'p=' in texto:
            return texto.split("p=")[1].split("|")[0]
        if 'chNFe=' in texto:
            return texto.split("chNFe=")[1].split("&")[0]
        
        # Buscar 44 dígitos (padrão NF-e/NFC-e)
        match = re.search(r'\d{44}', texto)
        return match.group() if match else None
    except Exception:
        return None

def salvar_dados(chave):
    """Salva chave no CSV se não existir, garantindo formato de texto."""
    
    # Normaliza a chave para salvar como STRING com aspas simples (força texto no Excel)
    chave_str = "'" + str(chave).strip()
    
    if os.path.exists(ARQUIVO_CHAVES):
        # Lê o CSV forçando TODAS as colunas a serem string
        df = pd.read_csv(ARQUIVO_CHAVES, dtype=str, encoding='utf-8-sig')
        
        # Verifica se a chave já existe (comparação como string)
        if 'Chave' in df.columns and chave_str in df['Chave'].astype(str).values:
            return False  # Já existe
        
        # Adiciona nova linha garantindo tipo STRING
        nova_linha = pd.DataFrame({'Chave': [chave_str]})
        df = pd.concat([df, nova_linha], ignore_index=True)
    else:
        # Cria DataFrame inicial com tipo STRING explícito
        df = pd.DataFrame({'Chave': [chave_str]})
    
    # Força TODAS as colunas como string antes de salvar
    df = df.astype(str)
    
    # Salva o CSV com aspas em TODOS os valores (força texto)
    df.to_csv(ARQUIVO_CHAVES, index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
    
    # Força atualização da interface Streamlit (se estiver rodando)
    try:
        if 'contador_chaves' in st.session_state:
            st.session_state['contador_chaves'] = len(df)
        if 'lista_atualizada' in st.session_state:
            st.session_state['lista_atualizada'] = False
    except Exception:
        pass
    
    return True

# === FUNÇÕES DE VISÃO COMPUTACIONAL PARA IMAGENS ESTÁTICAS (Upload) - REVERTIDO PARA APP.PY ===

def processar_imagem(img_pil):
    """
    [ORIGINAL APP.PY] Aplica técnicas (filtros, rotações e escalas) para maximizar detecção de QR Code
    """
    img_array = np.array(img_pil)
    if img_array.shape[2] == 4:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
    
    tecnicas = []
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    # Técnicas básicas
    tecnicas.append(("Original", img_array))
    tecnicas.append(("Cinza", gray))
    
    # Técnicas OpenCV (Filtros)
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    tecnicas.append(("Otsu", otsu))
    
    adaptivo = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    tecnicas.append(("Adaptativo", adaptivo))
    
    equalizado = cv2.equalizeHist(gray)
    tecnicas.append(("Equalizado", equalizado))
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    clahe_img = clahe.apply(gray)
    tecnicas.append(("CLAHE", clahe_img))
    
    bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
    tecnicas.append(("Bilateral", bilateral))
    
    # Rotações e escalas
    todas_tentativas = []
    for nome, img in tecnicas:
        # Testa rotações de 0°, 90°, 180°, 270°
        for angulo in [0, 90, 180, 270]:
            if angulo == 0:
                img_rot = img
            else:
                img_rot = np.rot90(img, k=angulo//90)
            
            todas_tentativas.append((f"{nome}_{angulo}°", img_rot))
            
            # Testa escalas
            for escala in [0.7, 1.5]:
                try:
                    h, w = img_rot.shape[:2]
                    novo_w, novo_h = int(w * escala), int(h * escala)
                    # Use INTER_CUBIC para ampliação, INTER_AREA para redução (mais adequado)
                    interp = cv2.INTER_CUBIC if escala > 1 else cv2.INTER_AREA
                    img_esc = cv2.resize(img_rot, (novo_w, novo_h), interpolation=interp)
                    todas_tentativas.append((f"{nome}_{angulo}°_{escala}x", img_esc))
                except Exception:
                    continue # Ignora se a imagem for muito pequena
    
    return todas_tentativas

def ler_qr_code(img_pil):
    """
    [ORIGINAL APP.PY] Tenta ler QR Code com PyZBar na imagem original 
    e em todas as imagens processadas (filtros, rotações, escalas).
    """
    # Tentar original primeiro
    resultado = decode(img_pil)
    if resultado:
        return resultado, "Original", 1
    
    # Aplicar todas as técnicas de pré-processamento
    tentativas = processar_imagem(img_pil)
    
    for i, (nome, img) in enumerate(tentativas, 2):
        try:
            # Converte array numpy processado para imagem PIL (requisito PyZBar)
            if len(img.shape) == 2: # Grayscale
                img_proc = img.astype('uint8') if img.dtype != np.uint8 else img
                img_pil_proc = Image.fromarray(img_proc, mode='L')
            else: # Color (RGB)
                img_proc = img.astype('uint8') if img.dtype != np.uint8 else img
                img_pil_proc = Image.fromarray(img_proc)
            
            resultado = decode(img_pil_proc)
            if resultado:
                # Retorna apenas o resultado, nome do método e tentativas (não retorna points)
                return resultado, nome, i
        except:
            continue
    
    return None, f"Falhou após {len(tentativas)+1} tentativas", len(tentativas)+1

# NOTA: draw_detection_frame_static FOI REMOVIDA POIS NÃO É USADA PELA LÓGICA DO APP.PY

# === LEITURA EM TEMPO REAL (Classe VideoTransformer) - Preservada ===

class QRReader(VideoTransformerBase):
    """Processa frames de vídeo para detectar QR Codes em tempo real usando algoritmos de visão computacional"""
    
    def __init__(self):
        self.detector_opencv = cv2.QRCodeDetector()
        self.feedback_counter = 0
        self.feedback_duration = 90  # frames para mostrar feedback (aprox. 3 segundos a 30fps)
    
    def apply_computer_vision_preprocessing(self, img):
        """Aplica algoritmos de visão computacional para melhorar detecção de QR Code"""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        processed_images = []
        
        # 1. Imagem original em cinza
        processed_images.append(("original", gray))
        
        # 2. Threshold adaptativo
        adaptive_thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        processed_images.append(("adaptive", adaptive_thresh))
        
        # 3. Filtro Gaussiano + Threshold
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, gaussian_thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed_images.append(("gaussian", gaussian_thresh))
        
        # 4. Operações morfológicas
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        morphology = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_CLOSE, kernel)
        processed_images.append(("morphology", morphology))
        
        # 5. CLAHE (Contraste adaptativo)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        processed_images.append(("enhanced", enhanced))
        
        return processed_images
    
    def detect_qr_with_computer_vision(self, img):
        """Usa múltiplos algoritmos de visão computacional para detectar QR Code"""
        # Tenta detecção na imagem original primeiro
        texto, points, _ = self.detector_opencv.detectAndDecode(img)
        if texto:
            return texto, points, "opencv_original"
        
        # Aplica pré-processamento com visão computacional
        processed_images = self.apply_computer_vision_preprocessing(img)
        
        # Tenta detectar em cada imagem processada
        for method_name, processed_img in processed_images:
            try:
                # OpenCV QR Detector
                texto, points, _ = self.detector_opencv.detectAndDecode(processed_img)
                if texto:
                    return texto, points, f"opencv_{method_name}"
                
                # Fallback: usar pyzbar
                try:
                    # Converte imagem processada para formato PIL (pyzbar requirement)
                    if len(processed_img.shape) == 2:
                        pil_img = Image.fromarray(processed_img)
                        resultado_pyzbar = decode(pil_img)
                        if resultado_pyzbar:
                            # Converte resultado pyzbar para formato OpenCV
                            rect = resultado_pyzbar[0].rect
                            points = np.array([[[rect.left, rect.top], 
                                              [rect.left + rect.width, rect.top],
                                              [rect.left + rect.width, rect.top + rect.height],
                                              [rect.left, rect.top + rect.height]]], dtype=np.float32)
                            texto = resultado_pyzbar[0].data.decode('utf-8')
                            return texto, points, f"pyzbar_{method_name}"
                except ImportError:
                    pass
                    
            except Exception:
                continue
        
        return None, None, "detection_failed"
    
    def draw_detection_frame(self, img, points, detection_method, status="detected"):
        """Desenha quadro dinâmico de detecção (preservado do appscanner.py)"""
        if points is None:
            return img
        
        try:
            pts = np.int32(points).reshape(-1, 1, 2)
            (x, y, w, h) = cv2.boundingRect(pts)
            
            # Cores baseadas no status
            if status == "success": primary_color, secondary_color = (0, 255, 0), (0, 200, 0)
            elif status == "duplicate": primary_color, secondary_color = (0, 255, 255), (0, 200, 200)
            elif status == "invalid": primary_color, secondary_color = (0, 165, 255), (0, 100, 200)
            else: primary_color, secondary_color = (255, 255, 0), (200, 200, 0)
            
            # Desenha contorno e quadro principal (simplificado)
            cv2.polylines(img, [pts], True, primary_color, 3)
            margin = 20
            cv2.rectangle(img, (x-margin, y-margin), (x+w+margin, y+h+margin), secondary_color, 2)
            
            # Informações da detecção
            cv2.putText(img, "QR DETECTADO", (x-margin, y-margin-10), cv2.FONT_HERSHEY_DUPLEX, 0.7, primary_color, 2)
            cv2.putText(img, f"Metodo: {detection_method}", (x-margin, y+h+margin+25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, primary_color, 1)
            
        except Exception:
            pass
        
        return img
    
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        height, width = img.shape[:2]
        
        # Lógica de Feedback e Trava
        if st.session_state.get('qr_lock_success', False):
            self.feedback_counter += 1
            if self.feedback_counter >= self.feedback_duration:
                st.session_state['qr_lock_success'] = False
                st.session_state['last_detected_key'] = None
                st.session_state['lista_atualizada'] = False
                self.feedback_counter = 0
            
            # Desenha overlay de pausa
            overlay = img.copy()
            cv2.rectangle(overlay, (0, 0), (width, 120), (0, 150, 0), -1)
            img = cv2.addWeighted(img, 0.7, overlay, 0.3, 0)
            
            remaining_time = max(0, self.feedback_duration - self.feedback_counter)
            seconds_left = int(remaining_time / 30)
            cv2.putText(img, "SUCESSO! PREPARANDO PARA PROXIMO...", (20, 35), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(img, f"Proximo QR em: {seconds_left + 1}s", (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
        elif not st.session_state.get('qr_lock_success', False):
            
            cv2.putText(img, "BUSCANDO QR CODE COM IA...", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            
            texto, points, metodo_deteccao = self.detect_qr_with_computer_vision(img)
            
            if texto:
                img = self.draw_detection_frame(img, points, metodo_deteccao, "detected")
                
                chave = extrair_chave(texto)
                
                if chave:
                    if salvar_dados(chave):
                        # CHAVE SALVA (Sucesso)
                        img = self.draw_detection_frame(img, points, metodo_deteccao, "success")
                        st.session_state['qr_lock_success'] = True
                        st.session_state['last_detected_key'] = chave
                        st.session_state['lista_atualizada'] = False
                        self.feedback_counter = 0
                        st.success("🔑 Chave de acesso detectada e SALVA com sucesso!")
                    else:
                        # CHAVE JÁ EXISTE (Aviso)
                        img = self.draw_detection_frame(img, points, metodo_deteccao, "duplicate")
                        st.session_state['qr_lock_success'] = True
                        st.session_state['lista_atualizada'] = False
                        self.feedback_counter = 0
                        st.warning("⚠️ Chave detectada, mas JÁ EXISTE no registro!")
                else:
                    # QR CODE LIDO, MAS CHAVE INVÁLIDA
                    img = self.draw_detection_frame(img, points, metodo_deteccao, "invalid")
            else:
                pass
        
        return img

# === INTERFACE STREAMLIT PRINCIPAL (Unificada) ===

st.set_page_config(page_title="Leitor QR Code Unificado", layout="centered")
st.title("📱 Leitor de QR Code - Cupons Fiscais")
st.write("Sistema eficaz para extrair chaves de acesso (44 dígitos)")

# Aviso sobre problemas de câmera
st.warning("""
⚠️ **Problema de Câmera Detectado?** 
Se você ver erro "navigator.mediaDevices is undefined", use:
- 📍 **localhost:8501** (ao invés do IP da rede)
- 📤 **Aba "Upload de Imagem"** (funciona sempre)
""")

# Inicializa estado
if 'qr_lock_success' not in st.session_state: st.session_state['qr_lock_success'] = False
if 'lista_atualizada' not in st.session_state: st.session_state['lista_atualizada'] = True
if 'contador_chaves' not in st.session_state: st.session_state['contador_chaves'] = 0

# Verifica mudanças no arquivo CSV para forçar atualização
def verificar_mudancas_csv():
    if os.path.exists(ARQUIVO_CHAVES):
        try:
            # Lê o CSV forçando TODAS as colunas a serem string
            df = pd.read_csv(ARQUIVO_CHAVES, dtype=str, encoding='utf-8-sig')
            novo_contador = len(df)
        except Exception:
            novo_contador = 0
    else:
        novo_contador = 0
    
    if novo_contador != st.session_state.get('contador_chaves', 0):
        st.session_state['contador_chaves'] = novo_contador
        return True
    return False

# Sistema de auto-refresh melhorado
if not st.session_state.get('lista_atualizada', True):
    st.session_state['lista_atualizada'] = True
    st.rerun()

# Detecta mudanças automáticas no CSV
if verificar_mudancas_csv():
    st.rerun()

# 1. Abas para organizar as opções
tab_camera, tab_upload = st.tabs(["📹 Câmera em Tempo Real", "📤 Upload de Imagem"])

# --- TAB: Câmera em Tempo Real ---
with tab_camera:
    st.header("🎯 Detecção Inteligente com Visão Computacional")
    st.info("🤖 O scanner usa algoritmos avançados para detecção em tempo real e trava após o sucesso para evitar múltiplas leituras.")
    
    # Verifica se WebRTC está disponível
    st.markdown("""
    <script>
    if (!navigator.mediaDevices) {
        document.write('<div class="stAlert"><div data-baseweb="notification" class="st-emotion-cache-1erivf3 e1fqkh3o16"><div class="st-emotion-cache-keje6w e1fqkh3o13"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="currentColor" xmlns="http://www.w3.org/2000/svg" color="inherit" class="e1fb0mya1 st-emotion-cache-fblp2m ex0cdmw0"><path fill="none" d="M0 0h24v24H0z"></path><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"></path></svg></div><div class="st-emotion-cache-1wrcr25 e1fqkh3o4"><div class="st-emotion-cache-j5r0tf e1fqkh3o7">⚠️ Câmera não disponível: Use HTTPS ou localhost</div></div></div></div>');
    }
    </script>
    """, unsafe_allow_html=True)
    
    try:
        webrtc_ctx = webrtc_streamer(
            key="qr-code-scanner", 
            video_processor_factory=QRReader,
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
            media_stream_constraints={"video": True, "audio": False}
        )
        
        if webrtc_ctx and webrtc_ctx.state.playing:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 Reiniciar Leitura", help="Força reinício imediato da leitura"):
                    st.session_state['qr_lock_success'] = False
                    st.session_state['last_detected_key'] = None
                    st.session_state['lista_atualizada'] = False
                    st.rerun()
            
            with col2:
                if st.session_state.get('last_detected_key'):
                    st.success(f"🔑 Última: `{st.session_state['last_detected_key'][-8:]}...`")
        
    except Exception as exc:
        st.error("❌ **Erro de Câmera Detectado**")
        
        with st.expander("🔧 Soluções para o Problema de Câmera"):
            st.markdown("""
            **O erro ocorre porque:**
            - O navegador requer HTTPS para acessar a câmera
            - Ou você não está usando `localhost`
            
            **💡 Soluções:**
            
            1. **Use localhost (Recomendado):**
               ```
               http://localhost:8501
               ```
            
            2. **Para acesso remoto, use HTTPS:**
               - Configure um certificado SSL
               - Ou use ngrok para túnel HTTPS
            
            3. **Alternativa: Use apenas Upload de Imagens**
               - Vá para a aba "Upload de Imagem"
               - Funciona sem problemas de câmera
            """)
        
        st.info("📱 **Dica:** Use a aba 'Upload de Imagem' que funciona perfeitamente!")
        
        try:
            from streamlit_webrtc.session_info import NoSessionError
            if isinstance(exc, NoSessionError):
                st.warning("⚠️ Sessão WebRTC não iniciada. Tente recarregar a página.")
        except ImportError:
            pass

# --- TAB: Upload de Imagem ---
with tab_upload:
    st.header("📤 Upload e Análise Avançada de Imagem")
    st.info("🔄 Sistema de Força Bruta: Testa múltiplos filtros, rotações (0°, 90°, 180°, 270°) e escalas para garantir a leitura em fotos complexas.")
    
    arquivo_img = st.file_uploader("Selecione uma imagem (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

    if arquivo_img:
        img = Image.open(arquivo_img)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(img, width=300, caption="Imagem Carregada")
            
        with col2:
            with st.spinner("🔍 Analisando imagem com algoritmos de força bruta..."):
                
                # --- CHAMA A FUNÇÃO DE FORÇA BRUTA DO APP.PY ---
                resultado, metodo, tentativas = ler_qr_code(img)
                # -----------------------------------------------
        
        st.markdown("---")
        
        if resultado:
            st.success("✅ QR Code detectado!")
            st.info(f"**Método:** {metodo} (tentativa {tentativas})")
            
            texto = resultado[0].data.decode("utf-8")
            chave = extrair_chave(texto)
            
            if chave:
                st.success(f"🔑 **Chave:** `{chave}`")
                
                # Salva os dados usando a função unificada
                if salvar_dados(chave):
                    st.success("💾 Chave salva!")
                    st.session_state['lista_atualizada'] = False
                    st.balloons()
                else:
                    st.warning("⚠️ Chave já existe")
            else:
                st.error("❌ Chave não encontrada")
            
            with st.expander("📋 Texto completo"):
                st.code(texto)

        else:
            st.error(f"❌ QR Code não detectado após {tentativas} tentativas")
            with st.expander("💡 Dicas para Melhorar a Detecção"):
                 st.write("A detecção de força bruta (testando mais de 100 variações) falhou. Verifique a qualidade da imagem.")

# --- Dados salvos (Rodapé) ---
st.markdown("---")

if os.path.exists(ARQUIVO_CHAVES):
    # Lê o CSV garantindo que todas as chaves sejam STRING
    df = pd.read_csv(ARQUIVO_CHAVES, dtype=str, encoding='utf-8-sig') 
    if not df.empty:
        st.subheader(f"📊 Chaves Salvas ({len(df)})")
        
        # Verifica se existem chaves sem máscara
        chaves_sem_aspas = df[~df['Chave'].str.startswith("'", na=False)] if 'Chave' in df.columns else pd.DataFrame()
        
        if not chaves_sem_aspas.empty:
            st.warning(f"⚠️ {len(chaves_sem_aspas)} chaves encontradas sem proteção para Excel!")
            if st.button("🔧 Aplicar Máscara de Proteção (Aspas Simples)", help="Adiciona aspas simples nas chaves existentes para proteção no Excel"):
                chaves_convertidas = aplicar_mascara_chaves_existentes()
                if chaves_convertidas > 0:
                    st.success(f"✅ {chaves_convertidas} chaves convertidas com sucesso!")
                    st.rerun()
                else:
                    st.info("ℹ️ Nenhuma chave precisava ser convertida.")
        
        # Exibe DataFrame garantindo que chaves apareçam como texto
        df_display = df.copy()
        st.dataframe(df_display, width='stretch')
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Gera CSV garantindo formato de texto
            csv_content = df.to_csv(index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL).encode('utf-8-sig')
            st.download_button(
                "📥 Baixar Chaves (CSV)", 
                csv_content, 
                ARQUIVO_CHAVES, 
                "text/csv"
            )
        
        with col2:
            if st.button("🔄 Atualizar Lista", help="Recarrega a lista de chaves do arquivo"):
                st.session_state['lista_atualizada'] = False
                st.session_state['contador_chaves'] = 0
                st.success("✅ Lista atualizada!")
                st.rerun()
        
        with col3:
            if st.button("🗑️ Limpar Todas as Chaves", type="secondary"):
                if os.path.exists(ARQUIVO_CHAVES):
                    os.remove(ARQUIVO_CHAVES)
                    st.session_state['lista_atualizada'] = False
                    st.session_state['contador_chaves'] = 0
                    st.success("✅ Todas as chaves foram removidas!")
                    st.rerun()
    else:
        st.info("Nenhuma chave salva ainda.")
else:
    st.info("Nenhuma chave salva ainda.")
