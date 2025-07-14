import requests
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import time
import random
import unicodedata
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_html_dia(url, d=False): 
    if not d:
        driver = configurar_driver()
    driver.get(url)
    time.sleep(5)
    html = driver.page_source
    return html

def extraer_url_categorias_general(html, base_url="https://www.dia.es"):
    soup = BeautifulSoup(html, "html.parser")
    elementos = soup.find_all("a", class_="category-item-link")
    urls_completas = [base_url + elemento.get('href') for elemento in elementos if elemento.get('href')]
    return urls_completas
    
def extraer_url_categorias_especifico(html, base_url="https://www.dia.es"):
    soup = BeautifulSoup(html, "html.parser")
    elementos = soup.find_all("a", class_="basic-section-l1__category")
    urls_completas = [base_url + elemento.get('href') for elemento in elementos if elemento.get('href')]
    return urls_completas

def extraer_url_productos(html, base_url="https://www.dia.es"):
    soup = BeautifulSoup(html, "html.parser")
    elementos = soup.find_all("a", class_="search-product-card__product-link")
    urls_completas = [base_url + elemento.get('href') for elemento in elementos if elemento.get('href')]
    return urls_completas
        

def normalizar_clave(texto):
    # Elimina tildes y pasa a minúsculas
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8').lower()
    # Reemplaza espacios y guiones por "_"
    texto = re.sub(r'[\s\-]+', '_', texto)
    # Elimina cualquier carácter que no sea letra, número o "_"
    texto = re.sub(r'[^\w_]', '', texto)
    return texto

def extraer_info_nutricional(html):
    soup = BeautifulSoup(html, "html.parser")
    nutritional_container = soup.find("div", class_="nutritional-values") 
    name_tag = soup.find("h1", class_="product-title")
    ingredients_tag = soup.find("div", id="html-container")
    price_tag = soup.find("p", class_="buy-box__active-price")
    price_per_unit_tag = soup.find("p", class_="buy-box__price-per-unit")
    name = name_tag.get_text(strip=True) if name_tag else None
    ingredients = ingredients_tag.get_text(strip=True) if ingredients_tag else None
    price = float(re.sub(r'[^0-9.,]', '', price_tag.get_text(strip=True)).replace(',', '.')) if price_tag else None
    price_per_unit = get_price_per_unit(price_per_unit_tag)


    info_nutricional = {}
    if nutritional_container is None:
        return info_nutricional, name, price, price_per_unit, ingredients
    energy_container = nutritional_container.find('div', class_='nutritional-values__title-energy')
    if energy_container:
        energy_values = energy_container.find_all('p', class_='nutritional-values__energy-value')
        if len(energy_values) >= 2:
            info_nutricional['valor_energetico'] = energy_values[1].get_text(strip=True)

    nutritional_items = nutritional_container.find_all('li', class_='nutritional-values__items')
    
    for item in nutritional_items:
        # Extraer título y cantidad principal
        title_elem = item.find('p', {'data-test-id': 'nutritional-list-title'})
        amount_elem = item.find('p', {'data-test-id': 'nutritional-list-amount'})
        
        if title_elem and amount_elem:
            nutriente = {
                'nombre': title_elem.get_text(strip=True),
                'cantidad': amount_elem.get_text(strip=True),
            }
            info_nutricional[nutriente['nombre']] = nutriente['cantidad'].replace(',', '.')
            
            # Extraer subtipos (para extraer azucares)
            subtypes_container = item.find('div', class_='nutritional-types')
            if subtypes_container:
                subtype_items = subtypes_container.find_all('li', class_='nutritional-types__items')
                for subtype in subtype_items:
                    sub_title = subtype.find('p', {'data-test-id': 'nutritional-item-title'})
                    sub_amount = subtype.find('p', {'data-test-id': 'nutritional-item-amount'})
                    
                    if sub_title and sub_amount and (sub_title.get_text(strip=True) != "de los cuales azúcares"): 
                        nutriente = {
                            'nombre': 'azucares',
                            'cantidad': sub_amount.get_text(strip=True)
                        }
                        info_nutricional[nutriente['nombre']] = nutriente['cantidad'].replace(',', '.')

    info_nutricional = {normalizar_clave(k): re.sub(r'[^0-9.,]', '', v) for k, v in info_nutricional.items()}
    return info_nutricional, name, price, price_per_unit, ingredients

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

def scroll_down(driver, scroll_pause_time=1):
    """
    Realiza un scroll hacia abajo en la página.
    """
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def rechazar_cookies(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "onetrust-reject-all-handler"))
    )
    try:
        reject_button = driver.find_element(By.ID, "onetrust-reject-all-handler")
        reject_button.click()
    except Exception as e:
        print(f"Error al hacer clic en el botón de rechazar cookies: {e}")

def click_menu(driver, timeout=10):
    try:
        menu_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".category-button.dia-icon-dehaze"))
        )
        menu_button = driver.find_element(By.CSS_SELECTOR, ".category-button.dia-icon-dehaze")
        menu_button.click()
    except Exception as e:
        print(f"Error al abrir el menú: {e}")

def get_price_per_unit(price_per_unit_tag):
    """Función mejorada para extraer precio por unidad"""
    if not price_per_unit_tag:
        return None
    
    price_text = price_per_unit_tag.get_text(strip=True)
    
    # Buscar patrón de precio (número con decimales)
    price_match = re.search(r'(\d+[.,]\d+)', price_text)
    if not price_match:
        return None
    
    try:
        price = float(price_match.group(1).replace(',', '.'))
        
        # Si es precio por 100g, convertir a precio por kilo
        if '100' in price_text.upper() and ('GR' in price_text.upper() or 'G' in price_text.upper()):
            price = price * 10
        
        return price
    except ValueError:
        return None