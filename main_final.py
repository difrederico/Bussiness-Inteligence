#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = '1.0'

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex, platform
from kivy.graphics import Color, RoundedRectangle
import json
import re
import os
from datetime import datetime

# Importações Android
if platform == 'android':
    try:
        from android.permissions import request_permissions, Permission
        ANDROID_AVAILABLE = True
    except ImportError:
        ANDROID_AVAILABLE = False
else:
    ANDROID_AVAILABLE = False

# Paleta de cores moderna
COLORS = {
    'primary': get_color_from_hex('#007AFF'),
    'success': get_color_from_hex('#34C759'),
    'warning': get_color_from_hex('#FF9500'),
    'error': get_color_from_hex('#FF3B30'),
    'background': get_color_from_hex('#F2F2F7'),
    'surface': get_color_from_hex('#FFFFFF'),
    'text': get_color_from_hex('#000000'),
    'text_light': get_color_from_hex('#8E8E93'),
    'white': get_color_from_hex('#FFFFFF')
}

class SavedKey:
    """Classe para gerenciar chaves fiscais salvas"""
    
    def __init__(self, key, timestamp=None):
        self.key = key
        self.timestamp = timestamp or datetime.now().timestamp()
        
    def to_dict(self):
        return {'key': self.key, 'timestamp': self.timestamp}
    
    @classmethod
    def from_dict(cls, data):
        return cls(data['key'], data.get('timestamp'))
    
    def get_formatted_date(self):
        return datetime.fromtimestamp(self.timestamp).strftime('%d/%m/%Y %H:%M')

class ModernCard(FloatLayout):
    """Widget de cartão moderno"""
    
    def __init__(self, bg_color=COLORS['surface'], **kwargs):
        super().__init__(**kwargs)
        
        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )
        
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class MainScreen(Screen):
    """Tela principal do aplicativo"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        self.app_ref = None
        self.setup_ui()
    
    def setup_ui(self):
        # Layout principal
        main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(15)
        )
        
        # Cabeçalho
        header = self.create_header()
        main_layout.add_widget(header)
        
        # Área de entrada manual
        input_section = self.create_input_section()
        main_layout.add_widget(input_section)
        
        # Botões de ação
        action_section = self.create_action_section()
        main_layout.add_widget(action_section)
        
        # Status
        self.status_label = Label(
            text='Pronto para processar chaves fiscais',
            font_size=sp(14),
            color=COLORS['text_light'],
            size_hint_y=None,
            height=dp(30),
            halign='center'
        )
        main_layout.add_widget(self.status_label)
        
        self.add_widget(main_layout)
    
    def create_header(self):
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60)
        )
        
        title = Label(
            text='📱 Leitor QR Fiscal',
            font_size=sp(24),
            bold=True,
            color=COLORS['text'],
            halign='center',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        
        header.add_widget(title)
        return header
    
    def create_input_section(self):
        card = ModernCard(size_hint_y=None, height=dp(120))
        layout = BoxLayout(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10)
        )
        
        # Label
        layout.add_widget(Label(
            text='Inserir Chave Fiscal:',
            font_size=sp(16),
            color=COLORS['text'],
            size_hint_y=None,
            height=dp(25),
            halign='left'
        ))
        
        # Input
        self.key_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            font_size=sp(14),
            hint_text='Cole ou digite a chave fiscal aqui...'
        )
        layout.add_widget(self.key_input)
        
        # Botão processar
        process_btn = Button(
            text='✅ Processar Chave',
            size_hint_y=None,
            height=dp(40),
            background_color=COLORS['primary'],
            color=COLORS['white']
        )
        process_btn.bind(on_press=self.process_key)
        layout.add_widget(process_btn)
        
        card.add_widget(layout)
        return card
    
    def create_action_section(self):
        card = ModernCard(size_hint_y=None, height=dp(180))
        layout = GridLayout(
            cols=2,
            padding=dp(15),
            spacing=dp(10)
        )
        
        # Botão Câmera
        camera_btn = Button(
            text='📷\nCâmera',
            font_size=sp(14),
            background_color=COLORS['primary'],
            color=COLORS['white']
        )
        camera_btn.bind(on_press=self.open_camera)
        
        # Botão Galeria
        gallery_btn = Button(
            text='🖼️\nGaleria',
            font_size=sp(14),
            background_color=COLORS['success'],
            color=COLORS['white']
        )
        gallery_btn.bind(on_press=self.open_gallery)
        
        # Botão Chaves Salvas
        saved_btn = Button(
            text='💾\nSalvas',
            font_size=sp(14),
            background_color=COLORS['warning'],
            color=COLORS['white']
        )
        saved_btn.bind(on_press=self.show_saved)
        
        # Botão Info
        info_btn = Button(
            text='ℹ️\nInfo',
            font_size=sp(14),
            background_color=COLORS['text_light'],
            color=COLORS['white']
        )
        info_btn.bind(on_press=self.show_info)
        
        layout.add_widget(camera_btn)
        layout.add_widget(gallery_btn)
        layout.add_widget(saved_btn)
        layout.add_widget(info_btn)
        
        card.add_widget(layout)
        return card
    
    def set_app_ref(self, app):
        self.app_ref = app
    
    def update_status(self, message, color='text_light'):
        self.status_label.text = message
        self.status_label.color = COLORS.get(color, COLORS['text_light'])
    
    def process_key(self, instance):
        if self.app_ref:
            key = self.key_input.text.strip()
            if key:
                self.app_ref.process_fiscal_key(key)
                self.key_input.text = ''
            else:
                self.update_status('Digite uma chave fiscal', 'error')
    
    def open_camera(self, instance):
        if platform == 'android':
            self.update_status('Abrindo câmera...', 'primary')
        else:
            self.update_status('Câmera disponível apenas no Android', 'warning')
    
    def open_gallery(self, instance):
        if platform == 'android':
            self.update_status('Abrindo galeria...', 'primary')
        else:
            self.update_status('Galeria disponível apenas no Android', 'warning')
    
    def show_saved(self, instance):
        if self.app_ref:
            self.app_ref.show_saved_keys()
    
    def show_info(self, instance):
        info_text = f'''
Leitor QR Fiscal v{__version__}

📱 Funcionalidades:
• Leitura de chaves fiscais
• Armazenamento local
• Interface moderna

🔧 Plataforma: {platform.title()}
🐍 Versão: Python/Kivy

Desenvolvido para Business Intelligence
        '''.strip()
        
        popup = Popup(
            title='Informações do App',
            content=Label(text=info_text, halign='center'),
            size_hint=(0.8, 0.6)
        )
        popup.open()

class LeitorQRApp(App):
    """Aplicativo principal"""
    
    def build(self):
        # Configuração da janela
        from kivy.core.window import Window
        Window.clearcolor = COLORS['background']
        
        # Gerenciador de telas
        self.sm = ScreenManager(transition=NoTransition())
        
        # Tela principal
        self.main_screen = MainScreen()
        self.main_screen.set_app_ref(self)
        self.sm.add_widget(self.main_screen)
        
        # Estado da aplicação
        self.saved_keys = []
        self.load_saved_keys()
        
        return self.sm
    
    def on_start(self):
        """Executado quando o app inicia"""
        if ANDROID_AVAILABLE:
            self.request_permissions()
        
        self.main_screen.update_status('Aplicativo iniciado com sucesso!', 'success')
    
    def request_permissions(self):
        """Solicita permissões do Android"""
        try:
            request_permissions([
                Permission.CAMERA,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])
        except Exception as e:
            print(f"Erro ao solicitar permissões: {e}")
    
    def process_fiscal_key(self, key):
        """Processa uma chave fiscal"""
        if self.validate_fiscal_key(key):
            # Salva a chave
            saved_key = SavedKey(key)
            self.saved_keys.insert(0, saved_key)
            self.save_keys()
            
            # Feedback visual
            short_key = key[:15] + '...' if len(key) > 15 else key
            self.main_screen.update_status(f'✅ Chave salva: {short_key}', 'success')
        else:
            self.main_screen.update_status('❌ Chave fiscal inválida', 'error')
    
    def validate_fiscal_key(self, key):
        """Valida formato da chave fiscal"""
        # Remove caracteres não numéricos
        clean_key = re.sub(r'\D', '', key)
        # Chave fiscal deve ter 44 dígitos
        return len(clean_key) == 44
    
    def load_saved_keys(self):
        """Carrega chaves salvas do arquivo"""
        try:
            if os.path.exists('saved_keys.json'):
                with open('saved_keys.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.saved_keys = [SavedKey.from_dict(item) for item in data]
        except Exception as e:
            print(f"Erro ao carregar chaves: {e}")
            self.saved_keys = []
    
    def save_keys(self):
        """Salva chaves no arquivo"""
        try:
            data = [key.to_dict() for key in self.saved_keys]
            with open('saved_keys.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar chaves: {e}")
    
    def show_saved_keys(self):
        """Exibe popup com chaves salvas"""
        if not self.saved_keys:
            self.main_screen.update_status('Nenhuma chave salva ainda', 'warning')
            return
        
        # Conteúdo do popup
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # Cabeçalho
        header = Label(
            text=f'Chaves Salvas ({len(self.saved_keys)})',
            font_size=sp(18),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(header)
        
        # Lista de chaves
        scroll = ScrollView()
        keys_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None
        )
        keys_layout.bind(minimum_height=keys_layout.setter('height'))
        
        # Mostra as 10 chaves mais recentes
        for saved_key in self.saved_keys[:10]:
            key_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(50),
                spacing=dp(10)
            )
            
            # Info da chave
            key_info = Label(
                text=f'{saved_key.key[:20]}...\n{saved_key.get_formatted_date()}',
                font_size=sp(11),
                halign='left',
                valign='middle'
            )
            key_info.bind(size=key_info.setter('text_size'))
            
            # Botão usar
            use_btn = Button(
                text='Usar',
                size_hint_x=None,
                width=dp(60),
                background_color=COLORS['primary']
            )
            use_btn.bind(
                on_press=lambda x, key=saved_key.key: self.use_saved_key(key)
            )
            
            key_layout.add_widget(key_info)
            key_layout.add_widget(use_btn)
            keys_layout.add_widget(key_layout)
        
        scroll.add_widget(keys_layout)
        content.add_widget(scroll)
        
        # Botão fechar
        close_btn = Button(
            text='Fechar',
            size_hint_y=None,
            height=dp(40),
            background_color=COLORS['text_light']
        )
        
        popup = Popup(
            title='Chaves Fiscais Salvas',
            content=content,
            size_hint=(0.9, 0.8)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()
    
    def use_saved_key(self, key):
        """Usa uma chave salva"""
        self.main_screen.key_input.text = key
        short_key = key[:15] + '...' if len(key) > 15 else key
        self.main_screen.update_status(f'Chave carregada: {short_key}', 'success')

if __name__ == '__main__':
    LeitorQRApp().run()