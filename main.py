#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 LEITOR DE CUPONS FISCAIS - VERSÃO ANDROID
🐍 Desenvolvido com Kivy + Buildozer
📅 Outubro 2025

Aplicação mobile para leitura de cupons fiscais via QR code
Convertida da versão desktop (Tkinter) para mobile (Kivy)
"""

import os
import re
import time
import json
import csv
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional

# === KIVY IMPORTS ===
import kivy
kivy.require('2.3.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.switch import Switch
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.camera import Camera
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.logger import Logger

# === PROCESSAMENTO DE IMAGEM ===
try:
    import cv2
    CV2_AVAILABLE = True
    Logger.info("OpenCV: Disponível")
except ImportError:
    CV2_AVAILABLE = False
    Logger.warning("OpenCV: Não disponível")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
    Logger.info("NumPy: Disponível")
except ImportError:
    NUMPY_AVAILABLE = False
    Logger.warning("NumPy: Não disponível")

try:
    from pyzbar import pyzbar
    PYZBAR_AVAILABLE = True
    Logger.info("pyzbar: Disponível")
except ImportError:
    PYZBAR_AVAILABLE = False
    Logger.warning("pyzbar: Não disponível")

try:
    from PIL import Image
    PIL_AVAILABLE = True
    Logger.info("PIL: Disponível")
except ImportError:
    PIL_AVAILABLE = False
    Logger.warning("PIL: Não disponível")

# === CLASSES DE DADOS ===
@dataclass
class SavedKey:
    """
    Representa uma chave fiscal salva
    Mantém compatibilidade com a versão desktop
    """
    key: str
    timestamp: float
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SavedKey':
        """Cria instância a partir de dicionário"""
        return cls(
            key=data['key'],
            timestamp=data['timestamp']
        )
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return asdict(self)

# === APLICAÇÃO PRINCIPAL ===
class QRReaderApp(App):
    """
    Aplicação principal - Leitor de Cupons Fiscais Android
    Convertida de Tkinter para Kivy mantendo funcionalidades
    """
    
    def __init__(self):
        super().__init__()
        
        # === CONFIGURAÇÕES DO ALGORITMO ===
        self.qr_config = {
            'detection_mode': 'enhanced',    # simple, enhanced, aggressive
            'processing_fps': 10,            # FPS para processamento mobile
            'cooldown_time': 1.5,            # Cooldown entre leituras
            'debug_mode': False,             # Modo debug
            'enhancement_level': 3,          # Nível de melhoria
            'multi_scale': True,             # Múltiplas escalas
            'rotation_correction': True,     # Correção rotação
            'noise_reduction': True          # Redução ruído
        }
        
        # === DADOS ===
        self.saved_keys: List[SavedKey] = []
        self.last_scan_time = 0
        self.is_scanning = False
        
        # === ARQUIVO DE CONFIGURAÇÃO ANDROID ===
        # Usa diretório específico do Android
        from kivy.utils import platform
        if platform == 'android':
            from android.storage import primary_external_storage_path
            storage_path = primary_external_storage_path()
            self.config_file = Path(storage_path) / "LeitorCupons" / "chaves_salvas.json"
            # Cria diretório se não existir
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
        else:
            # Para testes em desktop
            self.config_file = Path("chaves_salvas_android.json")
        
        # === ESTATÍSTICAS ===
        self.performance_stats = {
            'total_frames': 0,
            'qr_detections': 0,
            'avg_process_time': 0,
            'start_time': time.time()
        }
    
    def build(self):
        """
        Constrói a interface da aplicação
        Layout otimizado para mobile
        """
        Logger.info("QRReader: Iniciando construção da interface")
        
        # === LAYOUT PRINCIPAL ===
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # === CABEÇALHO ===
        header = self.create_header()
        main_layout.add_widget(header)
        
        # === ÁREA DA CÂMERA ===
        camera_section = self.create_camera_section()
        main_layout.add_widget(camera_section)
        
        # === CONTROLES ===
        controls = self.create_controls()
        main_layout.add_widget(controls)
        
        # === LISTA DE CHAVES ===
        keys_section = self.create_keys_section()
        main_layout.add_widget(keys_section)
        
        # === RODAPÉ ===
        footer = self.create_footer()
        main_layout.add_widget(footer)
        
        # === CARREGA DADOS SALVOS ===
        self.load_saved_keys()
        self.update_keys_display()
        
        Logger.info("QRReader: Interface construída com sucesso")
        return main_layout
    
    def create_header(self):
        """Cria cabeçalho da aplicação"""
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='60dp')
        
        # Título
        title = Label(
            text='📱 Leitor de Cupons Fiscais',
            font_size='20sp',
            bold=True,
            size_hint_x=0.7
        )
        
        # Contador de chaves
        self.keys_counter = Label(
            text='📊 0 chaves',
            font_size='16sp',
            size_hint_x=0.3,
            halign='right'
        )
        
        header_layout.add_widget(title)
        header_layout.add_widget(self.keys_counter)
        
        return header_layout
    
    def create_camera_section(self):
        """Cria seção da câmera"""
        camera_layout = BoxLayout(orientation='vertical', size_hint_y=None, height='300dp')
        
        # Label da câmera
        camera_label = Label(
            text='📷 Escaneamento em Tempo Real',
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height='40dp'
        )
        
        # Câmera (será inicializada quando necessário)
        self.camera = Camera(
            resolution=(640, 480),
            play=False
        )
        
        camera_layout.add_widget(camera_label)
        camera_layout.add_widget(self.camera)
        
        return camera_layout
    
    def create_controls(self):
        """Cria controles da aplicação"""
        controls_layout = BoxLayout(orientation='vertical', size_hint_y=None, height='200dp', spacing=10)
        
        # === LINHA 1: BOTÕES PRINCIPAIS ===
        buttons_row1 = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', spacing=10)
        
        self.camera_button = Button(
            text='📷 Iniciar Câmera',
            background_color=(0.2, 0.7, 0.3, 1),
            font_size='16sp'
        )
        self.camera_button.bind(on_press=self.toggle_camera)
        
        self.upload_button = Button(
            text='📤 Upload Imagem',
            background_color=(0.3, 0.6, 0.9, 1),
            font_size='16sp'
        )
        self.upload_button.bind(on_press=self.upload_image)
        
        buttons_row1.add_widget(self.camera_button)
        buttons_row1.add_widget(self.upload_button)
        
        # === LINHA 2: CONFIGURAÇÕES ===
        config_row = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', spacing=10)
        
        # Modo de detecção
        mode_label = Label(text='Modo:', size_hint_x=0.2, font_size='14sp')
        self.mode_spinner = Spinner(
            text='Melhorado',
            values=['Simples', 'Melhorado', 'Agressivo'],
            size_hint_x=0.4,
            font_size='14sp'
        )
        self.mode_spinner.bind(text=self.on_mode_change)
        
        # Debug switch
        debug_label = Label(text='Debug:', size_hint_x=0.2, font_size='14sp')
        self.debug_switch = Switch(size_hint_x=0.2, active=False)
        self.debug_switch.bind(active=self.on_debug_toggle)
        
        config_row.add_widget(mode_label)
        config_row.add_widget(self.mode_spinner)
        config_row.add_widget(debug_label)
        config_row.add_widget(self.debug_switch)
        
        # === LINHA 3: EXPORTAÇÃO ===
        export_row = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', spacing=10)
        
        self.export_button = Button(
            text='📊 Exportar CSV',
            background_color=(0.1, 0.7, 0.5, 1),
            font_size='16sp'
        )
        self.export_button.bind(on_press=self.export_csv)
        
        self.clear_button = Button(
            text='🗑️ Limpar Tudo',
            background_color=(0.8, 0.2, 0.2, 1),
            font_size='16sp'
        )
        self.clear_button.bind(on_press=self.clear_all_keys)
        
        export_row.add_widget(self.export_button)
        export_row.add_widget(self.clear_button)
        
        # === PERFORMANCE INFO ===
        self.performance_label = Label(
            text='📊 Aguardando...',
            size_hint_y=None,
            height='30dp',
            font_size='12sp'
        )
        
        controls_layout.add_widget(buttons_row1)
        controls_layout.add_widget(config_row)
        controls_layout.add_widget(export_row)
        controls_layout.add_widget(self.performance_label)
        
        return controls_layout
    
    def create_keys_section(self):
        """Cria seção da lista de chaves"""
        keys_layout = BoxLayout(orientation='vertical', size_hint_y=None, height='200dp')
        
        # Label da seção
        keys_label = Label(
            text='📋 Chaves Salvas',
            font_size='16sp',
            bold=True,
            size_hint_y=None,
            height='30dp'
        )
        
        # Campo de busca
        self.search_input = TextInput(
            hint_text='🔍 Buscar chaves...',
            multiline=False,
            size_hint_y=None,
            height='40dp',
            font_size='14sp'
        )
        self.search_input.bind(text=self.on_search_change)
        
        # Lista de chaves (ScrollView)
        scroll = ScrollView()
        self.keys_list_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.keys_list_layout.bind(minimum_height=self.keys_list_layout.setter('height'))
        scroll.add_widget(self.keys_list_layout)
        
        keys_layout.add_widget(keys_label)
        keys_layout.add_widget(self.search_input)
        keys_layout.add_widget(scroll)
        
        return keys_layout
    
    def create_footer(self):
        """Cria rodapé da aplicação"""
        footer = Label(
            text='🐍 Python • 📱 Kivy • 🔍 OpenCV • v2.0 Android',
            size_hint_y=None,
            height='30dp',
            font_size='12sp'
        )
        return footer
    
    # === MÉTODOS DE INTERFACE ===
    
    def toggle_camera(self, instance):
        """Inicia/para a câmera"""
        if not CV2_AVAILABLE:
            self.show_toast("OpenCV não disponível", "error")
            return
            
        if self.is_scanning:
            self.stop_camera()
        else:
            self.start_camera()
    
    def start_camera(self):
        """Inicia captura da câmera"""
        Logger.info("QRReader: Iniciando câmera...")
        
        try:
            self.camera.play = True
            self.is_scanning = True
            self.camera_button.text = '⏹️ Parar Câmera'
            self.camera_button.background_color = (0.8, 0.2, 0.2, 1)
            
            # Agenda processamento de frames
            self.camera_event = Clock.schedule_interval(self.process_camera_frame, 1.0 / self.qr_config['processing_fps'])
            
            Logger.info("QRReader: Câmera iniciada")
            
        except Exception as e:
            Logger.error(f"QRReader: Erro ao iniciar câmera: {e}")
            self.show_toast(f"Erro na câmera: {str(e)}", "error")
    
    def stop_camera(self):
        """Para captura da câmera"""
        Logger.info("QRReader: Parando câmera...")
        
        try:
            self.camera.play = False
            self.is_scanning = False
            self.camera_button.text = '📷 Iniciar Câmera'
            self.camera_button.background_color = (0.2, 0.7, 0.3, 1)
            
            # Cancela processamento
            if hasattr(self, 'camera_event'):
                self.camera_event.cancel()
            
            Logger.info("QRReader: Câmera parada")
            
        except Exception as e:
            Logger.error(f"QRReader: Erro ao parar câmera: {e}")
    
    def process_camera_frame(self, dt):
        """Processa frame da câmera para detecção de QR"""
        if not self.is_scanning or not self.camera.texture:
            return
        
        try:
            # Converte texture do Kivy para OpenCV
            frame = self.texture_to_opencv(self.camera.texture)
            if frame is None:
                return
            
            # Processa QR codes no frame
            current_time = time.time()
            if current_time - self.last_scan_time > self.qr_config['cooldown_time']:
                qr_codes = self.detect_qr_codes(frame)
                
                if qr_codes:
                    self.last_scan_time = current_time
                    for qr_code in qr_codes:
                        try:
                            data = qr_code.data.decode('utf-8')
                            Logger.info(f"QR detectado: {data[:50]}...")
                            self.handle_qr_code_result(data)
                            break  # Processa apenas o primeiro
                        except UnicodeDecodeError:
                            continue
            
            # Atualiza estatísticas
            self.update_performance_stats()
            
        except Exception as e:
            Logger.error(f"QRReader: Erro ao processar frame: {e}")
    
    def texture_to_opencv(self, texture):
        """Converte texture do Kivy para formato OpenCV"""
        try:
            # Obtém dados da texture
            buffer = texture.pixels
            size = texture.size
            
            # Converte para numpy array
            if NUMPY_AVAILABLE:
                arr = np.frombuffer(buffer, np.uint8)
                arr = arr.reshape(size[1], size[0], 4)  # RGBA
                
                # Converte RGBA para BGR (OpenCV)
                frame = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
                return frame
            
            return None
            
        except Exception as e:
            Logger.error(f"QRReader: Erro na conversão de texture: {e}")
            return None
    
    def upload_image(self, instance):
        """Abre seletor de arquivo para upload"""
        Logger.info("QRReader: Abrindo seletor de arquivo...")
        
        # Cria popup com file chooser
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # File chooser
        filechooser = FileChooserListView(
            filters=['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif', '*.tiff'],
            size_hint_y=0.8
        )
        
        # Botões
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=10)
        
        select_btn = Button(text='✅ Selecionar', size_hint_x=0.5)
        cancel_btn = Button(text='❌ Cancelar', size_hint_x=0.5)
        
        buttons_layout.add_widget(select_btn)
        buttons_layout.add_widget(cancel_btn)
        
        content.add_widget(filechooser)
        content.add_widget(buttons_layout)
        
        # Popup
        popup = Popup(
            title='📤 Selecionar Imagem',
            content=content,
            size_hint=(0.9, 0.8)
        )
        
        # Callbacks
        def select_file(btn):
            if filechooser.selection:
                file_path = filechooser.selection[0]
                popup.dismiss()
                self.process_uploaded_image(file_path)
        
        def cancel_selection(btn):
            popup.dismiss()
        
        select_btn.bind(on_press=select_file)
        cancel_btn.bind(on_press=cancel_selection)
        
        popup.open()

    def process_uploaded_image(self, file_path):
        """Processa imagem enviada via upload"""
        Logger.info(f"QRReader: Processando imagem: {file_path}")
        
        try:
            if PIL_AVAILABLE:
                pil_image = Image.open(file_path)
                img_array = np.array(pil_image)
                if len(img_array.shape) == 3:
                    frame = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                else:
                    frame = img_array
            else:
                frame = cv2.imread(file_path)
            
            if frame is None:
                self.show_toast("Erro ao carregar imagem", "error")
                return
            
            qr_codes = self.detect_qr_codes(frame)
            
            if qr_codes:
                Logger.info(f"QRReader: {len(qr_codes)} QR code(s) encontrado(s)")
                for qr_code in qr_codes:
                    try:
                        data = qr_code.data.decode('utf-8')
                        self.handle_qr_code_result(data)
                        break
                    except UnicodeDecodeError:
                        continue
                self.show_toast("QR code processado com sucesso!", "success")
            else:
                self.show_toast("Nenhum QR code encontrado na imagem", "warning")
                
        except Exception as e:
            Logger.error(f"QRReader: Erro ao processar imagem: {e}")
            self.show_toast(f"Erro ao processar: {str(e)}", "error")

    def detect_qr_codes(self, frame):
        """Detecta QR codes usando algoritmo avançado"""
        if not PYZBAR_AVAILABLE:
            return []
        
        mode = self.mode_spinner.text.lower()
        
        if mode == 'simples':
            return self.simple_qr_detection(frame)
        elif mode == 'melhorado':
            return self.enhanced_qr_detection(frame)
        elif mode == 'agressivo':
            return self.aggressive_qr_detection(frame)
        else:
            return self.enhanced_qr_detection(frame)

    def simple_qr_detection(self, frame):
        """Detecção simples e rápida"""
        try:
            qr_codes = pyzbar.decode(frame)
            if hasattr(self, 'debug_switch') and self.debug_switch.active and qr_codes:
                Logger.info(f"QRReader: Detecção simples: {len(qr_codes)} QR(s)")
            return qr_codes
        except Exception as e:
            if hasattr(self, 'debug_switch') and self.debug_switch.active:
                Logger.error(f"QRReader: Erro detecção simples: {e}")
            return []

    def enhanced_qr_detection(self, frame):
        """Detecção melhorada com pré-processamento"""
        qr_codes = []
        
        try:
            direct_codes = pyzbar.decode(frame)
            qr_codes.extend(direct_codes)
            
            if qr_codes:
                if hasattr(self, 'debug_switch') and self.debug_switch.active:
                    Logger.info(f"QRReader: Detecção direta: {len(qr_codes)} QR(s)")
                return qr_codes
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            techniques = []
            equalized = cv2.equalizeHist(gray)
            techniques.append(("Equalizado", equalized))
            
            adaptive_thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            techniques.append(("Adaptativo", adaptive_thresh))
            
            bilateral = cv2.bilateralFilter(gray, 5, 50, 50)
            techniques.append(("Bilateral", bilateral))
            
            for name, processed_frame in techniques:
                try:
                    codes = pyzbar.decode(processed_frame)
                    if codes:
                        if hasattr(self, 'debug_switch') and self.debug_switch.active:
                            Logger.info(f"QRReader: Detecção {name}: {len(codes)} QR(s)")
                        qr_codes.extend(codes)
                        break
                except:
                    continue
            
            return self.remove_duplicate_qrs(qr_codes)
            
        except Exception as e:
            if hasattr(self, 'debug_switch') and self.debug_switch.active:
                Logger.error(f"QRReader: Erro detecção melhorada: {e}")
        
        return qr_codes

    def aggressive_qr_detection(self, frame):
        """Detecção agressiva para casos difíceis"""
        qr_codes = []
        
        try:
            qr_codes = self.enhanced_qr_detection(frame)
            if qr_codes:
                return qr_codes
            
            if hasattr(self, 'debug_switch') and self.debug_switch.active:
                Logger.info("QRReader: Iniciando detecção agressiva...")
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            scales = [0.8, 1.2, 1.5]
            for scale in scales:
                try:
                    height, width = gray.shape
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    
                    scaled = cv2.resize(gray, (new_width, new_height))
                    codes = pyzbar.decode(scaled)
                    
                    if codes:
                        if hasattr(self, 'debug_switch') and self.debug_switch.active:
                            Logger.info(f"QRReader: Detecção escala {scale}: {len(codes)} QR(s)")
                        qr_codes.extend(codes)
                        break
                except:
                    continue
            
            if not qr_codes:
                angles = [-10, 10, -15, 15]
                center = (gray.shape[1] // 2, gray.shape[0] // 2)
                
                for angle in angles:
                    try:
                        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                        rotated = cv2.warpAffine(gray, rotation_matrix, (gray.shape[1], gray.shape[0]))
                        codes = pyzbar.decode(rotated)
                        
                        if codes:
                            if hasattr(self, 'debug_switch') and self.debug_switch.active:
                                Logger.info(f"QRReader: Detecção rotação {angle}°: {len(codes)} QR(s)")
                            qr_codes.extend(codes)
                            break
                    except:
                        continue
            
            return self.remove_duplicate_qrs(qr_codes)
            
        except Exception as e:
            if hasattr(self, 'debug_switch') and self.debug_switch.active:
                Logger.error(f"QRReader: Erro detecção agressiva: {e}")
        
        return qr_codes

    def remove_duplicate_qrs(self, qr_codes):
        """Remove QR codes duplicados"""
        unique_codes = []
        for code in qr_codes:
            is_duplicate = False
            for existing in unique_codes:
                if (abs(code.rect.left - existing.rect.left) < 20 and 
                    abs(code.rect.top - existing.rect.top) < 20):
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_codes.append(code)
        
        return unique_codes

    def handle_qr_code_result(self, data: str):
        """Processa resultado da leitura QR"""
        match = re.search(r'p=([0-9]{44})', data)
        key = match.group(1) if match else None
        
        if not key or not self.validate_access_key(key):
            self.show_toast("QR Code inválido ou não é cupom fiscal", "warning")
            return
        
        if any(item.key == key for item in self.saved_keys):
            self.show_toast("Este cupom já foi lido", "warning")
            return
        
        new_key = SavedKey(key, time.time())
        self.saved_keys.insert(0, new_key)
        
        self.save_keys_to_file()
        self.update_keys_display()
        
        self.show_toast("✅ Cupom salvo com sucesso!", "success")
        Logger.info(f"QRReader: Chave salva: {key[:20]}...")

    def validate_access_key(self, key: str) -> bool:
        """Valida chave de acesso fiscal (algoritmo DV)"""
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

    def load_saved_keys(self):
        """Carrega chaves salvas do arquivo"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.saved_keys = [SavedKey.from_dict(item) for item in data]
                    
                Logger.info(f"QRReader: {len(self.saved_keys)} chaves carregadas")
            else:
                self.saved_keys = []
                Logger.info("QRReader: Nenhum arquivo de chaves encontrado")
                
        except Exception as e:
            Logger.error(f"QRReader: Erro ao carregar chaves: {e}")
            self.saved_keys = []

    def save_keys_to_file(self):
        """Salva chaves no arquivo"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = [key.to_dict() for key in self.saved_keys]
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            Logger.info(f"QRReader: {len(self.saved_keys)} chaves salvas")
            
        except Exception as e:
            Logger.error(f"QRReader: Erro ao salvar chaves: {e}")

    def update_keys_display(self):
        """Atualiza display da lista de chaves"""
        count = len(self.saved_keys)
        if hasattr(self, 'keys_counter'):
            self.keys_counter.text = f'📊 {count} chaves'
        
        if hasattr(self, 'keys_list_layout'):
            self.keys_list_layout.clear_widgets()
        
        search_text = ""
        if hasattr(self, 'search_input'):
            search_text = self.search_input.text.lower()
            
        filtered_keys = [
            key for key in self.saved_keys
            if search_text in key.key.lower()
        ]
        
        if hasattr(self, 'keys_list_layout'):
            for key_obj in filtered_keys:
                key_item = self.create_key_item(key_obj)
                self.keys_list_layout.add_widget(key_item)
        
        Logger.info(f"QRReader: Lista atualizada - {len(filtered_keys)} de {count} chaves")

    def create_key_item(self, key_obj: SavedKey):
        """Cria widget para item da chave"""
        item_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='60dp',
            padding=5,
            spacing=10
        )
        
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.8)
        
        key_display = f"{key_obj.key[:15]}...{key_obj.key[-10:]}"
        key_label = Label(
            text=f"🔑 {key_display}",
            font_size='14sp',
            halign='left',
            size_hint_y=0.6
        )
        key_label.bind(size=key_label.setter('text_size'))
        
        date_str = datetime.fromtimestamp(key_obj.timestamp).strftime('%d/%m/%Y %H:%M')
        date_label = Label(
            text=f"📅 {date_str}",
            font_size='12sp',
            halign='left',
            size_hint_y=0.4
        )
        date_label.bind(size=date_label.setter('text_size'))
        
        info_layout.add_widget(key_label)
        info_layout.add_widget(date_label)
        
        copy_btn = Button(
            text='📋',
            size_hint_x=0.2,
            font_size='16sp'
        )
        copy_btn.bind(on_press=lambda x: self.copy_key_to_clipboard(key_obj.key))
        
        item_layout.add_widget(info_layout)
        item_layout.add_widget(copy_btn)
        
        return item_layout

    def copy_key_to_clipboard(self, key):
        """Copia chave para clipboard (Android)"""
        try:
            from kivy.utils import platform
            if platform == 'android':
                from jnius import autoclass
                Context = autoclass('android.content.Context')
                ClipboardManager = autoclass('android.content.ClipboardManager')
                ClipData = autoclass('android.content.ClipData')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                
                activity = PythonActivity.mActivity
                clipboard = activity.getSystemService(Context.CLIPBOARD_SERVICE)
                clip = ClipData.newPlainText("Chave Fiscal", key)
                clipboard.setPrimaryClip(clip)
                
                self.show_toast("Chave copiada!", "success")
            else:
                Logger.info(f"Chave para copiar: {key}")
                self.show_toast("Função de cópia disponível apenas no Android", "info")
                
        except Exception as e:
            Logger.error(f"QRReader: Erro ao copiar: {e}")
            self.show_toast("Erro ao copiar chave", "error")

    def show_toast(self, message, toast_type="info"):
        """Mostra toast/popup temporário"""
        colors = {
            "success": (0.2, 0.8, 0.3, 1),
            "warning": (1.0, 0.7, 0.0, 1), 
            "error": (0.9, 0.2, 0.2, 1),
            "info": (0.3, 0.6, 0.9, 1)
        }
        
        icons = {
            "success": "✅",
            "warning": "⚠️",
            "error": "❌", 
            "info": "ℹ️"
        }
        
        content = Label(
            text=f"{icons.get(toast_type, 'ℹ️')} {message}",
            font_size='16sp',
            halign='center'
        )
        content.bind(size=content.setter('text_size'))
        
        popup = Popup(
            title=toast_type.title(),
            content=content,
            size_hint=(0.8, 0.4),
            background_color=colors.get(toast_type, colors["info"])
        )
        
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 3)

    def update_performance_stats(self):
        """Atualiza estatísticas de performance"""
        try:
            self.performance_stats['total_frames'] += 1
            
            if self.performance_stats['total_frames'] % 30 == 0:
                elapsed = time.time() - self.performance_stats['start_time']
                fps = self.performance_stats['total_frames'] / elapsed if elapsed > 0 else 0
                
                if hasattr(self, 'performance_label'):
                    self.performance_label.text = f"📊 FPS: {fps:.1f} | Frames: {self.performance_stats['total_frames']}"
                
        except Exception as e:
            Logger.error(f"QRReader: Erro nas estatísticas: {e}")

    # === MÉTODOS DE CALLBACK ===

    def on_mode_change(self, spinner, text):
        """Callback mudança de modo"""
        mode_map = {
            'Simples': 'simple',
            'Melhorado': 'enhanced', 
            'Agressivo': 'aggressive'
        }
        self.qr_config['detection_mode'] = mode_map.get(text, 'enhanced')
        Logger.info(f"QRReader: Modo alterado para {text}")
    
    def on_debug_toggle(self, switch, value):
        """Callback toggle debug"""
        self.qr_config['debug_mode'] = value
        Logger.info(f"QRReader: Debug {'ativado' if value else 'desativado'}")
    
    def on_search_change(self, instance, value):
        """Callback mudança na busca"""
        self.update_keys_display()

    # === MÉTODOS DE AÇÃO ===
    
    def export_csv(self, instance):
        """Exporta chaves para CSV"""
        if not self.saved_keys:
            self.show_toast("Nenhuma chave para exportar", "warning")
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"chaves_fiscais_{timestamp}.csv"
            
            from kivy.utils import platform
            if platform == 'android':
                try:
                    from android.storage import primary_external_storage_path
                    export_path = Path(primary_external_storage_path()) / "Download" / filename
                except:
                    export_path = Path("/sdcard/Download") / filename
            else:
                export_path = Path(filename)
            
            with open(export_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_ALL)
                
                writer.writerow(['Chave_Fiscal', 'Data_Leitura', 'Hora_Leitura'])
                
                for key_obj in self.saved_keys:
                    dt = datetime.fromtimestamp(key_obj.timestamp)
                    date_str = dt.strftime('%d/%m/%Y')
                    time_str = dt.strftime('%H:%M:%S')
                    writer.writerow([key_obj.key, date_str, time_str])
            
            self.show_toast(f"✅ Exportado: {len(self.saved_keys)} chaves\n📂 {export_path.name}", "success")
            Logger.info(f"QRReader: Exportado para {export_path}")
            
        except Exception as e:
            Logger.error(f"QRReader: Erro na exportação: {e}")
            self.show_toast(f"Erro na exportação: {str(e)}", "error")
    
    def clear_all_keys(self, instance):
        """Limpa todas as chaves após confirmação"""
        if not self.saved_keys:
            self.show_toast("Nenhuma chave para limpar", "info")
            return
        
        content = BoxLayout(orientation='vertical', spacing=20, padding=20)
        
        message = Label(
            text=f'⚠️ Tem certeza que deseja limpar\ntodas as {len(self.saved_keys)} chaves salvas?\n\nEsta ação não pode ser desfeita!',
            font_size='16sp',
            halign='center'
        )
        message.bind(size=message.setter('text_size'))
        
        buttons = BoxLayout(orientation='horizontal', spacing=10)
        
        confirm_btn = Button(text='🗑️ Sim, Limpar', background_color=(0.8, 0.2, 0.2, 1))
        cancel_btn = Button(text='❌ Cancelar', background_color=(0.5, 0.5, 0.5, 1))
        
        buttons.add_widget(confirm_btn)
        buttons.add_widget(cancel_btn)
        
        content.add_widget(message)
        content.add_widget(buttons)
        
        popup = Popup(
            title='⚠️ Confirmação',
            content=content,
            size_hint=(0.8, 0.6)
        )
        
        def confirm_clear(btn):
            self.saved_keys.clear()
            self.save_keys_to_file()
            self.update_keys_display()
            popup.dismiss()
            self.show_toast("🗑️ Todas as chaves foram removidas", "success")
        
        def cancel_clear(btn):
            popup.dismiss()
        
        confirm_btn.bind(on_press=confirm_clear)
        cancel_btn.bind(on_press=cancel_clear)
        
        popup.open()


# === INICIALIZAÇÃO DA APLICAÇÃO ===

def main():
    """Função principal da aplicação"""
    try:
        Logger.info("QRReader: Iniciando aplicação Android...")
        
        # Verifica dependências críticas
        missing_deps = []
        if not CV2_AVAILABLE:
            missing_deps.append("OpenCV")
        if not PYZBAR_AVAILABLE:
            missing_deps.append("pyzbar")
        if not NUMPY_AVAILABLE:
            missing_deps.append("NumPy")
        
        if missing_deps:
            Logger.warning(f"QRReader: Dependências faltando: {', '.join(missing_deps)}")
            Logger.warning("QRReader: Algumas funcionalidades podem não funcionar")
        
        # Cria e executa aplicação
        app = QRReaderApp()
        app.title = "📱 Leitor de Cupons Fiscais"
        app.run()
        
    except Exception as e:
        Logger.error(f"QRReader: Erro fatal na aplicação: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()