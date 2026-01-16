"""
Script para eliminar emails desde la bandeja de recibidos en Gmail desde la web.
Requiere: pip install selenium webdriver-manager
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import getpass


class GmailEmailDeleter:
    def __init__(self, email=None, password=None, headless=False):
        """
        Inicializa el eliminador de emails de Gmail.
        
        Args:
            email: Email de Gmail (opcional, se pedirá si no se proporciona)
            password: Contraseña de Gmail (opcional, se pedirá si no se proporciona)
            headless: Si True, ejecuta el navegador en modo headless
        """
        self.email = email
        self.password = password
        self.driver = None
        self.headless = headless
        
    def setup_driver(self):
        """Configura el driver de Chrome."""
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.maximize_window()
        
    def login(self):
        """Inicia sesión en Gmail."""
        if not self.email:
            self.email = input("Ingresa tu email de Gmail: ")
        if not self.password:
            self.password = getpass.getpass("Ingresa tu contraseña de Gmail: ")
        
        print("Abriendo Gmail...")
        self.driver.get("https://mail.google.com")
        
        try:
            # Esperar a que aparezca el campo de email
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "identifierId"))
            )
            email_input.send_keys(self.email)
            email_input.send_keys(Keys.RETURN)
            time.sleep(2)
            
            # Esperar a que aparezca el campo de contraseña
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_input.send_keys(self.password)
            password_input.send_keys(Keys.RETURN)
            
            # Esperar a que cargue Gmail
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[role='main']"))
            )
            print("Sesión iniciada correctamente.")
            time.sleep(3)
            
        except Exception as e:
            print(f"Error durante el inicio de sesión: {e}")
            print("Puede que necesites verificar manualmente o usar autenticación de dos factores.")
            raise
    
    def select_all_emails(self):
        """Selecciona todos los emails visibles en la bandeja de entrada."""
        try:
            # Buscar el checkbox para seleccionar todos
            # Primero intentar con el selector más común
            select_all = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[role='checkbox'][aria-label*='Seleccionar'], [role='checkbox'][aria-label*='Select']"))
            )
            select_all.click()
            time.sleep(1)
            print("Todos los emails seleccionados.")
            return True
        except Exception as e:
            print(f"No se pudo seleccionar todos automáticamente: {e}")
            print("Intenta seleccionar manualmente los emails que deseas eliminar.")
            return False
    
    def delete_selected_emails(self, max_emails=None):
        """
        Elimina los emails seleccionados.
        
        Args:
            max_emails: Número máximo de emails a eliminar (None = todos los seleccionados)
        """
        try:
            deleted_count = 0
            
            while True:
                # Buscar el botón de eliminar
                delete_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[aria-label*='Eliminar'], [aria-label*='Delete'], [title*='Eliminar'], [title*='Delete']"))
                )
                delete_button.click()
                time.sleep(2)
                deleted_count += 1
                
                if max_emails and deleted_count >= max_emails:
                    print(f"Se eliminaron {deleted_count} emails (límite alcanzado).")
                    break
                
                # Verificar si hay más emails seleccionados
                try:
                    self.driver.find_element(By.CSS_SELECTOR, "[role='checkbox'][aria-checked='true']")
                except:
                    print(f"Se eliminaron {deleted_count} emails.")
                    break
                    
        except Exception as e:
            print(f"Error al eliminar emails: {e}")
            print(f"Total eliminados antes del error: {deleted_count}")
    
    def delete_emails_by_criteria(self, sender=None, subject_contains=None, max_emails=None):
        """
        Elimina emails según criterios específicos.
        
        Args:
            sender: Email del remitente a filtrar
            subject_contains: Texto que debe contener el asunto
            max_emails: Número máximo de emails a eliminar
        """
        try:
            # Navegar a la bandeja de entrada si no estamos ahí
            self.driver.get("https://mail.google.com/mail/u/0/#inbox")
            time.sleep(3)
            
            deleted_count = 0
            email_elements = self.driver.find_elements(By.CSS_SELECTOR, "tr.zA")
            
            for email in email_elements:
                if max_emails and deleted_count >= max_emails:
                    break
                
                try:
                    # Verificar criterios
                    should_delete = True
                    
                    if sender:
                        sender_text = email.find_element(By.CSS_SELECTOR, "span.y2").text
                        if sender.lower() not in sender_text.lower():
                            should_delete = False
                    
                    if subject_contains and should_delete:
                        try:
                            subject_text = email.find_element(By.CSS_SELECTOR, "span.bog").text
                            if subject_contains.lower() not in subject_text.lower():
                                should_delete = False
                        except:
                            pass
                    
                    if should_delete:
                        # Seleccionar el email
                        checkbox = email.find_element(By.CSS_SELECTOR, "[role='checkbox']")
                        checkbox.click()
                        time.sleep(0.5)
                        deleted_count += 1
                        
                except Exception as e:
                    continue
            
            # Eliminar los emails seleccionados
            if deleted_count > 0:
                self.delete_selected_emails()
            else:
                print("No se encontraron emails que coincidan con los criterios.")
                
        except Exception as e:
            print(f"Error al eliminar emails por criterios: {e}")
    
    def delete_all_inbox_emails(self, confirm=True):
        """
        Elimina todos los emails de la bandeja de entrada.
        
        Args:
            confirm: Si True, requiere confirmación antes de eliminar
        """
        if confirm:
            response = input("¿Estás seguro de que quieres eliminar TODOS los emails de la bandeja de entrada? (sí/no): ")
            if response.lower() not in ['sí', 'si', 'yes', 'y', 's']:
                print("Operación cancelada.")
                return
        
        try:
            # Navegar a la bandeja de entrada
            self.driver.get("https://mail.google.com/mail/u/0/#inbox")
            time.sleep(3)
            
            # Seleccionar todos los emails
            if self.select_all_emails():
                # Eliminar
                self.delete_selected_emails()
            else:
                print("No se pudieron seleccionar los emails automáticamente.")
                
        except Exception as e:
            print(f"Error al eliminar todos los emails: {e}")
    
    def close(self):
        """Cierra el navegador."""
        if self.driver:
            self.driver.quit()
            print("Navegador cerrado.")


def main():
    """Función principal para ejecutar el script."""
    print("=" * 50)
    print("Script de eliminación de emails de Gmail")
    print("=" * 50)
    print("\nOpciones:")
    print("1. Eliminar todos los emails de la bandeja de entrada")
    print("2. Eliminar emails por remitente")
    print("3. Eliminar emails por texto en el asunto")
    print("4. Eliminar emails manualmente (selección manual)")
    
    opcion = input("\nSelecciona una opción (1-4): ")
    
    # Inicializar el eliminador
    deleter = GmailEmailDeleter()
    
    try:
        deleter.setup_driver()
        deleter.login()
        
        if opcion == "1":
            deleter.delete_all_inbox_emails(confirm=True)
        elif opcion == "2":
            sender = input("Ingresa el email del remitente a filtrar: ")
            max_emails = input("Número máximo de emails a eliminar (Enter para todos): ")
            max_emails = int(max_emails) if max_emails else None
            deleter.delete_emails_by_criteria(sender=sender, max_emails=max_emails)
        elif opcion == "3":
            subject = input("Ingresa el texto que debe contener el asunto: ")
            max_emails = input("Número máximo de emails a eliminar (Enter para todos): ")
            max_emails = int(max_emails) if max_emails else None
            deleter.delete_emails_by_criteria(subject_contains=subject, max_emails=max_emails)
        elif opcion == "4":
            print("\nSelecciona manualmente los emails que deseas eliminar en el navegador.")
            input("Presiona Enter cuando hayas terminado de seleccionar...")
            deleter.delete_selected_emails()
        else:
            print("Opción no válida.")
        
        print("\nOperación completada.")
        input("Presiona Enter para cerrar el navegador...")
        
    except KeyboardInterrupt:
        print("\n\nOperación cancelada por el usuario.")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        deleter.close()


if __name__ == "__main__":
    main()
