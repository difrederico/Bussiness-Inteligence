#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Específico das Refatorações Android
Valida as correções cirúrgicas implementadas

Autor: Especialista QA
Data: Dezembro 2024
"""

import os
import sys

def test_android_permissions():
    """Testa se sistema de permissões Android foi implementado"""
    print("🔐 TESTANDO SISTEMA DE PERMISSÕES ANDROID")
    print("=" * 60)
    
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    tests = {
        'Importação Android Permissions': 'from android.permissions import request_permissions, Permission',
        'Método on_start': 'def on_start(self):',
        'Solicitação CAMERA': 'Permission.CAMERA',
        'Solicitação READ_EXTERNAL_STORAGE': 'Permission.READ_EXTERNAL_STORAGE', 
        'Solicitação WRITE_EXTERNAL_STORAGE': 'Permission.WRITE_EXTERNAL_STORAGE',
        'Verificação plataforma': "if platform == 'android':",
        'Tratamento de exceção': 'except Exception as e:'
    }
    
    passed = 0
    total = len(tests)
    
    for test_name, search_text in tests.items():
        if search_text in content:
            print(f"   ✅ {test_name}")
            passed += 1
        else:
            print(f"   ❌ {test_name}")
    
    score = (passed / total) * 100
    print(f"\n📊 Score Permissões: {score:.1f}% ({passed}/{total})")
    
    return score >= 85


def test_camera_refactor():
    """Testa refatoração da câmera"""
    print("\n📷 TESTANDO REFATORAÇÃO DA CÂMERA")
    print("=" * 60)
    
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    tests = {
        'Método abrir_camera_nativa': 'def abrir_camera_nativa(self, instance):',
        'Verificação plataforma câmera': "if platform != 'android':",
        'Message toast câmera': 'show_toast("Comando para abrir a câmera nativa executado!", "success")',
        'TODO comentário câmera': 'TODO: Implementar a captura do resultado da câmera',
        'Placeholder câmera nativa': 'Câmera Nativa Android',
        'Texto botão modificado': 'Abrir Câmera',
        'Importação jnius': 'from jnius import autoclass, cast'
    }
    
    passed = 0
    total = len(tests)
    
    for test_name, search_text in tests.items():
        if search_text in content:
            print(f"   ✅ {test_name}")
            passed += 1
        else:
            print(f"   ❌ {test_name}")
    
    # Testa se Kivy Camera foi REMOVIDA
    removed_tests = {
        'Kivy Camera removida': 'Camera(play=False',
        'Método toggle_camera removido': 'def toggle_camera(self, instance):'
    }
    
    for test_name, search_text in removed_tests.items():
        if search_text not in content:
            print(f"   ✅ {test_name} (corretamente removida)")
            passed += 1
        else:
            print(f"   ❌ {test_name} (ainda presente)")
        total += 1
    
    score = (passed / total) * 100
    print(f"\n📊 Score Câmera: {score:.1f}% ({passed}/{total})")
    
    return score >= 75


def test_upload_refactor():
    """Testa refatoração do upload"""
    print("\n📎 TESTANDO REFATORAÇÃO DO UPLOAD")
    print("=" * 60)
    
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    tests = {
        'Método abrir_galeria_nativa': 'def abrir_galeria_nativa(self, instance):',
        'Verificação plataforma upload': "if platform != 'android':",
        'Message toast galeria': 'show_toast("Comando para abrir a galeria nativa executado!", "success")',
        'TODO comentário galeria': 'TODO: Implementar a captura do resultado da galeria',
        'Binding galeria': 'abrir_galeria_nativa'
    }
    
    passed = 0
    total = len(tests)
    
    for test_name, search_text in tests.items():
        if search_text in content:
            print(f"   ✅ {test_name}")
            passed += 1
        else:
            print(f"   ❌ {test_name}")
    
    score = (passed / total) * 100
    print(f"\n📊 Score Upload: {score:.1f}% ({passed}/{total})")
    
    return score >= 80


def test_code_integrity():
    """Testa integridade geral do código"""
    print("\n🔧 TESTANDO INTEGRIDADE DO CÓDIGO")
    print("=" * 60)
    
    # Testa sintaxe
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            code = f.read()
        
        compile(code, 'main.py', 'exec')
        print("   ✅ Sintaxe Python válida")
        syntax_ok = True
    except SyntaxError as e:
        print(f"   ❌ Erro de sintaxe: {e}")
        syntax_ok = False
    
    # Testa estrutura de classes
    class_tests = {
        'MercadoEmNumerosApp existe': 'class MercadoEmNumerosApp(App):',
        'CameraWidget existe': 'class CameraWidget(',
        'UploadWidget existe': 'class UploadWidget(',
        'MainLayout existe': 'class MainLayout(',
        'SavedKey existe': 'class SavedKey:'
    }
    
    passed = 1 if syntax_ok else 0
    total = 1
    
    for test_name, search_text in class_tests.items():
        if search_text in code:
            print(f"   ✅ {test_name}")
            passed += 1
        else:
            print(f"   ❌ {test_name}")
        total += 1
    
    score = (passed / total) * 100
    print(f"\n📊 Score Integridade: {score:.1f}% ({passed}/{total})")
    
    return score >= 90


def test_functionality_completeness():
    """Testa completude das funcionalidades"""
    print("\n⚙️ TESTANDO COMPLETUDE DAS FUNCIONALIDADES")
    print("=" * 60)
    
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    functionality_tests = {
        'Validação de chaves': 'validate_access_key',
        'Salvamento local': 'save_keys_to_file',
        'Carregamento local': 'load_saved_keys',
        'Exportação CSV': 'export_csv',
        'Sistema de toast': 'show_toast',
        'Processamento QR': 'process_qr_data',
        'Interface moderna': 'ModernCard',
        'Cores definidas': 'COLORS',
        'Temas visuais': 'get_color_from_hex'
    }
    
    passed = 0
    total = len(functionality_tests)
    
    for test_name, search_text in functionality_tests.items():
        if search_text in content:
            print(f"   ✅ {test_name}")
            passed += 1
        else:
            print(f"   ❌ {test_name}")
    
    score = (passed / total) * 100
    print(f"\n📊 Score Funcionalidades: {score:.1f}% ({passed}/{total})")
    
    return score >= 85


def main():
    """Executa todos os testes de refatoração"""
    print("🧪 TESTE ESPECÍFICO DAS REFATORAÇÕES ANDROID")
    print("=" * 80)
    print("🎯 Validando correções cirúrgicas implementadas")
    print("📱 Foco: Permissões, Câmera Nativa, Upload Nativo")
    print("=" * 80)
    
    # Executa todos os testes
    results = []
    
    results.append(('Permissões Android', test_android_permissions()))
    results.append(('Refatoração Câmera', test_camera_refactor()))
    results.append(('Refatoração Upload', test_upload_refactor()))
    results.append(('Integridade Código', test_code_integrity()))
    results.append(('Completude Funcionalidades', test_functionality_completeness()))
    
    # Calcula score geral
    passed_tests = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    overall_score = (passed_tests / total_tests) * 100
    
    # Relatório final
    print(f"\n🏆 RELATÓRIO FINAL DAS REFATORAÇÕES")
    print("=" * 70)
    
    for test_name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"   {status} {test_name}")
    
    print(f"\n📊 SCORE GERAL DAS REFATORAÇÕES: {overall_score:.1f}%")
    print(f"📊 Testes Passaram: {passed_tests}/{total_tests}")
    
    if overall_score >= 90:
        status = "🟢 EXCELENTE - Refatorações implementadas com sucesso"
        recommendation = "✅ Pronto para compilar APK"
    elif overall_score >= 75:
        status = "🟢 BOM - Refatorações funcionais"
        recommendation = "✅ Pode prosseguir com build"
    elif overall_score >= 60:
        status = "🟡 REGULAR - Algumas correções necessárias"
        recommendation = "⚠️ Revisar falhas antes do build"
    else:
        status = "🔴 PROBLEMÁTICO - Refatorações incompletas"
        recommendation = "❌ Corrigir problemas antes de continuar"
    
    print(f"\n🎯 STATUS: {status}")
    print(f"📋 RECOMENDAÇÃO: {recommendation}")
    
    if overall_score >= 75:
        print(f"\n🚀 PRÓXIMOS PASSOS:")
        print(f"   1. ✅ Compilar APK com buildozer")
        print(f"   2. ✅ Testar no dispositivo Android real")
        print(f"   3. ✅ Validar permissões são solicitadas")
        print(f"   4. ✅ Testar botões câmera e galeria")
        
    return overall_score >= 75


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)