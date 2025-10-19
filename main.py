#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Leitor de Cupons Fiscais - Versão Android Completa
Aplicação Kivy com todas as funcionalidades essenciais

Funcionalidades:
- Leitura de QR codes via câmera
- Upload de imagens com QR codes
- Validação de chaves fiscais brasileiras
- Armazenamento local das chaves
- Exportação para CSV
- Interface touch-friendly
- Busca nas chaves salvas
- Modo batch para leitura rápida

Autor: Convertido de Desktop para Android
Data: Dezembro 2024
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
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.switch import Switch
from kivy.uix.progressbar import ProgressBar
from kivy.utils import platform
import json
import re
import os
import csv
import threading
import time
from datetime import datetime

# Tentativa de importar bibliotecas para câmera e QR
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from pyzbar import pyzbar
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False

# Importações do Kivy para câmera
try:
    from kivy.uix.camera import Camera
    KIVY_CAMERA_AVAILABLE = True
except ImportError:
    KIVY_CAMERA_AVAILABLE = False

# Para Android - permissões
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])


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


class KeyItemWidget(BoxLayout):
    """Widget para exibir uma chave salva na lista"""
    
    def __init__(self, key_obj, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.key_obj = key_obj
        self.app_instance = app_instance
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 100
        self.spacing = 2
        
        # Layout principal da chave
        main_layout = BoxLayout(orientation='horizontal', spacing=5)
        
        # Informações da chave
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
        
        # Chave (truncada)
        key_text = f"🔑 {key_obj.key[:20]}...{key_obj.key[-8:]}"
        key_label = Label(
            text=key_text,
            font_size='13sp',
            size_hint_y=None,
            height=30,
            halign='left'
        )
        key_label.bind(size=key_label.setter('text_size'))
        info_layout.add_widget(key_label)
        
        # Data
        date_label = Label(
            text=f"📅 {key_obj.get_formatted_date()}",
            font_size='11sp',
            size_hint_y=None,
            height=25,
            halign='left',
            color=(0.7, 0.7, 0.7, 1)
        )
        date_label.bind(size=date_label.setter('text_size'))
        info_layout.add_widget(date_label)
        
        main_layout.add_widget(info_layout)
        
        # Botões de ação
        buttons_layout = BoxLayout(orientation='vertical', size_hint_x=0.3, spacing=2)
        
        copy_btn = Button(
            text='📋 Copiar',
            size_hint_y=None,
            height=30,
            font_size='11sp'
        )
        copy_btn.bind(on_press=self.copy_key)
        buttons_layout.add_widget(copy_btn)
        
        delete_btn = Button(
            text='🗑️ Excluir',
            size_hint_y=None,
            height=30,
            font_size='11sp'
        )
        delete_btn.bind(on_press=self.delete_key)
        buttons_layout.add_widget(delete_btn)
        
        main_layout.add_widget(buttons_layout)
        
        self.add_widget(main_layout)
        
        # Linha separadora
        separator = Label(text='─' * 50, size_hint_y=None, height=10, font_size='10sp')
        self.add_widget(separator)
    
    def copy_key(self, instance):
        """Copia chave para área de transferência"""
        try:
            # No Android, usa clipboard do Kivy
            from kivy.core.clipboard import Clipboard
            Clipboard.copy(self.key_obj.key)
            
            # Feedback visual
            instance.text = '✅ Copiado!'
            instance.disabled = True
            Clock.schedule_once(lambda dt: self.restore_copy_button(instance), 2)
            
            self.app_instance.show_message('Chave copiada para área de transferência!', 'Sucesso')
            
        except Exception as e:
            self.app_instance.show_message(f'Erro ao copiar: {str(e)}', 'Erro')
    
    def restore_copy_button(self, button):
        """Restaura botão de cópia"""
        button.text = '📋 Copiar'
        button.disabled = False
    
    def delete_key(self, instance):
        """Exclui chave após confirmação"""
        self.app_instance.confirm_delete_key(self.key_obj)


class CameraWidget(BoxLayout):
    """Widget personalizado para câmera com controles"""
    
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app_instance = app_instance
        self.orientation = 'vertical'
        self.is_scanning = False
        
        if KIVY_CAMERA_AVAILABLE:
            # Câmera Kivy
            self.camera = Camera(play=True, resolution=(640, 480))
            self.add_widget(self.camera)
            
            # Botões de controle
            controls = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=5)
            
            capture_btn = Button(text='📸 Capturar QR', size_hint_x=0.4, font_size='14sp')
            capture_btn.bind(on_press=self.capture_image)
            controls.add_widget(capture_btn)
            
            auto_btn = Button(text='🔄 Auto Scan', size_hint_x=0.3, font_size='14sp')
            auto_btn.bind(on_press=self.toggle_auto_scan)
            controls.add_widget(auto_btn)
            
            close_btn = Button(text='❌ Fechar', size_hint_x=0.3, font_size='14sp')
            close_btn.bind(on_press=self.close_camera)
            controls.add_widget(close_btn)
            
            self.add_widget(controls)
            
            # Status
            self.status_label = Label(
                text='📷 Câmera ativa - Posicione o QR code do cupom fiscal', 
                size_hint_y=None, 
                height=50,
                font_size='13sp',
                halign='center'
            )
            self.status_label.bind(size=self.status_label.setter('text_size'))
            self.add_widget(self.status_label)
            
            # Auto scan se disponível
            if CV2_AVAILABLE and PYZBAR_AVAILABLE:
                self.start_auto_scan()
        else:
            error_label = Label(
                text='❌ Câmera não disponível\n\nPara usar a câmera:\n• Instale: pip install kivy[base]\n• Permita acesso à câmera no Android',
                font_size='14sp',
                halign='center'
            )
            error_label.bind(size=error_label.setter('text_size'))
            self.add_widget(error_label)
    
    def start_auto_scan(self):
        """Inicia escaneamento automático"""
        self.is_scanning = True
        Clock.schedule_interval(self.auto_scan_frame, 1.0)  # Verifica a cada segundo
    
    def stop_auto_scan(self):
        """Para escaneamento automático"""
        self.is_scanning = False
        Clock.unschedule(self.auto_scan_frame)
    
    def toggle_auto_scan(self, instance):
        """Liga/desliga escaneamento automático"""
        if self.is_scanning:
            self.stop_auto_scan()
            instance.text = '▶️ Iniciar Auto'
            self.status_label.text = '⏸️ Auto scan pausado - Use capturar manual'
        else:
            self.start_auto_scan()
            instance.text = '⏸️ Parar Auto'
            self.status_label.text = '🔄 Auto scan ativo - Posicione o QR code'
    
    def auto_scan_frame(self, dt):
        """Captura e processa frame automaticamente"""
        if not self.is_scanning:
            return False
        
        try:
            filename = f'temp_auto_scan.png'
            if hasattr(self.camera, 'export_to_png'):
                self.camera.export_to_png(filename)
                Clock.schedule_once(lambda dt: self.process_auto_capture(filename), 0.1)
        except Exception as e:
            print(f"Erro no auto scan: {e}")
        
        return True
    
    def process_auto_capture(self, filename):
        """Processa captura automática"""
        self.process_image(filename, auto_mode=True)
    
    def capture_image(self, instance):
        """Captura imagem manualmente"""
        if hasattr(self.camera, 'export_to_png'):
            filename = f'qr_capture_{int(time.time())}.png'
            self.camera.export_to_png(filename)
            Clock.schedule_once(lambda dt: self.process_image(filename), 0.1)
    
    def process_image(self, filename, auto_mode=False):
        """Processa imagem capturada para detectar QR codes"""
        if not CV2_AVAILABLE or not PYZBAR_AVAILABLE:
            if not auto_mode:
                self.app_instance.show_message(
                    'Bibliotecas necessárias não instaladas:\n• pip install opencv-python\n• pip install pyzbar', 
                    'Aviso'
                )
            return
        
        try:
            # Carrega imagem
            import cv2
            from pyzbar import pyzbar
            
            if not os.path.exists(filename):
                return
            
            image = cv2.imread(filename)
            if image is not None:
                # Detecta QR codes
                qr_codes = pyzbar.decode(image)
                if qr_codes:
                    data = qr_codes[0].data.decode('utf-8')
                    
                    # Para auto scan, evita processar o mesmo QR repetidamente
                    if auto_mode:
                        if hasattr(self, 'last_qr_data') and self.last_qr_data == data:
                            return
                        self.last_qr_data = data
                    
                    self.app_instance.process_qr_data(data)
                    
                    if not auto_mode:  # Só fecha em modo manual
                        Clock.schedule_once(lambda dt: self.close_camera(None), 1)
                    else:
                        self.status_label.text = f'✅ QR detectado! Processando...'
                        Clock.schedule_once(lambda dt: self.reset_status(), 3)
                else:
                    if not auto_mode:
                        self.status_label.text = '❌ Nenhum QR code encontrado - Tente novamente'
            
            # Remove arquivo temporário
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except:
                    pass
                
        except Exception as e:
            if not auto_mode:
                self.app_instance.show_message(f'Erro ao processar imagem: {str(e)}', 'Erro')
    
    def reset_status(self):
        """Reseta status da câmera"""
        if self.is_scanning:
            self.status_label.text = '🔄 Auto scan ativo - Posicione o QR code'
    
    def close_camera(self, instance):
        """Fecha câmera"""
        self.stop_auto_scan()
        self.app_instance.close_camera_popup()


class FiscalKeyReaderApp(App):
    def build(self):
        self.saved_keys = []
        self.current_search = ""
        self.batch_mode = False
        self.batch_counter = 0
        self.camera_popup = None
        self.last_key_read = ""
        
        # Carrega dados salvos
        self.load_saved_keys()
        
        # Layout principal
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Título
        title = Label(
            text='📊 Mercado em Números\nLeitor de Cupons Fiscais',
            size_hint_y=None,
            height=80,
            font_size='16sp',
            halign='center'
        )
        title.bind(size=title.setter('text_size'))
        layout.add_widget(title)
        
        # Accordion para organizar funcionalidades
        accordion = Accordion(orientation='vertical')
        
        # === SEÇÃO: ENTRADA DE DADOS ===
        input_item = AccordionItem(title='📝 Entrada de Dados', min_space=250)
        input_layout = BoxLayout(orientation='vertical', padding=5, spacing=10)
        
        # Campo de entrada
        self.key_input = TextInput(
            hint_text='Digite ou cole a chave fiscal (44 dígitos)',
            multiline=False,
            size_hint_y=None,
            height=50,
            font_size='14sp'
        )
        input_layout.add_widget(self.key_input)
        
        # Botões de ação
        buttons_layout = GridLayout(cols=2, spacing=5, size_hint_y=None, height=120)
        
        validate_btn = Button(text='✅ Validar\nChave', font_size='13sp')
        validate_btn.bind(on_press=self.validate_key)
        buttons_layout.add_widget(validate_btn)
        
        camera_btn = Button(text='📷 Câmera\nQR Code', font_size='13sp')
        camera_btn.bind(on_press=self.open_camera)
        buttons_layout.add_widget(camera_btn)
        
        upload_btn = Button(text='🖼️ Upload\nImagem', font_size='13sp')
        upload_btn.bind(on_press=self.upload_image)
        buttons_layout.add_widget(upload_btn)
        
        clear_btn = Button(text='🧹 Limpar\nCampo', font_size='13sp')
        clear_btn.bind(on_press=self.clear_input)
        buttons_layout.add_widget(clear_btn)
        
        input_layout.add_widget(buttons_layout)
        
        # Resultado da validação
        self.result_label = Label(
            text='Digite uma chave fiscal ou use a câmera para escanear QR code',
            text_size=(None, None),
            size_hint_y=None,
            height=80,
            font_size='13sp',
            halign='center'
        )
        self.result_label.bind(size=self.result_label.setter('text_size'))
        input_layout.add_widget(self.result_label)
        
        input_item.add_widget(input_layout)
        accordion.add_widget(input_item)
        
        # === SEÇÃO: CHAVES SALVAS ===
        saved_item = AccordionItem(title='💾 Chaves Salvas', min_space=350)
        saved_layout = BoxLayout(orientation='vertical', padding=5, spacing=10)
        
        # Controles superiores
        controls_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        
        # Contador e modo batch
        self.keys_count_label = Label(text='Chaves: 0', size_hint_x=0.4, font_size='14sp')
        controls_layout.add_widget(self.keys_count_label)
        
        batch_label = Label(text='Batch:', size_hint_x=0.3, font_size='12sp')
        controls_layout.add_widget(batch_label)
        
        self.batch_switch = Switch(size_hint_x=0.3)
        self.batch_switch.bind(active=self.toggle_batch_mode)
        controls_layout.add_widget(self.batch_switch)
        
        saved_layout.add_widget(controls_layout)
        
        # Campo de busca
        self.search_input = TextInput(
            hint_text='🔍 Buscar nas chaves salvas...',
            multiline=False,
            size_hint_y=None,
            height=40,
            font_size='14sp'
        )
        self.search_input.bind(text=self.on_search_change)
        saved_layout.add_widget(self.search_input)
        
        # Lista de chaves (ScrollView)
        scroll = ScrollView()
        self.keys_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        self.keys_layout.bind(minimum_height=self.keys_layout.setter('height'))
        scroll.add_widget(self.keys_layout)
        saved_layout.add_widget(scroll)
        
        # Botões de ação para chaves salvas
        actions_layout = GridLayout(cols=2, spacing=5, size_hint_y=None, height=80)
        
        export_btn = Button(text='📤 Exportar\nCSV', font_size='13sp')
        export_btn.bind(on_press=self.export_csv)
        actions_layout.add_widget(export_btn)
        
        clear_all_btn = Button(text='🗑️ Limpar\nTodas', font_size='13sp')
        clear_all_btn.bind(on_press=self.clear_all_keys)
        actions_layout.add_widget(clear_all_btn)
        
        saved_layout.add_widget(actions_layout)
        
        saved_item.add_widget(saved_layout)
        accordion.add_widget(saved_item)
        
        # === SEÇÃO: CONFIGURAÇÕES ===
        config_item = AccordionItem(title='⚙️ Configurações & Info', min_space=200)
        config_layout = BoxLayout(orientation='vertical', padding=5, spacing=10)
        
        # Status das bibliotecas
        status_text = f"""
📱 Status do Sistema:
• OpenCV: {'✅ Instalado' if CV2_AVAILABLE else '❌ Não instalado'}
• pyzbar: {'✅ Instalado' if PYZBAR_AVAILABLE else '❌ Não instalado'}
• Câmera Kivy: {'✅ Disponível' if KIVY_CAMERA_AVAILABLE else '❌ Não disponível'}

🔧 Funcionalidades:
• ✅ Validação de chaves fiscais
• {'✅' if KIVY_CAMERA_AVAILABLE else '❌'} Câmera para QR codes
• {'✅' if CV2_AVAILABLE and PYZBAR_AVAILABLE else '❌'} Processamento de QR
• ✅ Armazenamento local
• ✅ Exportação CSV
• ✅ Busca nas chaves

📊 Estatísticas:
• Chaves salvas: {len(self.saved_keys)}
• Modo batch: {'Ativo' if self.batch_mode else 'Inativo'}
        """
        
        status_label = Label(
            text=status_text.strip(),
            text_size=(None, None),
            font_size='11sp',
            halign='left'
        )
        status_label.bind(size=status_label.setter('text_size'))
        config_layout.add_widget(status_label)
        
        # Botão para instalar dependências
        if not CV2_AVAILABLE or not PYZBAR_AVAILABLE:
            install_btn = Button(
                text='📦 Como Instalar Dependências',
                size_hint_y=None,
                height=50,
                font_size='13sp'
            )
            install_btn.bind(on_press=self.show_install_instructions)
            config_layout.add_widget(install_btn)
        
        config_item.add_widget(config_layout)
        accordion.add_widget(config_item)
        
        layout.add_widget(accordion)
        
        # Atualiza interface inicial
        self.update_keys_display()
        
        return layout
    
    def validate_access_key(self, key):
        """
        Valida chave de acesso brasileira usando algoritmo de dígito verificador
        Baseado na validação do app original
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
            self.show_result('❌ Digite uma chave fiscal', 'error')
            return
        
        # Remove caracteres não numéricos
        key = re.sub(r'[^0-9]', '', key)
        
        if len(key) != 44:
            self.show_result(f'❌ Chave deve ter 44 dígitos (atual: {len(key)})', 'error')
            return
        
        if self.validate_access_key(key):
            # Verifica duplicata
            if any(item.key == key for item in self.saved_keys):
                self.show_result('⚠️ Esta chave já foi salva anteriormente', 'warning')
                return
            
            # Salva chave válida
            new_key = SavedKey(key)
            self.saved_keys.insert(0, new_key)
            self.save_keys_to_file()
            
            if self.batch_mode:
                self.batch_counter += 1
                self.show_result(f'✅ Chave {self.batch_counter} salva!', 'success')
            else:
                self.show_result('✅ Chave fiscal válida e salva!', 'success')
            
            self.clear_input(None)
            self.update_keys_display()
        else:
            self.show_result('❌ Chave fiscal inválida', 'error')
    
    def process_qr_data(self, data):
        """
        Processa dados de QR code capturado
        Extrai chave fiscal e valida
        """
        # Extrai chave fiscal do QR (busca padrão p=44digitos)
        match = re.search(r'p=([0-9]{44})', data)
        
        if not match:
            self.show_result('❌ QR Code não contém chave fiscal válida', 'error')
            return
        
        key = match.group(1)
        
        # Valida chave
        if not self.validate_access_key(key):
            self.show_result('❌ Chave fiscal inválida no QR Code', 'error')
            return
        
        # Verifica duplicata
        if any(item.key == key for item in self.saved_keys):
            self.show_result('⚠️ Este cupom já foi lido anteriormente', 'warning')
            return
        
        # Salva chave válida
        new_key = SavedKey(key)
        self.saved_keys.insert(0, new_key)
        self.last_key_read = key
        self.save_keys_to_file()
        
        if self.batch_mode:
            self.batch_counter += 1
            self.show_result(f'✅ QR {self.batch_counter} processado com sucesso!', 'success')
        else:
            self.show_result('✅ QR Code lido e chave salva com sucesso!', 'success')
        
        self.update_keys_display()
    
    def open_camera(self, instance):
        """Abre popup da câmera"""
        if self.camera_popup:
            return
        
        camera_widget = CameraWidget(self)
        self.camera_popup = Popup(
            title='📷 Leitura de QR Code',
            content=camera_widget,
            size_hint=(0.9, 0.8),
            auto_dismiss=False
        )
        self.camera_popup.open()
    
    def close_camera_popup(self):
        """Fecha popup da câmera"""
        if self.camera_popup:
            self.camera_popup.dismiss()
            self.camera_popup = None
    
    def upload_image(self, instance):
        """Abre seletor de arquivo para upload de imagem"""
        if not CV2_AVAILABLE or not PYZBAR_AVAILABLE:
            self.show_message(
                'Funcionalidade não disponível!\n\nInstale as dependências:\n• pip install opencv-python\n• pip install pyzbar',
                'Bibliotecas Necessárias'
            )
            return
        
        # Layout do seletor
        layout = BoxLayout(orientation='vertical', spacing=10)
        
        # Instruções
        instructions = Label(
            text='📁 Selecione uma imagem contendo QR code de cupom fiscal',
            size_hint_y=None,
            height=50,
            font_size='14sp',
            halign='center'
        )
        instructions.bind(size=instructions.setter('text_size'))
        layout.add_widget(instructions)
        
        # File chooser
        filechooser = FileChooserIconView(
            filters=['*.png', '*.jpg', '*.jpeg', '*.bmp']
        )
        layout.add_widget(filechooser)
        
        # Botões
        buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        select_btn = Button(text='✅ Processar Imagem')
        select_btn.bind(on_press=lambda x: self.process_selected_image(filechooser.selection, upload_popup))
        buttons.add_widget(select_btn)
        
        cancel_btn = Button(text='❌ Cancelar')
        cancel_btn.bind(on_press=lambda x: upload_popup.dismiss())
        buttons.add_widget(cancel_btn)
        
        layout.add_widget(buttons)
        
        # Popup
        upload_popup = Popup(
            title='📤 Upload de Imagem',
            content=layout,
            size_hint=(0.9, 0.8)
        )
        upload_popup.open()
    
    def process_selected_image(self, selection, popup):
        """Processa imagem selecionada"""
        if not selection:
            self.show_message('Selecione um arquivo de imagem', 'Aviso')
            return
        
        file_path = selection[0]
        popup.dismiss()
        
        try:
            import cv2
            from pyzbar import pyzbar
            
            # Carrega imagem
            image = cv2.imread(file_path)
            if image is None:
                self.show_message('Erro ao carregar imagem. Verifique o formato.', 'Erro')
                return
            
            # Detecta QR codes
            qr_codes = pyzbar.decode(image)
            
            if qr_codes:
                data = qr_codes[0].data.decode('utf-8')
                self.process_qr_data(data)
            else:
                self.show_message('Nenhum QR Code encontrado na imagem', 'Aviso')
                
        except Exception as e:
            self.show_message(f'Erro ao processar imagem: {str(e)}', 'Erro')
    
    def clear_input(self, instance):
        """Limpa campo de entrada"""
        self.key_input.text = ''
        self.show_result('Campo limpo - Digite nova chave ou use câmera', 'info')
    
    def toggle_batch_mode(self, instance, value):
        """Liga/desliga modo batch"""
        self.batch_mode = value
        if value:
            self.batch_counter = 0
            self.show_result('🔄 Modo Batch ATIVO - Leitura rápida habilitada', 'info')
        else:
            if self.batch_counter > 0:
                self.show_result(f'✅ Modo Batch finalizado - {self.batch_counter} chaves processadas', 'success')
            else:
                self.show_result('ℹ️ Modo Batch desativado', 'info')
    
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
            self.keys_count_label.text = f'Chaves: {filtered}/{total}'
        else:
            self.keys_count_label.text = f'Chaves: {total}'
        
        # Adiciona widgets das chaves
        for key_obj in filtered_keys:
            key_widget = KeyItemWidget(key_obj, self)
            self.keys_layout.add_widget(key_widget)
        
        # Mensagem se vazio
        if not filtered_keys:
            if self.current_search:
                msg = f'Nenhuma chave encontrada para: "{self.current_search}"'
            else:
                msg = 'Nenhuma chave salva ainda\n\nUse a câmera ou digite uma chave fiscal para começar'
            
            empty_label = Label(
                text=msg,
                font_size='14sp',
                halign='center',
                size_hint_y=None,
                height=100
            )
            empty_label.bind(size=empty_label.setter('text_size'))
            self.keys_layout.add_widget(empty_label)
    
    def confirm_delete_key(self, key_obj):
        """Confirma exclusão de chave"""
        layout = BoxLayout(orientation='vertical', spacing=20)
        
        message = Label(
            text=f'Excluir esta chave?\n\n🔑 {key_obj.key[:20]}...{key_obj.key[-8:]}\n📅 {key_obj.get_formatted_date()}',
            font_size='14sp',
            halign='center'
        )
        message.bind(size=message.setter('text_size'))
        layout.add_widget(message)
        
        buttons = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        
        confirm_btn = Button(text='✅ Sim, Excluir', font_size='14sp')
        confirm_btn.bind(on_press=lambda x: self.delete_key_confirmed(key_obj, confirm_popup))
        buttons.add_widget(confirm_btn)
        
        cancel_btn = Button(text='❌ Cancelar', font_size='14sp')
        cancel_btn.bind(on_press=lambda x: confirm_popup.dismiss())
        buttons.add_widget(cancel_btn)
        
        layout.add_widget(buttons)
        
        confirm_popup = Popup(
            title='🗑️ Confirmar Exclusão',
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
            self.show_message('Chave excluída com sucesso', 'Sucesso')
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
            
            # Diretório de saída (Android-friendly)
            if platform == 'android':
                from android.storage import primary_external_storage_path
                export_dir = primary_external_storage_path()
                filepath = os.path.join(export_dir, filename)
            else:
                filepath = filename
            
            # Escreve CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
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
            
            self.show_message(f'✅ Exportado com sucesso!\n\n📁 {filepath}\n📊 {len(self.saved_keys)} chaves exportadas', 'Sucesso')
            
        except Exception as e:
            self.show_message(f'Erro ao exportar: {str(e)}', 'Erro')
    
    def clear_all_keys(self, instance):
        """Confirma e limpa todas as chaves"""
        if not self.saved_keys:
            self.show_message('Nenhuma chave para limpar', 'Aviso')
            return
        
        layout = BoxLayout(orientation='vertical', spacing=20)
        
        message = Label(
            text=f'⚠️ ATENÇÃO!\n\nIsto irá excluir TODAS as {len(self.saved_keys)} chaves salvas.\n\nEsta ação não pode ser desfeita.\n\nTem certeza?',
            font_size='14sp',
            halign='center'
        )
        message.bind(size=message.setter('text_size'))
        layout.add_widget(message)
        
        buttons = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        
        confirm_btn = Button(text='🗑️ Sim, Excluir Todas', font_size='13sp')
        confirm_btn.bind(on_press=lambda x: self.clear_all_confirmed(clear_popup))
        buttons.add_widget(confirm_btn)
        
        cancel_btn = Button(text='❌ Cancelar', font_size='13sp')
        cancel_btn.bind(on_press=lambda x: clear_popup.dismiss())
        buttons.add_widget(cancel_btn)
        
        layout.add_widget(buttons)
        
        clear_popup = Popup(
            title='⚠️ Confirmação Necessária',
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
            self.show_message(f'✅ {count} chaves foram excluídas', 'Sucesso')
        except Exception as e:
            self.show_message(f'Erro ao limpar chaves: {str(e)}', 'Erro')
    
    def show_install_instructions(self, instance):
        """Mostra instruções de instalação"""
        instructions = """
📦 Como Instalar Dependências:

🔧 Para funcionalidade completa, instale:

1️⃣ OpenCV (processamento de imagem):
   pip install opencv-python

2️⃣ pyzbar (decodificação QR):
   pip install pyzbar

📱 No Android/Termux:
   pkg install python-opencv
   pkg install zbar
   pip install pyzbar

✅ Após instalar, reinicie o app para usar:
   • Upload de imagens com QR
   • Processamento automático na câmera
   • Detecção avançada de QR codes

ℹ️ O app funciona sem essas bibliotecas, mas com funcionalidade limitada.
        """
        
        layout = BoxLayout(orientation='vertical', spacing=10)
        
        text_label = Label(
            text=instructions.strip(),
            font_size='12sp',
            halign='left'
        )
        text_label.bind(size=text_label.setter('text_size'))
        layout.add_widget(text_label)
        
        close_btn = Button(text='✅ Entendi', size_hint_y=None, height=50)
        close_btn.bind(on_press=lambda x: install_popup.dismiss())
        layout.add_widget(close_btn)
        
        install_popup = Popup(
            title='📦 Instruções de Instalação',
            content=layout,
            size_hint=(0.9, 0.8)
        )
        install_popup.open()
    
    def show_result(self, message, msg_type='info'):
        """Atualiza label de resultado com cores"""
        if msg_type == 'success':
            color = [0, 0.8, 0, 1]  # Verde
        elif msg_type == 'error':
            color = [0.8, 0, 0, 1]  # Vermelho  
        elif msg_type == 'warning':
            color = [0.8, 0.6, 0, 1]  # Laranja
        else:
            color = [0, 0, 0.8, 1]  # Azul
        
        self.result_label.text = message
        self.result_label.color = color
    
    def show_message(self, message, title='Informação'):
        """Mostra popup com mensagem"""
        layout = BoxLayout(orientation='vertical', spacing=20)
        
        msg_label = Label(
            text=message,
            font_size='14sp',
            halign='center'
        )
        msg_label.bind(size=msg_label.setter('text_size'))
        layout.add_widget(msg_label)
        
        ok_btn = Button(text='✅ OK', size_hint_y=None, height=50)
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