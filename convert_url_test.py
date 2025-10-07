"""
Script para convertir URLs de share.google a URLs completas de Google Maps
Usa Selenium para seguir la redirección y capturar la URL final

Uso:
    uv run python convert_url_test.py
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def convert_share_url_to_maps_url(share_url: str, timeout: int = 10) -> str:
    """
    Convierte una URL de share.google a una URL completa de Google Maps
    
    Args:
        share_url: URL en formato https://share.google/...
        timeout: Segundos máximos de espera
        
    Returns:
        URL completa de Google Maps
    """
    # Configurar Chrome en modo headless (sin ventana visible)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Inicializar driver
    print(f"🔄 Abriendo URL: {share_url}")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Abrir la URL corta
        driver.get(share_url)
        
        # Esperar un poco para la redirección
        time.sleep(3)
        
        # Esperar a que la URL cambie (redirección completa)
        wait = WebDriverWait(driver, timeout)
        
        # La URL debería cambiar a google.com/maps
        for _ in range(5):  # Intentar 5 veces
            current_url = driver.current_url
            if "google.com/maps" in current_url:
                print(f"✅ Redirección completa detectada")
                break
            print(f"⏳ Esperando redirección... (URL actual: {current_url[:50]}...)")
            time.sleep(2)
        
        # Obtener la URL final
        final_url = driver.current_url
        
        print(f"📍 URL final: {final_url}")
        
        return final_url
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
        
    finally:
        driver.quit()


if __name__ == "__main__":
    # URL de prueba del archivo low_income.json
    test_url = "https://share.google/BZ1MKnpaihk5PX6OO"
    restaurant_name = "East Harlem Bottling Co."
    
    print("=" * 70)
    print(f"🧪 TEST: Convirtiendo URL para {restaurant_name}")
    print("=" * 70)
    
    maps_url = convert_share_url_to_maps_url(test_url)
    
    print("\n" + "=" * 70)
    print("📊 RESULTADO:")
    print("=" * 70)
    print(f"URL original:  {test_url}")
    print(f"URL convertida: {maps_url}")
    print("=" * 70)
    
    # Verificar que sea una URL válida para Apify
    if maps_url and "/maps/place" in maps_url:
        print("✅ URL VÁLIDA para Apify Actor")
    elif maps_url:
        print("⚠️  URL convertida pero podría no ser válida para Apify")
    else:
        print("❌ CONVERSIÓN FALLÓ")