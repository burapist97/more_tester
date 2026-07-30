# --- SAĞ TARAF: ÜRETİLEN PYTHON KODU ---
with col_code:
    st.subheader(f"📄 Üretilen Python Kodu ({st.session_state.platform})")
    
    gen_code = f"""import time
import requests
import json
import re
import os
import threading
import logging
from datetime import datetime, timezone
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions import interaction

logger = logging.getLogger(__name__)

# --- CLOUD API LOGGER ENTEGRASYONU (ASENKRON & SINGLETON) ---
_api_logger_instance = None

class APILogger:
    def __init__(self, run_id=None, agent_id=None):
        self.run_id = run_id or os.getenv("RUN_ID", "default_run")
        self.agent_id = agent_id or os.getenv("AGENT_ID", "qa_agent")
        
        base_url = os.getenv("PUBLIC_BASE_URL")
        self.base_url = f"{{base_url}}/api/v1" if base_url else None
        
        self.headers = {{
            "Content-Type": "application/json",
            "x-runner-shared-secret": os.getenv("RUNNER_SHARED_SECRET"),
        }}
        self.headers = {{k: v for k, v in self.headers.items() if v is not None}}
        
        self.seq = 0
        self.step = 0
        self.start_time = datetime.now()

    def _post_async(self, url, payload, headers):
        try:
            requests.post(url, json=payload, headers=headers, timeout=5)
        except Exception as e:
            logger.error(f"Event gönderilemedi: {{e}}")

    def send_event(self, event_type, detail):
        self.step += 1
        self.seq += 1
        
        formatted_detail = f"[Adım {{self.step}}] {{detail}}" if detail and not detail.startswith("[Adım") else detail
        
        if not self.base_url: return False
            
        url = f"{{self.base_url}}/agents/runs/{{self.run_id}}/event"
        payload = {{
            "ok": True,
            "runEvent": {{
                "runId": self.run_id,
                "agentId": self.agent_id,
                "type": event_type,
                "payload": {{"detail": formatted_detail}},
                "is": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
                "seq": self.seq,
            }}
        }}
        
        threading.Thread(target=self._post_async, args=(url, payload, self.headers), daemon=True).start()
        print(f"[EVENT] {{event_type}}: {{formatted_detail}}")
        return True

    def log_step_passed(self, desc): self.send_event("step_passed", desc)
    def log_message(self, msg): self.send_event("log", msg)
    def log_test_app_launched(self, app): self.send_event("test_app_launched", f"{{app}} test app has started")

    def save_step_count_to_config(self):
        config_dir = "config"
        os.makedirs(config_dir, exist_ok=True)
        config_file = os.path.join(config_dir, f"step_count_{{self.run_id}}.json")
        
        duration = datetime.now() - self.start_time
        data = {{
            "total_steps": self.step,
            "duration_seconds": duration.total_seconds(),
            "run_id": self.run_id
        }}
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

def get_api_logger(run_id=None, agent_id=None):
    global _api_logger_instance
    if _api_logger_instance is None:
        _api_logger_instance = APILogger(run_id, agent_id)
    return _api_logger_instance

api_logger = get_api_logger()

def akilli_element_bulucu(driver, locator):
    locator = str(locator).strip()
    if not locator: raise Exception("Hedef veri (XPath/ID) bos birakilmis!")
    
    if locator.count("/") > 3 and "android.widget" in locator:
        son_dugum = locator.split("/")[-1]
        if ("@" in son_dugum) and (son_dugum.startswith("android.") or son_dugum.startswith("android.widget.")):
            locator = "//" + son_dugum

    if ("[@content-desc=" in locator or "[@text=" in locator) and ("'" in locator or '"' in locator):
        try:
            attr_part = locator.split("[@")[1].split("=")[0]
            val_part = locator.split("=")[1].split("]")[0].replace('"', '').replace("'", "")
            if len(val_part) > 12 or " " in val_part:
                kelimeler = re.findall(r'[\\wİıÖöÜüŞşÇçĞğ]+', val_part)
                if kelimeler:
                    secilen = sorted([k for k in kelimeler if len(k) >= 4], key=len, reverse=True)[0]
                    locator = f"//*[contains(@{{attr_part}}, '{{secilen}}')]"
        except: pass
    
    if locator.startswith("//") or locator.startswith("(") or locator.startswith("hierarchy"):
        return driver.find_element(by=AppiumBy.XPATH, value=locator)
    return driver.find_element(by=AppiumBy.ID, value=locator)

def ekran_kaydir(driver, yon, x=0, y=0):
    size = driver.get_window_size()
    merkez_x = x if x > 0 else int(size['width'] * 0.05) if yon in ['down', 'up'] else int(size['width'] / 2)
    merkez_y = y if y > 0 else int(size['height'] / 2) if yon in ['down', 'up'] else int(size['height'] * 0.1)
    
    start_x, start_y, end_x, end_y = merkez_x, merkez_y, merkez_x, merkez_y
    x_offset, y_offset = int(size['width'] * 0.25), int(size['height'] * 0.25)
    
    if yon == 'down': start_y += y_offset; end_y -= y_offset
    elif yon == 'up': start_y -= y_offset; end_y += y_offset
    elif yon == 'right': start_x -= x_offset; end_x += x_offset
    elif yon == 'left': start_x += x_offset; end_x -= x_offset

    try:
        actions = ActionChains(driver)
        actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(start_x, start_y)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.pause(0.05) 
        actions.w3c_actions.pointer_action.move_to_location(end_x, end_y)
        actions.w3c_actions.pointer_action.pointer_up()
        actions.perform()
    except Exception as e: print(f"Kaydirma hatasi: {{e}}")

"""
    if st.session_state.platform == "Android":
        gen_code += "options = UiAutomator2Options()\n"
        if st.session_state.app_pkg: gen_code += f"options.app_package = '{st.session_state.app_pkg}'\n"
        if st.session_state.app_act: gen_code += f"options.app_activity = '{st.session_state.app_act}'\n"
    else:
        gen_code += "options = XCUITestOptions()\n"
        if st.session_state.bundle_id: gen_code += f"options.bundle_id = '{st.session_state.bundle_id}'\n"
        
    gen_code += "options.no_reset = True\n"
    gen_code += "executor = os.getenv('COMMAND_EXECUTOR', 'http://127.0.0.1:4723')\n"
    gen_code += "driver = webdriver.Remote(executor, options=options)\n"
    gen_code += "driver.implicitly_wait(10)\n\n"

    calls = []
    for case in st.session_state.cases:
        c_name = case["name"]
        calls.append(f"    {c_name}()")
        gen_code += f"def {c_name}():\n    try:\n        api_logger.log_message('--- {c_name.upper()} BAŞLADI ---')\n"
        for s_idx, step in enumerate(case["steps"]):
            act = step["action"]
            s_name = step.get("step_name", f"Adım {s_idx+1}").replace("'", "\\'")
            xp = step.get('xpath', '')
            exact = step.get('exact_match', False)
            
            if act == "Başlık / Yorum":
                gen_code += f"\n        # --- {step.get('val', '')} ---\n"
                gen_code += f"        api_logger.log_message('{step.get('val', '')}')\n"
                continue
                
            gen_code += f"        api_logger.log_message('Adım başlatılıyor: {s_name}...')\n"
            
            def get_finder(xpath, exact_match):
                if exact_match:
                    return f"driver.find_element(by=AppiumBy.XPATH, value=r'''{xpath}''')"
                return f"akilli_element_bulucu(driver, r'''{xpath}''')"
            
            if act == "Tıkla":
                if step.get("x", 0) > 0 or step.get("y", 0) > 0:
                    gen_code += f"        driver.tap([({step['x']}, {step['y']})])\n        time.sleep(1)\n"
                else:
                    gen_code += f"        {get_finder(xp, exact)}.click()\n        time.sleep(1)\n"
                    
            elif act == "Metin Yaz":
                safe_val = step.get("val", "").replace("'", "\\'")
                gen_code += f"        kutu = {get_finder(xp, exact)}\n"
                gen_code += f"        kutu.click(); time.sleep(0.5)\n" 
                gen_code += f"        kutu.clear(); kutu.send_keys('{safe_val}'); time.sleep(1)\n"
                
            elif act == "Güvenli Metin Yaz (Fiziksel)":
                safe_val = step.get("val", "").replace("'", "\\'")
                d_count = step.get("count", 10)
                gen_code += f"        kutu = {get_finder(xp, exact)}\n"
                gen_code += f"        kutu.click(); time.sleep(0.5)\n"
                gen_code += f"        driver.press_keycode(123) # İmleci sona al\n"
                gen_code += f"        for _ in range({d_count}): driver.press_keycode(67) # SİL\n"
                gen_code += f"        time.sleep(0.5)\n"
                gen_code += f"        for rakam in '{safe_val}':\n"
                gen_code += f"            driver.press_keycode(int(rakam) + 7)\n"
                gen_code += f"            time.sleep(0.2)\n"
                gen_code += f"        time.sleep(1)\n"

            elif act == "Sistem Tuşu":
                sk = step.get("sys_key", "")
                if sk == "Klavyeyi Kapat": gen_code += "        try: driver.hide_keyboard()\n        except: pass\n"
                elif sk == "Geri": gen_code += "        driver.press_keycode(4)\n"
                elif sk == "Ana Sayfa": gen_code += "        driver.press_keycode(3)\n"
                elif sk == "Kutuyu Temizle":
                    gen_code += f"        kutu = {get_finder(xp, exact)}\n"
                    gen_code += f"        kutu.clear(); time.sleep(1)\n"
                elif sk == "Fiziksel Sil (Backspace)":
                    d_count = step.get("count", 10)
                    gen_code += f"        kutu = {get_finder(xp, exact)}\n"
                    gen_code += f"        kutu.click(); time.sleep(0.5)\n"
                    gen_code += f"        driver.press_keycode(123)\n"
                    gen_code += f"        for _ in range({d_count}): driver.press_keycode(67)\n        time.sleep(1)\n"

            elif act == "Kaydır (Swipe)":
                s_dir = {"Aşağı": "down", "Yukarı": "up", "Sağa": "right", "Sola": "left"}.get(step.get('direction','Aşağı'))
                sx, sy = step.get('x', 0), step.get('y', 0)
                gen_code += f"        for _ in range({step.get('count',1)}):\n            ekran_kaydir(driver, '{s_dir}', {sx}, {sy})\n            time.sleep(0.5)\n"
            
            elif act == "Bekle (Sleep)":
                gen_code += f"        time.sleep({step.get('val',1)})\n"
                
            gen_code += f"        api_logger.log_step_passed('{s_name}')\n"
                
        gen_code += f"        api_logger.log_message('{c_name} Başarıyla Tamamlandı')\n    except Exception as e:\n        api_logger.log_message(f'HATA: {{e}}')\n\n"
    
    gen_code += "try:\n" + ("\n".join(calls) if calls else "    pass") + "\nfinally:\n    api_logger.save_step_count_to_config()\n    driver.quit()\n"

    export_metadata = json.dumps({
        "platform": st.session_state.platform,
        "app_pkg": st.session_state.app_pkg, 
        "app_act": st.session_state.app_act, 
        "bundle_id": st.session_state.bundle_id,
        "cases": st.session_state.cases
    })
    gen_code += f"\n\n# --- IDE_METADATA_START ---\n# {export_metadata}\n"

    st.code(gen_code, language="python")
    
    st.divider()
    
    if st.session_state.export_state == 0:
        if st.button("📤 Kodu Dışa Aktar (Export)", use_container_width=True, type="primary"):
            st.session_state.export_state = 1
            st.rerun()
            
    elif st.session_state.export_state == 1:
        st.info("İndirmek istediğiniz dosyanın adını belirleyin:")
        c_name_col, c_btn_col = st.columns([6, 4])
        with c_name_col:
            st.session_state.out_filename = st.text_input("Dosya Adı:", value=st.session_state.out_filename, label_visibility="collapsed")
        with c_btn_col:
            if st.button("⚙️ İndirmeye Hazırla", use_container_width=True):
                st.session_state.export_state = 2
                st.rerun()
                
    elif st.session_state.export_state == 2:
        final_name = st.session_state.out_filename
        if not final_name.endswith(".py"): final_name += ".py"
        st.success(f"✅ Dosya hazırlandı: **{final_name}**")
        st.download_button("📥 İndirmeyi Başlat", data=gen_code, file_name=final_name, mime="text/x-python", use_container_width=True)
        if st.button("❌ İptal Et", use_container_width=True):
            st.session_state.export_state = 0
            st.rerun()