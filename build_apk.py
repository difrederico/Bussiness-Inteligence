#!/usr/bin/env python3
"""
🔥 COMPILADOR APK DIRETO 
Cria APK do leitor QR Fiscal para Android
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_apk():
    print("🚀 COMPILANDO APK ANDROID...")
    print("=" * 50)
    
    # Verifica se está no diretório correto
    if not os.path.exists("main.py"):
        print("❌ Erro: main.py não encontrado!")
        print("Execute este script no diretório do projeto.")
        return False
    
    # Verifica buildozer.spec
    if not os.path.exists("buildozer.spec"):
        print("❌ Erro: buildozer.spec não encontrado!")
        return False
    
    print("✅ Arquivos encontrados")
    print("📦 Iniciando compilação...")
    
    try:
        # Tenta buildozer primeiro
        result = subprocess.run([
            "buildozer", "android", "debug"
        ], capture_output=True, text=True, timeout=1800)  # 30 min timeout
        
        if result.returncode == 0:
            print("✅ APK compilado com sucesso!")
            
            # Procura o APK gerado
            bin_dir = Path("bin")
            if bin_dir.exists():
                apk_files = list(bin_dir.glob("*.apk"))
                if apk_files:
                    apk_file = apk_files[0]
                    print(f"📱 APK criado: {apk_file}")
                    print(f"📁 Localização: {apk_file.absolute()}")
                    
                    # Cria cópia fácil de encontrar
                    easy_name = "LeitorQR_Fiscal.apk"
                    shutil.copy(apk_file, easy_name)
                    print(f"📋 Cópia criada: {easy_name}")
                    
                    return True
            
        else:
            print("❌ Erro na compilação:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏱️ Timeout na compilação (30 min)")
        return False
    except FileNotFoundError:
        print("❌ Buildozer não encontrado!")
        print("💡 Tentando método alternativo...")
        return build_with_p4a()
    except Exception as e:
        print(f"❌ Erro: {e}")
        return build_with_p4a()

def build_with_p4a():
    """Método alternativo com python-for-android"""
    print("🔄 Usando python-for-android...")
    
    try:
        cmd = [
            "p4a", "apk",
            "--private", ".",
            "--package", "com.leitorqr.fiscal",
            "--name", "LeitorQRFiscal",
            "--version", "1.0",
            "--bootstrap", "sdl2",
            "--requirements", "python3,kivy,opencv-python,pyzbar,numpy",
            "--permission", "CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE",
            "--arch", "arm64-v8a"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        
        if result.returncode == 0:
            print("✅ APK compilado com p4a!")
            return True
        else:
            print("❌ Erro p4a:", result.stderr)
            return show_manual_steps()
            
    except Exception as e:
        print(f"❌ Erro p4a: {e}")
        return show_manual_steps()

def show_manual_steps():
    """Mostra passos manuais para compilar"""
    print("\n" + "="*50)
    print("📋 COMPILAÇÃO MANUAL - OPÇÕES:")
    print("="*50)
    
    print("\n🎯 OPÇÃO 1: GitHub Codespaces")
    print("1. Abra este projeto no GitHub")
    print("2. Clique em 'Code' → 'Codespaces' → 'New codespace'")
    print("3. No terminal: buildozer android debug")
    print("4. Baixe o APK gerado")
    
    print("\n🎯 OPÇÃO 2: Replit")
    print("1. Importe projeto no Replit.com")
    print("2. Execute: buildozer android debug")
    print("3. Baixe o APK")
    
    print("\n🎯 OPÇÃO 3: WSL (Windows)")
    print("1. Instale WSL: wsl --install")
    print("2. No WSL: sudo apt install buildozer")
    print("3. Execute: buildozer android debug")
    
    print("\n🎯 OPÇÃO 4: Docker")
    print("1. Instale Docker Desktop")
    print("2. Execute: docker run --rm -v \"$PWD\":/app kivy/buildozer android debug")
    
    print("\n📱 INSTALAÇÃO NO CELULAR:")
    print("1. Transfira o APK para o celular")
    print("2. Ative 'Fontes Desconhecidas' nas configurações")
    print("3. Instale o APK")
    print("4. Permita acesso à câmera")
    
    return False

def main():
    print("📱 COMPILADOR APK - LEITOR QR FISCAL")
    print("Desenvolvido para Android")
    print("="*50)
    
    if build_apk():
        print("\n🎉 SUCESSO!")
        print("✅ APK criado com sucesso")
        print("📋 Próximos passos:")
        print("  1. Transfira o APK para o celular")
        print("  2. Instale no Android")
        print("  3. Permita acesso à câmera")
        print("  4. Teste o aplicativo!")
    else:
        print("\n⚠️  Compilação não concluída automaticamente")
        print("💡 Use uma das opções manuais mostradas acima")
    
    input("\n📱 Pressione Enter para continuar...")

if __name__ == "__main__":
    main()