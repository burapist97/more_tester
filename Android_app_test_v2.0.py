import time
import requests
import json
import re
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions import interaction

def send_run_event(test_name, status):
    run_id = "senin_gercek_run_id_degerin"
    url = f"https://dustless-brittani-jangly.ngrok-free.dev/api/v1/agents/runs/{run_id}/event"
    headers = {"Content-Type": "application/json", "Authorization": "felina"}
    payload = {"test_name": test_name, "status": status}
    try:
        requests.post(url, json=payload, headers=headers)
        print(f"[{test_name}] -> {status}")
    except Exception as e:
        pass

# YENİ ZIRHLI AKILLI SEÇİCİ (Çökmelere Karşı Korumalı)
def akilli_element_bulucu(driver, locator):
    locator = str(locator).strip()
    if locator.startswith("//") or locator.startswith("hierarchy"):
        return driver.find_element(by=AppiumBy.XPATH, value=locator)
    
    acc_id_match = re.search(r'"accessibility[-_]id"\s*:\s*"([^"]+)"', locator, re.IGNORECASE) or re.search(r'accessibility id\s*:\s*([^\n]+)', locator, re.IGNORECASE)
    if acc_id_match: return driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value=acc_id_match.group(1).strip())
    
    res_id_match = re.search(r'"resource-id"\s*:\s*"([^"]+)"', locator, re.IGNORECASE) or re.search(r'resource-id\s*:\s*([^\n]+)', locator, re.IGNORECASE)
    if res_id_match: return driver.find_element(by=AppiumBy.ID, value=res_id_match.group(1).strip())
    
    xpath_match = re.search(r'"xpath"\s*:\s*"([^"]+)"', locator, re.IGNORECASE) or re.search(r'xpath\s*:\s*([^\n]+)', locator, re.IGNORECASE)
    if xpath_match: return driver.find_element(by=AppiumBy.XPATH, value=xpath_match.group(1).strip())
    
    return driver.find_element(by=AppiumBy.ID, value=locator)

def ekran_kaydir(driver, yon):
    size = driver.get_window_size()
    start_x = int(size['width'] / 2)
    start_y = int(size['height'] / 2)
    end_x, end_y = start_x, start_y
    if yon == 'down': start_y, end_y = int(size['height'] * 0.75), int(size['height'] * 0.25)
    elif yon == 'up': start_y, end_y = int(size['height'] * 0.25), int(size['height'] * 0.75)
    elif yon == 'right': start_x, end_x = int(size['width'] * 0.25), int(size['width'] * 0.75)
    elif yon == 'left': start_x, end_x = int(size['width'] * 0.75), int(size['width'] * 0.25)
    try:
        actions = ActionChains(driver)
        actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(start_x, start_y)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.pause(0.5)
        actions.w3c_actions.pointer_action.move_to_location(end_x, end_y)
        actions.w3c_actions.pointer_action.pointer_up()
        actions.perform()
    except Exception as e: print(f"Kaydirma hatasi: {e}")

options = UiAutomator2Options()
options.no_reset = True
driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
driver.implicitly_wait(10)

def chronos_adım_1():
    try:
        print('--- CHRONOS_ADIM_1 BAŞLADI ---')
        print('Adım: adım 1 (Tıkla)...')
        akilli_element_bulucu(driver, r'''//android.widget.FrameLayout[@content-desc="Bildirimler"]''').click()
        time.sleep(1)
        print('Adım: adım 2 (Metin Yaz)...')
        kutu = akilli_element_bulucu(driver, r'''//android.widget.EditText[@resource-id="com.fbiego.chronos:id/notificationText"]''')
        kutu.clear(); kutu.send_keys('5555'); time.sleep(1)
        print('Adım: adım 3 (Sistem Tuşu)...')
        driver.press_keycode(3)
        send_run_event('chronos_adım_1', 'Passed')
    except Exception as e:
        print(f'Hata: {e}')
        send_run_event('chronos_adım_1', 'Failed')

try:
    chronos_adım_1()
finally:
    driver.quit()


# --- IDE_METADATA_START ---
# {"platform": "Android", "app_pkg": "", "app_act": "", "bundle_id": "com.apple.Preferences", "cases": [{"name": "chronos_ad\u0131m_1", "steps": [{"step_name": "ad\u0131m 1", "action": "T\u0131kla", "xpath": "//android.widget.FrameLayout[@content-desc=\"Bildirimler\"]", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "ad\u0131m 2", "action": "Metin Yaz", "xpath": "//android.widget.EditText[@resource-id=\"com.fbiego.chronos:id/notificationText\"]", "val": "5555", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "ad\u0131m 3", "action": "Sistem Tu\u015fu", "xpath": "", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Ana Sayfa"}]}]}
