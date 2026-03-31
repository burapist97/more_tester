import streamlit as st
import json
import re

st.set_page_config(page_title="Görsel Appium IDE", layout="wide", initial_sidebar_state="expanded")

# --- SCRATCH / BLOCKLY CANLI CSS TASARIMI ---
st.markdown("""
    <style>
    .stApp { background-color: #F4F5F7; }
    
    /* Canlı Yapboz Blokları */
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
    
    /* Canlı Renk Paleti */
    .s-setup { background-color: #0FBD8C; font-size: 16px; border-radius: 10px; margin-bottom: 20px;} /* Koyu Yeşil */
    .s-case { background-color: #FF6680; font-size: 16px; margin-top: 15px; border-radius: 10px 10px 0 0; } /* Pembe/Kırmızı */
    .s-click { background-color: #4C97FF; } /* Mavi */
    .s-type { background-color: #59C059; } /* Açık Yeşil */
    .s-swipe { background-color: #FFBF00; color: #333; } /* Sarı */
    .s-wait { background-color: #9966FF; } /* Mor */
    .s-sys { background-color: #8A9BAC; } /* Gri */
    
    /* Gömülü Değer Kutucukları (Senin örnekteki gibi) */
    .s-val {
        background: white;
        color: #333;
        border-radius: 16px;
        padding: 4px 12px;
        font-size: 13px;
        font-weight: 600;
        box-shadow: inset 0px 2px 3px rgba(0,0,0,0.15);
        border: 1px solid rgba(0,0,0,0.1);
        margin-left: auto; /* Sağa yasla */
        max-width: 300px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    /* Düzenleme Alanı */
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
if 'app_pkg' not in st.session_state: st.session_state.app_pkg = "com.arcelik.oliz"
if 'app_act' not in st.session_state: st.session_state.app_act = "com.arcelik.oliz.MainActivity"
if 'cases' not in st.session_state: st.session_state.cases = []
if 'loaded_file' not in st.session_state: st.session_state.loaded_file = None
if 'editing_step' not in st.session_state: st.session_state.editing_step = None # HANGİ ADIMIN DÜZENLENDİĞİNİ TUTAR

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
                    st.session_state.app_pkg = data.get("app_pkg", "com.arcelik.oliz")
                    st.session_state.app_act = data.get("app_act", "com.arcelik.oliz.MainActivity")
                    st.session_state.cases = data.get("cases", [])
                    st.session_state.loaded_file = uploaded_file.name
                    st.success("Test başarıyla yüklendi!")
                    st.rerun()
            except Exception as e: st.error(f"Dosya okunamadı: {e}")
    else:
        st.session_state.loaded_file = None

    st.divider()
    st.header("⚙️ Temel Ayarlar")
    st.session_state.app_pkg = st.text_input("App Package:", st.session_state.app_pkg)
    st.session_state.app_act = st.text_input("App Activity:", st.session_state.app_act)
    
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
        action = st.selectbox("İşlem Tipi:", ["Tıkla", "Metin Yaz", "Kaydır (Swipe)", "Klavyeyi Kapat", "Bekle (Sleep)"])
        xpath, val, count, direction = "", "", 1, "down"
        
        if action in ["Tıkla", "Metin Yaz"]: xpath = st.text_input("Hedef Alan (JSON/XPATH):")
        if action == "Metin Yaz": val = st.text_input("Yazılacak Değer:")
        if action == "Kaydır (Swipe)":
            direction = st.selectbox("Yön:", ["Aşağı", "Yukarı", "Sağa", "Sola"])
            count = st.number_input("Tekrar Sayısı:", min_value=1, value=1)
        if action == "Bekle (Sleep)": val = st.number_input("Saniye:", min_value=1, value=1)
        
        if st.button("⬇️ Aktif Case'e Adım Ekle", use_container_width=True):
            st.session_state.cases[-1]["steps"].append({"action": action, "xpath": xpath, "val": str(val), "count": count, "direction": direction})
            st.rerun()
    
    st.divider()
    if st.button("🗑️ Tüm Tuvali Temizle"):
        st.session_state.cases = []
        st.session_state.loaded_file = None
        st.session_state.editing_step = None
        st.rerun()

col_canvas, col_code = st.columns(2)

# --- SOL TARAF: GÖRSEL TUVAL VE AÇIK DÜZENLEYİCİ ---
with col_canvas:
    st.subheader("🎨 Görsel Test Tuvali")
    st.markdown(f'<div class="s-block s-setup">▶️ Başlat: <span class="s-val">{st.session_state.app_pkg}</span></div>', unsafe_allow_html=True)
    
    for c_idx, case in enumerate(st.session_state.cases):
        # Case Başlığı Bloğu
        col_c_name, col_c_del = st.columns([8, 2])
        with col_c_name:
            st.markdown(f'<div class="s-block s-case">⚙️ CASE: {case["name"]}</div>', unsafe_allow_html=True)
        with col_c_del:
            st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
            if st.button("🗑️ Sil", key=f"del_c_{c_idx}", use_container_width=True):
                st.session_state.cases.pop(c_idx)
                st.session_state.editing_step = None # Silince edit modunu kapat
                st.rerun()
                
        # Adımlar Döngüsü
        for s_idx, step in enumerate(case["steps"]):
            act = step["action"]
            css, icon, info = "s-sys", "⚙️", ""
            
            # Renkleri Scratch mantığına göre eşleştir
            if act == "Tıkla": css, icon = "s-click", "👆"
            elif act == "Metin Yaz": css, icon = "s-type", "⌨️"
            elif act == "Kaydır (Swipe)": css, icon, info = "s-swipe", "↔️", f'<span class="s-val">{step.get("direction", "Aşağı")} x{step.get("count", 1)}</span>'
            elif act == "Bekle (Sleep)": css, icon = "s-wait", "⏳"
            
            xp_disp = f'<span class="s-val">{step.get("xpath", "")[:35]}...</span>' if step.get("xpath") else ""
            val_disp = f'<span class="s-val">{step.get("val", "")}</span>' if step.get("val") and act not in ["Kaydır (Swipe)"] else ""
            
            html_block = f'<div class="s-block {css}"><span>{icon} {act}</span> {xp_disp} {val_disp} {info}</div>'
            
            # BLOK VE YANINDAKİ DÜZENLE / SİL BUTONLARI
            col_block, col_edit, col_del = st.columns([8, 1, 1])
            with col_block:
                st.markdown(html_block, unsafe_allow_html=True)
            with col_edit:
                st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
                # Düzenle butonuna basılınca o adımı "edit" moduna alır
                if st.button("✏️", key=f"edit_btn_{c_idx}_{s_idx}"):
                    if st.session_state.editing_step == f"{c_idx}_{s_idx}":
                        st.session_state.editing_step = None # Açıkken tekrar basarsa kapatır
                    else:
                        st.session_state.editing_step = f"{c_idx}_{s_idx}"
                    st.rerun()
            with col_del:
                st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True) 
                if st.button("🗑️", key=f"del_s_{c_idx}_{s_idx}"):
                    st.session_state.cases[c_idx]["steps"].pop(s_idx)
                    st.session_state.editing_step = None
                    st.rerun()
            
            # EĞER BU ADIM İÇİN "DÜZENLE" BUTONUNA BASILDIYSA AŞAĞIYA DİREKT AÇIK KUTULARI GETİR
            if st.session_state.editing_step == f"{c_idx}_{s_idx}":
                st.markdown('<div class="edit-box">', unsafe_allow_html=True)
                st.write(f"**🛠️ Adım {s_idx+1} İçeriğini Düzenle**")
                
                if act in ["Tıkla", "Metin Yaz"]:
                    new_xp = st.text_area("Hedef Veri (JSON/XPATH):", value=step.get("xpath", ""), key=f"edit_xp_{c_idx}_{s_idx}")
                    step["xpath"] = new_xp
                        
                if act == "Metin Yaz":
                    new_val = st.text_input("Yazılacak Değer:", value=step.get("val", ""), key=f"edit_val_{c_idx}_{s_idx}")
                    step["val"] = new_val
                        
                if act == "Bekle (Sleep)":
                    new_wait = st.number_input("Saniye:", min_value=1, value=int(step.get("val", 1)), key=f"edit_wait_{c_idx}_{s_idx}")
                    step["val"] = str(new_wait)
                        
                if act == "Kaydır (Swipe)":
                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        dirs = ["Aşağı", "Yukarı", "Sağa", "Sola"]
                        idx = dirs.index(step.get("direction", "Aşağı")) if step.get("direction", "Aşağı") in dirs else 0
                        new_dir = st.selectbox("Yön:", dirs, index=idx, key=f"edit_dir_{c_idx}_{s_idx}")
                        step["direction"] = new_dir
                    with col_d2:
                        new_count = st.number_input("Tekrar:", min_value=1, value=int(step.get("count", 1)), key=f"edit_count_{c_idx}_{s_idx}")
                        step["count"] = new_count
                
                # Değişiklikler anlık olarak (step objesine) yansır. İşlemi bitirmek için butona basar.
                if st.button("✅ Kaydet ve Kapat", key=f"save_{c_idx}_{s_idx}", use_container_width=True):
                    st.session_state.editing_step = None
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

# --- SAĞ TARAF: ÜRETİLEN PYTHON KODU ---
with col_code:
    st.subheader("📄 Üretilen Python Kodu")
    gen_code = f"""import time
import requests
import json
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions import interaction

def send_run_event(test_name, status):
    run_id = "senin_gercek_run_id_degerin"
    url = f"https://dustless-brittani-jangly.ngrok-free.dev/api/v1/agents/runs/{{run_id}}/event"
    headers = {{"Content-Type": "application/json", "Authorization": "felina"}}
    payload = {{"test_name": test_name, "status": status}}
    try:
        requests.post(url, json=payload, headers=headers)
        print(f"[{{test_name}}] -> {{status}}")
    except Exception as e:
        print(f"API Hatası: {{e}}")

def akilli_element_bulucu(driver, locator):
    locator = locator.strip()
    if locator.startswith("[") and locator.endswith("]"):
        try:
            attrs = json.loads(locator)
            attr_dict = {{item.get("name"): item.get("value") for item in attrs if item.get("value")}}
            if attr_dict.get("resource-id"):
                return driver.find_element(by=AppiumBy.ID, value=attr_dict["resource-id"])
            elif attr_dict.get("content-desc"):
                return driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value=attr_dict["content-desc"])
            elif attr_dict.get("xpath"):
                return driver.find_element(by=AppiumBy.XPATH, value=attr_dict["xpath"])
            else:
                raise Exception("Bu elementin gecerli bir XPATH, ID veya Content-Desc degeri yok!")
        except Exception as e:
            if "XPATH, ID" in str(e): raise e
            pass 
            
    if ":id/" in locator:
        return driver.find_element(by=AppiumBy.ID, value=locator)
    elif locator.startswith("//") or locator.startswith("hierarchy"):
        return driver.find_element(by=AppiumBy.XPATH, value=locator)
    else:
        try: return driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value=locator)
        except: return driver.find_element(by=AppiumBy.XPATH, value=locator)

def ekran_kaydir(driver, yon):
    size = driver.get_window_size()
    start_x = int(size['width'] / 2)
    start_y = int(size['height'] / 2)
    end_x = start_x
    end_y = start_y
    if yon == 'down':
        start_y = int(size['height'] * 0.75)
        end_y = int(size['height'] * 0.25)
    elif yon == 'up':
        start_y = int(size['height'] * 0.25)
        end_y = int(size['height'] * 0.75)
    elif yon == 'right':
        start_x = int(size['width'] * 0.25)
        end_x = int(size['width'] * 0.75)
    elif yon == 'left':
        start_x = int(size['width'] * 0.75)
        end_x = int(size['width'] * 0.25)
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

options = UiAutomator2Options()
options.app_package = '{st.session_state.app_pkg}'
options.app_activity = '{st.session_state.app_act}'
options.no_reset = True
driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
driver.implicitly_wait(10)

try:
    driver.activate_app('{st.session_state.app_pkg}')
    time.sleep(1)
except: pass

"""
    calls = []
    for case in st.session_state.cases:
        c_name = case["name"]
        calls.append(f"    {c_name}()")
        gen_code += f"def {c_name}():\n    try:\n        print('--- {c_name.upper()} BAŞLADI ---')\n"
        for s_idx, step in enumerate(case["steps"]):
            act = step["action"]
            if act == "Tıkla":
                gen_code += f"        print('Adım {s_idx+1}: Tıklanıyor...')\n"
                gen_code += f"        akilli_element_bulucu(driver, r'''{step['xpath']}''').click()\n        time.sleep(1)\n"
            elif act == "Metin Yaz":
                gen_code += f"        print('Adım {s_idx+1}: Veri giriliyor...')\n"
                gen_code += f"        kutu = akilli_element_bulucu(driver, r'''{step['xpath']}''')\n"
                gen_code += f"        kutu.clear(); kutu.send_keys('{step['val']}'); time.sleep(1)\n"
            elif act == "Kaydır (Swipe)":
                dir_map = {"Aşağı": "down", "Yukarı": "up", "Sağa": "right", "Sola": "left"}
                gen_code += f"        print('Adım {s_idx+1}: {step['direction']} yönüne {step['count']} kez kaydırılıyor...')\n"
                gen_code += f"        for _ in range({step['count']}):\n            ekran_kaydir(driver, '{dir_map[step['direction']]}')\n            time.sleep(0.5)\n"
            elif act == "Klavyeyi Kapat":
                gen_code += f"        try: driver.hide_keyboard()\n        except: pass\n"
            elif act == "Bekle (Sleep)":
                gen_code += f"        time.sleep({step['val']})\n"
        gen_code += f"        send_run_event('{c_name}', 'Passed')\n    except Exception as e:\n        print(f'Hata: {{e}}')\n        send_run_event('{c_name}', 'Failed')\n\n"
    
    gen_code += "try:\n" + ("\n".join(calls) if calls else "    pass") + "\nfinally:\n    driver.quit()\n"

    export_metadata = json.dumps({"app_pkg": st.session_state.app_pkg, "app_act": st.session_state.app_act, "cases": st.session_state.cases})
    gen_code += f"\n\n# --- IDE_METADATA_START ---\n# {export_metadata}\n"

    st.code(gen_code, language="python")
    st.download_button("📥 Kodu İndir (.py)", data=gen_code, file_name="otomasyon_testi.py", mime="text/x-python", use_container_width=True)