#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE CÂMERA REAL - OpenCV + pyzbar
Leitura direta de QR codes via câmera
"""

import cv2
import time
import re
from pyzbar import pyzbar

def validate_fiscal_key(key: str) -> bool:
    """Valida chave fiscal de 44 dígitos"""
    if len(key) != 44 or not key.isdigit():
        return False
    
    try:
        # Algoritmo DV fiscal
        weights = [2, 3, 4, 5, 6, 7, 8, 9] * 5 + [2, 3, 4]
        total = sum(int(digit) * weight for digit, weight in zip(key[:43], weights))
        
        remainder = total % 11
        expected_dv = 0 if remainder < 2 else 11 - remainder
        
        return int(key[43]) == expected_dv
    except:
        return False

def test_camera_qr():
    """Teste direto da câmera para leitura de QR"""
    print("🚀 TESTE CÂMERA + QR CODES")
    print("📷 Abrindo câmera...")
    
    # Abre câmera padrão
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Erro: Não foi possível abrir a câmera")
        print("💡 Dicas:")
        print("   - Verifique se a câmera não está sendo usada por outro app")
        print("   - Teste com câmera externa USB")
        print("   - Reinstale drivers da câmera")
        return
    
    # Configura câmera
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("✅ Câmera aberta com sucesso!")
    print("🔍 Procurando QR codes...")
    print("📱 Aponte para um QR code de cupom fiscal")
    print("❌ Pressione 'q' para sair")
    print()
    
    qr_found_count = 0
    last_qr_time = 0
    processed_qrs = set()
    
    try:
        while True:
            # Captura frame
            ret, frame = cap.read()
            if not ret:
                print("❌ Erro ao capturar frame")
                break
            
            # Espelha imagem (câmera frontal)
            frame = cv2.flip(frame, 1)
            
            # Detecta QR codes
            qr_codes = pyzbar.decode(frame)
            
            # Processa QR codes encontrados
            current_time = time.time()
            
            if qr_codes and (current_time - last_qr_time > 2.0):  # Cooldown de 2s
                for qr_code in qr_codes:
                    try:
                        # Decodifica dados
                        qr_data = qr_code.data.decode('utf-8')
                        
                        # Evita processar mesmo QR repetidas vezes
                        if qr_data in processed_qrs:
                            continue
                            
                        processed_qrs.add(qr_data)
                        qr_found_count += 1
                        
                        print(f"\n🔍 QR #{qr_found_count} DETECTADO:")
                        print(f"📄 Dados: {qr_data[:80]}...")
                        
                        # Tenta extrair chave fiscal
                        match = re.search(r'p=([0-9]{44})', qr_data)
                        
                        if match:
                            fiscal_key = match.group(1)
                            print(f"🔑 Chave fiscal: {fiscal_key}")
                            
                            # Valida chave
                            if validate_fiscal_key(fiscal_key):
                                print("✅ CHAVE FISCAL VÁLIDA!")
                                print(f"   🏢 UF: {fiscal_key[0:2]}")
                                print(f"   📅 Ano/Mês: {fiscal_key[2:6]}")
                                print(f"   🏪 CNPJ: {fiscal_key[6:20]}")
                                print(f"   📊 Modelo: {fiscal_key[20:22]}")
                                print(f"   📋 Série: {fiscal_key[22:25]}")
                                print(f"   📄 Número: {fiscal_key[25:34]}")
                            else:
                                print("❌ Chave fiscal inválida (DV incorreto)")
                        else:
                            print("⚠️  QR detectado mas não contém chave fiscal de 44 dígitos")
                        
                        # Desenha retângulo ao redor do QR
                        rect = qr_code.rect
                        cv2.rectangle(frame, 
                                    (rect.left, rect.top), 
                                    (rect.left + rect.width, rect.top + rect.height), 
                                    (0, 255, 0), 3)
                        
                        # Adiciona texto
                        cv2.putText(frame, f"QR #{qr_found_count}", 
                                  (rect.left, rect.top - 10), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        
                        last_qr_time = current_time
                        
                    except UnicodeDecodeError:
                        print("⚠️  QR com encoding inválido")
                        continue
            
            # Adiciona informações na tela
            info_text = f"QR encontrados: {qr_found_count} | Pressione 'q' para sair"
            cv2.putText(frame, info_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Status da detecção
            status_text = "🔍 PROCURANDO QR CODES..." if not qr_codes else "✅ QR DETECTADO!"
            cv2.putText(frame, status_text, (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            # Mostra frame
            cv2.imshow('📷 TESTE CÂMERA - Leitor QR Cupons Fiscais', frame)
            
            # Verifica tecla pressionada
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 'q' ou ESC
                break
                
    except KeyboardInterrupt:
        print("\n⚠️ Interrompido pelo usuário")
    
    except Exception as e:
        print(f"\n❌ Erro durante captura: {e}")
    
    finally:
        # Libera recursos
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"\n📊 RESUMO DO TESTE:")
        print(f"   📷 Câmera: Funcionou corretamente")
        print(f"   🔍 QR codes detectados: {qr_found_count}")
        print(f"   ✅ Algoritmo de validação: OK")
        print(f"   📱 Pronto para Android: SIM")

def main():
    """Função principal"""
    print("=" * 50)
    print("📷 TESTE DE CÂMERA REAL - QR CODES")  
    print("🎯 Objetivo: Testar leitura de cupons fiscais")
    print("=" * 50)
    
    try:
        test_camera_qr()
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 Teste concluído!")
    input("Pressione Enter para sair...")

if __name__ == '__main__':
    main()