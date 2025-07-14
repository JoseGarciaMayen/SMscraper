import requests
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import time
import random
import unicodedata
import re

def get_producto(id_producto: int):
    url1 = f"https://tienda.mercadona.es/api/products/{id_producto}/"
    response = requests.get(url1)
    data = response.json()
    # Por si no existen los campos:
    
    nombre = data.get('details', {}).get('description', '')
    precio = data.get('price_instructions', {}).get('bulk_price', '')
    precioUd = data.get('price_instructions', {}).get('unit_price', '')
    ingredientes = data.get('nutrition_information', {}).get('ingredients', '') 
    if ingredientes:
        ingredientes_limpios = re.sub(r'<p>\s*(Ingredientes:)?\s*', '', ingredientes, flags=re.IGNORECASE).strip()
    else:
        ingredientes_limpios = ""
    url = data['thumbnail']
    return nombre, precio, precioUd, ingredientes_limpios, url

def extraer_ids_categorias(data):
    ids_categorias = []

    if "results" in data:
        for resultado in data["results"]:
            if "categories" in resultado:
                for categoria in resultado["categories"]:
                    if "id" in categoria:
                        ids_categorias.append(categoria["id"])
        
    return ids_categorias

def extraer_ids_productos(data):
        ids_productos = []

        if "categories" in data:
            for categoria in data["categories"]:
                if "products" in categoria:
                    for producto in categoria["products"]:
                        if "id" in producto:
                            ids_productos.append(producto["id"])
            
        return ids_productos

def normalizar_clave(texto):
    # Elimina tildes y pasa a minúsculas
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8').lower()
    # Reemplaza espacios y guiones por "_"
    texto = re.sub(r'[\s\-]+', '_', texto)
    # Elimina cualquier carácter que no sea letra, número o "_"
    texto = re.sub(r'[^\w_]', '', texto)
    return texto

def extraer_info_nutricional(id_producto, html):
    soup = BeautifulSoup(html, "html.parser")
    tabla = soup.find("div", id="tabla_tipo_NUT")

    if not tabla:
        return {}

    tbody = tabla.find('tbody')
    info_nutricional = {}

    if tbody:
        filas = tbody.find_all('tr')

        for fila in filas:
            celdas = fila.find_all('td')
            nutriente = celdas[0].get_text(strip=True)
            cantidad = celdas[1].get_text(strip=True)

            clave = normalizar_clave(nutriente)
            # Elimina unidades de medida comunes
            cantidad = re.sub(r'[^0-9.]', '', cantidad)
            info_nutricional[clave] = cantidad

    return info_nutricional  

def configurar_driver():
    options = uc.ChromeOptions()
    
    # Anti-detección básica
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-images")
    options.add_argument("--disable-javascript")
    options.headless = False
    
    # User agent realista
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = uc.Chrome(options=options)
    
    # Ocultar webdriver
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def espera():
    tiempo = random.uniform(1, 2)
    time.sleep(tiempo)

def escribir_humano(elemento, texto):
    for char in texto:
        elemento.send_keys(char)
        time.sleep(random.uniform(0.05, 0.15))