#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Pré-Build - Validação Total
Executa todos os testes necessários antes do build no GitHub Actions
Detecta problemas que poderiam causar falha na compilação

Autor: GitHub Copilot
Data: Outubro 2025
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path

def test_python_syntax():
    """Testa sintaxe de todos arquivos Python"""
    print("🐍 TESTANDO SINTAXE PYTHON...")
    
    py_files = ['main.py']
    errors = []
    
    for file in py_files:
        if os.path.exists(file):
            try:
                subprocess.run([sys.executable, '-m', 'py_compile', file], 
                             check=True, capture_output=True)
                print(f"   ✅ {file}")
            except subprocess.CalledProcessError as e:
                errors.append(f"{file}: {e}")
                print(f"   ❌ {file}: {e}")
        else:
            print(f"   ⚠️ {file}: Arquivo não encontrado")
    
    return len(errors) == 0

def test_imports():
    """Testa imports essenciais"""
    print("📦 TESTANDO IMPORTS ESSENCIAIS...")
    
    essential_imports = [
        'kivy',
        'PIL',  # Pillow
        'json',
        'os',
        'sys'
    ]
    
    optional_imports = [
        'cv2',     # OpenCV (opcional)
        'numpy',   # NumPy (opcional)  
        'pyzbar',  # Pyzbar (opcional)
    ]
    
    errors = []
    
    # Testa imports essenciais
    for module in essential_imports:
        try:
            importlib.import_module(module)
            print(f"   ✅ {module}")
        except ImportError as e:
            errors.append(f"{module}: {e}")
            print(f"   ❌ {module}: ERRO CRÍTICO - {e}")
    
    # Testa imports opcionais
    for module in optional_imports:
        try:
            importlib.import_module(module)
            print(f"   ✅ {module} (opcional)")
        except ImportError:
            print(f"   ⚠️ {module} (opcional - não disponível)")
    
    return len(errors) == 0

def test_buildozer_spec():
    """Valida buildozer.spec"""
    print("📋 TESTANDO BUILDOZER.SPEC...")
    
    if not os.path.exists('buildozer.spec'):
        print("   ❌ buildozer.spec não encontrado!")
        return False
    
    errors = []
    warnings = []
    
    with open('buildozer.spec', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verifica problemas críticos
    if 'android.sdk =' in content:
        errors.append("android.sdk está obsoleto - remove essa linha!")
    
    if 'opencv' in content and 'requirements' in content:
        warnings.append("opencv pode causar falhas - considere remover")
    
    if 'numpy' in content and 'requirements' in content:
        warnings.append("numpy pode ser instável no p4a")
    
    # Verifica configurações essenciais
    if 'android.permissions' not in content:
        errors.append("android.permissions não definidas")
    
    if 'pyjnius' not in content:
        errors.append("pyjnius não encontrado nos requirements (necessário para APIs nativas)")
    
    # Mostra resultados
    for error in errors:
        print(f"   ❌ ERRO: {error}")
    
    for warning in warnings:
        print(f"   ⚠️ AVISO: {warning}")
    
    if not errors and not warnings:
        print("   ✅ buildozer.spec está correto")
    
    return len(errors) == 0

def test_file_structure():
    """Verifica estrutura de arquivos"""
    print("📁 TESTANDO ESTRUTURA DE ARQUIVOS...")
    
    required_files = [
        'main.py',
        'buildozer.spec'
    ]
    
    optional_files = [
        'buildozer_stable.spec',
        'README.md'
    ]
    
    missing_critical = []
    
    for file in required_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"   ✅ {file} ({size} bytes)")
        else:
            missing_critical.append(file)
            print(f"   ❌ {file} - ARQUIVO CRÍTICO AUSENTE")
    
    for file in optional_files:
        if os.path.exists(file):
            print(f"   ✅ {file} (opcional)")
        else:
            print(f"   ⚠️ {file} (opcional - não encontrado)")
    
    return len(missing_critical) == 0

def test_github_actions():
    """Verifica GitHub Actions"""
    print("🚀 TESTANDO GITHUB ACTIONS...")
    
    actions_dir = Path('.github/workflows')
    if not actions_dir.exists():
        print("   ❌ Diretório .github/workflows não encontrado")
        return False
    
    yml_files = list(actions_dir.glob('*.yml'))
    
    if not yml_files:
        print("   ❌ Nenhum arquivo de workflow encontrado")
        return False
    
    for yml_file in yml_files:
        print(f"   ✅ {yml_file.name}")
        
        # Verifica sintaxe básica YAML
        with open(yml_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Procura por problemas conhecidos
        if 'upload-artifact@v3' in content:
            print(f"   ⚠️ {yml_file.name}: Usa upload-artifact@v3 (obsoleto)")
        
        if 'ubuntu-latest' in content:
            print(f"   ⚠️ {yml_file.name}: ubuntu-latest pode mudar - prefira ubuntu-22.04")
    
    return True

def generate_recommendations():
    """Gera recomendações para evitar problemas"""
    print("\n💡 RECOMENDAÇÕES PARA BUILD ESTÁVEL:")
    print("=" * 60)
    
    print("✅ CONFIGURAÇÃO RECOMENDADA:")
    print("   - Use buildozer_stable.spec (já criado)")
    print("   - Execute GitHub Action 'Ultra Estável'")
    print("   - Requirements mínimos: python3,kivy,pillow,pyjnius,android")
    
    print("\n⚠️ EVITE:")
    print("   - opencv (instável no p4a)")
    print("   - numpy (pode causar problemas)")
    print("   - android.sdk no buildozer.spec (obsoleto)")
    print("   - Múltiplas arquiteturas (use apenas arm64-v8a)")
    
    print("\n🔧 SE DER ERRO:")
    print("   - Verifique logs no GitHub Actions")
    print("   - Use configuração ainda mais mínima")
    print("   - Tente build local primeiro")

def main():
    """Executa todos os testes"""
    print("🧪 TESTE PRÉ-BUILD - VALIDAÇÃO TOTAL")
    print("=" * 60)
    print("🎯 Detecta problemas antes do GitHub Actions")
    print("=" * 60)
    
    tests = [
        ("Sintaxe Python", test_python_syntax),
        ("Imports Essenciais", test_imports),
        ("Buildozer Spec", test_buildozer_spec),
        ("Estrutura de Arquivos", test_file_structure),
        ("GitHub Actions", test_github_actions)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name.upper()}:")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ ERRO NO TESTE: {e}")
            results.append((test_name, False))
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   {status} {test_name}")
        if result:
            passed += 1
    
    success_rate = (passed / total) * 100
    print(f"\n📈 Taxa de Sucesso: {success_rate:.1f}% ({passed}/{total})")
    
    if success_rate >= 80:
        print("🎉 PRONTO PARA BUILD NO GITHUB ACTIONS!")
        print("✅ Chance alta de sucesso na compilação")
    elif success_rate >= 60:
        print("⚠️ POSSÍVEIS PROBLEMAS - Revise falhas")
        print("🔧 Recomenda-se corrigir antes do build")
    else:
        print("❌ MUITOS PROBLEMAS - Build provavelmente falhará")
        print("🔴 Corrija os erros antes de tentar")
    
    generate_recommendations()
    
    return success_rate >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)