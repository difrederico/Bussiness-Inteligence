#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE CÂMERA - Leitor de Cupons Fiscais Android
Versão de teste com simulação de câmera para desktop
"""

import os
import sys
import time
import json
import re
from pathlib import Path
from datetime import datetime

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
    from kivy.uix.image import Image
    from kivy.uix.filechooser import FileChooserListView
    from kivy.clock import Clock
    from kivy.logger import Logger
    KIVY_AVAILABLE = True
except ImportError as e:
    print(f"❌ Kivy não disponível: {e}")
    KIVY_AVAILABLE = False
    sys.exit(1)

# Tenta importar OpenCV para teste de câmera
try:
    import cv2
    CV2_AVAILABLE = True
    print("✅ OpenCV disponível - câmera real possível")
except ImportError:
    CV2_AVAILABLE = False
    print("⚠️ OpenCV não disponível - usando simulação")

# Tenta importar pyzbar para QR real
try:
    from pyzbar import pyzbar
    import numpy as np
    PYZBAR_AVAILABLE = True
    print("✅ pyzbar disponível - QR real possível")
except ImportError:
    PYZBAR_AVAILABLE = False
    print("⚠️ pyzbar não disponível - usando simulação")

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

class CameraTestApp(App):
    """Aplicação de teste com câmera simulada"""
    
    def __init__(self):
        super().__init__()
        self.saved_keys = []
        self.config_file = Path.home() / "qr_reader_test" / "chaves.json"
        self.is_camera_on = False
        self.camera_simulation_event = None
        
        # QR codes de exemplo para simulação
        self.sample_qrs = [
            "https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p=43200114200166000166550010000000046176777681&v=2.00",
            "https://www.fazenda.sp.gov.br/nfce/qrcode?p=35210707526557000184650010000000015180816190&v=3.10",
            "https://www.nfce.se.gov.br/portal/consultarNFCe.jsp?p=28220314200166000166550010000000123456789012&v=1.50"
        ]
        
    def build(self):
        """Constrói a interface de teste com câmera"""
        Logger.info("CameraTest: Iniciando interface com simulação de câmera...")
        
        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Título
        title = Label(
            text='📷 TESTE CÂMERA - Leitor de Cupons Fiscais',
            font_size='24sp',
            size_hint_y=None,
            height='60dp',
            bold=True
        )
        main_layout.add_widget(title)
        
        # Status da câmera
        status_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        
        camera_status = "📷 OpenCV" if CV2_AVAILABLE else "🎭 Simulação"
        qr_status = "🔍 pyzbar" if PYZBAR_AVAILABLE else "🎲 Mock"
        
        self.status_label = Label(
            text=f'Status: {camera_status} | QR: {qr_status}',
            font_size='16sp',
            color=(0, 0.8, 0, 1) if (CV2_AVAILABLE and PYZBAR_AVAILABLE) else (1, 0.7, 0, 1)
        )
        status_layout.add_widget(self.status_label)
        
        main_layout.add_widget(status_layout)
        
        # Área da câmera
        camera_frame = BoxLayout(orientation='vertical', spacing=10)
        
        camera_title = Label(
            text='📹 Área da Câmera',
            font_size='18sp',
            size_hint_y=None,
            height='40dp'
        )
        camera_frame.add_widget(camera_title)
        
        # Display da câmera (simulado)
        self.camera_display = Label(
            text='📷 Câmera Desligada\n\nClique em "Ligar Câmera" para simular\ndetecção automática de QR codes',
            font_size='16sp',
            size_hint_y=None,
            height='200dp'
        )
        
        camera_frame.add_widget(self.camera_display)
        
        # Controles da câmera
        camera_controls = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height='50dp')
        
        self.camera_btn = Button(
            text='📷 Ligar Câmera',
            background_color=(0.2, 0.7, 0.3, 1),
            size_hint_x=0.4
        )
        self.camera_btn.bind(on_press=self.toggle_camera)
        
        upload_btn = Button(
            text='📤 Upload Imagem',
            background_color=(0.3, 0.5, 0.8, 1),
            size_hint_x=0.3
        )
        upload_btn.bind(on_press=self.upload_image)
        
        simulate_qr_btn = Button(
            text='🎲 Simular QR',
            background_color=(0.8, 0.5, 0.2, 1),
            size_hint_x=0.3
        )
        simulate_qr_btn.bind(on_press=self.simulate_qr_detection)
        
        camera_controls.add_widget(self.camera_btn)
        camera_controls.add_widget(upload_btn)
        camera_controls.add_widget(simulate_qr_btn)
        
        camera_frame.add_widget(camera_controls)
        main_layout.add_widget(camera_frame)
        
        # Configurações
        config_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing=20)
        
        # Modo
        mode_sub = BoxLayout(orientation='horizontal', spacing=10, size_hint_x=0.5)
        mode_label = Label(text='🎛️ Modo:', size_hint_x=0.4)
        self.mode_spinner = Spinner(
            text='Melhorado',
            values=['Simples', 'Melhorado', 'Agressivo'],
            size_hint_x=0.6
        )
        mode_sub.add_widget(mode_label)
        mode_sub.add_widget(self.mode_spinner)
        
        # Debug
        debug_sub = BoxLayout(orientation='horizontal', spacing=10, size_hint_x=0.5)
        debug_label = Label(text='🐛 Debug:', size_hint_x=0.4)
        self.debug_switch = Switch(active=True, size_hint_x=0.6)
        debug_sub.add_widget(debug_label)
        debug_sub.add_widget(self.debug_switch)
        
        config_layout.add_widget(mode_sub)
        config_layout.add_widget(debug_sub)
        main_layout.add_widget(config_layout)
        
        # Lista de chaves
        keys_frame = BoxLayout(orientation='vertical', spacing=10)
        
        keys_header = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        
        self.keys_counter = Label(
            text=f'📊 {len(self.saved_keys)} chaves',
            font_size='16sp',
            size_hint_x=0.5
        )
        
        export_btn = Button(
            text='📁 Exportar',
            size_hint_x=0.25,
            background_color=(0.2, 0.6, 0.4, 1)
        )
        export_btn.bind(on_press=self.simulate_export)
        
        clear_btn = Button(
            text='🗑️ Limpar',
            size_hint_x=0.25,
            background_color=(0.8, 0.2, 0.2, 1)
        )
        clear_btn.bind(on_press=self.clear_all_keys)
        
        keys_header.add_widget(self.keys_counter)
        keys_header.add_widget(export_btn)
        keys_header.add_widget(clear_btn)
        
        keys_frame.add_widget(keys_header)
        
        # ScrollView para lista
        scroll = ScrollView()
        self.keys_list_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.keys_list_layout.bind(minimum_height=self.keys_list_layout.setter('height'))
        
        scroll.add_widget(self.keys_list_layout)
        keys_frame.add_widget(scroll)
        
        main_layout.add_widget(keys_frame)
        
        # Carrega chaves salvas
        self.load_saved_keys()
        self.update_keys_display()
        
        return main_layout
    
    def toggle_camera(self, instance):
        """Liga/desliga simulação da câmera"""
        if not self.is_camera_on:
            self.start_camera_simulation()
        else:
            self.stop_camera_simulation()
    
    def start_camera_simulation(self):
        """Inicia simulação da câmera"""
        Logger.info("CameraTest: Iniciando simulação da câmera...")
        
        self.is_camera_on = True
        self.camera_btn.text = '📷 Desligar Câmera'
        self.camera_btn.background_color = (0.8, 0.2, 0.2, 1)
        
        self.camera_display.text = '📹 CÂMERA ATIVA\n\n🔍 Procurando QR codes...\n\n(Simulação rodando)\nAguarde detecção automática'
        
        # Agenda detecção automática a cada 5-10 segundos
        self.schedule_random_detection()
        
        if CV2_AVAILABLE:
            self.try_real_camera()
    
    def stop_camera_simulation(self):
        """Para simulação da câmera"""
        Logger.info("CameraTest: Parando simulação da câmera...")
        
        self.is_camera_on = False
        self.camera_btn.text = '📷 Ligar Câmera'
        self.camera_btn.background_color = (0.2, 0.7, 0.3, 1)
        
        self.camera_display.text = '📷 Câmera Desligada\n\nClique em "Ligar Câmera" para simular\ndetecção automática de QR codes'
        
        # Cancela agendamentos
        if self.camera_simulation_event:
            self.camera_simulation_event.cancel()
            self.camera_simulation_event = None
    
    def schedule_random_detection(self):
        """Agenda próxima detecção aleatória"""
        if self.is_camera_on:
            # Detecta QR a cada 8-15 segundos
            import random
            next_detection = random.uniform(8, 15)
            
            self.camera_simulation_event = Clock.schedule_once(
                lambda dt: self.auto_detect_qr(), 
                next_detection
            )
            
            Logger.info(f"CameraTest: Próxima detecção em {next_detection:.1f}s")
    
    def auto_detect_qr(self):
        """Detecta QR automaticamente (simulação)"""
        if not self.is_camera_on:
            return
        
        Logger.info("CameraTest: Simulando detecção automática de QR...")
        
        self.camera_display.text = '📹 CÂMERA ATIVA\n\n✨ QR CODE DETECTADO!\n\nProcessando...'
        
        # Simula processamento
        Clock.schedule_once(lambda dt: self.process_detected_qr(), 2.0)
    
    def process_detected_qr(self):
        """Processa QR detectado"""
        if not self.is_camera_on:
            return
        
        import random
        
        # Escolhe QR aleatório
        qr_url = random.choice(self.sample_qrs)
        
        # Simula falhas ocasionais (20% chance)
        if random.random() < 0.2:
            Logger.info("CameraTest: Simulando falha na detecção...")
            self.camera_display.text = '📹 CÂMERA ATIVA\n\n❌ QR ilegível\n\n🔍 Procurando novamente...'
            self.schedule_random_detection()
            return
        
        # Processa QR válido
        self.handle_qr_detection(qr_url)
        
        # Agenda próxima detecção
        self.schedule_random_detection()
    
    def handle_qr_detection(self, qr_data):
        """Processa QR detectado"""
        Logger.info(f"CameraTest: Processando QR: {qr_data[:50]}...")
        
        # Extrai chave fiscal
        match = re.search(r'p=([0-9]{44})', qr_data)
        if not match:
            self.camera_display.text = '📹 CÂMERA ATIVA\n\n⚠️ QR inválido\n\n🔍 Procurando QR fiscal...'
            return
        
        key = match.group(1)
        
        # Valida chave
        if not self.validate_access_key(key):
            self.camera_display.text = '📹 CÂMERA ATIVA\n\n❌ Chave inválida\n\n🔍 Procurando QR válido...'
            return
        
        # Verifica duplicata
        if any(item.key == key for item in self.saved_keys):
            self.camera_display.text = '📹 CÂMERA ATIVA\n\n⚠️ Cupom já lido\n\n🔍 Procurando novos cupons...'
            return
        
        # Salva chave
        new_key = SavedKey(key, time.time())
        self.saved_keys.insert(0, new_key)
        
        self.save_keys_to_file()
        self.update_keys_display()
        
        # Feedback visual
        self.camera_display.text = f'📹 CÂMERA ATIVA\n\n✅ CUPOM SALVO!\n\nChave: {key[:20]}...\n\n🔍 Procurando próximo...'
        
        # Toast de sucesso
        self.show_toast(f"✅ Cupom #{len(self.saved_keys)} salvo automaticamente!", "success")
        
        Logger.info(f"CameraTest: Chave salva automaticamente: {key[:20]}...")
    
    def simulate_qr_detection(self, instance):
        """Força simulação de detecção de QR"""
        if not self.is_camera_on:
            self.show_toast("❌ Ligue a câmera primeiro", "error")
            return
        
        Logger.info("CameraTest: Forçando simulação de detecção...")
        self.auto_detect_qr()
    
    def try_real_camera(self):
        """Tenta usar câmera real do OpenCV"""
        if not CV2_AVAILABLE:
            return
        
        try:
            Logger.info("CameraTest: Tentando acessar câmera real...")
            
            # Tenta abrir câmera padrão
            cap = cv2.VideoCapture(0)
            
            if cap.isOpened():
                Logger.info("CameraTest: ✅ Câmera real detectada!")
                self.status_label.text = "Status: 📷 Câmera Real Ativa | QR: " + ("🔍 pyzbar" if PYZBAR_AVAILABLE else "🎲 Mock")
                self.status_label.color = (0, 1, 0, 1)
                
                # Libera câmera imediatamente (só teste)
                cap.release()
            else:
                Logger.info("CameraTest: ⚠️ Câmera real não acessível")
        
        except Exception as e:
            Logger.error(f"CameraTest: Erro ao acessar câmera: {e}")
    
    def upload_image(self, instance):
        """Simula upload de imagem"""
        Logger.info("CameraTest: Abrindo seletor de arquivo...")
        
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Info
        info_label = Label(
            text='📤 Simulação de Upload\n\nEm Android: acessaria galeria\nNo desktop: usa FileChooser',
            font_size='16sp',
            size_hint_y=0.3,
            halign='center'
        )
        info_label.bind(size=info_label.setter('text_size'))
        
        # File chooser simulado
        chooser_label = Label(
            text='🖼️ Selecione imagem com QR code:\n\n(Funcionalidade completa no Android)',
            font_size='14sp',
            size_hint_y=0.5,
            halign='center'
        )
        chooser_label.bind(size=chooser_label.setter('text_size'))
        
        # Botões
        buttons = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=10)
        
        mock_btn = Button(text='🎭 Simular Upload')
        cancel_btn = Button(text='❌ Cancelar')
        
        buttons.add_widget(mock_btn)
        buttons.add_widget(cancel_btn)
        
        content.add_widget(info_label)
        content.add_widget(chooser_label)
        content.add_widget(buttons)
        
        popup = Popup(
            title='📤 Upload de Imagem',
            content=content,
            size_hint=(0.9, 0.7)
        )
        
        def mock_upload(btn):
            popup.dismiss()
            # Simula processamento de imagem
            import random
            qr_data = random.choice(self.sample_qrs)
            self.handle_qr_detection(qr_data)
            self.show_toast("📤 Imagem processada com sucesso!", "success")
        
        def cancel_upload(btn):
            popup.dismiss()
        
        mock_btn.bind(on_press=mock_upload)
        cancel_btn.bind(on_press=cancel_upload)
        
        popup.open()
    
    def validate_access_key(self, key: str) -> bool:
        """Valida chave de acesso fiscal"""
        if len(key) != 44 or not key.isdigit():
            return False
        
        try:
            weights = [2, 3, 4, 5, 6, 7, 8, 9] * 5 + [2, 3, 4]
            total = sum(int(digit) * weight for digit, weight in zip(key[:43], weights))
            
            remainder = total % 11
            expected_dv = 0 if remainder < 2 else 11 - remainder
            
            is_valid = int(key[43]) == expected_dv
            
            if self.debug_switch.active:
                Logger.info(f"CameraTest: Validação DV - Válido: {is_valid}")
            
            return is_valid
            
        except Exception as e:
            Logger.error(f"CameraTest: Erro na validação: {e}")
            return False
    
    def load_saved_keys(self):
        """Carrega chaves salvas"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.saved_keys = [SavedKey.from_dict(item) for item in data]
                    
                Logger.info(f"CameraTest: {len(self.saved_keys)} chaves carregadas")
            else:
                self.saved_keys = []
                
        except Exception as e:
            Logger.error(f"CameraTest: Erro ao carregar: {e}")
            self.saved_keys = []
    
    def save_keys_to_file(self):
        """Salva chaves no arquivo"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = [key.to_dict() for key in self.saved_keys]
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            Logger.info(f"CameraTest: {len(self.saved_keys)} chaves salvas")
            
        except Exception as e:
            Logger.error(f"CameraTest: Erro ao salvar: {e}")
    
    def update_keys_display(self):
        """Atualiza display da lista"""
        count = len(self.saved_keys)
        self.keys_counter.text = f'📊 {count} chaves'
        
        self.keys_list_layout.clear_widgets()
        
        for key_obj in self.saved_keys[-10:]:  # Últimas 10
            key_item = self.create_key_item(key_obj)
            self.keys_list_layout.add_widget(key_item)
    
    def create_key_item(self, key_obj: SavedKey):
        """Cria item da chave"""
        item_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='50dp',
            spacing=10
        )
        
        # Info
        key_display = f"{key_obj.key[:12]}...{key_obj.key[-8:]}"
        date_str = datetime.fromtimestamp(key_obj.timestamp).strftime('%H:%M')
        
        info_label = Label(
            text=f"🔑 {key_display} - {date_str}",
            font_size='12sp',
            size_hint_x=0.8,
            halign='left'
        )
        info_label.bind(size=info_label.setter('text_size'))
        
        # Botão
        copy_btn = Button(
            text='📋',
            size_hint_x=0.2,
            font_size='14sp'
        )
        copy_btn.bind(on_press=lambda x: self.show_toast(f"📋 {key_obj.key}", "info"))
        
        item_layout.add_widget(info_label)
        item_layout.add_widget(copy_btn)
        
        return item_layout
    
    def simulate_export(self, instance):
        """Simula exportação CSV"""
        if not self.saved_keys:
            self.show_toast("❌ Nenhuma chave para exportar", "warning")
            return
        
        Logger.info("CameraTest: Simulando exportação CSV...")
        
        filename = f"cupons_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.show_toast(f"✅ Exportado: {len(self.saved_keys)} chaves\n📁 {filename}", "success")
    
    def clear_all_keys(self, instance):
        """Limpa todas as chaves"""
        if not self.saved_keys:
            self.show_toast("ℹ️ Nenhuma chave para limpar", "info")
            return
        
        self.saved_keys.clear()
        self.save_keys_to_file()
        self.update_keys_display()
        self.show_toast(f"🗑️ Todas as chaves removidas", "success")
    
    def show_toast(self, message, toast_type="info"):
        """Mostra toast"""
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
            title=toast_type.title(),
            content=content,
            size_hint=(0.8, 0.4)
        )
        
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 3)
    
    def on_stop(self):
        """Cleanup ao fechar"""
        if self.is_camera_on:
            self.stop_camera_simulation()


def main():
    """Função principal"""
    print("📷 Teste de Câmera - Leitor de Cupons Fiscais")
    print("🎭 Simulação completa da funcionalidade Android")
    print("✅ Detecção automática de QR codes")
    print("📱 Interface idêntica ao Android")
    print()
    
    try:
        app = CameraTestApp()
        app.title = "📷 TESTE CÂMERA - QR Reader"
        app.run()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()