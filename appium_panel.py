import streamlit as st
import json
import re

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
    .s-swipe { background-color: #FFBF00; color: #333; } 
    .s-wait { background-color: #9966FF; } 
    .s-sys { background-color: #8A9BAC; } 
    .s-clear { background-color: #E74C3C; }
    
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
    elif action == "Kaydır (Swipe)": return f"Kaydır: {direction}"
    elif action == "Sistem Tuşu": 
        if sys_key == "Kutuyu Temizle": return "İçeriği Sil"
        return f"Tuş: {sys_key}"
    elif action == "Bekle (Sleep)": return f"Bekle: {val} sn"
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
    
    st.caption("*(Tüm cihazı test etmek için aşağıdaki alanları boş bırakın)*")
    if st.session_state.platform == "Android":
        st.session_state.app_pkg = st.text_input("App Package:", st.session_state.app_pkg)
        st.session_state.app_act = st.text_input("App Activity:", st.session_state.app_act)
    else:
        st.session_state.bundle_id = st.text_input("Bundle ID:", st.session_state.bundle_id)
    
    st.divider()
    st.header("🧱 Senaryo Ekle")
    case_name = st.text_input("Yeni Case Adı:", placeholder="Örn: test_login")
    if st.button("➕ Yeni Case Oluştur", type="primary", use_container_width=True):
        if case_name:
            st.session_state.cases.append({"name": case_name.replace(" ", "_"), "steps": []})
            st.rerun()

    st.divider()
    if st.session_state.cases:
        st.subheader("🧩 Blok Ekle")
        action = st.selectbox("İşlem Tipi:", ["Tıkla", "Metin Yaz", "Kaydır (Swipe)", "Sistem Tuşu", "Bekle (Sleep)"])
        step_name = st.text_input("Adım İsmi (Boş bırakırsanız otomatik verilir):", placeholder="Örn: Ayarlara Tıkla")
        
        xpath, val, count, direction, step_x, step_y, sys_key = "", "", 1, "Aşağı", 0, 0, "Geri"
        fragile_text = ""
        
        if action == "Tıkla": 
            xpath = st.text_area("Hedef Alan (Boş bırakıp koordinat girebilirsiniz):")
            
            if xpath and ("//" in xpath) and ("@" not in xpath) and ("[" in xpath):
                st.warning("⚠️ Bu yol kırılgan görünüyor (sıra numarasına dayanıyor). Sayfa kaydığında bozulabilir! Daha sağlam olması için buton üzerinde yazan yazıyı (birebir) aşağıya girin:")
                fragile_text = st.text_input("Buton Üzerindeki Yazı:")
                
            c1, c2 = st.columns(2)
            with c1: step_x = st.number_input("X (Koordinat):", value=0)
            with c2: step_y = st.number_input("Y (Koordinat):", value=0)
            
        elif action == "Metin Yaz": 
            xpath = st.text_area("Hedef Alan (JSON/XPATH):")
            
            if xpath and ("//" in xpath) and ("@" not in xpath) and ("[" in xpath):
                st.warning("⚠️ Bu yol kırılgan görünüyor. Daha sağlam olması için lütfen kutu üzerinde yazan yazıyı (birebir) aşağıya girin:")
                fragile_text = st.text_input("Kutu Üzerindeki İpucu/Yazı:")
            
            val = st.text_input("Yazılacak Değer:")
            
        elif action == "Kaydır (Swipe)":
            direction = st.selectbox("Yön:", ["Aşağı", "Yukarı", "Sağa", "Sola"])
            count = st.number_input("Tekrar Sayısı:", min_value=1, value=1)
            st.caption("Kaydırmanın Merkez Koordinatları (Tüm ekranın ortası için 0 bırakın):")
            c1, c2 = st.columns(2)
            with c1: step_x = st.number_input("X (Koor):", value=0, key="sw_x")
            with c2: step_y = st.number_input("Y (Koor):", value=0, key="sw_y")
            
        elif action == "Sistem Tuşu":
            sys_key = st.selectbox("Tuş Seçimi:", ["Geri", "Ana Sayfa", "Arka Plan", "Klavyeyi Kapat", "Kutuyu Temizle"])
            if sys_key == "Kutuyu Temizle":
                xpath = st.text_area("Hedef Alan (JSON/XPATH) - Silinecek Kutu:")
                if xpath and ("//" in xpath) and ("@" not in xpath) and ("[" in xpath):
                    st.warning("⚠️ Bu yol kırılgan görünüyor. Daha sağlam olması için lütfen kutu üzerinde yazan yazıyı aşağıya girin:")
                    fragile_text = st.text_input("Kutu Üzerindeki Yazı:")
                
        elif action == "Bekle (Sleep)": 
            val = st.number_input("Saniye:", min_value=1, value=1)
        
        if st.button("⬇️ Aktif Case'e Adım Ekle", use_container_width=True):
            final_xpath = xpath
            if fragile_text:
                final_xpath = f"//*[contains(@content-desc, '{fragile_text}') or contains(@text, '{fragile_text}')]"

            if not step_name:
                step_name = akilli_isim_uret(action, final_xpath, val, direction, sys_key, step_x, step_y)

            st.session_state.cases[-1]["steps"].append({
                "step_name": step_name, "action": action, "xpath": final_xpath, "val": str(val), 
                "count": count, "direction": direction, "x": step_x, "y": step_y, "sys_key": sys_key
            })
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
                if step.get("x", 0) > 0 or step.get("y", 0) > 0: info = f'<span class="s-val">X:{step["x"]} Y:{step["y"]}</span>'
            elif act == "Metin Yaz": css, icon = "s-type", "⌨️"
            elif act == "Kaydır (Swipe)": 
                css, icon = "s-swipe", "↔️"
                if step.get("x", 0) > 0 or step.get("y", 0) > 0:
                    info = f'<span class="s-val">{step.get("direction", "Aşağı")} (Merkez X:{step.get("x",0)} Y:{step.get("y",0)}) x{step.get("count", 1)}</span>'
                else:
                    info = f'<span class="s-val">{step.get("direction", "Aşağı")} (Ekran Ortası) x{step.get("count", 1)}</span>'
            elif act == "Bekle (Sleep)": css, icon = "s-wait", "⏳"
            elif act == "Sistem Tuşu": 
                if step.get("sys_key") == "Kutuyu Temizle":
                    css, icon, info = "s-clear", "🧹", ""
                else:
                    css, icon, info = "s-sys", "📱", f'<span class="s-val">{step.get("sys_key", "")}</span>'
            
            xp_disp = f'<span class="s-val">{step.get("xpath", "")[:30]}...</span>' if step.get("xpath") and (act in ["Tıkla", "Metin Yaz"] or (act == "Sistem Tuşu" and step.get("sys_key") == "Kutuyu Temizle")) else ""
            val_disp = f'<span class="s-val">{step.get("val", "")}</span>' if step.get("val") and act not in ["Kaydır (Swipe)", "Bekle (Sleep)", "Sistem Tuşu"] else ""
            if act == "Bekle (Sleep)": val_disp = f'<span class="s-val">{step.get("val", "")} sn</span>'
            
            html_block = f'<div class="s-block {css}"><span>{icon} <b>{s_name}</b></span> {xp_disp} {info} {val_disp}</div>'
            
            col_block, col_edit, col_del = st.columns([8, 1, 1])
            with col_block: st.markdown(html_block, unsafe_allow_html=True)
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
                
                if act in ["Tıkla", "Metin Yaz"] or (act == "Sistem Tuşu" and step.get("sys_key") == "Kutuyu Temizle"):
                    step["xpath"] = st.text_area("Hedef Veri (JSON/XPATH):", value=step.get("xpath", ""), key=f"edit_xp_{c_idx}_{s_idx}")
                    if step["xpath"] and ("//" in step["xpath"]) and ("@" not in step["xpath"]) and ("[" in step["xpath"]):
                        st.warning("⚠️ Bu yol kırılgan. Daha sağlam olması için üzerindeki yazıyı (birebir) aşağıya girebilirsiniz:")
                        edit_fragile = st.text_input("Üzerindeki Yazı:", key=f"edit_fragile_{c_idx}_{s_idx}")
                        if edit_fragile:
                            step["xpath"] = f"//*[contains(@content-desc, '{edit_fragile}') or contains(@text, '{edit_fragile}')]"
                            
                if act == "Tıkla":
                    ec1, ec2 = st.columns(2)
                    with ec1: step["x"] = st.number_input("X (Koor):", value=step.get("x", 0), key=f"edit_x_{c_idx}_{s_idx}")
                    with ec2: step["y"] = st.number_input("Y (Koor):", value=step.get("y", 0), key=f"edit_y_{c_idx}_{s_idx}")
                if act == "Metin Yaz":
                    step["val"] = st.text_input("Yazılacak Değer:", value=step.get("val", ""), key=f"edit_val_{c_idx}_{s_idx}")
                if act == "Bekle (Sleep)":
                    step["val"] = str(st.number_input("Saniye:", min_value=1, value=int(step.get("val", 1)), key=f"edit_wait_{c_idx}_{s_idx}"))
                if act == "Sistem Tuşu":
                    dirs = ["Geri", "Ana Sayfa", "Arka Plan", "Klavyeyi Kapat", "Kutuyu Temizle"]
                    idx = dirs.index(step.get("sys_key", "Geri")) if step.get("sys_key", "Geri") in dirs else 0
                    step["sys_key"] = st.selectbox("Tuş Seçimi:", dirs, index=idx, key=f"edit_sys_{c_idx}_{s_idx}")

                if act == "Kaydır (Swipe)":
                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        dirs = ["Aşağı", "Yukarı", "Sağa", "Sola"]
                        idx = dirs.index(step.get("direction", "Aşağı")) if step.get("direction", "Aşağı") in dirs else 0
                        step["direction"] = st.selectbox("Yön:", dirs, index=idx, key=f"edit_dir_{c_idx}_{s_idx}")
                    with col_d2:
                        step["count"] = st.number_input("Tekrar:", min_value=1, value=int(step.get("count", 1)), key=f"edit_count_{c_idx}_{s_idx}")
                    st.caption("Kaydırmanın Merkez Koordinatları (Tüm ekran için 0 bırakın):")
                    ec1, ec2 = st.columns(2)
                    with ec1: step["x"] = st.number_input("X (Koor):", value=step.get("x", 0), key=f"edit_sx_{c_idx}_{s_idx}")
                    with ec2: step["y"] = st.number_input("Y (Koor):", value=step.get("y", 0), key=f"edit_sy_{c_idx}_{s_idx}")
                
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
from datetime import datetime
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions import interaction

# --- CLOUD API LOGGER ENTEGRASYONU ---
class APILogger:
    def __init__(self):
        self.run_id = os.getenv("RUN_ID", "default_run")
        self.agent_id = os.getenv("AGENT_ID", "default_agent")
        base_url = os.getenv("PUBLIC_BASE_URL", "https://dustless-brittani-jangly.ngrok-free.dev")
        self.api_url = f"{{base_url}}/api/v1/agents/runs/{{self.run_id}}/event"
        self.headers = {{
            "Content-Type": "application/json",
            "x-runner-shared-secret": os.getenv("RUNNER_SHARED_SECRET", "felina"),
            "ngrok-skip-browser-warning": "true"
        }}
        self.seq = 0

    def send_event(self, event_type, detail):
        self.seq += 1
        payload = {{
            "ok": True,
            "runEvent": {{
                "runId": self.run_id,
                "agentId": self.agent_id,
                "type": event_type,
                "payload": {{"detail": detail}},
                "is": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
                "seq": self.seq,
            }}
        }}
        try:
            requests.post(self.api_url, json=payload, headers=self.headers, timeout=10)
            print(f"[EVENT] {{event_type}}: {{detail}}")
        except Exception:
            pass 

    def log_step_passed(self, desc): self.send_event("step_passed", desc)
    def log_message(self, msg): self.send_event("log", msg)
    def log_test_app_launched(self, app): self.send_event("test_app_launched", f"{{app}} test app has started")

api_logger = APILogger()

def akilli_element_bulucu(driver, locator):
    locator = str(locator).strip()
    if not locator: raise Exception("Hedef veri (XPath/ID) bos birakilmis!")
    
    if locator.count("/") > 3 and "android.widget" in locator:
        son_dugum = locator.split("/")[-1]
        if ("@" in son_dugum) and (son_dugum.startswith("android.") or son_dugum.startswith("android.widget.")):
            yeni_locator = "//" + son_dugum
            print("[AKILLI BULUCU] Kirilgan XPath kisaltildi: " + yeni_locator)
            locator = yeni_locator

    if ("[@content-desc=" in locator or "[@text=" in locator) and ("'" in locator or '"' in locator):
        try:
            attr_part = locator.split("[@")[1].split("=")[0]
            val_part = locator.split("=")[1].split("]")[0].replace('"', '').replace("'", "")
            
            if len(val_part) > 12 or " " in val_part or "\\n" in val_part:
                kelimeler = re.findall(r'[\\wİıÖöÜüŞşÇçĞğ]+', val_part)
                if kelimeler:
                    secilen_kelime = sorted([k for k in kelimeler if len(k) >= 4], key=len, reverse=True)[0]
                    locator = f"//*[contains(@{{attr_part}}, '{{secilen_kelime}}')]"
        except Exception:
            pass
    
    if locator.startswith("//") or locator.startswith("(") or locator.startswith("hierarchy"):
        return driver.find_element(by=AppiumBy.XPATH, value=locator)
    
    acc_id_match = re.search(r'"accessibility[-_]id"\\s*:\\s*"([^"]+)"', locator, re.IGNORECASE) or re.search(r'accessibility id\\s*:\\s*([^\\n]+)', locator, re.IGNORECASE)
    if acc_id_match: return driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value=acc_id_match.group(1).strip())
    
    res_id_match = re.search(r'"resource-id"\\s*:\\s*"([^"]+)"', locator, re.IGNORECASE) or re.search(r'resource-id\\s*:\\s*([^\\n]+)', locator, re.IGNORECASE)
    if res_id_match: return driver.find_element(by=AppiumBy.ID, value=res_id_match.group(1).strip())
    
    xpath_match = re.search(r'"xpath"\\s*:\\s*"([^"]+)"', locator, re.IGNORECASE) or re.search(r'xpath\\s*:\\s*([^\\n]+)', locator, re.IGNORECASE)
    if xpath_match: return driver.find_element(by=AppiumBy.XPATH, value=xpath_match.group(1).strip())
    
    return driver.find_element(by=AppiumBy.ID, value=locator)

def ekran_kaydir(driver, yon, x=0, y=0):
    size = driver.get_window_size()
    
    # Eger kullanici (0,0) disinda bir koordinat verdiyse orayi merkez al, vermediyse ekranin ortasini merkez al
    if x > 0 or y > 0:
        merkez_x = x
        merkez_y = y
    else:
        merkez_x = int(size['width'] / 2)
        merkez_y = int(size['height'] / 2)
        
    start_x, start_y = merkez_x, merkez_y
    end_x, end_y = merkez_x, merkez_y
    
    x_offset = int(size['width'] * 0.25)
    y_offset = int(size['height'] * 0.25)
    
    if yon == 'down': 
        start_y += y_offset
        end_y -= y_offset
    elif yon == 'up': 
        start_y -= y_offset
        end_y += y_offset
    elif yon == 'right': 
        start_x -= x_offset
        end_x += x_offset
    elif yon == 'left': 
        start_x += x_offset
        end_x -= x_offset
        
    # Appium'un ekran disina tasip cokmemesi icin sinirlari guvenceye aliyoruz
    start_x = max(10, min(size['width'] - 10, start_x))
    start_y = max(10, min(size['height'] - 10, start_y))
    end_x = max(10, min(size['width'] - 10, end_x))
    end_y = max(10, min(size['height'] - 10, end_y))

    try:
        actions = ActionChains(driver)
        actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(start_x, start_y)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.pause(0.5)
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

    if st.session_state.platform == "Android" and st.session_state.app_pkg:
        gen_code += f"try:\n    api_logger.log_message('Uygulama baslatiliyor / one getiriliyor: {st.session_state.app_pkg}')\n"
        gen_code += f"    driver.activate_app('{st.session_state.app_pkg}')\n"
        gen_code += f"    api_logger.log_test_app_launched('{st.session_state.app_pkg}')\n"
        gen_code += f"    time.sleep(3)\nexcept Exception as e:\n    api_logger.log_message(f'Uygulama baslatma uyarisi: {{e}}')\n\n"
    elif st.session_state.platform == "iOS" and st.session_state.bundle_id:
        gen_code += f"try:\n    api_logger.log_message('Uygulama baslatiliyor / one getiriliyor: {st.session_state.bundle_id}')\n"
        gen_code += f"    driver.activate_app('{st.session_state.bundle_id}')\n"
        gen_code += f"    api_logger.log_test_app_launched('{st.session_state.bundle_id}')\n"
        gen_code += f"    time.sleep(3)\nexcept Exception as e:\n    api_logger.log_message(f'Uygulama baslatma uyarisi: {{e}}')\n\n"

    calls = []
    for case in st.session_state.cases:
        c_name = case["name"]
        calls.append(f"    {c_name}()")
        gen_code += f"def {c_name}():\n    try:\n        api_logger.log_message('--- {c_name.upper()} BAŞLADI ---')\n"
        for s_idx, step in enumerate(case["steps"]):
            act = step["action"]
            s_name = step.get("step_name", f"Adım {s_idx+1}")
            
            safe_s_name = s_name.replace("'", "\\'").replace('"', '\\"')
            gen_code += f"        api_logger.log_message('Adım başlatılıyor: {safe_s_name}...')\n"
            
            if act == "Tıkla":
                if step.get("x", 0) > 0 or step.get("y", 0) > 0:
                    gen_code += f"        driver.tap([({step['x']}, {step['y']})])\n        time.sleep(1)\n"
                else:
                    gen_code += f"        akilli_element_bulucu(driver, r'''{step.get('xpath','')}''').click()\n        time.sleep(1)\n"
            elif act == "Metin Yaz":
                safe_val = step.get("val", "").replace("'", "\\'")
                gen_code += f"        kutu = akilli_element_bulucu(driver, r'''{step.get('xpath','')}''')\n"
                gen_code += f"        kutu.clear(); kutu.send_keys('{safe_val}'); time.sleep(1)\n"
            elif act == "Sistem Tuşu":
                sk = step.get("sys_key", "")
                if sk == "Klavyeyi Kapat": gen_code += "        try: driver.hide_keyboard()\n        except: pass\n"
                elif sk == "Geri": gen_code += "        driver.press_keycode(4)\n"
                elif sk == "Ana Sayfa": gen_code += "        driver.press_keycode(3)\n"
                elif sk == "Arka Plan": gen_code += "        driver.press_keycode(187)\n"
                elif sk == "Kutuyu Temizle":
                    gen_code += f"        kutu = akilli_element_bulucu(driver, r'''{step.get('xpath','')}''')\n"
                    gen_code += f"        kutu.clear(); time.sleep(1)\n"
            elif act == "Kaydır (Swipe)":
                dir_map = {"Aşağı": "down", "Yukarı": "up", "Sağa": "right", "Sola": "left"}
                s_dir = dir_map.get(step.get('direction','Aşağı'))
                sx, sy = step.get('x', 0), step.get('y', 0)
                gen_code += f"        for _ in range({step.get('count',1)}):\n            ekran_kaydir(driver, '{s_dir}', {sx}, {sy})\n            time.sleep(0.5)\n"
            elif act == "Bekle (Sleep)":
                gen_code += f"        time.sleep({step.get('val',1)})\n"
                
            gen_code += f"        api_logger.log_step_passed('{safe_s_name}')\n"
                
        gen_code += f"        api_logger.log_message('{c_name} Başarıyla Tamamlandı')\n    except Exception as e:\n        api_logger.log_message(f'HATA: {{e}}')\n\n"
    
    gen_code += "try:\n" + ("\n".join(calls) if calls else "    pass") + "\nfinally:\n    driver.quit()\n"

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
    
    # --- ENTER GEREKTİRMEYEN ÇİFT AŞAMALI İNDİRME SİSTEMİ ---
    if st.session_state.export_state == 0:
        if st.button("📤 Kodu Dışa Aktar (Export)", use_container_width=True, type="primary"):
            st.session_state.export_state = 1
            st.rerun()
            
    elif st.session_state.export_state == 1:
        st.info("İndirmek istediğiniz dosyanın adını belirleyin (Yazıp Hazırla'ya basmanız yeterli):")
        c_name_col, c_btn_col, c_cancel_col = st.columns([5, 4, 1])
        with c_name_col:
            st.session_state.out_filename = st.text_input("Dosya Adı:", value=st.session_state.out_filename, label_visibility="collapsed")
        with c_btn_col:
            if st.button("⚙️ İndirmeye Hazırla", use_container_width=True):
                st.session_state.export_state = 2
                st.rerun()
        with c_cancel_col:
            if st.button("❌", use_container_width=True, key="c1"):
                st.session_state.export_state = 0
                st.rerun()
                
    elif st.session_state.export_state == 2:
        final_name = st.session_state.out_filename
        if not final_name.endswith(".py"): final_name += ".py"
        st.success(f"✅ Dosya hazırlandı: **{final_name}**")
        c_dummy, c_btn_col, c_cancel_col = st.columns([5, 4, 1])
        with c_dummy:
            st.write("") # Görselliği ve hizayı korumak için boşluk
        with c_btn_col:
            st.download_button("📥 İndirmeyi Başlat", data=gen_code, file_name=final_name, mime="text/x-python", use_container_width=True)
        with c_cancel_col:
            if st.button("❌", use_container_width=True, key="c2"):
                st.session_state.export_state = 0
                st.rerun()
