import requests
import json

def extraer_paths_dia(url):
    """
    Extrae todos los paths de la API de Dia
    
    Args:
        url (str): URL de la API de Dia
        
    Returns:
        list: Lista de paths encontrados
    """
    try:
        # Realizar petición GET
        response = requests.get(url)
        response.raise_for_status()
        
        # Parsear JSON
        data = response.json()
        
        # Lista para almacenar todos los paths
        paths = []
        
        # Navegar por la estructura: menu_analytics > L(numero) > children > L(numero) > path
        menu_analytics = data.get('menu_analytics', {})
        
        # Recorrer todos los elementos L(numero) en menu_analytics
        for key, value in menu_analytics.items():
            if key.startswith('L') and isinstance(value, dict):
                print(f"Procesando categoría: {key}")
                
                # Buscar children en este nivel
                children = value.get('children', {})
                
                # Recorrer todos los elementos L(numero) en children
                for child_key, child_value in children.items():
                    if child_key.startswith('L') and isinstance(child_value, dict):
                        # Buscar el path
                        path = child_value.get('path')
                        if path:
                            paths.append({
                                'categoria_padre': key,
                                'categoria_hijo': child_key,
                                'path': path
                            })
                            print(f"  - {child_key}: {path}")
        
        return paths
        
    except requests.exceptions.RequestException as e:
        print(f"Error en la petición: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error al parsear JSON: {e}")
        return []
    except Exception as e:
        print(f"Error inesperado: {e}")
        return []

def extraer_solo_paths(url):
    """
    Extrae solo los paths como lista simple
    
    Args:
        url (str): URL de la API de Dia
        
    Returns:
        list: Lista simple de paths
    """
    paths_completos = extraer_paths_dia(url)
    return [item['path'] for item in paths_completos]

def mostrar_estructura_json(url):
    """
    Muestra la estructura del JSON para debugging
    """
    try:
        response = requests.get(url)
        data = response.json()
        
        print("=== ESTRUCTURA DEL JSON ===")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:1000] + "...")
        
    except Exception as e:
        print(f"Error: {e}")

# Ejemplo de uso
if __name__ == "__main__":
    url = "https://www.dia.es/api/v1/plp-insight/initial_analytics/l1/L125"
    
    print("=== EXTRAYENDO PATHS ===")
    paths = extraer_paths_dia(url)
    
    print(f"\n=== RESULTADOS ({len(paths)} paths encontrados) ===")
    for item in paths:
        print(f"Padre: {item['categoria_padre']} | Hijo: {item['categoria_hijo']} | Path: {item['path']}")
    
    print(f"\n=== SOLO PATHS ===")
    solo_paths = extraer_solo_paths(url)
    for path in solo_paths:
        print(path)
    
    # Descomenta para ver la estructura completa del JSON
    # mostrar_estructura_json(url)