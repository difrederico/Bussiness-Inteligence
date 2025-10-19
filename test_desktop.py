#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE RÁPIDO - Leitor de Cupons Fiscais Android
Versão simplificada para teste desktop
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
    from kivy.clock import Clock
    from kivy.logger import Logger
    KIVY_AVAILABLE = True
except ImportError as e:
    print(f"❌ Kivy não disponível: {e}")
    KIVY_AVAILABLE = False
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

class QRReaderTestApp(App):
    """Aplicação de teste simplificada"""
    
    def __init__(self):
        super().__init__()
        self.saved_keys = []
        self.config_file = Path.home() / "qr_reader_test" / "chaves.json"
        
    def build(self):
        """Constrói a interface de teste"""
        Logger.info("QRTest: Iniciando interface de teste...")
        
        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Título
        title = Label(
            text='📱 TESTE - Leitor de Cupons Fiscais',
            font_size='24sp',
            size_hint_y=None,
            height='60dp',
            bold=True
        )
        main_layout.add_widget(title)
        
        # Informações
        info_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        
        self.status_label = Label(
            text='✅ Kivy funcionando! Pronto para Android.',
            font_size='16sp',
            color=(0, 0.8, 0, 1)
        )
        info_layout.add_widget(self.status_label)
        
        main_layout.add_widget(info_layout)
        
        # Área de teste de QR
        test_frame = BoxLayout(orientation='vertical', spacing=10)
        
        test_title = Label(
            text='🔍 Teste de Validação de QR',
            font_size='18sp',
            size_hint_y=None,
            height='40dp'
        )
        test_frame.add_widget(test_title)
        
        # Input para teste
        self.qr_input = TextInput(
            hint_text='Cole aqui um QR code de teste ou chave de 44 dígitos...',
            multiline=False,
            size_hint_y=None,
            height='40dp'
        )
        test_frame.add_widget(self.qr_input)
        
        # Botões de teste
        buttons_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height='50dp')
        
        test_btn = Button(text='🧪 Testar QR', background_color=(0.2, 0.6, 0.9, 1))
        test_btn.bind(on_press=self.test_qr_validation)
        
        sample_btn = Button(text='📋 QR Exemplo', background_color=(0.5, 0.5, 0.5, 1))
        sample_btn.bind(on_press=self.load_sample_qr)
        
        buttons_layout.add_widget(test_btn)
        buttons_layout.add_widget(sample_btn)
        
        test_frame.add_widget(buttons_layout)
        main_layout.add_widget(test_frame)
        
        # Modo de detecção
        mode_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing=10)
        
        mode_label = Label(text='🎛️ Modo:', size_hint_x=0.3)
        self.mode_spinner = Spinner(
            text='Melhorado',
            values=['Simples', 'Melhorado', 'Agressivo'],
            size_hint_x=0.7
        )
        
        mode_layout.add_widget(mode_label)
        mode_layout.add_widget(self.mode_spinner)
        
        main_layout.add_widget(mode_layout)
        
        # Switch de debug
        debug_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing=10)
        
        debug_label = Label(text='🐛 Debug:', size_hint_x=0.3)
        self.debug_switch = Switch(active=True, size_hint_x=0.7)
        
        debug_layout.add_widget(debug_label)
        debug_layout.add_widget(self.debug_switch)
        
        main_layout.add_widget(debug_layout)
        
        # Lista de chaves
        keys_frame = BoxLayout(orientation='vertical', spacing=10)
        
        keys_header = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        
        self.keys_counter = Label(
            text=f'📊 {len(self.saved_keys)} chaves',
            font_size='16sp',
            size_hint_x=0.7
        )
        
        clear_btn = Button(
            text='🗑️ Limpar',
            size_hint_x=0.3,
            background_color=(0.8, 0.2, 0.2, 1)
        )
        clear_btn.bind(on_press=self.clear_all_keys)
        
        keys_header.add_widget(self.keys_counter)
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
    
    def test_qr_validation(self, instance):
        """Testa validação de QR code"""
        qr_text = self.qr_input.text.strip()
        
        if not qr_text:
            self.show_toast("❌ Digite um QR code para testar", "error")
            return
        
        Logger.info(f"QRTest: Testando QR: {qr_text[:50]}...")
        
        # Tenta extrair chave fiscal
        match = re.search(r'p=([0-9]{44})', qr_text)
        if match:
            key = match.group(1)
            Logger.info(f"QRTest: Chave extraída: {key}")
        else:
            # Testa se é chave direta
            if len(qr_text) == 44 and qr_text.isdigit():
                key = qr_text
                Logger.info(f"QRTest: Usando chave direta: {key}")
            else:
                self.show_toast("❌ QR inválido - deve conter chave de 44 dígitos", "error")
                return
        
        # Valida chave
        if self.validate_access_key(key):
            # Verifica duplicata
            if any(item.key == key for item in self.saved_keys):
                self.show_toast("⚠️ Este cupom já foi lido", "warning")
                return
            
            # Adiciona nova chave
            new_key = SavedKey(key, time.time())
            self.saved_keys.insert(0, new_key)
            
            # Salva e atualiza
            self.save_keys_to_file()
            self.update_keys_display()
            
            self.show_toast("✅ Cupom fiscal válido e salvo!", "success")
            self.qr_input.text = ""  # Limpa input
            
        else:
            self.show_toast("❌ Chave fiscal inválida (falha no DV)", "error")
    
    def load_sample_qr(self, instance):
        """Carrega QR de exemplo"""
        sample_qr = "https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p=43200114200166000166550010000000046176777681&v=2.00"
        self.qr_input.text = sample_qr
        self.show_toast("📋 QR de exemplo carregado", "info")
    
    def validate_access_key(self, key: str) -> bool:
        """Valida chave de acesso fiscal usando algoritmo DV"""
        if len(key) != 44 or not key.isdigit():
            return False
        
        try:
            # Algoritmo de validação do dígito verificador
            weights = [2, 3, 4, 5, 6, 7, 8, 9] * 5 + [2, 3, 4]
            total = sum(int(digit) * weight for digit, weight in zip(key[:43], weights))
            
            remainder = total % 11
            expected_dv = 0 if remainder < 2 else 11 - remainder
            
            is_valid = int(key[43]) == expected_dv
            
            if self.debug_switch.active:
                Logger.info(f"QRTest: Validação DV - Total: {total}, Resto: {remainder}, DV esperado: {expected_dv}, DV real: {key[43]}, Válido: {is_valid}")
            
            return is_valid
            
        except Exception as e:
            Logger.error(f"QRTest: Erro na validação: {e}")
            return False
    
    def load_saved_keys(self):
        """Carrega chaves salvas do arquivo"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.saved_keys = [SavedKey.from_dict(item) for item in data]
                    
                Logger.info(f"QRTest: {len(self.saved_keys)} chaves carregadas")
            else:
                self.saved_keys = []
                Logger.info("QRTest: Nenhum arquivo de chaves encontrado")
                
        except Exception as e:
            Logger.error(f"QRTest: Erro ao carregar chaves: {e}")
            self.saved_keys = []
    
    def save_keys_to_file(self):
        """Salva chaves no arquivo"""
        try:
            # Cria diretório se necessário
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = [key.to_dict() for key in self.saved_keys]
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            Logger.info(f"QRTest: {len(self.saved_keys)} chaves salvas")
            
        except Exception as e:
            Logger.error(f"QRTest: Erro ao salvar chaves: {e}")
    
    def update_keys_display(self):
        """Atualiza display da lista de chaves"""
        count = len(self.saved_keys)
        self.keys_counter.text = f'📊 {count} chaves'
        
        # Limpa lista atual
        self.keys_list_layout.clear_widgets()
        
        # Adiciona chaves
        for key_obj in self.saved_keys:
            key_item = self.create_key_item(key_obj)
            self.keys_list_layout.add_widget(key_item)
        
        Logger.info(f"QRTest: Lista atualizada - {count} chaves")
    
    def create_key_item(self, key_obj: SavedKey):
        """Cria widget para item da chave"""
        item_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='60dp',
            spacing=10
        )
        
        # Informações da chave
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.8)
        
        # Chave (truncada)
        key_display = f"{key_obj.key[:15]}...{key_obj.key[-10:]}"
        key_label = Label(
            text=f"🔑 {key_display}",
            font_size='14sp',
            size_hint_y=0.6,
            halign='left'
        )
        key_label.bind(size=key_label.setter('text_size'))
        
        # Data/Hora
        date_str = datetime.fromtimestamp(key_obj.timestamp).strftime('%d/%m/%Y %H:%M')
        date_label = Label(
            text=f"📅 {date_str}",
            font_size='12sp',
            size_hint_y=0.4,
            halign='left'
        )
        date_label.bind(size=date_label.setter('text_size'))
        
        info_layout.add_widget(key_label)
        info_layout.add_widget(date_label)
        
        # Botão copiar
        copy_btn = Button(
            text='📋',
            size_hint_x=0.2,
            font_size='16sp'
        )
        copy_btn.bind(on_press=lambda x: self.copy_key_simulation(key_obj.key))
        
        item_layout.add_widget(info_layout)
        item_layout.add_widget(copy_btn)
        
        return item_layout
    
    def copy_key_simulation(self, key):
        """Simula cópia da chave (versão teste)"""
        Logger.info(f"QRTest: Simulando cópia da chave: {key}")
        self.show_toast(f"📋 Chave simulada na clipboard:\n{key[:20]}...", "info")
    
    def clear_all_keys(self, instance):
        """Limpa todas as chaves"""
        if not self.saved_keys:
            self.show_toast("ℹ️ Nenhuma chave para limpar", "info")
            return
        
        # Popup de confirmação simples
        content = BoxLayout(orientation='vertical', spacing=20, padding=20)
        
        message = Label(
            text=f'⚠️ Limpar todas as {len(self.saved_keys)} chaves?\n\nEsta ação não pode ser desfeita!',
            font_size='16sp',
            halign='center'
        )
        message.bind(size=message.setter('text_size'))
        
        buttons = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height='50dp')
        
        confirm_btn = Button(text='🗑️ Sim', background_color=(0.8, 0.2, 0.2, 1))
        cancel_btn = Button(text='❌ Não', background_color=(0.5, 0.5, 0.5, 1))
        
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
            size_hint=(0.8, 0.5),
            background_color=colors.get(toast_type, colors["info"])
        )
        
        popup.open()
        
        # Auto-fecha após 3 segundos
        Clock.schedule_once(lambda dt: popup.dismiss(), 3)


def main():
    """Função principal de teste"""
    print("🚀 Iniciando teste da aplicação Android...")
    print("📱 Interface Kivy será aberta em janela desktop")
    print("🔍 Teste funcionalidades básicas antes do build Android")
    print()
    
    if not KIVY_AVAILABLE:
        print("❌ Erro: Kivy não está disponível")
        return
    
    try:
        app = QRReaderTestApp()
        app.title = "🧪 TESTE - Leitor de Cupons Fiscais"
        app.run()
        
    except Exception as e:
        print(f"❌ Erro na execução: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()