#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Simplificado de Qualidade Android - Executável
Valida funcionalidades críticas antes do deploy Git

Autor: Especialista em Testes QA
Data: Dezembro 2024
"""

import os
import sys
import time
from datetime import datetime

def check_file_structure():
    """Verifica estrutura de arquivos essenciais"""
    print("🔍 Verificando estrutura de arquivos...")
    
    essential_files = {
        'main.py': 'Arquivo principal do aplicativo',
        'buildozer.spec': 'Configuração de build Android'
    }
    
    optional_files = {
        'README.md': 'Documentação do projeto',
        'test_camera.py': 'Testes de câmera',
        'test_desktop.py': 'Testes de desktop'
    }
    
    score = 100
    issues = []
    
    # Verifica arquivos essenciais
    for filename, description in essential_files.items():
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            print(f"   ✅ {filename} - {file_size} bytes - {description}")
            
            if file_size < 1000:
                issues.append(f"Arquivo {filename} muito pequeno ({file_size} bytes)")
                score -= 20
        else:
            print(f"   ❌ {filename} - AUSENTE - {description}")
            issues.append(f"Arquivo essencial ausente: {filename}")
            score -= 30
    
    # Verifica arquivos opcionais
    for filename, description in optional_files.items():
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            print(f"   ✅ {filename} - {file_size} bytes - {description}")
        else:
            print(f"   ⚠️  {filename} - Opcional - {description}")
    
    return score, issues


def analyze_main_file():
    """Analisa arquivo principal do aplicativo"""
    print("\n📱 Analisando arquivo principal (main.py)...")
    
    if not os.path.exists('main.py'):
        print("   ❌ main.py não encontrado")
        return 0, ["Arquivo main.py ausente"]
    
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        score = 100
        issues = []
        
        # Verificações críticas
        critical_imports = [
            'kivy',
            'json',
            'os'
        ]
        
        # Funcionalidades essenciais
        essential_features = [
            'class',
            'def',
            'App',
            'run'
        ]
        
        # Android específicos
        android_features = [
            'android',
            'Camera',
            'permissions'
        ]
        
        print("   🔍 Verificando imports críticos...")
        for imp in critical_imports:
            if imp in content:
                print(f"      ✅ Import {imp} encontrado")
            else:
                print(f"      ⚠️  Import {imp} não encontrado")
                score -= 10
        
        print("   🔍 Verificando funcionalidades essenciais...")
        for feature in essential_features:
            if feature in content:
                print(f"      ✅ {feature} encontrado")
            else:
                print(f"      ❌ {feature} não encontrado")
                issues.append(f"Funcionalidade essencial ausente: {feature}")
                score -= 15
        
        print("   🔍 Verificando recursos Android...")
        android_score = 0
        for feature in android_features:
            if feature in content:
                print(f"      ✅ {feature} encontrado")
                android_score += 1
            else:
                print(f"      ⚠️  {feature} não encontrado")
        
        if android_score == 0:
            issues.append("Nenhum recurso Android específico encontrado")
            score -= 20
        
        # Verifica tamanho do código
        lines = len(content.split('\n'))
        print(f"   📏 Linhas de código: {lines}")
        
        if lines < 100:
            issues.append("Código muito pequeno - possível implementação incompleta")
            score -= 15
        elif lines > 2000:
            issues.append("Código muito grande - considerar modularização")
            score -= 5
        
        return score, issues
        
    except Exception as e:
        print(f"   ❌ Erro ao analisar main.py: {e}")
        return 0, [f"Erro na análise: {e}"]


def analyze_buildozer_config():
    """Analisa configuração do buildozer"""
    print("\n🏗️ Analisando configuração Buildozer...")
    
    if not os.path.exists('buildozer.spec'):
        print("   ❌ buildozer.spec não encontrado")
        return 0, ["Arquivo buildozer.spec ausente"]
    
    try:
        with open('buildozer.spec', 'r', encoding='utf-8') as f:
            content = f.read()
        
        score = 100
        issues = []
        
        # Configurações obrigatórias
        required_configs = [
            'title =',
            'package.name =',
            'source.main =',
            'requirements =',
            'android.permissions ='
        ]
        
        print("   🔍 Verificando configurações obrigatórias...")
        for config in required_configs:
            if config in content:
                print(f"      ✅ {config} configurado")
            else:
                print(f"      ❌ {config} ausente")
                issues.append(f"Configuração obrigatória ausente: {config}")
                score -= 20
        
        # Permissões Android essenciais
        essential_permissions = ['CAMERA', 'WRITE_EXTERNAL_STORAGE']
        
        print("   🔍 Verificando permissões Android...")
        for permission in essential_permissions:
            if permission in content:
                print(f"      ✅ Permissão {permission} configurada")
            else:
                print(f"      ⚠️  Permissão {permission} não encontrada")
                issues.append(f"Permissão recomendada ausente: {permission}")
                score -= 10
        
        # Verifica dependências
        if 'kivy' in content:
            print("      ✅ Kivy configurado nas dependências")
        else:
            print("      ❌ Kivy não encontrado nas dependências")
            issues.append("Kivy não configurado como dependência")
            score -= 25
        
        return score, issues
        
    except Exception as e:
        print(f"   ❌ Erro ao analisar buildozer.spec: {e}")
        return 0, [f"Erro na análise: {e}"]


def check_python_syntax():
    """Verifica sintaxe Python"""
    print("\n🐍 Verificando sintaxe Python...")
    
    python_files = [f for f in os.listdir('.') if f.endswith('.py')]
    
    if not python_files:
        print("   ❌ Nenhum arquivo Python encontrado")
        return 0, ["Nenhum arquivo Python no projeto"]
    
    score = 100
    issues = []
    
    for py_file in python_files:
        if py_file.startswith('test_'):
            continue  # Pula arquivos de teste
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Tenta compilar para verificar sintaxe
            compile(code, py_file, 'exec')
            print(f"   ✅ {py_file} - Sintaxe válida")
            
        except SyntaxError as e:
            print(f"   ❌ {py_file} - Erro de sintaxe: {e}")
            issues.append(f"Erro de sintaxe em {py_file}: {e}")
            score -= 30
            
        except Exception as e:
            print(f"   ⚠️  {py_file} - Aviso: {e}")
            score -= 5
    
    return score, issues


def evaluate_project_readiness():
    """Avalia prontidão do projeto"""
    print("\n🎯 Avaliando prontidão para deploy...")
    
    # Verifica se tem commits Git
    git_ready = os.path.exists('.git') or os.path.exists('../.git')
    
    # Verifica documentação
    docs_ready = os.path.exists('README.md')
    
    # Verifica se tem testes
    test_files = [f for f in os.listdir('.') if f.startswith('test_') and f.endswith('.py')]
    tests_ready = len(test_files) > 0
    
    readiness_score = 0
    readiness_items = []
    
    if git_ready:
        print("   ✅ Repositório Git detectado")
        readiness_score += 25
        readiness_items.append("Git configurado")
    else:
        print("   ⚠️  Repositório Git não detectado")
    
    if docs_ready:
        print("   ✅ Documentação (README.md) presente")
        readiness_score += 25
        readiness_items.append("Documentação presente")
    else:
        print("   ⚠️  README.md não encontrado")
    
    if tests_ready:
        print(f"   ✅ {len(test_files)} arquivos de teste encontrados")
        readiness_score += 25
        readiness_items.append(f"{len(test_files)} testes")
    else:
        print("   ⚠️  Nenhum arquivo de teste encontrado")
    
    # Build readiness
    build_ready = os.path.exists('buildozer.spec') and os.path.exists('main.py')
    
    if build_ready:
        print("   ✅ Configuração de build presente")
        readiness_score += 25
        readiness_items.append("Build configurado")
    else:
        print("   ❌ Configuração de build incompleta")
    
    return readiness_score, readiness_items


def generate_final_report(results):
    """Gera relatório final de qualidade"""
    print("\n" + "=" * 80)
    print("🎯 RELATÓRIO FINAL DE QUALIDADE - LEITOR DE CUPONS FISCAIS ANDROID")
    print("=" * 80)
    
    # Informações gerais
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"📁 Diretório: {os.getcwd()}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    # Resultados por categoria
    total_score = 0
    total_weight = 0
    
    categories = {
        'Estrutura de Arquivos': {'score': results.get('structure', 0), 'weight': 20},
        'Código Principal': {'score': results.get('main_code', 0), 'weight': 30},
        'Configuração Build': {'score': results.get('buildozer', 0), 'weight': 25},
        'Sintaxe Python': {'score': results.get('syntax', 0), 'weight': 15},
        'Prontidão Deploy': {'score': results.get('readiness', 0), 'weight': 10}
    }
    
    print(f"\n📊 SCORES POR CATEGORIA:")
    print("-" * 50)
    
    for category, data in categories.items():
        score = data['score']
        weight = data['weight']
        
        weighted_score = (score * weight) / 100
        total_score += weighted_score
        total_weight += weight
        
        if score >= 90:
            status = "🟢 EXCELENTE"
        elif score >= 75:
            status = "🟢 BOM"
        elif score >= 60:
            status = "🟡 REGULAR"
        elif score >= 40:
            status = "🟠 PROBLEMÁTICO"
        else:
            status = "🔴 CRÍTICO"
        
        print(f"{category:<25} {score:>3.0f}% - {status}")
    
    # Score geral
    overall_score = (total_score / total_weight) * 100
    
    print(f"\n🏆 SCORE GERAL: {overall_score:.1f}%")
    
    if overall_score >= 90:
        final_status = "🟢 EXCELENTE - APROVADO PARA PRODUÇÃO"
        recommendation = "Deploy imediato aprovado"
    elif overall_score >= 75:
        final_status = "🟢 BOM - APROVADO PARA PRODUÇÃO"
        recommendation = "Deploy aprovado"
    elif overall_score >= 60:
        final_status = "🟡 REGULAR - APROVADO CONDICIONALMENTE"
        recommendation = "Revisar avisos e deploy"
    elif overall_score >= 40:
        final_status = "🟠 PROBLEMÁTICO - CORREÇÕES RECOMENDADAS"
        recommendation = "Corrigir problemas antes do deploy"
    else:
        final_status = "🔴 CRÍTICO - CORREÇÕES OBRIGATÓRIAS"
        recommendation = "Não deploy até correções"
    
    print(f"\n🎯 STATUS: {final_status}")
    print(f"📋 RECOMENDAÇÃO: {recommendation}")
    
    # Próximos passos
    print(f"\n🚀 PRÓXIMOS PASSOS RECOMENDADOS:")
    print("-" * 50)
    
    if overall_score >= 75:
        print("1. ✅ buildozer android clean")
        print("2. ✅ buildozer android debug")
        print("3. ✅ Testar APK em dispositivo Android")
        print("4. ✅ git add . && git commit -m 'Release version'")
        print("5. ✅ git push origin main")
    elif overall_score >= 60:
        print("1. ⚠️  Revisar avisos identificados")
        print("2. ⚠️  buildozer android debug (teste)")
        print("3. ⚠️  Validar funcionalidades críticas")
        print("4. ⚠️  Deploy após validação")
    else:
        print("1. ❌ Corrigir problemas críticos")
        print("2. ❌ Re-executar testes")
        print("3. ❌ Não deploy até score >= 60%")
    
    # Todos os problemas encontrados
    all_issues = []
    for category_issues in results.get('all_issues', []):
        all_issues.extend(category_issues)
    
    if all_issues:
        print(f"\n⚠️  PROBLEMAS IDENTIFICADOS ({len(all_issues)}):")
        print("-" * 50)
        for i, issue in enumerate(all_issues[:10], 1):  # Mostra até 10 problemas
            print(f"{i:2d}. {issue}")
        
        if len(all_issues) > 10:
            print(f"    ... e mais {len(all_issues) - 10} problemas")
    
    return overall_score >= 60  # Aprovado se score >= 60%


def main():
    """Função principal de testes"""
    print("🎯 ESPECIALISTA EM TESTES QA - VALIDAÇÃO ANDROID SIMPLIFICADA")
    print("=" * 80)
    print("📱 Projeto: Leitor de Cupons Fiscais Android")
    print("🎯 Objetivo: Validar qualidade antes do deploy Git")
    print("=" * 80)
    
    start_time = time.time()
    results = {}
    all_issues = []
    
    try:
        # 1. Estrutura de arquivos
        print("\n📁 FASE 1: ESTRUTURA DE ARQUIVOS")
        print("=" * 50)
        structure_score, structure_issues = check_file_structure()
        results['structure'] = structure_score
        all_issues.append(structure_issues)
        
        # 2. Análise do código principal
        print("\n💻 FASE 2: CÓDIGO PRINCIPAL")
        print("=" * 50)
        main_score, main_issues = analyze_main_file()
        results['main_code'] = main_score
        all_issues.append(main_issues)
        
        # 3. Configuração do buildozer
        print("\n🔧 FASE 3: CONFIGURAÇÃO BUILD")
        print("=" * 50)
        buildozer_score, buildozer_issues = analyze_buildozer_config()
        results['buildozer'] = buildozer_score
        all_issues.append(buildozer_issues)
        
        # 4. Sintaxe Python
        print("\n🐍 FASE 4: SINTAXE PYTHON")
        print("=" * 50)
        syntax_score, syntax_issues = check_python_syntax()
        results['syntax'] = syntax_score
        all_issues.append(syntax_issues)
        
        # 5. Prontidão para deploy
        print("\n🚀 FASE 5: PRONTIDÃO DEPLOY")
        print("=" * 50)
        readiness_score, readiness_items = evaluate_project_readiness()
        results['readiness'] = readiness_score
        
        # Adiciona todos os problemas
        results['all_issues'] = all_issues
        
        # Gera relatório final
        approved = generate_final_report(results)
        
        duration = time.time() - start_time
        print(f"\n⏱️  Tempo total de execução: {duration:.2f} segundos")
        
        if approved:
            print(f"\n🎉 PROJETO APROVADO PARA GIT DEPLOY!")
            return True
        else:
            print(f"\n⛔ PROJETO NÃO APROVADO - Correções necessárias")
            return False
            
    except Exception as e:
        print(f"\n💥 ERRO CRÍTICO: {e}")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)