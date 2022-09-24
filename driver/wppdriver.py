from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions

from driver import chromedriver

import re

class NotLogin(Exception):
    pass

class WhatsAppDriver:
    def __init__(self):
        self.driver = None
    def open(self):
        if not self.driver:
            self.driver = chromedriver.get(self)
    def close(self):
        if self.driver:
            self.driver.close()
            self.driver = None

    def wait_visible(self, element, time=15):
        try:
            return WebDriverWait(self.driver, time).until(EC.visibility_of_element_located((By.XPATH, element)))
        except exceptions.TimeoutException as e:
            raise Exception(f'Element {element} not found') from e
    def wait_invisible(self, element, time=15):
        try:
            return WebDriverWait(self.driver, time).until(EC.invisibility_of_element_located((By.XPATH, element)))
        except exceptions.TimeoutException as e:
            raise Exception(f'Element {element} visible') from e

    def main_page(self):
        #Esperar a que cargue la pagina
        max_tries = 2
        for _ in range(max_tries):
            try:
                self.driver.get("https://web.whatsapp.com/")
                self.wait_visible("//progress", 10)
                print("progress found")
                break
            except Exception:
                #Hay veces que no se carga directamente el whatsapp y hay que cargar primero otra pagina
                print("cant load main page, reloading")
                self.driver.get("https://www.google.com/search?client=firefox-b-d&q=test")

        self.wait_invisible("//progress", 40)
        print("main page load")

    def is_login(self):
        try:
            self.wait_visible('//div[@data-testid="chat-list-search"]', 40)
        except Exception as e:
            raise NotLogin() from e

    #Returns a base64 encoded qr image
    def generate_qr(self):
        self.wait_visible('//div[@data-testid="qrcode"]', 20)
        return self.driver.execute_script('return document.getElementsByTagName("canvas")[0].toDataURL()')

    def consumed(self):
        total_bytes = 0

        performance = self.driver.get_log('performance')

        for entry in performance:
            if "Network.dataReceived" in str(entry):
                r = re.search(r'dataLength\":(.*?),', str(entry))
                total_bytes += int(r.group(1))

        #size in MegaBytes
        return round(float(total_bytes) / (1024 * 1024), 4)

    def get_messages(self):
        #todos los class de mensajes sin leer
        #no aparecen en orden, y no son todos
        containers = self.driver.find_elements(By.XPATH, '//div[@class="_2nY6U vq6sj _3C4Vf"]')

        messages = []
        for container in containers:
            try:
                number = container.find_element(By.XPATH, './/div[@class="zoWT4"]//span')
                text   = container.find_element(By.XPATH, './/span[@class="Hy9nV"]')

                messages.append({
                    "number": re.sub(r" |\+", "", number.get_attribute("title")).encode("ascii", "ignore").decode(),
                    "text": text.get_attribute("title").encode("ascii", "ignore").decode()
                })
            except Exception as e:
                print(e)

        return messages

    def send(self, phone, msg):
        send_url = "https://web.whatsapp.com/send/?phone={phone}&text={text}&app_absent=0"
        print(send_url.format(phone=phone, text="test"))

        max_time = 10
        self.driver.get(send_url.format(phone=phone, text=msg))

        self.is_login()

        self.wait_visible('//div[@data-animate-modal-popup="true"]', max_time)

        self.wait_invisible('//div[@data-testid="popup-controls-cancel"]', max_time)

        try:
            self.driver.find_element(By.XPATH, '//div[@data-testid="popup-controls-ok"]')
            print("boton ok found")
            raise Exception('Number wrong')
        except exceptions.NoSuchElementException:
            pass

        #Find send button and clickit
        self.wait_visible("//button[@data-testid='compose-btn-send']", max_time).click()

        #Wait until the message has sended
        self.wait_invisible('//span[@data-testid="msg-time"]', 15)
