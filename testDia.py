from diaScraper import *
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import os
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if __name__ == "__main__":
    print("Testing Dia Scraper")

    driver = configurar_driver()

    driver.get("https://www.dia.es")
    rechazar_cookies(driver=driver)
    click_menu(driver=driver)
    time.sleep(random.uniform(4, 5))
    html = driver.page_source
    urls_categorias = extraer_url_categorias_general(html)
    driver.quit()

    for url in urls_categorias:
        print("********************************************************************")
        print(f"Procesando URL de categoría: {url}")
        driver = configurar_driver()
        driver.get(url)
        rechazar_cookies(driver=driver)
        time.sleep(random.uniform(2, 4))  
        html = driver.page_source
        urls_categorias_e = extraer_url_categorias_especifico(html)

        for url_e in urls_categorias_e:
            print("------------------------------------------------------------------")
            print(f"Procesando URL de categoría: {url_e}")
            driver.get(url_e)
            scroll_down(driver=driver)
            time.sleep(random.uniform(0.5, 1))  
            html = driver.page_source
            urls_productos = extraer_url_productos(html)

            for url_p in urls_productos:
                driver.get(url_p)
                time.sleep(random.uniform(0.2, 0.5))  
                html = driver.page_source
            
                data_nutricional, name, price, price_per_unit, ingredients = extraer_info_nutricional(html)
                valores_float = {
                k: float(v) if re.match(r'^-?\d+(\.\d+)?$', v) else 0.0
                for k, v in data_nutricional.items()
                }
                headers = {
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation"
                }

                data = {
                "nombre": name,
                "supermercado": "Dia",
                "precio": price,
                "precio_por_unidad": price_per_unit,
                "ingredientes": ingredients,
                "valor_energetico": valores_float.get('valor_energetico', 0),
                "grasas": valores_float.get('grasas', 0),
                "hidratos": valores_float.get('hidratos_de_carbono', 0),
                "azucares": valores_float.get('azucares', 0),
                "proteinas": valores_float.get('proteinas', 0),
                "sal": valores_float.get('sal', 0),
                "url_producto": url_p
                }

                res = requests.post(
                    f"{SUPABASE_URL}/rest/v1/productos_dia", 
                    headers=headers,
                    json=data
                )
                
                if res.status_code == 201:
                    print(f"Producto insertado: {name}")
                else:
                    print(f"Error al insertar producto: {res.status_code}, {res.text}")
        driver.quit()


    