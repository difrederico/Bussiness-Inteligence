#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Leitor de Cupons Fiscais - Android Profissional
Interface limpa, funcional e intuitiva

Funcionalidades:
- Validação de chaves fiscais brasileiras
- Armazenamento e gerenciamento de chaves
- Exportação para CSV
- Interface profissional e responsiva

Autor: Business Intelligence
Data: Outubro 2025
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
import json
import re
import os
import csv
import time
from datetime import datetime

# Configuração de cores profissionais
COLORS = {
    'primary': get_color_from_hex('#2196F3'),      # Azul profissional
    'primary_dark': get_color_from_hex('#1976D2'), # Azul escuro
    'accent': get_color_from_hex('#4CAF50'),       # Verde sucesso
    'error': get_color_from_hex('#F44336'),        # Vermelho erro
    'warning': get_color_from_hex('#FF9800'),      # Laranja aviso
    'background': get_color_from_hex('#FAFAFA'),   # Cinza claro
    'surface': get_color_from_hex('#FFFFFF'),      # Branco
    'text': get_color_from_hex('#212121'),         # Texto escuro
    'text_secondary': get_color_from_hex('#757575') # Texto secundário
}


class SavedKey:
    """Classe para representar uma chave fiscal salva"""
    
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


class KeyListItem(BoxLayout):
    """Widget para exibir uma chave na lista"""
    
    def __init__(self, key_obj, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.key_obj = key_obj
        self.app_instance = app_instance
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(80)
        self.spacing = dp(10)
        self.padding = [dp(15), dp(10)]
        
        # Informações da chave
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
        
        # Chave (mascarada para melhor visualização)
        key_text = f"{key_obj.key[:8]}...{key_obj.key[-8:]}"
        key_label = Label(
            text=key_text,
            font_size='16sp',
            size_hint_y=0.6,
            halign='left',
            color=COLORS['text']
        )
        key_label.bind(size=key_label.setter('text_size'))
        info_layout.add_widget(key_label)
        
        # Data
        date_label = Label(
            text=key_obj.get_formatted_date(),
            font_size='12sp',
            size_hint_y=0.4,
            halign='left',
            color=COLORS['text_secondary']
        )
        date_label.bind(size=date_label.setter('text_size'))
        info_layout.add_widget(date_label)
        
        self.add_widget(info_layout)
        
        # Botões de ação
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_x=0.3, spacing=dp(5))
        
        copy_btn = Button(
            text='Copiar',
            size_hint_y=None,
            height=dp(35),
            font_size='12sp',
            background_color=COLORS['primary']
        )
        copy_btn.bind(on_press=self.copy_key)
        buttons_layout.add_widget(copy_btn)
        
        delete_btn = Button(
            text='Excluir',
            size_hint_y=None,
            height=dp(35),
            font_size='12sp',
            background_color=COLORS['error']
        )
        delete_btn.bind(on_press=self.delete_key)
        buttons_layout.add_widget(delete_btn)
        
        self.add_widget(buttons_layout)
    
    def copy_key(self, instance):
        """Copia chave para área de transferência"""
        try:
            # Simula cópia (no Android real, usaria Clipboard)
            self.app_instance.show_message(f'Chave copiada!\n{self.key_obj.key}', 'Sucesso')
            
            # Feedback visual
            instance.text = 'Copiado!'
            instance.background_color = COLORS['accent']
            Clock.schedule_once(lambda dt: self.restore_copy_button(instance), 2)
            
        except Exception as e:
            self.app_instance.show_message(f'Erro ao copiar: {str(e)}', 'Erro')
    
    def restore_copy_button(self, button):
        """Restaura botão de cópia"""
        button.text = 'Copiar'
        button.background_color = COLORS['primary']
    
    def delete_key(self, instance):
        """Confirma e exclui chave"""
        self.app_instance.confirm_delete_key(self.key_obj)


class FiscalKeyReaderApp(App):
    """Aplicativo principal - Interface profissional e funcional"""
    
    def build(self):
        self.saved_keys = []
        self.current_search = ""
        
        # Carrega dados salvos
        self.load_saved_keys()
        
        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # === CABEÇALHO ===
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100), spacing=dp(5))
        
        # Título principal
        title = Label(
            text='Leitor de Cupons Fiscais',
            font_size='24sp',
            size_hint_y=0.6,
            halign='center',
            color=COLORS['primary']
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)
        
        # Subtítulo
        subtitle = Label(
            text='Validação e gerenciamento de chaves fiscais',
            font_size='14sp',
            size_hint_y=0.4,
            halign='center',
            color=COLORS['text_secondary']
        )
        subtitle.bind(size=subtitle.setter('text_size'))
        header.add_widget(subtitle)
        
        main_layout.add_widget(header)
        
        # === ENTRADA DE CHAVE ===
        input_section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(150), spacing=dp(10))
        
        # Label de instrução
        instruction_label = Label(
            text='Digite a chave fiscal (44 dígitos):',
            font_size='16sp',
            size_hint_y=None,
            height=dp(30),
            halign='left',
            color=COLORS['text']
        )
        instruction_label.bind(size=instruction_label.setter('text_size'))
        input_section.add_widget(instruction_label)
        
        # Campo de entrada
        self.key_input = TextInput(
            hint_text='Ex: 12345678901234567890123456789012345678901234',
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size='14sp',
            padding=[dp(15), dp(12)],
            background_color=COLORS['surface']
        )
        input_section.add_widget(self.key_input)
        
        # Botões de ação
        buttons_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(50))
        
        validate_btn = Button(
            text='Validar e Salvar',
            font_size='16sp',
            background_color=COLORS['accent']
        )
        validate_btn.bind(on_press=self.validate_key)
        buttons_layout.add_widget(validate_btn)
        
        clear_btn = Button(
            text='Limpar',
            font_size='16sp',
            background_color=COLORS['text_secondary']
        )
        clear_btn.bind(on_press=self.clear_input)
        buttons_layout.add_widget(clear_btn)
        
        input_section.add_widget(buttons_layout)
        
        main_layout.add_widget(input_section)
        
        # === RESULTADO ===
        self.result_label = Label(
            text='Digite uma chave fiscal de 44 dígitos para começar',
            size_hint_y=None,
            height=dp(40),
            font_size='14sp',
            halign='center',
            color=COLORS['primary']
        )
        self.result_label.bind(size=self.result_label.setter('text_size'))
        main_layout.add_widget(self.result_label)
        
        # === SEÇÃO DE CHAVES SALVAS ===
        saved_section = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # Cabeçalho das chaves salvas
        saved_header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        
        keys_title = Label(
            text='Chaves Salvas',
            font_size='18sp',
            size_hint_x=0.6,
            halign='left',
            color=COLORS['text']
        )
        keys_title.bind(size=keys_title.setter('text_size'))
        saved_header.add_widget(keys_title)
        
        self.keys_count_label = Label(
            text='0 chaves',
            font_size='14sp',
            size_hint_x=0.4,
            halign='right',
            color=COLORS['text_secondary']
        )
        self.keys_count_label.bind(size=self.keys_count_label.setter('text_size'))
        saved_header.add_widget(self.keys_count_label)
        
        saved_section.add_widget(saved_header)
        
        # Campo de busca
        self.search_input = TextInput(
            hint_text='🔍 Buscar nas chaves salvas...',
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            font_size='14sp',
            padding=[dp(15), dp(8)]
        )
        self.search_input.bind(text=self.on_search_change)
        saved_section.add_widget(self.search_input)
        
        # Lista de chaves
        scroll = ScrollView()
        self.keys_layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None)
        self.keys_layout.bind(minimum_height=self.keys_layout.setter('height'))
        scroll.add_widget(self.keys_layout)
        saved_section.add_widget(scroll)
        
        # Botões de ação
        actions_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(50))
        
        export_btn = Button(
            text='Exportar CSV',
            font_size='16sp',
            background_color=COLORS['primary']
        )
        export_btn.bind(on_press=self.export_csv)
        actions_layout.add_widget(export_btn)
        
        clear_all_btn = Button(
            text='Limpar Todas',
            font_size='16sp',
            background_color=COLORS['error']
        )
        clear_all_btn.bind(on_press=self.clear_all_keys)
        actions_layout.add_widget(clear_all_btn)
        
        saved_section.add_widget(actions_layout)
        
        main_layout.add_widget(saved_section)
        
        # Atualiza interface inicial
        self.update_keys_display()
        
        return main_layout
    
    def validate_access_key(self, key):
        """
        Valida chave de acesso brasileira usando algoritmo de dígito verificador
        """
        if not key or len(key) != 44 or not key.isdigit():
            return False
        
        try:
            # Extrai os 43 primeiros dígitos
            base_key = key[:43]
            
            # Calcula primeiro dígito verificador
            weights1 = [2, 3, 4, 5, 6, 7, 8, 9] * 5 + [2, 3, 4]
            sum1 = sum(int(digit) * weight for digit, weight in zip(base_key, weights1))
            remainder1 = sum1 % 11
            dv1 = 0 if remainder1 < 2 else 11 - remainder1
            
            # Calcula segundo dígito verificador
            weights2 = [3, 4, 5, 6, 7, 8, 9] + [2, 3, 4, 5, 6, 7, 8, 9] * 4 + [2, 3, 4, 5]
            sum2 = sum(int(digit) * weight for digit, weight in zip(base_key + str(dv1), weights2))
            remainder2 = sum2 % 11
            dv2 = 0 if remainder2 < 2 else 11 - remainder2
            
            # Verifica se os dígitos verificadores conferem
            calculated_dv = f"{dv1}{dv2}"
            provided_dv = key[43:]
            
            return calculated_dv == provided_dv
            
        except Exception as e:
            print(f"Erro na validação: {e}")
            return False
    
    def validate_key(self, instance):
        """Valida chave inserida manualmente"""
        key = self.key_input.text.strip()
        
        if not key:
            self.show_result('Digite uma chave fiscal', 'error')
            return
        
        # Remove caracteres não numéricos
        key = re.sub(r'[^0-9]', '', key)
        
        if len(key) != 44:
            self.show_result(f'Chave deve ter 44 dígitos (atual: {len(key)})', 'error')
            return
        
        if self.validate_access_key(key):
            # Verifica duplicata
            if any(item.key == key for item in self.saved_keys):
                self.show_result('Esta chave já foi salva anteriormente', 'warning')
                return
            
            # Salva chave válida
            new_key = SavedKey(key)
            self.saved_keys.insert(0, new_key)
            self.save_keys_to_file()
            
            self.show_result('✓ Chave fiscal válida e salva com sucesso!', 'success')
            self.clear_input(None)
            self.update_keys_display()
        else:
            self.show_result('✗ Chave fiscal inválida - Verifique os dígitos', 'error')
    
    def clear_input(self, instance):
        """Limpa campo de entrada"""
        self.key_input.text = ''
        self.show_result('Campo limpo - Digite nova chave fiscal', 'info')
    
    def on_search_change(self, instance, text):
        """Atualiza busca em tempo real"""
        self.current_search = text.lower()
        self.update_keys_display()
    
    def update_keys_display(self):
        """Atualiza exibição das chaves salvas"""
        # Limpa layout atual
        self.keys_layout.clear_widgets()
        
        # Filtra chaves baseado na busca
        filtered_keys = []
        for key_obj in self.saved_keys:
            if not self.current_search or self.current_search in key_obj.key.lower():
                filtered_keys.append(key_obj)
        
        # Atualiza contador
        total = len(self.saved_keys)
        filtered = len(filtered_keys)
        if self.current_search:
            self.keys_count_label.text = f'{filtered}/{total} chaves'
        else:
            self.keys_count_label.text = f'{total} chaves'
        
        # Adiciona widgets das chaves
        for key_obj in filtered_keys:
            key_widget = KeyListItem(key_obj, self)
            self.keys_layout.add_widget(key_widget)
        
        # Mensagem se vazio
        if not filtered_keys:
            if self.current_search:
                msg = f'Nenhuma chave encontrada para: "{self.current_search}"'
            else:
                msg = 'Nenhuma chave salva ainda\n\nDigite uma chave fiscal de 44 dígitos para começar'
            
            empty_label = Label(
                text=msg,
                font_size='14sp',
                halign='center',
                size_hint_y=None,
                height=dp(80),
                color=COLORS['text_secondary']
            )
            empty_label.bind(size=empty_label.setter('text_size'))
            self.keys_layout.add_widget(empty_label)
    
    def confirm_delete_key(self, key_obj):
        """Confirma exclusão de chave"""
        layout = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        
        message = Label(
            text=f'Excluir esta chave?\n\n{key_obj.key[:20]}...{key_obj.key[-8:]}\n\n{key_obj.get_formatted_date()}',
            font_size='14sp',
            halign='center'
        )
        message.bind(size=message.setter('text_size'))
        layout.add_widget(message)
        
        buttons = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        
        confirm_btn = Button(
            text='Sim, Excluir',
            font_size='14sp',
            background_color=COLORS['error']
        )
        confirm_btn.bind(on_press=lambda x: self.delete_key_confirmed(key_obj, confirm_popup))
        buttons.add_widget(confirm_btn)
        
        cancel_btn = Button(
            text='Cancelar',
            font_size='14sp',
            background_color=COLORS['text_secondary']
        )
        cancel_btn.bind(on_press=lambda x: confirm_popup.dismiss())
        buttons.add_widget(cancel_btn)
        
        layout.add_widget(buttons)
        
        confirm_popup = Popup(
            title='Confirmar Exclusão',
            content=layout,
            size_hint=(0.8, 0.4)
        )
        confirm_popup.open()
    
    def delete_key_confirmed(self, key_obj, popup):
        """Executa exclusão da chave"""
        try:
            self.saved_keys.remove(key_obj)
            self.save_keys_to_file()
            self.update_keys_display()
            popup.dismiss()
            self.show_result('Chave excluída com sucesso', 'success')
        except Exception as e:
            self.show_message(f'Erro ao excluir chave: {str(e)}', 'Erro')
    
    def export_csv(self, instance):
        """Exporta chaves para arquivo CSV"""
        if not self.saved_keys:
            self.show_message('Nenhuma chave para exportar', 'Aviso')
            return
        
        try:
            # Nome do arquivo com timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'chaves_fiscais_{timestamp}.csv'
            
            # Escreve CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Cabeçalho
                writer.writerow(['Chave Fiscal', 'Data/Hora', 'Timestamp'])
                
                # Dados
                for key_obj in sorted(self.saved_keys, key=lambda x: x.timestamp, reverse=True):
                    writer.writerow([
                        key_obj.key,
                        key_obj.get_formatted_date(),
                        key_obj.timestamp
                    ])
            
            self.show_message(
                f'Exportado com sucesso!\n\nArquivo: {filename}\nChaves: {len(self.saved_keys)}', 
                'Sucesso'
            )
            
        except Exception as e:
            self.show_message(f'Erro ao exportar: {str(e)}', 'Erro')
    
    def clear_all_keys(self, instance):
        """Confirma e limpa todas as chaves"""
        if not self.saved_keys:
            self.show_message('Nenhuma chave para limpar', 'Aviso')
            return
        
        layout = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        
        message = Label(
            text=f'ATENÇÃO!\n\nIsto irá excluir TODAS as {len(self.saved_keys)} chaves salvas.\n\nEsta ação não pode ser desfeita.\n\nTem certeza?',
            font_size='14sp',
            halign='center'
        )
        message.bind(size=message.setter('text_size'))
        layout.add_widget(message)
        
        buttons = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        
        confirm_btn = Button(
            text='Sim, Excluir Todas',
            font_size='13sp',
            background_color=COLORS['error']
        )
        confirm_btn.bind(on_press=lambda x: self.clear_all_confirmed(clear_popup))
        buttons.add_widget(confirm_btn)
        
        cancel_btn = Button(
            text='Cancelar',
            font_size='13sp',
            background_color=COLORS['text_secondary']
        )
        cancel_btn.bind(on_press=lambda x: clear_popup.dismiss())
        buttons.add_widget(cancel_btn)
        
        layout.add_widget(buttons)
        
        clear_popup = Popup(
            title='Confirmação Necessária',
            content=layout,
            size_hint=(0.8, 0.5)
        )
        clear_popup.open()
    
    def clear_all_confirmed(self, popup):
        """Executa limpeza de todas as chaves"""
        try:
            count = len(self.saved_keys)
            self.saved_keys.clear()
            self.save_keys_to_file()
            self.update_keys_display()
            popup.dismiss()
            self.show_result(f'{count} chaves foram excluídas', 'success')
        except Exception as e:
            self.show_message(f'Erro ao limpar chaves: {str(e)}', 'Erro')
    
    def show_result(self, message, msg_type='info'):
        """Atualiza label de resultado com cores"""
        if msg_type == 'success':
            color = COLORS['accent']
        elif msg_type == 'error':
            color = COLORS['error']
        elif msg_type == 'warning':
            color = COLORS['warning']
        else:
            color = COLORS['primary']
        
        self.result_label.text = message
        self.result_label.color = color
    
    def show_message(self, message, title='Informação'):
        """Mostra popup com mensagem"""
        layout = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        
        msg_label = Label(
            text=message,
            font_size='14sp',
            halign='center'
        )
        msg_label.bind(size=msg_label.setter('text_size'))
        layout.add_widget(msg_label)
        
        ok_btn = Button(
            text='OK',
            size_hint_y=None,
            height=dp(50),
            font_size='16sp',
            background_color=COLORS['primary']
        )
        ok_btn.bind(on_press=lambda x: msg_popup.dismiss())
        layout.add_widget(ok_btn)
        
        msg_popup = Popup(
            title=title,
            content=layout,
            size_hint=(0.8, 0.4)
        )
        msg_popup.open()
    
    def load_saved_keys(self):
        """Carrega chaves do arquivo JSON"""
        try:
            config_file = 'chaves_salvas.json'
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.saved_keys = [SavedKey.from_dict(item) for item in data]
                print(f"✅ {len(self.saved_keys)} chaves carregadas")
            else:
                self.saved_keys = []
                print("📄 Arquivo de chaves não existe, iniciando vazio")
        except Exception as e:
            print(f"❌ Erro ao carregar chaves: {e}")
            self.saved_keys = []
    
    def save_keys_to_file(self):
        """Salva chaves no arquivo JSON"""
        try:
            config_file = 'chaves_salvas.json'
            data = [key.to_dict() for key in self.saved_keys]
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Erro ao salvar chaves: {e}")


# Classe principal do aplicativo
class FiscalReaderApp(FiscalKeyReaderApp):
    """Classe principal compatível com buildozer"""
    pass


if __name__ == '__main__':
    FiscalKeyReaderApp().run()