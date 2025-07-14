from bs4 import BeautifulSoup

def parsear_informacion_nutricional(html):
    """
    Parsea la información nutricional de un producto desde HTML
    
    Args:
        html (str): HTML que contiene la información nutricional
        
    Returns:
        dict: Diccionario con la información nutricional estructurada
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # Buscar el contenedor principal
    nutritional_container = soup.find('div', class_='nutritional-values')
    
    if not nutritional_container:
        return None
    
    # Inicializar el diccionario de resultados
    info_nutricional = {}
    
    # Extraer título y cantidad de referencia
    title_element = nutritional_container.find('p', {'data-test-id': 'nutritional-info-title'})
    amount_element = nutritional_container.find('p', {'data-test-id': 'nutritional-info-amount'})
    
    if title_element:
        info_nutricional['titulo'] = title_element.get_text(strip=True)
    if amount_element:
        info_nutricional['cantidad_referencia'] = amount_element.get_text(strip=True)
    
    # Extraer valor energético
    energy_container = nutritional_container.find('div', class_='nutritional-values__title-energy')
    if energy_container:
        energy_values = energy_container.find_all('p', class_='nutritional-values__energy-value')
        if len(energy_values) >= 2:
            info_nutricional['valor_energetico'] = {
                'kj': energy_values[0].get_text(strip=True),
                'kcal': energy_values[1].get_text(strip=True)
            }
    
    # Extraer valores nutricionales principales
    nutritional_items = nutritional_container.find_all('li', class_='nutritional-values__items')
    info_nutricional['valores'] = []
    
    for item in nutritional_items:
        # Extraer título y cantidad principal
        title_elem = item.find('p', {'data-test-id': 'nutritional-list-title'})
        amount_elem = item.find('p', {'data-test-id': 'nutritional-list-amount'})
        
        if title_elem and amount_elem:
            nutriente = {
                'nombre': title_elem.get_text(strip=True),
                'cantidad': amount_elem.get_text(strip=True),
                'subtipos': []
            }
            
            # Extraer subtipos (como "de las cuales saturadas")
            subtypes_container = item.find('div', class_='nutritional-types')
            if subtypes_container:
                subtype_items = subtypes_container.find_all('li', class_='nutritional-types__items')
                for subtype in subtype_items:
                    sub_title = subtype.find('p', {'data-test-id': 'nutritional-item-title'})
                    sub_amount = subtype.find('p', {'data-test-id': 'nutritional-item-amount'})
                    
                    if sub_title and sub_amount:
                        nutriente['subtipos'].append({
                            'nombre': sub_title.get_text(strip=True),
                            'cantidad': sub_amount.get_text(strip=True)
                        })
            
            info_nutricional['valores'].append(nutriente)
    
    return info_nutricional

def mostrar_informacion_nutricional(info):
    """
    Muestra la información nutricional de forma legible
    """
    if not info:
        print("No se encontró información nutricional")
        return
    
    print(f"=== {info.get('titulo', 'Información Nutricional')} ===")
    print(f"Referencia: {info.get('cantidad_referencia', 'N/A')}")
    
    if 'valor_energetico' in info:
        energia = info['valor_energetico']
        print(f"Valor energético: {energia.get('kj', 'N/A')} / {energia.get('kcal', 'N/A')}")
    
    print("\n--- Valores nutricionales ---")
    for valor in info.get('valores', []):
        print(f"{valor['nombre']}: {valor['cantidad']}")
        
        for subtipo in valor.get('subtipos', []):
            print(f"  - {subtipo['nombre']}: {subtipo['cantidad']}")
    
    print()

# Ejemplo de uso
if __name__ == "__main__":
    # Tu HTML de ejemplo
    html_ejemplo = """
    <div class="nutritional-values" data-test-id="nutritional-list-values">
        <div class="nutritional-values__title">
            <p class="nutritional-values__title-description" data-test-id="nutritional-info-title">Valor nutricional</p>
            <p class="nutritional-values__title-amount" data-test-id="nutritional-info-amount">Valores por 100g </p>
        </div>
        <div class="nutritional-values__title-energy">
            <p class="nutritional-values__title-energy--description">Valor energético</p>
            <div class="nutritional-values__title-energy--amount" data-test-id="nutritional-info-energy">
                <p class="nutritional-values__energy-value">583kJ</p>
                <span class="nutritional-values__separator" data-test-id="nutritional-values-separator">/</span>
                <p class="nutritional-values__energy-value">139kcal</p>
            </div>
        </div>
        <ul class="nutritional-values__list">
            <li class="nutritional-values__items">
                <p class="nutritional-values__items-title" data-test-id="nutritional-list-title">Grasas</p>
                <p class="nutritional-values__items-amount" data-test-id="nutritional-list-amount">3,5g</p>
                <div class="nutritional-types" data-test-id="nutritional-item-types">
                    <ul class="nutritional-types__list">
                        <li class="nutritional-types__items">
                            <p class="nutritional-types__items-title" data-test-id="nutritional-item-title">de las cuales saturadas</p>
                            <p class="nutritional-types__items-amount" data-test-id="nutritional-item-amount">0,4g</p>
                        </li>
                    </ul>
                </div>
            </li>
            <li class="nutritional-values__items">
                <p class="nutritional-values__items-title" data-test-id="nutritional-list-title">Hidratos de Carbono</p>
                <p class="nutritional-values__items-amount" data-test-id="nutritional-list-amount">23g</p>
                <div class="nutritional-types" data-test-id="nutritional-item-types">
                    <ul class="nutritional-types__list">
                        <li class="nutritional-types__items">
                            <p class="nutritional-types__items-title" data-test-id="nutritional-item-title">de los cuales azúcares</p>
                            <p class="nutritional-types__items-amount" data-test-id="nutritional-item-amount">0,5g</p>
                        </li>
                    </ul>
                </div>
            </li>
            <li class="nutritional-values__items">
                <p class="nutritional-values__items-title" data-test-id="nutritional-list-title">Proteínas</p>
                <p class="nutritional-values__items-amount" data-test-id="nutritional-list-amount">2,5g</p>
            </li>
            <li class="nutritional-values__items">
                <p class="nutritional-values__items-title" data-test-id="nutritional-list-title">Sal</p>
                <p class="nutritional-values__items-amount" data-test-id="nutritional-list-amount">0,1g</p>
            </li>
        </ul>
    </div>
    """
    
    # Parsear la información
    info = parsear_informacion_nutricional(html_ejemplo)
    
    # Mostrar resultado
    mostrar_informacion_nutricional(info)
    
    # También puedes acceder a los datos directamente
    print("Datos estructurados:")
    print(info)