#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SIMULADOR ANDROID COMPLETO - Leitor de Cupons Fiscais
Experiência completa do app Android no desktop com câmera real
"""

import os
import sys
import time
import json
import re
import csv
import threading
from pathlib import Path
from datetime import datetime

# Imports principais
try:
    import cv2
    import numpy as np
    from pyzbar import pyzbar
    CV2_AVAILABLE = True
    PYZBAR_AVAILABLE = True
except ImportError as e:
    print(f"❌ Dependências necessárias: {e}")
    print("📦 Execute: pip install opencv-python pyzbar")
    sys.exit(1)

# Kivy imports
try:
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.textinput import TextInput
    from kivy.uix.popup import Popup
    from kivy.uix.spinner import Spinner
    from kivy.uix.switch import Switch
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.image import Image as KivyImage
    from kivy.uix.filechooser import FileChooserListView
    from kivy.clock import Clock
    from kivy.logger import Logger
    from kivy.graphics.texture import Texture
    KIVY_AVAILABLE = True
except ImportError as e:
    print(f"❌ Kivy não disponível: {e}")
    sys.exit(1)

# Classe para dados das chaves
class SavedKey:
    def __init__(self, key: str, timestamp: float):
        self.key = key
        self.timestamp = timestamp
    
    def to_dict(self):
        return {"key": self.key, "timestamp": self.timestamp}
    
    @classmethod
    def from_dict(cls, data):
        return cls(data["key"], data["timestamp"])

class AndroidQRReaderApp(App):
    """Simulador completo do app Android com câmera real"""
    
    def __init__(self):
        super().__init__()
        
        # Configurações
        self.saved_keys = []
        self.config_file = Path.home() / "android_qr_reader" / "chaves.json"
        
        # Estado da câmera
        self.camera_active = False
        self.camera_capture = None
        self.camera_thread = None
        self.camera_running = False
        self.last_qr_time = 0
        self.processed_qrs = set()
        
        # Estatísticas
        self.stats = {
            'total_scans': 0,
            'valid_keys': 0,
            'duplicates': 0,
            'invalid_qrs': 0,
            'session_start': time.time()
        }
        
        # Configuração QR
        self.qr_config = {
            'detection_mode': 'enhanced',
            'debug_mode': True,
            'cooldown_time': 2.0,
            'auto_save': True
        }
        
    def build(self):
        """Constrói interface Android completa"""
        Logger.info("AndroidQR: Iniciando simulador Android completo...")
        
        # Layout principal (vertical - mobile style)
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # === HEADER ===
        header = self.create_header()
        main_layout.add_widget(header)
        
        # === CÂMERA SECTION ===
        camera_section = self.create_camera_section()
        main_layout.add_widget(camera_section)
        
        # === CONTROLES ===
        controls_section = self.create_controls_section()
        main_layout.add_widget(controls_section)
        
        # === ESTATÍSTICAS ===
        stats_section = self.create_stats_section()
        main_layout.add_widget(stats_section)
        
        # === LISTA DE CHAVES ===
        keys_section = self.create_keys_section()
        main_layout.add_widget(keys_section)
        
        # Carrega dados salvos
        self.load_saved_keys()
        self.update_display()
        
        # Inicia atualização automática
        Clock.schedule_interval(self.update_stats, 1.0)
        
        return main_layout
    
    def create_header(self):
        """Cria cabeçalho do app"""
        header = BoxLayout(orientation='vertical', size_hint_y=None, height='120dp', spacing=5)
        
        # Título
        title = Label(
            text='📱 ANDROID QR READER',
            font_size='24sp',
            size_hint_y=0.6,
            bold=True,
            color=(0.2, 0.6, 1, 1)
        )
        
        # Subtítulo
        subtitle = Label(
            text='🔍 Leitor de Cupons Fiscais - Câmera Real',
            font_size='14sp',
            size_hint_y=0.4,
            color=(0.5, 0.5, 0.5, 1)
        )
        
        header.add_widget(title)
        header.add_widget(subtitle)
        
        return header
    
    def create_camera_section(self):
        """Cria seção da câmera"""
        camera_frame = BoxLayout(orientation='vertical', size_hint_y=None, height='320dp', spacing=10)
        
        # Label da câmera
        camera_label = Label(
            text='📹 Visualização da Câmera',
            font_size='16sp',
            size_hint_y=None,
            height='30dp'
        )
        
        # Display da câmera
        self.camera_display = KivyImage(
            size_hint_y=None,
            height='240dp',
            allow_stretch=True,
            keep_ratio=False
        )
        
        # Placeholder inicial
        self.camera_display.source = ''
        
        # Status da câmera
        self.camera_status = Label(
            text='📷 Câmera Desligada - Clique para iniciar',
            font_size='14sp',
            size_hint_y=None,
            height='30dp',
            color=(0.8, 0.8, 0.8, 1)
        )
        
        camera_frame.add_widget(camera_label)
        camera_frame.add_widget(self.camera_display)
        camera_frame.add_widget(self.camera_status)
        
        return camera_frame
    
    def create_controls_section(self):
        """Cria controles do app"""
        controls = BoxLayout(orientation='vertical', size_hint_y=None, height='120dp', spacing=10)
        
        # Botões principais
        main_buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', spacing=10)
        
        self.camera_btn = Button(
            text='📷 Iniciar Câmera',
            background_color=(0.2, 0.7, 0.3, 1),
            size_hint_x=0.5
        )
        self.camera_btn.bind(on_press=self.toggle_camera)
        
        upload_btn = Button(
            text='📤 Galeria',
            background_color=(0.3, 0.5, 0.8, 1),
            size_hint_x=0.25
        )
        upload_btn.bind(on_press=self.simulate_gallery)
        
        export_btn = Button(
            text='📊 Export',
            background_color=(0.6, 0.4, 0.8, 1),
            size_hint_x=0.25
        )
        export_btn.bind(on_press=self.export_csv)
        
        main_buttons.add_widget(self.camera_btn)
        main_buttons.add_widget(upload_btn)
        main_buttons.add_widget(export_btn)
        
        # Configurações
        config_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing=20)
        
        # Modo
        mode_layout = BoxLayout(orientation='horizontal', size_hint_x=0.6, spacing=5)
        mode_label = Label(text='🎛️', size_hint_x=0.2, font_size='16sp')
        self.mode_spinner = Spinner(
            text='Melhorado',
            values=['Simples', 'Melhorado', 'Agressivo'],
            size_hint_x=0.8
        )
        self.mode_spinner.bind(text=self.on_mode_change)
        
        mode_layout.add_widget(mode_label)
        mode_layout.add_widget(self.mode_spinner)
        
        # Debug
        debug_layout = BoxLayout(orientation='horizontal', size_hint_x=0.4, spacing=5)
        debug_label = Label(text='🐛', size_hint_x=0.3, font_size='16sp')
        self.debug_switch = Switch(active=True, size_hint_x=0.7)
        self.debug_switch.bind(active=self.on_debug_toggle)
        
        debug_layout.add_widget(debug_label)
        debug_layout.add_widget(self.debug_switch)
        
        config_layout.add_widget(mode_layout)
        config_layout.add_widget(debug_layout)
        
        # Busca
        search_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing=10)
        search_label = Label(text='🔍', size_hint_x=0.1, font_size='16sp')
        self.search_input = TextInput(
            hint_text='Buscar chaves...',
            multiline=False,
            size_hint_x=0.9
        )
        self.search_input.bind(text=self.on_search_change)
        
        search_layout.add_widget(search_label)
        search_layout.add_widget(self.search_input)
        
        controls.add_widget(main_buttons)
        controls.add_widget(config_layout)
        #controls.add_widget(search_layout)
        
        return controls
    
    def create_stats_section(self):
        """Cria seção de estatísticas"""
        stats_frame = BoxLayout(orientation='horizontal', size_hint_y=None, height='60dp', spacing=5)
        
        self.stats_labels = {
            'scans': Label(text='📊 0', font_size='12sp', halign='center'),
            'valid': Label(text='✅ 0', font_size='12sp', halign='center'),
            'dupes': Label(text='⚠️ 0', font_size='12sp', halign='center'),
            'errors': Label(text='❌ 0', font_size='12sp', halign='center'),
            'time': Label(text='⏱️ 00:00', font_size='12sp', halign='center')
        }
        
        for label in self.stats_labels.values():
            label.bind(size=label.setter('text_size'))
            stats_frame.add_widget(label)
        
        return stats_frame
    
    def create_keys_section(self):
        """Cria seção da lista de chaves"""
        keys_frame = BoxLayout(orientation='vertical', spacing=10)
        
        # Header da lista
        keys_header = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing=10)
        
        self.keys_counter = Label(
            text='📋 0 chaves',
            font_size='16sp',
            size_hint_x=0.7,
            bold=True
        )
        
        clear_btn = Button(
            text='🗑️ Limpar',
            size_hint_x=0.3,
            background_color=(0.8, 0.2, 0.2, 1)
        )
        clear_btn.bind(on_press=self.clear_all_keys)
        
        keys_header.add_widget(self.keys_counter)
        keys_header.add_widget(clear_btn)
        
        # ScrollView para lista
        scroll = ScrollView()
        self.keys_list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.keys_list_layout.bind(minimum_height=self.keys_list_layout.setter('height'))
        
        scroll.add_widget(self.keys_list_layout)
        
        keys_frame.add_widget(keys_header)
        keys_frame.add_widget(scroll)
        
        return keys_frame
    
    # === CÂMERA FUNCTIONS ===
    
    def toggle_camera(self, instance):
        """Liga/desliga câmera"""
        if not self.camera_active:
            self.start_camera()
        else:
            self.stop_camera()
    
    def start_camera(self):
        """Inicia captura da câmera"""
        Logger.info("AndroidQR: Iniciando câmera...")
        
        try:
            # Abre câmera
            self.camera_capture = cv2.VideoCapture(0)
            
            if not self.camera_capture.isOpened():
                self.show_toast("❌ Erro: Câmera não disponível", "error")
                return
            
            # Configura câmera
            self.camera_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera_capture.set(cv2.CAP_PROP_FPS, 30)
            
            # Estado
            self.camera_active = True
            self.camera_running = True
            
            # UI
            self.camera_btn.text = '📷 Parar Câmera'
            self.camera_btn.background_color = (0.8, 0.2, 0.2, 1)
            self.camera_status.text = '📹 Câmera Ativa - Procurando QR codes...'
            self.camera_status.color = (0.2, 0.8, 0.2, 1)
            
            # Inicia thread da câmera
            self.camera_thread = threading.Thread(target=self.camera_loop, daemon=True)
            self.camera_thread.start()
            
            Logger.info("AndroidQR: ✅ Câmera iniciada com sucesso")
            
        except Exception as e:
            Logger.error(f"AndroidQR: Erro ao iniciar câmera: {e}")
            self.show_toast(f"❌ Erro na câmera: {str(e)}", "error")
    
    def stop_camera(self):
        """Para captura da câmera"""
        Logger.info("AndroidQR: Parando câmera...")
        
        self.camera_running = False
        self.camera_active = False
        
        # UI
        self.camera_btn.text = '📷 Iniciar Câmera'
        self.camera_btn.background_color = (0.2, 0.7, 0.3, 1)
        self.camera_status.text = '📷 Câmera Desligada - Clique para iniciar'
        self.camera_status.color = (0.8, 0.8, 0.8, 1)
        
        # Libera câmera
        if self.camera_capture:
            self.camera_capture.release()
            self.camera_capture = None
        
        # Limpa display
        self.camera_display.texture = None
        
        Logger.info("AndroidQR: Câmera parada")
    
    def camera_loop(self):
        """Loop principal da câmera (thread separada)"""
        Logger.info("AndroidQR: Iniciando loop da câmera...")
        
        while self.camera_running and self.camera_capture:
            try:
                # Captura frame
                ret, frame = self.camera_capture.read()
                if not ret:
                    continue
                
                # Espelha frame (câmera frontal)
                frame = cv2.flip(frame, 1)
                
                # Detecta QR codes
                current_time = time.time()
                if current_time - self.last_qr_time > self.qr_config['cooldown_time']:
                    qr_codes = self.detect_qr_codes(frame)
                    
                    if qr_codes:
                        self.last_qr_time = current_time
                        self.process_qr_codes(qr_codes, frame)
                
                # Atualiza display (thread-safe via Clock)
                Clock.schedule_once(lambda dt: self.update_camera_display(frame), 0)
                
                # Controle de FPS
                time.sleep(1/30)  # 30 FPS
                
            except Exception as e:
                Logger.error(f"AndroidQR: Erro no loop da câmera: {e}")
                break
        
        Logger.info("AndroidQR: Loop da câmera finalizado")
    
    def update_camera_display(self, frame):
        """Atualiza display da câmera (thread principal)"""
        try:
            # Redimensiona frame
            height, width = frame.shape[:2]
            display_height = 240
            display_width = int(width * display_height / height)
            
            resized_frame = cv2.resize(frame, (display_width, display_height))
            
            # Converte BGR para RGB
            rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            
            # Cria texture
            texture = Texture.create(size=(display_width, display_height))
            texture.blit_buffer(rgb_frame.flatten(), colorfmt='rgb', bufferfmt='ubyte')
            texture.flip_vertical()
            
            # Atualiza display
            self.camera_display.texture = texture
            
        except Exception as e:
            Logger.error(f"AndroidQR: Erro ao atualizar display: {e}")
    
    # === QR DETECTION ===
    
    def detect_qr_codes(self, frame):
        """Detecta QR codes no frame"""
        try:
            mode = self.qr_config['detection_mode']
            
            if mode == 'simple':
                return pyzbar.decode(frame)
            elif mode == 'enhanced':
                return self.enhanced_detection(frame)
            elif mode == 'aggressive':
                return self.aggressive_detection(frame)
            else:
                return pyzbar.decode(frame)
        
        except Exception as e:
            if self.qr_config['debug_mode']:
                Logger.error(f"AndroidQR: Erro na detecção: {e}")
            return []
    
    def enhanced_detection(self, frame):
        """Detecção melhorada"""
        qr_codes = []
        
        # Detecção direta
        direct_codes = pyzbar.decode(frame)
        qr_codes.extend(direct_codes)
        
        if qr_codes:
            return qr_codes
        
        # Pré-processamento
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Técnicas de melhoria
        techniques = [
            cv2.equalizeHist(gray),
            cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2),
            cv2.bilateralFilter(gray, 9, 75, 75)
        ]
        
        for processed in techniques:
            codes = pyzbar.decode(processed)
            if codes:
                qr_codes.extend(codes)
                break
        
        return qr_codes
    
    def aggressive_detection(self, frame):
        """Detecção agressiva"""
        qr_codes = self.enhanced_detection(frame)
        if qr_codes:
            return qr_codes
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Múltiplas escalas
        for scale in [0.8, 1.2, 1.5]:
            height, width = gray.shape
            new_size = (int(width * scale), int(height * scale))
            scaled = cv2.resize(gray, new_size)
            codes = pyzbar.decode(scaled)
            if codes:
                qr_codes.extend(codes)
                break
        
        # Rotações
        if not qr_codes:
            center = (gray.shape[1] // 2, gray.shape[0] // 2)
            for angle in [-10, 10, -15, 15]:
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(gray, M, (gray.shape[1], gray.shape[0]))
                codes = pyzbar.decode(rotated)
                if codes:
                    qr_codes.extend(codes)
                    break
        
        return qr_codes
    
    def process_qr_codes(self, qr_codes, frame):
        """Processa QR codes detectados"""
        for qr_code in qr_codes:
            try:
                # Decodifica dados
                qr_data = qr_code.data.decode('utf-8')
                
                # Evita processar mesmo QR
                if qr_data in self.processed_qrs:
                    continue
                
                self.processed_qrs.add(qr_data)
                self.stats['total_scans'] += 1
                
                Logger.info(f"AndroidQR: QR detectado: {qr_data[:50]}...")
                
                # Desenha retângulo no frame
                rect = qr_code.rect
                cv2.rectangle(frame, 
                            (rect.left, rect.top),
                            (rect.left + rect.width, rect.top + rect.height),
                            (0, 255, 0), 3)
                
                cv2.putText(frame, "QR DETECTADO", 
                          (rect.left, rect.top - 10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Processa dados
                Clock.schedule_once(lambda dt: self.handle_qr_result(qr_data), 0)
                
            except UnicodeDecodeError:
                self.stats['invalid_qrs'] += 1
                continue
    
    def handle_qr_result(self, qr_data):
        """Processa resultado do QR (thread principal)"""
        # Extrai chave fiscal
        match = re.search(r'p=([0-9]{44})', qr_data)
        
        if not match:
            self.stats['invalid_qrs'] += 1
            self.show_toast("⚠️ QR detectado mas não é cupom fiscal", "warning")
            return
        
        key = match.group(1)
        
        # Valida chave
        if not self.validate_fiscal_key(key):
            self.stats['invalid_qrs'] += 1
            self.show_toast("❌ Chave fiscal inválida", "error")
            return
        
        # Verifica duplicata
        if any(item.key == key for item in self.saved_keys):
            self.stats['duplicates'] += 1
            self.show_toast("⚠️ Este cupom já foi lido", "warning")
            return
        
        # Salva chave
        new_key = SavedKey(key, time.time())
        self.saved_keys.insert(0, new_key)
        
        self.stats['valid_keys'] += 1
        
        # Salva e atualiza
        if self.qr_config['auto_save']:
            self.save_keys_to_file()
        
        self.update_display()
        
        # Feedback
        self.show_toast(f"✅ Cupom #{len(self.saved_keys)} salvo!", "success")
        self.camera_status.text = f'📹 Último QR: {key[:20]}... - Total: {len(self.saved_keys)}'
        
        Logger.info(f"AndroidQR: Chave salva: {key[:20]}...")
    
    def validate_fiscal_key(self, key: str) -> bool:
        """Valida chave fiscal usando algoritmo DV"""
        if len(key) != 44 or not key.isdigit():
            return False
        
        try:
            weights = [2, 3, 4, 5, 6, 7, 8, 9] * 5 + [2, 3, 4]
            total = sum(int(digit) * weight for digit, weight in zip(key[:43], weights))
            
            remainder = total % 11
            expected_dv = 0 if remainder < 2 else 11 - remainder
            
            return int(key[43]) == expected_dv
        
        except Exception:
            return False
    
    # === DATA MANAGEMENT ===
    
    def load_saved_keys(self):
        """Carrega chaves salvas"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.saved_keys = [SavedKey.from_dict(item) for item in data]
                    
                Logger.info(f"AndroidQR: {len(self.saved_keys)} chaves carregadas")
            else:
                self.saved_keys = []
        
        except Exception as e:
            Logger.error(f"AndroidQR: Erro ao carregar: {e}")
            self.saved_keys = []
    
    def save_keys_to_file(self):
        """Salva chaves no arquivo"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = [key.to_dict() for key in self.saved_keys]
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            Logger.error(f"AndroidQR: Erro ao salvar: {e}")
    
    def update_display(self):
        """Atualiza displays"""
        # Contador de chaves
        count = len(self.saved_keys)
        self.keys_counter.text = f'📋 {count} chaves'
        
        # Lista de chaves
        self.keys_list_layout.clear_widgets()
        
        # Filtra por busca
        search_text = ""
        if hasattr(self, 'search_input'):
            search_text = self.search_input.text.lower()
        
        filtered_keys = [
            key for key in self.saved_keys
            if search_text in key.key.lower()
        ]
        
        # Mostra últimas 20
        for key_obj in filtered_keys[:20]:
            key_item = self.create_key_item(key_obj)
            self.keys_list_layout.add_widget(key_item)
    
    def create_key_item(self, key_obj: SavedKey):
        """Cria item da lista de chaves"""
        item_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='50dp',
            spacing=10,
            padding=[5, 0]
        )
        
        # Info da chave
        key_display = f"{key_obj.key[:12]}...{key_obj.key[-8:]}"
        time_display = datetime.fromtimestamp(key_obj.timestamp).strftime('%H:%M')
        
        info_label = Label(
            text=f"🔑 {key_display} • {time_display}",
            font_size='12sp',
            size_hint_x=0.8,
            halign='left'
        )
        info_label.bind(size=info_label.setter('text_size'))
        
        # Botão copiar
        copy_btn = Button(
            text='📋',
            size_hint_x=0.2,
            font_size='16sp'
        )
        copy_btn.bind(on_press=lambda x: self.copy_key(key_obj.key))
        
        item_layout.add_widget(info_label)
        item_layout.add_widget(copy_btn)
        
        return item_layout
    
    def update_stats(self, dt):
        """Atualiza estatísticas"""
        elapsed = time.time() - self.stats['session_start']
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        self.stats_labels['scans'].text = f"📊 {self.stats['total_scans']}"
        self.stats_labels['valid'].text = f"✅ {self.stats['valid_keys']}"
        self.stats_labels['dupes'].text = f"⚠️ {self.stats['duplicates']}"
        self.stats_labels['errors'].text = f"❌ {self.stats['invalid_qrs']}"
        self.stats_labels['time'].text = f"⏱️ {minutes:02d}:{seconds:02d}"
    
    # === CALLBACKS ===
    
    def on_mode_change(self, spinner, text):
        """Mudança de modo"""
        mode_map = {
            'Simples': 'simple',
            'Melhorado': 'enhanced',
            'Agressivo': 'aggressive'
        }
        self.qr_config['detection_mode'] = mode_map.get(text, 'enhanced')
        Logger.info(f"AndroidQR: Modo alterado para {text}")
    
    def on_debug_toggle(self, switch, value):
        """Toggle debug"""
        self.qr_config['debug_mode'] = value
    
    def on_search_change(self, instance, value):
        """Mudança na busca"""
        self.update_display()
    
    def simulate_gallery(self, instance):
        """Simula galeria Android"""
        self.show_toast("📤 Em Android: Abriria galeria de fotos", "info")
    
    def copy_key(self, key):
        """Simula cópia"""
        self.show_toast(f"📋 Chave copiada:\n{key}", "info")
    
    def export_csv(self, instance):
        """Exporta CSV"""
        if not self.saved_keys:
            self.show_toast("❌ Nenhuma chave para exportar", "warning")
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"cupons_android_{timestamp}.csv"
            export_path = Path.home() / "Downloads" / filename
            
            with open(export_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_ALL)
                writer.writerow(['Chave_Fiscal', 'Data_Leitura', 'Hora_Leitura'])
                
                for key_obj in self.saved_keys:
                    dt = datetime.fromtimestamp(key_obj.timestamp)
                    writer.writerow([key_obj.key, dt.strftime('%d/%m/%Y'), dt.strftime('%H:%M:%S')])
            
            self.show_toast(f"✅ {len(self.saved_keys)} chaves exportadas\n📁 {filename}", "success")
            
        except Exception as e:
            self.show_toast(f"❌ Erro na exportação: {str(e)}", "error")
    
    def clear_all_keys(self, instance):
        """Limpa todas as chaves"""
        if not self.saved_keys:
            self.show_toast("ℹ️ Nenhuma chave para limpar", "info")
            return
        
        # Confirmação rápida
        self.saved_keys.clear()
        self.save_keys_to_file()
        self.update_display()
        self.show_toast(f"🗑️ {len(self.saved_keys)} chaves removidas", "success")
    
    def show_toast(self, message, toast_type="info"):
        """Mostra toast Android-style"""
        colors = {
            "success": (0.2, 0.8, 0.3, 1),
            "warning": (1.0, 0.7, 0.0, 1),
            "error": (0.9, 0.2, 0.2, 1),
            "info": (0.3, 0.6, 0.9, 1)
        }
        
        content = Label(
            text=message,
            font_size='14sp',
            halign='center'
        )
        content.bind(size=content.setter('text_size'))
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.8, 0.3),
            separator_height=0
        )
        
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2.5)
    
    def on_stop(self):
        """Cleanup ao fechar"""
        if self.camera_active:
            self.stop_camera()

def main():
    """Função principal"""
    print("📱 SIMULADOR ANDROID COMPLETO")
    print("🚀 Leitor de Cupons Fiscais - Câmera Real")
    print("✅ Interface móvel no desktop")
    print("📷 Câmera funcional com detecção automática")
    print("🔍 Algoritmos de QR code avançados")
    print("💾 Persistência de dados")
    print("📊 Estatísticas em tempo real")
    print()
    
    try:
        app = AndroidQRReaderApp()
        app.title = "📱 Android QR Reader - Simulador"
        app.run()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()