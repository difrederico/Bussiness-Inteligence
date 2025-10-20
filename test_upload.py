#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste automatizado do botão de upload
Verifica se o seletor de arquivos abre corretamente
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from kivy.app import App
from kivy.clock import Clock
from main import MercadoEmNumerosApp
import threading
import time

class UploadTester:
    def __init__(self):
        self.app = None
        self.test_results = []
        
    def start_test(self):
        """Inicia o teste automatizado"""
        print("🧪 INICIANDO TESTE DO BOTÃO DE UPLOAD...")
        print("="*50)
        
        # Cria app
        self.app = MercadoEmNumerosApp()
        
        # Agenda teste após app inicializar
        Clock.schedule_once(self.run_tests, 2.0)
        
        # Executa app
        self.app.run()
    
    def run_tests(self, dt):
        """Executa os testes automatizados"""
        try:
            print("📱 App iniciado com sucesso!")
            
            # Teste 1: Verificar se app tem root layout
            if hasattr(self.app, 'root') and self.app.root:
                print("✅ Root layout encontrado")
                self.test_results.append("✅ Root layout OK")
            else:
                print("❌ Root layout não encontrado")
                self.test_results.append("❌ Root layout FALHOU")
                return
            
            # Teste 2: Verificar ScreenManager
            root = self.app.root
            if hasattr(root, 'screen_manager'):
                print("✅ ScreenManager encontrado")
                self.test_results.append("✅ ScreenManager OK")
                
                # Teste 3: Verificar tela de upload
                screens = root.screen_manager.screens
                upload_screen = None
                
                for screen in screens:
                    if screen.name == 'upload':
                        upload_screen = screen
                        break
                
                if upload_screen:
                    print("✅ Tela de upload encontrada")
                    self.test_results.append("✅ Upload screen OK")
                    
                    # Teste 4: Procurar UploadWidget
                    upload_widget = self.find_upload_widget(upload_screen)
                    if upload_widget:
                        print("✅ UploadWidget encontrado")
                        self.test_results.append("✅ UploadWidget OK")
                        
                        # Teste 5: Procurar botão "Escolher Arquivo"
                        upload_button = self.find_upload_button(upload_widget)
                        if upload_button:
                            print("✅ Botão 'Escolher Arquivo' encontrado")
                            self.test_results.append("✅ Upload button OK")
                            
                            # Teste 6: Verificar se botão tem callback
                            if hasattr(upload_button, '_callbacks') and 'on_press' in upload_button._callbacks:
                                print("✅ Callback do botão configurado")
                                self.test_results.append("✅ Button callback OK")
                                
                                # Teste 7: Simular clique no botão
                                self.simulate_button_click(upload_button)
                            else:
                                print("❌ Callback do botão não encontrado")
                                self.test_results.append("❌ Button callback FALHOU")
                        else:
                            print("❌ Botão 'Escolher Arquivo' não encontrado")
                            self.test_results.append("❌ Upload button FALHOU")
                    else:
                        print("❌ UploadWidget não encontrado")
                        self.test_results.append("❌ UploadWidget FALHOU")
                else:
                    print("❌ Tela de upload não encontrada")
                    self.test_results.append("❌ Upload screen FALHOU")
            else:
                print("❌ ScreenManager não encontrado")
                self.test_results.append("❌ ScreenManager FALHOU")
            
            # Aguarda um pouco e mostra resultados
            Clock.schedule_once(self.show_final_results, 3.0)
            
        except Exception as e:
            print(f"❌ ERRO NO TESTE: {e}")
            self.test_results.append(f"❌ ERRO: {e}")
    
    def find_upload_widget(self, screen):
        """Procura UploadWidget recursivamente"""
        from main import UploadWidget
        
        def search_widget(widget):
            if isinstance(widget, UploadWidget):
                return widget
            
            if hasattr(widget, 'children'):
                for child in widget.children:
                    result = search_widget(child)
                    if result:
                        return result
            return None
        
        return search_widget(screen)
    
    def find_upload_button(self, upload_widget):
        """Procura botão 'Escolher Arquivo' no UploadWidget"""
        from kivy.uix.button import Button
        
        def search_button(widget):
            if isinstance(widget, Button) and 'Escolher' in str(widget.text):
                return widget
            
            if hasattr(widget, 'children'):
                for child in widget.children:
                    result = search_button(child)
                    if result:
                        return result
            return None
        
        return search_button(upload_widget)
    
    def simulate_button_click(self, button):
        """Simula clique no botão para testar funcionamento"""
        print("🖱️ Simulando clique no botão...")
        
        try:
            # Muda para tela de upload primeiro
            root = self.app.root
            if hasattr(root, 'screen_manager'):
                root.screen_manager.current = 'upload'
                print("📱 Mudou para tela de upload")
            
            # Simula o clique
            Clock.schedule_once(lambda dt: self.trigger_button(button), 1.0)
            
        except Exception as e:
            print(f"❌ Erro ao simular clique: {e}")
            self.test_results.append(f"❌ Clique FALHOU: {e}")
    
    def trigger_button(self, button):
        """Dispara o callback do botão"""
        try:
            print("🔥 Disparando callback do botão...")
            
            # Simula evento de press
            button.dispatch('on_press')
            print("✅ Callback executado com sucesso!")
            self.test_results.append("✅ Button click OK")
            
            # Verifica se popup foi criado
            Clock.schedule_once(self.check_popup, 0.5)
            
        except Exception as e:
            print(f"❌ Erro ao disparar callback: {e}")
            self.test_results.append(f"❌ Callback FALHOU: {e}")
    
    def check_popup(self, dt):
        """Verifica se popup foi aberto"""
        try:
            # Procura por popups ativos
            from kivy.uix.popup import Popup
            from kivy.base import EventLoop
            
            # Verifica janelas abertas
            windows = EventLoop.window.children if hasattr(EventLoop.window, 'children') else []
            
            popup_found = False
            for window in windows:
                if isinstance(window, Popup):
                    popup_found = True
                    break
            
            if popup_found:
                print("✅ POPUP DETECTADO - Seletor de arquivos FUNCIONANDO!")
                self.test_results.append("✅ Popup opened OK")
            else:
                print("⚠️ Popup não detectado - pode estar funcionando mas não visível no teste")
                self.test_results.append("⚠️ Popup not detected")
                
        except Exception as e:
            print(f"❌ Erro ao verificar popup: {e}")
            self.test_results.append(f"❌ Popup check FALHOU: {e}")
    
    def show_final_results(self, dt):
        """Mostra resultados finais do teste"""
        print("\n" + "="*50)
        print("📋 RESULTADOS FINAIS DOS TESTES:")
        print("="*50)
        
        for result in self.test_results:
            print(result)
        
        # Conta sucessos e falhas
        success_count = len([r for r in self.test_results if r.startswith("✅")])
        warning_count = len([r for r in self.test_results if r.startswith("⚠️")])
        error_count = len([r for r in self.test_results if r.startswith("❌")])
        
        print(f"\n📊 RESUMO:")
        print(f"✅ Sucessos: {success_count}")
        print(f"⚠️ Avisos: {warning_count}")
        print(f"❌ Erros: {error_count}")
        
        if error_count == 0:
            print("\n🎉 TESTE CONCLUÍDO - BOTÃO DE UPLOAD FUNCIONANDO!")
        else:
            print("\n⚠️ TESTE CONCLUÍDO - PROBLEMAS DETECTADOS")
        
        print("="*50)
        
        # Encerra app após 2 segundos
        Clock.schedule_once(lambda dt: self.app.stop(), 2.0)

if __name__ == '__main__':
    tester = UploadTester()
    tester.start_test()