from mercadonaScraper import *
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
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


if __name__ == "__main__":
    # Usamos la api de mercadona para obtener las categorías
    url1 = "https://tienda.mercadona.es/api/categories/"
    response = requests.get(url1)
    data1 = response.json()
    
    ids_categorias = extraer_ids_categorias(data1)
    print(f"Total de categorías encontradas: {len(ids_categorias)}")
    
    # Usamos la api para obtener los productos de cada categoría 
    # y los agrupamos en una lista donde estarán todos los ids de productos
    ids_productos = []

    for id_categoria in ids_categorias:  

        url2 = f"https://tienda.mercadona.es/api/categories/{id_categoria}/"
        
        try:
            response = requests.get(url2)
            if response.status_code == 200:
                data2 = response.json()
                ids_productos.extend(extraer_ids_productos(data2))
            else:
                print(f"Categoría {id_categoria}: error {response.status_code}, saltada.")
        except Exception as e:
            print(f"Error al acceder a la categoría {id_categoria}: {e}")
    
    print(f"Total de productos encontrados: {len(ids_productos)}")

driver = configurar_driver()
    
driver.get("https://www.telecompra.mercadona.es/ns/entrada.php?js=1")
espera()
usuario_input = driver.find_element(By.NAME, "username") 
password_input = driver.find_element(By.NAME, "password") 

escribir_humano(usuario_input, USER)
espera()
escribir_humano(password_input, PASSWORD)


boton_login = driver.find_element(By.ID, "ImgEntradaAut")  
boton_login.click()

# Scrapeamos con bs4 la información nutricional de un producto
for id_producto in ids_productos:  # Limitar a 1 producto para pruebas

    nombre, precio, precioUd, ingredientes, url = get_producto(id_producto)

    driver.get(f"https://www.telecompra.mercadona.es/detall_producte.php?id={id_producto}")
    time.sleep(0.02)
    html = driver.page_source

    data_nutricional = extraer_info_nutricional(id_producto, html)
    print(data_nutricional)
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
    "nombre": nombre,
    "supermercado": "Mercadona",
    "precio": precio,
    "precio_por_unidad": precioUd,
    "ingredientes": ingredientes,
    "valor_energetico": valores_float.get('valor_energetico', 0),
    "grasas": valores_float.get('grasas', 0),
    "hidratos": valores_float.get('hidratos_de_carbono', 0),
    "azucares": valores_float.get('azucares', 0),
    "proteinas": valores_float.get('proteinas', 0),
    "sal": valores_float.get('sal', 0),
    "url_producto": f"https://www.telecompra.mercadona.es/detall_producte.php?id={id_producto}"
}

    res = requests.post(
        f"{SUPABASE_URL}/rest/v1/productos_mercadona", 
        headers=headers,
        json=data
    )
    print(f"Producto ID {id_producto} insertado: {nombre}")
    print(res.status_code)

driver.quit()




    