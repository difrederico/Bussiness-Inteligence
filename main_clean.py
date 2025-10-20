#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.switch import Switch
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.widget import Widget
from kivy.utils import platform
import json
import re
import os
import csv
import time
import threading
from datetime import datetime

# Importações para Android
if platform == 'android':
    try:
        from android.permissions import request_permissions, Permission
        from jnius import autoclass, cast
        from android import activity, mActivity
        PYJNIUS_AVAILABLE = True
    except ImportError:
        PYJNIUS_AVAILABLE = False
else:
    PYJNIUS_AVAILABLE = False

# Cores do sistema
COLORS = {
    'primary': get_color_from_hex('#007AFF'),
    'primary_dark': get_color_from_hex('#0056D3'),
    'accent': get_color_from_hex('#34C759'),
    'error': get_color_from_hex('#FF3B30'),
    'warning': get_color_from_hex('#FF9500'),
    'background': get_color_from_hex('#F2F2F7'),
    'surface': get_color_from_hex('#FFFFFF'),
    'text': get_color_from_hex('#000000'),
    'text_secondary': get_color_from_hex('#8E8E93'),
    'text_light': get_color_from_hex('#FFFFFF')
}

class SavedKey:
    def __init__(self, key, timestamp=None):
        self.key = key
        self.timestamp = timestamp or datetime.now().timestamp()
        
    def to_dict(self):
        return {
            'key': self.key,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(data['key'], data.get('timestamp'))
    
    def get_formatted_date(self):
        return datetime.fromtimestamp(self.timestamp).strftime('%d/%m/%Y %H:%M')

class ModernCard(FloatLayout):
    def __init__(self, bg_color=COLORS['surface'], **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        
        with self.canvas.before:
            Color(*self.bg_color)
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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        self.app_ref = None
        
        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60))
        
        title_label = Label(
            text='Leitor de Cupons Fiscais',
            font_size=sp(24),
            bold=True,
            color=COLORS['text'],
            size_hint_x=0.7,
            halign='left',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))
        
        header.add_widget(title_label)
        
        # Campo de entrada manual
        input_card = ModernCard(size_hint_y=None, height=dp(120))
        input_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        input_layout.add_widget(Label(
            text='Inserir Chave Fiscal Manualmente:',
            font_size=sp(16),
            color=COLORS['text'],
            size_hint_y=None,
            height=dp(25)
        ))
        
        self.key_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            font_size=sp(14),
            hint_text='Insira ou cole a chave fiscal aqui...'
        )
        
        process_btn = Button(
            text='Processar Chave',
            size_hint_y=None,
            height=dp(40),
            background_color=COLORS['primary'],
            color=COLORS['text_light']
        )
        process_btn.bind(on_press=self.process_manual_key)
        
        input_layout.add_widget(self.key_input)
        input_layout.add_widget(process_btn)
        input_card.add_widget(input_layout)
        
        # Botões de ação
        action_card = ModernCard(size_hint_y=None, height=dp(200))
        action_layout = GridLayout(cols=2, padding=dp(15), spacing=dp(10))
        
        # Botão Câmera
        camera_btn = Button(
            text='📷\nAbrir Câmera',
            font_size=sp(14),
            background_color=COLORS['primary'],
            color=COLORS['text_light']
        )
        camera_btn.bind(on_press=self.open_camera)
        
        # Botão Upload
        upload_btn = Button(
            text='📁\nUpload Imagem',
            font_size=sp(14),
            background_color=COLORS['accent'],
            color=COLORS['text_light']
        )
        upload_btn.bind(on_press=self.upload_image)
        
        # Botão Chaves Salvas
        saved_btn = Button(
            text='💾\nChaves Salvas',
            font_size=sp(14),
            background_color=COLORS['warning'],
            color=COLORS['text_light']
        )
        saved_btn.bind(on_press=self.show_saved_keys)
        
        # Botão Configurações
        config_btn = Button(
            text='⚙️\nConfigurações',
            font_size=sp(14),
            background_color=COLORS['text_secondary'],
            color=COLORS['text_light']
        )
        config_btn.bind(on_press=self.show_config)
        
        action_layout.add_widget(camera_btn)
        action_layout.add_widget(upload_btn)
        action_layout.add_widget(saved_btn)
        action_layout.add_widget(config_btn)
        action_card.add_widget(action_layout)
        
        # Status
        self.status_label = Label(
            text='Pronto para processar chaves fiscais',
            font_size=sp(14),
            color=COLORS['text_secondary'],
            size_hint_y=None,
            height=dp(30)
        )
        
        # Montagem final
        main_layout.add_widget(header)
        main_layout.add_widget(input_card)
        main_layout.add_widget(action_card)
        main_layout.add_widget(self.status_label)
        
        self.add_widget(main_layout)
    
    def set_app_ref(self, app):
        self.app_ref = app
    
    def process_manual_key(self, instance):
        if self.app_ref:
            key = self.key_input.text.strip()
            if key:
                self.app_ref.process_fiscal_key(key)
                self.key_input.text = ''
    
    def open_camera(self, instance):
        if self.app_ref:
            self.app_ref.abrir_camera_nativa(instance)
    
    def upload_image(self, instance):
        if self.app_ref:
            self.app_ref.abrir_galeria_nativa(instance)
    
    def show_saved_keys(self, instance):
        if self.app_ref:
            self.app_ref.show_saved_keys()
    
    def show_config(self, instance):
        self.status_label.text = 'Configurações em desenvolvimento'

class MercadoEmNumerosApp(App):
    def build(self):
        # Configurações da janela
        from kivy.core.window import Window
        Window.clearcolor = COLORS['background']
        
        # Screen Manager
        self.sm = ScreenManager(transition=NoTransition())
        
        # Tela principal
        self.main_screen = MainScreen()
        self.main_screen.set_app_ref(self)
        self.sm.add_widget(self.main_screen)
        
        # Variáveis de estado
        self.saved_keys = []
        self.load_saved_keys()
        
        return self.sm
    
    def on_start(self):
        if platform == 'android':
            self.request_android_permissions()
    
    def request_android_permissions(self):
        if PYJNIUS_AVAILABLE:
            try:
                request_permissions([
                    Permission.CAMERA,
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.WRITE_EXTERNAL_STORAGE
                ])
            except Exception as e:
                print(f"Erro ao solicitar permissões: {e}")
    
    def process_fiscal_key(self, key):
        # Valida e processa a chave fiscal
        if self.validate_fiscal_key(key):
            saved_key = SavedKey(key)
            self.saved_keys.insert(0, saved_key)
            self.save_keys()
            self.main_screen.status_label.text = f'Chave processada e salva: {key[:20]}...'
        else:
            self.main_screen.status_label.text = 'Chave fiscal inválida'
    
    def validate_fiscal_key(self, key):
        # Validação básica de chave fiscal (44 dígitos)
        cleaned_key = re.sub(r'\D', '', key)
        return len(cleaned_key) == 44
    
    def load_saved_keys(self):
        try:
            if os.path.exists('saved_keys.json'):
                with open('saved_keys.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.saved_keys = [SavedKey.from_dict(item) for item in data]
        except Exception as e:
            print(f"Erro ao carregar chaves: {e}")
            self.saved_keys = []
    
    def save_keys(self):
        try:
            data = [key.to_dict() for key in self.saved_keys]
            with open('saved_keys.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar chaves: {e}")
    
    def show_saved_keys(self):
        if not self.saved_keys:
            self.main_screen.status_label.text = 'Nenhuma chave salva'
            return
        
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # Header
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
        keys_layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None)
        keys_layout.bind(minimum_height=keys_layout.setter('height'))
        
        for i, saved_key in enumerate(self.saved_keys[:10]):  # Mostra apenas as 10 mais recentes
            key_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(60),
                spacing=dp(10)
            )
            
            key_info = Label(
                text=f'{saved_key.key[:20]}...\n{saved_key.get_formatted_date()}',
                font_size=sp(12),
                halign='left',
                valign='middle'
            )
            key_info.bind(size=key_info.setter('text_size'))
            
            use_btn = Button(
                text='Usar',
                size_hint_x=None,
                width=dp(60),
                background_color=COLORS['primary']
            )
            use_btn.bind(on_press=lambda x, key=saved_key.key: self.use_saved_key(key))
            
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
            background_color=COLORS['text_secondary']
        )
        
        popup = Popup(
            title='Chaves Salvas',
            content=content,
            size_hint=(0.9, 0.8)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()
    
    def use_saved_key(self, key):
        self.main_screen.key_input.text = key
        self.main_screen.status_label.text = f'Chave carregada: {key[:20]}...'
    
    def abrir_camera_nativa(self, instance):
        if platform != 'android':
            self.main_screen.status_label.text = 'Câmera disponível apenas no Android'
            return
        
        self.main_screen.status_label.text = 'Abrindo câmera nativa...'
    
    def abrir_galeria_nativa(self, instance):
        if platform != 'android':
            self.main_screen.status_label.text = 'Galeria disponível apenas no Android'
            return
        
        self.main_screen.status_label.text = 'Abrindo galeria nativa...'

if __name__ == '__main__':
    MercadoEmNumerosApp().run()