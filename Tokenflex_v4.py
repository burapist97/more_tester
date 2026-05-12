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

def akilli_element_bulucu(driver, locator):
    locator = str(locator).strip()
    if not locator: raise Exception("Hedef veri (XPath/ID) bos birakilmis!")
    
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
    start_x, start_y = int(size['width'] / 2), int(size['height'] / 2)
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
options.app_package = 'com.tokenflexapp.test'
options.app_activity = 'com.tokenflexapp.MainActivity}'
options.no_reset = True
driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
driver.implicitly_wait(10)

try:
    print('Uygulama baslatiliyor / one getiriliyor: com.tokenflexapp.test')
    driver.activate_app('com.tokenflexapp.test')
    time.sleep(3)
except Exception as e:
    print(f'Uygulama baslatma uyarisi: {e}')

def Giriş_Yapılıyor():
    try:
        print('--- GIRIŞ_YAPILIYOR BAŞLADI ---')
        print('Adım: Numara Girişi...')
        kutu = akilli_element_bulucu(driver, r'''//android.widget.EditText[@content-desc="loginPhoneNumberTextInput"]''')
        kutu.clear(); kutu.send_keys('5363463853'); time.sleep(1)
        print('Adım: Bekle: 1 sn...')
        time.sleep(1)
        print('Adım: Tuş: Klavyeyi Kapat...')
        try: driver.hide_keyboard()
        except: pass
        print('Adım: Devam et butonuna tıklanılıyor...')
        akilli_element_bulucu(driver, r'''//android.widget.TextView[@text="Devam et"]''').click()
        time.sleep(1)
        print('Adım: Doğum tarihi giriliyor...')
        kutu = akilli_element_bulucu(driver, r'''//android.widget.EditText[@content-desc="birthdateTextInput"]''')
        kutu.clear(); kutu.send_keys('01012000'); time.sleep(1)
        print('Adım: Tuş: Klavyeyi Kapat...')
        try: driver.hide_keyboard()
        except: pass
        print('Adım: Hesabı aktive et butonuna tıklanılıyor...')
        akilli_element_bulucu(driver, r'''//android.widget.TextView[@text="Hesabını aktive et"]''').click()
        time.sleep(1)
        print('Adım: OTP yazılıyor...')
        kutu = akilli_element_bulucu(driver, r'''//android.widget.EditText[@content-desc="otpCell_1"]''')
        kutu.clear(); kutu.send_keys('1111'); time.sleep(1)
        print('Adım: Bekle: 1 sn...')
        time.sleep(1)
        print('Adım: Tokenkfex yemek butonuna tıklanlılıyor...')
        akilli_element_bulucu(driver, r'''//android.view.ViewGroup[@content-desc="mainDashboardFoodCardButton"]/android.view.ViewGroup/android.widget.ImageView''').click()
        time.sleep(1)
        print('Adım: Tuş: Geri...')
        driver.press_keycode(4)
        print('Adım: Tokenflex mobilite butonuna tıklanılıyor...')
        akilli_element_bulucu(driver, r'''//android.view.ViewGroup[@content-desc="mainDashboardPassageCardButton"]/android.view.ViewGroup/android.widget.ImageView''').click()
        time.sleep(1)
        print('Adım: Tuş: Geri...')
        driver.press_keycode(4)
        print('Adım: Tokenflex hediye butonuna tıklanılır...')
        akilli_element_bulucu(driver, r'''//android.view.ViewGroup[@content-desc="mainDashboardGiftCardButton"]/android.view.ViewGroup/android.widget.ImageView''').click()
        time.sleep(1)
        print('Adım: Tuş: Geri...')
        driver.press_keycode(4)
        print('Adım: Tekrar Tokenflex yemek butonuna tıklanılıyor...')
        akilli_element_bulucu(driver, r'''//android.view.ViewGroup[@content-desc="mainDashboardFoodCardButton"]/android.view.ViewGroup/android.widget.ImageView''').click()
        time.sleep(1)
        print('Adım: Bekle: 2 sn...')
        time.sleep(2)
        print('Adım: Bakiye yükle butonuna tıklanılıyor...')
        akilli_element_bulucu(driver, r'''//android.view.ViewGroup[@content-desc="Bakiye Yükle"]''').click()
        time.sleep(1)
        print('Adım: Geri dönülüyor...')
        akilli_element_bulucu(driver, r'''//android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[1]/android.widget.ImageView''').click()
        time.sleep(1)
        print('Adım: Geri dönülüyor...')
        akilli_element_bulucu(driver, r'''//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[2]/android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[1]/android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup[1]/android.widget.ImageView''').click()
        time.sleep(1)
        print('Adım: Profile giriliyor...')
        akilli_element_bulucu(driver, r'''//android.view.ViewGroup[@content-desc="mainDashboardUserIcon"]''').click()
        time.sleep(1)
        print('Adım: Sözleşmelere tıklanılıyor...')
        akilli_element_bulucu(driver, r'''//android.widget.TextView[@text="Sözleşmeler ve KVKK Metinleri"]''').click()
        time.sleep(1)
        print('Adım: Aydınlatma Metnine tıklanılıyor...')
        akilli_element_bulucu(driver, r'''//android.widget.TextView[@text="Aydınlatma Metni"]''').click()
        time.sleep(1)
        print('Adım: Geri dönülüyor...')
        akilli_element_bulucu(driver, r'''//android.widget.ImageView[@content-desc="contractDetailBackButton"]''').click()
        time.sleep(1)
        print('Adım: Geri dönülüyor...')
        akilli_element_bulucu(driver, r'''//android.widget.ImageView[@content-desc="contractsBackButton"]''').click()
        time.sleep(1)
        print('Adım: Geri dönülüyor...')
        akilli_element_bulucu(driver, r'''//android.widget.ImageView[@content-desc="profileBackButton"]''').click()
        time.sleep(1)
        print('Adım: Kampanyalar görüntüleniyor...')
        akilli_element_bulucu(driver, r'''//android.widget.TextView[@text="Tümü"]''').click()
        time.sleep(1)
        print('Adım: Kampanyalar görüntüleniyor...')
        for _ in range(4):
            ekran_kaydir(driver, 'down')
            time.sleep(0.5)
        print('Adım: Geri dönülüyor...')
        akilli_element_bulucu(driver, r'''//android.widget.ImageView[@content-desc="campaignsAndAnnouncementsBackButton"]''').click()
        time.sleep(1)
        send_run_event('Giriş_Yapılıyor', 'Passed')
    except Exception as e:
        print(f'Hata: {e}')
        send_run_event('Giriş_Yapılıyor', 'Failed')

def Çıkış_Yapılıyor():
    try:
        print('--- ÇIKIŞ_YAPILIYOR BAŞLADI ---')
        print('Adım: Profil butonuna tıklanılıyor...')
        akilli_element_bulucu(driver, r'''//android.view.ViewGroup[@content-desc="mainDashboardUserIcon"]''').click()
        time.sleep(1)
        print('Adım: Oturumu kapat butonuna tıklanılıyor...')
        akilli_element_bulucu(driver, r'''//android.widget.TextView[@text="Oturumu kapat"]''').click()
        time.sleep(1)
        print('Adım: Bu cihazda oturumu kapat butonuna tıklanılıyor...')
        akilli_element_bulucu(driver, r'''//android.widget.TextView[@text="Bu cihazda oturumu kapat"]''').click()
        time.sleep(1)
        print('Adım: Oturum kapatma onaylanıyor...')
        driver.tap([(784, 2122)])
        time.sleep(1)
        print('Adım: Test sonlandı...')
        driver.press_keycode(3)
        send_run_event('Çıkış_Yapılıyor', 'Passed')
    except Exception as e:
        print(f'Hata: {e}')
        send_run_event('Çıkış_Yapılıyor', 'Failed')

try:
    Giriş_Yapılıyor()
    Çıkış_Yapılıyor()
finally:
    driver.quit()


# --- IDE_METADATA_START ---
# {"platform": "Android", "app_pkg": "com.tokenflexapp.test", "app_act": "com.tokenflexapp.MainActivity}", "bundle_id": "", "cases": [{"name": "Giri\u015f_Yap\u0131l\u0131yor", "steps": [{"step_name": "Numara Giri\u015fi", "action": "Metin Yaz", "xpath": "//android.widget.EditText[@content-desc=\"loginPhoneNumberTextInput\"]", "val": "5363463853", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Bekle: 1 sn", "action": "Bekle (Sleep)", "xpath": "", "val": "1", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Tu\u015f: Klavyeyi Kapat", "action": "Sistem Tu\u015fu", "xpath": "", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Klavyeyi Kapat"}, {"step_name": "Devam et butonuna t\u0131klan\u0131l\u0131yor", "action": "T\u0131kla", "xpath": "//android.widget.TextView[@text=\"Devam et\"]", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Do\u011fum tarihi giriliyor", "action": "Metin Yaz", "xpath": "//android.widget.EditText[@content-desc=\"birthdateTextInput\"]", "val": "01012000", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Tu\u015f: Klavyeyi Kapat", "action": "Sistem Tu\u015fu", "xpath": "", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Klavyeyi Kapat"}, {"step_name": "Hesab\u0131 aktive et butonuna t\u0131klan\u0131l\u0131yor", "action": "T\u0131kla", "xpath": "//android.widget.TextView[@text=\"Hesab\u0131n\u0131 aktive et\"]", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "OTP yaz\u0131l\u0131yor", "action": "Metin Yaz", "xpath": "//android.widget.EditText[@content-desc=\"otpCell_1\"]", "val": "1111", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Bekle: 1 sn", "action": "Bekle (Sleep)", "xpath": "", "val": "1", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Tokenkfex yemek butonuna t\u0131klanl\u0131l\u0131yor", "action": "T\u0131kla", "xpath": "//android.view.ViewGroup[@content-desc=\"mainDashboardFoodCardButton\"]/android.view.ViewGroup/android.widget.ImageView", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Tu\u015f: Geri", "action": "Sistem Tu\u015fu", "xpath": "", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Tokenflex mobilite butonuna t\u0131klan\u0131l\u0131yor", "action": "T\u0131kla", "xpath": "//android.view.ViewGroup[@content-desc=\"mainDashboardPassageCardButton\"]/android.view.ViewGroup/android.widget.ImageView", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Tu\u015f: Geri", "action": "Sistem Tu\u015fu", "xpath": "", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Tokenflex hediye butonuna t\u0131klan\u0131l\u0131r", "action": "T\u0131kla", "xpath": "//android.view.ViewGroup[@content-desc=\"mainDashboardGiftCardButton\"]/android.view.ViewGroup/android.widget.ImageView", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Tu\u015f: Geri", "action": "Sistem Tu\u015fu", "xpath": "", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Tekrar Tokenflex yemek butonuna t\u0131klan\u0131l\u0131yor", "action": "T\u0131kla", "xpath": "//android.view.ViewGroup[@content-desc=\"mainDashboardFoodCardButton\"]/android.view.ViewGroup/android.widget.ImageView", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Bekle: 2 sn", "action": "Bekle (Sleep)", "xpath": "", "val": "2", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Bakiye y\u00fckle butonuna t\u0131klan\u0131l\u0131yor", "action": "T\u0131kla", "xpath": "//android.view.ViewGroup[@content-desc=\"Bakiye Y\u00fckle\"]", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Geri d\u00f6n\u00fcl\u00fcyor", "action": "T\u0131kla", "xpath": "//android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[1]/android.widget.ImageView", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Geri d\u00f6n\u00fcl\u00fcyor", "action": "T\u0131kla", "xpath": "//android.widget.FrameLayout[@resource-id=\"android:id/content\"]/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[2]/android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup[1]/android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup[1]/android.widget.ImageView", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Profile giriliyor", "action": "T\u0131kla", "xpath": "//android.view.ViewGroup[@content-desc=\"mainDashboardUserIcon\"]", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "S\u00f6zle\u015fmelere t\u0131klan\u0131l\u0131yor", "action": "T\u0131kla", "xpath": "//android.widget.TextView[@text=\"S\u00f6zle\u015fmeler ve KVKK Metinleri\"]", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Ayd\u0131nlatma Metnine t\u0131klan\u0131l\u0131yor", "action": "T\u0131kla", "xpath": "//android.widget.TextView[@text=\"Ayd\u0131nlatma Metni\"]", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Geri d\u00f6n\u00fcl\u00fcyor", "action": "T\u0131kla", "xpath": "//android.widget.ImageView[@content-desc=\"contractDetailBackButton\"]", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Geri d\u00f6n\u00fcl\u00fcyor", "action": "T\u0131kla", "xpath": "//android.widget.ImageView[@content-desc=\"contractsBackButton\"]", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Geri d\u00f6n\u00fcl\u00fcyor", "action": "T\u0131kla", "xpath": "//android.widget.ImageView[@content-desc=\"profileBackButton\"]", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Kampanyalar g\u00f6r\u00fcnt\u00fcleniyor", "action": "T\u0131kla", "xpath": "//android.widget.TextView[@text=\"T\u00fcm\u00fc\"]", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Kampanyalar g\u00f6r\u00fcnt\u00fcleniyor", "action": "Kayd\u0131r (Swipe)", "xpath": "", "val": "", "count": 4, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Geri d\u00f6n\u00fcl\u00fcyor", "action": "T\u0131kla", "xpath": "//android.widget.ImageView[@content-desc=\"campaignsAndAnnouncementsBackButton\"]", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}]}, {"name": "\u00c7\u0131k\u0131\u015f_Yap\u0131l\u0131yor", "steps": [{"step_name": "Profil butonuna t\u0131klan\u0131l\u0131yor", "action": "T\u0131kla", "xpath": "//android.view.ViewGroup[@content-desc=\"mainDashboardUserIcon\"]", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Oturumu kapat butonuna t\u0131klan\u0131l\u0131yor", "action": "T\u0131kla", "xpath": "//android.widget.TextView[@text=\"Oturumu kapat\"]", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Bu cihazda oturumu kapat butonuna t\u0131klan\u0131l\u0131yor", "action": "T\u0131kla", "xpath": "//android.widget.TextView[@text=\"Bu cihazda oturumu kapat\"]", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Geri"}, {"step_name": "Oturum kapatma onaylan\u0131yor", "action": "T\u0131kla", "xpath": "", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 784, "y": 2122, "sys_key": "Geri"}, {"step_name": "Test sonland\u0131", "action": "Sistem Tu\u015fu", "xpath": "", "val": "", "count": 1, "direction": "A\u015fa\u011f\u0131", "x": 0, "y": 0, "sys_key": "Ana Sayfa"}]}]}
