#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 LEITOR DE CUPONS FISCAIS - VERSÃO ANDROID SIMPLIFICADA
🐍 Desenvolvido com Kivy
📅 Outubro 2025
"""

import re
import json
import os
from datetime import datetime
from pathlib import Path

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
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.logger import Logger

class CupomFiscal:
    """Classe para representar um cupom fiscal"""
    def __init__(self, chave_acesso, data_leitura=None):
        self.chave_acesso = chave_acesso
        self.data_leitura = data_leitura or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.valido = self.validar_chave()
    
    def validar_chave(self):
        """Valida a chave de acesso do cupom fiscal"""
        if not self.chave_acesso or len(self.chave_acesso) != 44:
            return False
        
        if not self.chave_acesso.isdigit():
            return False
        
        # Validação do dígito verificador (algoritmo módulo 11)
        try:
            return self._calcular_dv() == int(self.chave_acesso[43])
        except:
            return False
    
    def _calcular_dv(self):
        """Calcula o dígito verificador da chave"""
        sequencia = "432987654329876543298765432987654329876543"
        soma = sum(int(self.chave_acesso[i]) * int(sequencia[i]) for i in range(43))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

class QRReaderApp(App):
    def __init__(self):
        super().__init__()
        self.cupons = []
        self.data_file = "cupons_android.json"
        
    def build(self):
        """Constrói a interface principal"""
        self.title = "📱 Leitor Cupons Fiscais"
        
        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Título
        title = Label(
            text='📱 LEITOR DE CUPONS FISCAIS',
            size_hint_y=None,
            height='48dp',
            font_size='20sp',
            bold=True
        )
        main_layout.add_widget(title)
        
        # Área de entrada de chave
        input_layout = BoxLayout(orientation='vertical', size_hint_y=None, height='120dp', spacing=5)
        
        input_label = Label(text='Digite a chave de acesso (44 dígitos):', size_hint_y=None, height='30dp')
        input_layout.add_widget(input_label)
        
        self.chave_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height='40dp',
            font_size='14sp',
            input_filter='int'
        )
        input_layout.add_widget(self.chave_input)
        
        # Botões
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing=10)
        
        btn_validar = Button(text='✅ Validar', on_press=self.validar_chave)
        btn_limpar = Button(text='🗑️ Limpar', on_press=self.limpar_campos)
        btn_exportar = Button(text='📤 Exportar JSON', on_press=self.exportar_json)
        
        btn_layout.add_widget(btn_validar)
        btn_layout.add_widget(btn_limpar)
        btn_layout.add_widget(btn_exportar)
        
        input_layout.add_widget(btn_layout)
        main_layout.add_widget(input_layout)
        
        # Área de resultados
        self.resultado_label = Label(
            text='Resultado aparecerá aqui...',
            size_hint_y=None,
            height='60dp',
            text_size=(None, None),
            halign='center'
        )
        main_layout.add_widget(self.resultado_label)
        
        # Lista de cupons
        lista_label = Label(text='📋 Histórico de Cupons:', size_hint_y=None, height='30dp')
        main_layout.add_widget(lista_label)
        
        # ScrollView para a lista
        scroll = ScrollView()
        self.cupons_layout = GridLayout(cols=1, size_hint_y=None, spacing=2)
        self.cupons_layout.bind(minimum_height=self.cupons_layout.setter('height'))
        scroll.add_widget(self.cupons_layout)
        main_layout.add_widget(scroll)
        
        # Carregar cupons salvos
        self.carregar_cupons()
        self.atualizar_lista()
        
        return main_layout
    
    def validar_chave(self, instance):
        """Valida a chave de acesso inserida"""
        chave = self.chave_input.text.strip()
        
        if not chave:
            self.mostrar_resultado("⚠️ Digite uma chave de acesso", "orange")
            return
        
        cupom = CupomFiscal(chave)
        
        if cupom.valido:
            self.cupons.append(cupom)
            self.salvar_cupons()
            self.atualizar_lista()
            self.mostrar_resultado(f"✅ Chave válida! Total: {len(self.cupons)} cupons", "green")
            self.chave_input.text = ""
        else:
            self.mostrar_resultado("❌ Chave inválida! Verifique os 44 dígitos", "red")
    
    def limpar_campos(self, instance):
        """Limpa os campos de entrada"""
        self.chave_input.text = ""
        self.mostrar_resultado("🗑️ Campos limpos", "blue")
    
    def mostrar_resultado(self, texto, cor):
        """Mostra o resultado na tela"""
        self.resultado_label.text = texto
        # Kivy usa formato RGBA para cores
        cores = {
            "green": [0, 1, 0, 1],
            "red": [1, 0, 0, 1], 
            "orange": [1, 0.5, 0, 1],
            "blue": [0, 0, 1, 1]
        }
        self.resultado_label.color = cores.get(cor, [0, 0, 0, 1])
    
    def atualizar_lista(self):
        """Atualiza a lista de cupons na tela"""
        self.cupons_layout.clear_widgets()
        
        for i, cupom in enumerate(reversed(self.cupons)):
            cupom_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
            
            # Texto do cupom
            chave_texto = f"{cupom.chave_acesso[:8]}...{cupom.chave_acesso[-8:]}"
            texto = f"{i+1:03d} | {chave_texto} | {cupom.data_leitura}"
            
            cupom_label = Label(
                text=texto,
                size_hint_x=0.8,
                text_size=(None, None),
                halign='left',
                font_size='12sp'
            )
            
            # Botão remover
            btn_remover = Button(
                text='🗑️',
                size_hint_x=0.2,
                size_hint_y=None,
                height='35dp'
            )
            btn_remover.bind(on_press=lambda x, idx=len(self.cupons)-1-i: self.remover_cupom(idx))
            
            cupom_layout.add_widget(cupom_label)
            cupom_layout.add_widget(btn_remover)
            self.cupons_layout.add_widget(cupom_layout)
    
    def remover_cupom(self, indice):
        """Remove um cupom da lista"""
        if 0 <= indice < len(self.cupons):
            self.cupons.pop(indice)
            self.salvar_cupons()
            self.atualizar_lista()
            self.mostrar_resultado(f"🗑️ Cupom removido! Total: {len(self.cupons)}", "blue")
    
    def exportar_json(self, instance):
        """Exporta os cupons para JSON"""
        if not self.cupons:
            self.mostrar_resultado("⚠️ Nenhum cupom para exportar", "orange")
            return
        
        try:
            dados = []
            for cupom in self.cupons:
                dados.append({
                    "chave_acesso": cupom.chave_acesso,
                    "data_leitura": cupom.data_leitura,
                    "valido": cupom.valido
                })
            
            arquivo = f"cupons_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # No Android, salvar na pasta de documentos da app
            if hasattr(self, 'user_data_dir'):
                caminho = os.path.join(self.user_data_dir, arquivo)
            else:
                caminho = arquivo
            
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
            
            self.mostrar_resultado(f"📤 Exportado: {arquivo}", "green")
            
        except Exception as e:
            self.mostrar_resultado(f"❌ Erro ao exportar: {str(e)}", "red")
    
    def salvar_cupons(self):
        """Salva os cupons em arquivo JSON"""
        try:
            dados = []
            for cupom in self.cupons:
                dados.append({
                    "chave_acesso": cupom.chave_acesso,
                    "data_leitura": cupom.data_leitura,
                    "valido": cupom.valido
                })
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            Logger.error(f"Erro ao salvar: {e}")
    
    def carregar_cupons(self):
        """Carrega os cupons do arquivo JSON"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                
                self.cupons = []
                for item in dados:
                    cupom = CupomFiscal(
                        item["chave_acesso"],
                        item["data_leitura"]
                    )
                    self.cupons.append(cupom)
                    
        except Exception as e:
            Logger.error(f"Erro ao carregar: {e}")
            self.cupons = []

if __name__ == '__main__':
    QRReaderApp().run()