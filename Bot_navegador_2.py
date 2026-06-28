from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import procesador_datos as analista
import time

#(Configuración de Options y Traje de Invisibilidad igual que antes)
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# --- INICIO DEL BLOQUE DE NAVEGACIÓN ---
lista_final = []
pagina = 1

try:
    print("Infiltrándonos en la zona Lenovo de SoloTodo...")
    
    while pagina <= 6:
        print(f"📄 Succionando Página {pagina}...")
        driver.get(f"https://www.solotodo.cl/notebooks?brands=148151&page={pagina}")
        
        # Espera de seguridad para que el JavaScript dibuje las laptops
        time.sleep(10) 

        # Buscamos las tarjetas usando la ruta estructural (XPath)
        tarjetas = driver.find_elements(By.XPATH, "//div[contains(@class, 'MuiCardContent-root')]")
        
        for t in tarjetas:
            try:
                # Extracción quirúrgica de datos
                nombre = t.find_element(By.XPATH, ".//div[contains(@class, 'MuiTypography-h5')]").text
                precio_raw = t.find_element(By.XPATH, ".//div[contains(@class, 'MuiTypography-h2')]").text
                
                # Limpieza Mentalidad M4: convertimos a número para tus finanzas
                precio_limpio = int(precio_raw.replace("$", "").replace(".", ""))

                lista_final.append({
                    "Modelo": nombre, 
                    "Precio_CLP": precio_limpio, 
                    "Fecha": time.strftime("%d/%m/%Y")
                })
                print(f"Capturado: {nombre} | {precio_raw}")
            except:
                # Si una tarjeta falla, el bot salta a la siguiente sin detenerse
                continue
        
        pagina += 1 # Saltamos a la siguiente página

    # Al terminar el bucle, refinamos los datos
    if lista_final:
        df_sucio = pd.DataFrame(lista_final)
        print(f"\n Succión completa. Enviando {len(lista_final)} equipos a la refinería...")
        analista.limpiar_y_clasificar(df_sucio, "REPORTE_LENOVO_CHILE.xlsx")
        print("Proceso finalizado con éxito.")
    
    driver.quit() # Cerramos el búnker y liberamos RAM

except Exception as e:
    print(f"Error en la operación: {e}")
    driver.quit() # También cerramos si hay error para no dejar procesos basura