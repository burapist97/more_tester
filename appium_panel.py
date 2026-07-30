import streamlit as st
import json
import re
import os

st.set_page_config(page_title="Görsel Appium IDE", layout="wide", initial_sidebar_state="expanded")

# --- SCRATCH / BLOCKLY CANLI CSS TASARIMI ---
st.markdown("""
    <style>
    .stApp { background-color: #F4F5F7; }
    
    .s-block {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 700;
        color: white;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 4px;
        box-shadow: inset 0px -3px 0px rgba(0,0,0,0.15), 0px 3px 5px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        gap: 10px;
        width: 100%;
        font-size: 14px;
        border: 1px solid rgba(0,0,0,0.1);
    }
    
    .s-setup { background-color: #0FBD8C; font-size: 16px; border-radius: 10px; margin-bottom: 20px;} 
    .s-case { background-color: #FF6680; font-size: 16px; margin-top: 15px; border-radius: 10px 10px 0 0; } 
    .s-click { background-color: #4C97FF; } 
    .s-type { background-color: #59C059; } 
    .s-secure-type { background-color: #D35400; } /* Maskeli alanlar için yeni renk */
    .s-swipe { background-color: #FFBF00; color: #333; } 
    .s-wait { background-color: #9966FF; } 
    .s-sys { background-color: #8A9BAC; } 
    .s-clear { background-color: #E74C3C; }
    .s-comment { background-color: #34495E; color: #F1C40F; border-left: 5px solid #F1C40F;}
    
    .s-val {
        background: white;
        color: #333;
        border-radius: 16px;
        padding: 4px 12px;
        font-size: 13px;
        font-weight: 600;
        box-shadow: inset 0px 2px 3px rgba(0,0,0,0.15);
        border: 1px solid rgba(0,0,0,0.1);
        margin-left: auto;
        max-width: 300px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .edit-box {
        background-color: #E2E8F0;
        padding: 15px;
        border-radius: 8px;
        margin-top: 2px;
        margin-bottom: 10px;
        border-left: 5px solid #FFBF00;
    }
    </style>
""", unsafe_allow_html=True)

# --- HAFIZA (SESSION STATE) ---
if 'platform' not in st.session_state: st.session_state.platform = "Android"
if 'app_pkg' not in st.session_state: st.session_state.app_pkg = ""
if 'app_act' not in st.session_state: st.session_state.app_act = ""
if 'bundle_id' not in st.session_state: st.session_state.bundle_id = ""
if 'cases' not in st.session_state: st.session_state.cases = []
if 'loaded_file' not in st.session_state: st.session_state.loaded_file = None
if 'editing_step' not in st.session_state: st.session_state.editing_step = None
if 'export_state' not in st.session_state: st.session_state.export_state = 0
if 'out_filename' not in st.session_state: st.session_state.out_filename = "otomasyon_testi"

# --- AKILLI İSİMLENDİRME MOTORU ---
def akilli_isim_uret(action, xpath, val, direction, sys_key, x, y):
    if action == "Tıkla":
        if x > 0 or y > 0: return f"Tıkla ({x},{y})"
        match_text = re.search(r'@text=["\']([^"\']+)["\']', xpath)
        if match_text: return f"Tıkla: {match_text.group(1)}"
        match_id = re.search(r'@resource-id=["\']([^"\']+)["\']', xpath)
        if match_id: return f"Tıkla: {match_id.group(1).split('/')[-1]}"
        match_desc = re.search(r'@content-desc=["\']([^"\']+)["\']', xpath)
        if match_desc: return f"Tıkla: {match_desc.group(1)}"
        if xpath and not xpath.startswith("//") and len(xpath) < 25: return f"Tıkla: {xpath}"
        return "Tıklama Adımı"
    elif action == "Metin Yaz": return f"Yaz: '{val}'"
    elif action == "Güvenli Metin Yaz (Fiziksel)": return f"Güvenli Yaz: '{val}'"
    elif action == "Kaydır (Swipe)": return f"Kaydır: {direction}"
    elif action == "Sistem Tuşu": 
        if sys_key == "Kutuyu Temizle": return "İçeriği Sil"
        if sys_key == "Fiziksel Sil (Backspace)": return "Fiziksel Olarak Sil"
        return f"Tuş: {sys_key}"
    elif action == "Bekle (Sleep)": return f"Bekle: {val} sn"
    elif action == "Başlık / Yorum": return f"--- {val} ---"
    return "Yeni Adım"

# --- SOL MENÜ: AKSİYON KÜTÜPHANESİ ---
with st.sidebar:
    st.header("📂 Proje Yönetimi")
    
    uploaded_file = st.file_uploader("📥 Kayıtlı Testi Yükle (.py)", type="py")
    if uploaded_file is not None:
        if st.session_state.loaded_file != uploaded_file.name:
            try:
                content = uploaded_file.read().decode("utf-8")
                match = re.search(r'# --- IDE_METADATA_START ---\s*#\s*(.*)', content, re.DOTALL)
                if match:
                    meta_string = match.group(1).strip()
                    clean_json = "".join([line.replace("#", "").strip() for line in meta_string.splitlines()])
                    data = json.loads(clean_json)
                    st.session_state.platform = data.get("platform", "Android")
                    st.session_state.app_pkg = data.get("app_pkg", "")
                    st.session_state.app_act = data.get("app_act", "")
                    st.session_state.bundle_id = data.get("bundle_id", "")
                    st.session_state.cases = data.get("cases", [])
                    st.session_state.loaded_file = uploaded_file.name
                    st.success("Test başarıyla yüklendi!")
                    st.rerun()
            except Exception as e: st.error(f"Dosya okunamadı: {e}")
    else:
        st.session_state.loaded_file = None

    st.divider()
    st.header("⚙️ Temel Ayarlar")
    st.session_state.platform = st.radio("Platform Seçimi:", ["Android", "iOS"], index=0 if st.session_state.platform == "Android" else 1)
    
    if st.session_state.platform == "Android":
        st.session_state.app_pkg = st.text_input("App Package:", st.session_state.app_pkg)
        st.session_state.app_act = st.text_input("App Activity:", st.session_state.app_act)
    else:
        st.session_state.bundle_id = st.text_input("Bundle ID:", st.session_state.bundle_id)
    
    st.divider()
    st.header("🧱 Senaryo Ekle")
    case_name = st.text_input("Yeni Case Adı:", placeholder="Örn: para_yukleme_testi")
    if st.button("➕ Yeni Case Oluştur", type="primary", use_container_width=True):
        if case_name:
            st.session_state.cases.append({"name": case_name.replace(" ", "_"), "steps": []})
            st.rerun()

    st.divider()
    if st.session_state.cases:
        st.subheader("🧩 Blok Ekle")
        action = st.selectbox("İşlem Tipi:", [
            "Tıkla", 
            "Metin Yaz", 
            "Güvenli Metin Yaz (Fiziksel)", 
            "Kaydır (Swipe)", 
            "Sistem Tuşu", 
            "Bekle (Sleep)",
            "Başlık / Yorum"
        ])
        step_name = st.text_input("Adım İsmi (Boş: Otomatik):", placeholder="Örn: Ayarlara Tıkla")
        
        xpath, val, count, direction, step_x, step_y, sys_key = "", "", 1, "Aşağı", 0, 0, "Geri"
        exact_match = False
        
        if action in ["Tıkla", "Metin Yaz", "Güvenli Metin Yaz (Fiziksel)"]: 
            xpath = st.text_area("Hedef XPath veya ID:")
            exact_match = st.checkbox("Kesin Eşleşme (Akıllı Bulucuyu Kapat)")
            
            if action == "Tıkla":
                c1, c2 = st.columns(2)
                with c1: step_x = st.number_input("X (Koor):", value=0)
                with c2: step_y = st.number_input("Y (Koor):", value=0)
            else:
                val = st.text_input("Yazılacak Değer (Rakamlar vb):")
                if action == "Güvenli Metin Yaz (Fiziksel)":
                    count = st.number_input("Yazmadan Önce Kaç Karakter Silinsin?", min_value=1, value=10)
            
        elif action == "Kaydır (Swipe)":
            direction = st.selectbox("Yön:", ["Aşağı", "Yukarı", "Sağa", "Sola"])
            count = st.number_input("Tekrar Sayısı:", min_value=1, value=1)
            c1, c2 = st.columns(2)
            with c1: step_x = st.number_input("Merkez X:", value=0)
            with c2: step_y = st.number_input("Merkez Y:", value=0)
            
        elif action == "Sistem Tuşu":
            sys_key = st.selectbox("İşlem:", ["Geri", "Ana Sayfa", "Arka Plan", "Klavyeyi Kapat", "Kutuyu Temizle", "Fiziksel Sil (Backspace)"])
            if sys_key in ["Kutuyu Temizle", "Fiziksel Sil (Backspace)"]:
                xpath = st.text_area("Silinecek Kutu (XPath/ID):")
                exact_match = st.checkbox("Kesin Eşleşme")
                if sys_key == "Fiziksel Sil (Backspace)":
                    count = st.number_input("Kaç Kere Silme Tuşuna Basılsın?", min_value=1, value=10)
                
        elif action == "Bekle (Sleep)": 
            val = st.number_input("Saniye:", min_value=1, value=1)
            
        elif action == "Başlık / Yorum":
            val = st.text_input("Başlık Metni:", placeholder="Örn: --- KART EKLEME ADIMI ---")
            
        # ARAYA EKLEME ÖZELLİĞİ
        insert_options = ["Sona Ekle"] + [f"{i+1}. Adımdan Önce" for i in range(len(st.session_state.cases[-1]["steps"]))]
        insert_idx = st.selectbox("Nereye Eklensin?", insert_options)

        if st.button("⬇️ Aktif Case'e Adım Ekle", use_container_width=True):
            if not step_name:
                step_name = akilli_isim_uret(action, xpath, val, direction, sys_key, step_x, step_y)

            new_step = {
                "step_name": step_name, "action": action, "xpath": xpath, "val": str(val), 
                "count": count, "direction": direction, "x": step_x, "y": step_y, "sys_key": sys_key,
                "exact_match": exact_match
            }
            
            if insert_idx == "Sona Ekle":
                st.session_state.cases[-1]["steps"].append(new_step)
            else:
                idx = int(insert_idx.split(".")[0]) - 1
                st.session_state.cases[-1]["steps"].insert(idx, new_step)
                
            st.rerun()
    
    st.divider()
    if st.button("🗑️ Tüm Tuvali Temizle"):
        st.session_state.cases = []
        st.session_state.loaded_file = None
        st.session_state.editing_step = None
        st.session_state.export_state = 0
        st.rerun()

col_canvas, col_code = st.columns(2)

# --- SOL TARAF: GÖRSEL TUVAL ---
with col_canvas:
    st.subheader("🎨 Görsel Test Tuvali")
    baslat_text = st.session_state.app_pkg if st.session_state.platform == "Android" else st.session_state.bundle_id
    if not baslat_text: baslat_text = "Tüm Cihaz (OS Level)"
    st.markdown(f'<div class="s-block s-setup">▶️ Başlat ({st.session_state.platform}): <span class="s-val">{baslat_text}</span></div>', unsafe_allow_html=True)
    
    for c_idx, case in enumerate(st.session_state.cases):
        col_c_name, col_c_del = st.columns([8, 2])
        with col_c_name: st.markdown(f'<div class="s-block s-case">⚙️ CASE: {case["name"]}</div>', unsafe_allow_html=True)
        with col_c_del:
            st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
            if st.button("🗑️ Sil", key=f"del_c_{c_idx}", use_container_width=True):
                st.session_state.cases.pop(c_idx)
                st.session_state.editing_step = None 
                st.rerun()
                
        for s_idx, step in enumerate(case["steps"]):
            act = step["action"]
            s_name = step.get("step_name", f"Adım {s_idx+1}")
            css, icon, info = "s-sys", "⚙️", ""
            
            if act == "Tıkla": 
                css, icon = "s-click", "👆"
                if step.get("exact_match"): info += " 🔒 Kesin"
            elif act == "Metin Yaz": css, icon = "s-type", "⌨️"
            elif act == "Güvenli Metin Yaz (Fiziksel)": css, icon = "s-secure-type", "🤖"
            elif act == "Kaydır (Swipe)": css, icon = "s-swipe", "↔️"
            elif act == "Bekle (Sleep)": css, icon = "s-wait", "⏳"
            elif act == "Başlık / Yorum": css, icon = "s-comment", "📝"
            elif act == "Sistem Tuşu": 
                if step.get("sys_key") == "Kutuyu Temizle": css, icon = "s-clear", "🧹"
                elif step.get("sys_key") == "Fiziksel Sil (Backspace)": css, icon = "s-clear", "🔙"
                else: css, icon, info = "s-sys", "📱", f'<span class="s-val">{step.get("sys_key", "")}</span>'
            
            xp_disp = f'<span class="s-val">{step.get("xpath", "")[:25]}...</span>' if step.get("xpath") else ""
            val_disp = f'<span class="s-val">{step.get("val", "")}</span>' if step.get("val") and act not in ["Kaydır (Swipe)", "Bekle (Sleep)", "Sistem Tuşu"] else ""
            
            html_block = f'<div class="s-block {css}"><span>{icon} <b>{s_name}</b></span> {info} {xp_disp} {val_disp}</div>'
            
            # --- YENİ ADIM KONTROL BUTONLARI (YUKARI/AŞAĞI) ---
            col_block, col_up, col_down, col_edit, col_del = st.columns([6, 0.8, 0.8, 0.8, 0.8])
            with col_block: st.markdown(html_block, unsafe_allow_html=True)
            with col_up:
                st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
                if st.button("⬆️", key=f"up_{c_idx}_{s_idx}", disabled=(s_idx == 0)):
                    case["steps"][s_idx], case["steps"][s_idx-1] = case["steps"][s_idx-1], case["steps"][s_idx]
                    st.rerun()
            with col_down:
                st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
                if st.button("⬇️", key=f"dw_{c_idx}_{s_idx}", disabled=(s_idx == len(case["steps"])-1)):
                    case["steps"][s_idx], case["steps"][s_idx+1] = case["steps"][s_idx+1], case["steps"][s_idx]
                    st.rerun()
            with col_edit:
                st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
                if st.button("✏️", key=f"edit_btn_{c_idx}_{s_idx}"):
                    st.session_state.editing_step = None if st.session_state.editing_step == f"{c_idx}_{s_idx}" else f"{c_idx}_{s_idx}"
                    st.rerun()
            with col_del:
                st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True) 
                if st.button("🗑️", key=f"del_s_{c_idx}_{s_idx}"):
                    st.session_state.cases[c_idx]["steps"].pop(s_idx)
                    st.session_state.editing_step = None
                    st.rerun()
            
            # DÜZENLEME EKRANI
            if st.session_state.editing_step == f"{c_idx}_{s_idx}":
                st.markdown('<div class="edit-box">', unsafe_allow_html=True)
                step["step_name"] = st.text_input("Adım Adı:", value=step.get("step_name", ""), key=f"edit_name_{c_idx}_{s_idx}")
                
                if act in ["Tıkla", "Metin Yaz", "Güvenli Metin Yaz (Fiziksel)"] or (act == "Sistem Tuşu" and step.get("sys_key") in ["Kutuyu Temizle", "Fiziksel Sil (Backspace)"]):
                    step["xpath"] = st.text_area("Hedef Veri (JSON/XPATH):", value=step.get("xpath", ""), key=f"edit_xp_{c_idx}_{s_idx}")
                    step["exact_match"] = st.checkbox("Kesin Eşleşme (Akıllı Bulucuyu Kapat)", value=step.get("exact_match", False), key=f"edit_exact_{c_idx}_{s_idx}")
                            
                if act in ["Metin Yaz", "Güvenli Metin Yaz (Fiziksel)", "Başlık / Yorum"]:
                    step["val"] = st.text_input("Değer / Metin:", value=step.get("val", ""), key=f"edit_val_{c_idx}_{s_idx}")
                    
                if act in ["Güvenli Metin Yaz (Fiziksel)", "Kaydır (Swipe)"] or (act == "Sistem Tuşu" and step.get("sys_key") == "Fiziksel Sil (Backspace)"):
                    step["count"] = st.number_input("Adet / Tekrar:", min_value=1, value=int(step.get("count", 1)), key=f"edit_count_{c_idx}_{s_idx}")

                if st.button("✅ Kaydet ve Kapat", key=f"save_{c_idx}_{s_idx}", use_container_width=True):
                    st.session_state.editing_step = None
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

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
