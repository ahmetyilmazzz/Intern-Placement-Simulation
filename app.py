import streamlit as st
import pandas as pd
import time
import numpy as np
import matplotlib.pyplot as plt

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Stajyer Simülatörü", layout="wide", page_icon="🎓")

# --- CSS (Masaüstü Havası İçin) ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        font-weight: bold;
        border: 1px solid #ddd;
        height: 3em;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 Stajyer Yerleştirme Simülasyonu")

# --- MODÜLLERİ YÜKLE ---
try:
    import veri_olustur
    import algo_greedy
    import algo_heuristic_hill_climbing
    import algo_heuristic_annealing
except ImportError as e:
    st.error(f"⚠️ Kritik Hata: Modüller bulunamadı! ({e})")
    st.stop()

# --- SESSION STATE (HAFIZA) ---
if 'ogrenciler' not in st.session_state: st.session_state['ogrenciler'] = pd.DataFrame()
if 'firmalar' not in st.session_state: st.session_state['firmalar'] = pd.DataFrame()
if 'analiz_sonuclari' not in st.session_state: st.session_state['analiz_sonuclari'] = {}

# --- YARDIMCI FONKSİYONLAR ---
def puan_hesapla(df):
    """Masaüstü uygulamasıyla aynı puanlama mantığı"""
    if df.empty or 'Yerleştiği_Firma' not in df.columns: return 0
    puan_tablosu = {1: 100, 2: 85, 3: 70, 4: 50, 5: 30}
    toplam = 0
    for _, row in df[df['Yerleştiği_Firma'].notna()].iterrows():
        yf = row['Yerleştiği_Firma']
        for i in range(1, 6):
            if f'Tercih{i}' in row and row[f'Tercih{i}'] == yf:
                toplam += puan_tablosu.get(i, 10)
                break
    return toplam

def dinamik_fonksiyon_bul(modul, anahtar_kelimeler):
    """
    Modül içindeki fonksiyon adını bilmesek bile bulup getirir.
    Örn: 'hill_climbing' arar, bulamazsa 'heuristic_atama'yı getirir.
    """
    for name in dir(modul):
        # Python'un kendi gömülü metodlarını atla
        if name.startswith("__") or name in ['deepcopy', 'copy', 'math', 'pd', 'np', 'random']:
            continue
            
        # Anahtar kelimelerden biri geçiyor mu?
        for anahtar in anahtar_kelimeler:
            if anahtar in name:
                attr = getattr(modul, name)
                if callable(attr):
                    return attr
    return None

# --- SOL MENÜ ---
with st.sidebar:
    st.header("⚙️ Ayarlar")
    
    ogr_sayisi = st.number_input("Öğrenci Sayısı", value=150)
    firma_sayisi = st.number_input("Firma Sayısı", value=40)
    
    if st.button("🎲 Veri Oluştur", type="primary"):
        # Sonuçların tutarlı olması için seed sabitliyoruz
        np.random.seed(42)
        
        d1, d2 = veri_olustur.veri_seti_olustur(ogr_sayisi, firma_sayisi)
        
        # Hangi dataframe hangisi kontrol et
        if 'Firma' in d1.columns:
            firmalar_df, ogrenciler_df = d1, d2
        else:
            ogrenciler_df, firmalar_df = d1, d2

        # Sütun İsimlerini Düzelt
        mapping = {'Ortalama': 'GNO', 'Not': 'GNO', 'Puan': 'GNO', 'Ogrenci_No': 'Öğrenci'}
        ogrenciler_df.rename(columns=mapping, inplace=True)
        
        if 'Yerleştiği_Firma' not in ogrenciler_df.columns:
            ogrenciler_df['Yerleştiği_Firma'] = None

        st.session_state['ogrenciler'] = ogrenciler_df
        st.session_state['firmalar'] = firmalar_df
        st.session_state['analiz_sonuclari'] = {}
        
        st.success(f"Veri Hazır: {len(ogrenciler_df)} Öğrenci")

    st.markdown("---")
    st.subheader("Algoritmalar")
    
    btn_greedy = st.button("🚀 Greedy")
    btn_hill = st.button("⛰️ Hill Climbing")
    btn_anneal = st.button("🔥 Annealing")
    
    st.markdown("---")
    btn_kiyasla = st.button("📊 Analiz & Kıyasla")
    
    if st.button("🗑️ Sıfırla"):
        st.session_state.clear()
        st.rerun()

# --- ANA EKRAN MANTIĞI ---
if st.session_state['ogrenciler'].empty:
    st.info("👈 Lütfen sol menüden **'Veri Oluştur'** butonuna basın.")
    st.stop()

islem_bitti = False
secilen_algo = ""
sure = 0

# 1. GREEDY
if btn_greedy:
    secilen_algo = "Greedy"
    t1 = time.time()
    
    # Greedy genelde standart isimlendirilir ama yine de kontrol edelim
    try:
        if hasattr(algo_greedy, 'greedy_atama'):
            res = algo_greedy.greedy_atama(st.session_state['ogrenciler'].copy(), st.session_state['firmalar'].copy())
        else:
            # Bulamazsa dinamik ara
            func = dinamik_fonksiyon_bul(algo_greedy, ['greedy', 'atama'])
            res = func(st.session_state['ogrenciler'].copy(), st.session_state['firmalar'].copy())

        st.session_state['ogrenciler'] = res[0] if isinstance(res, tuple) else res
        if isinstance(res, tuple): st.session_state['firmalar'] = res[1]
        
    except Exception as e:
        st.error(f"Greedy Hatası: {e}")
        st.stop()
        
    sure = time.time() - t1
    islem_bitti = True

# 2. HILL CLIMBING
elif btn_hill:
    secilen_algo = "Hill Climbing"
    t1 = time.time()
    bar = st.progress(0)
    
    def step(i): 
        if i % 500 == 0: bar.progress(min(i/3000, 1.0))
    
    try:
        # Fonksiyon adını dinamik bul (Hata Riskini Sıfırla)
        func = dinamik_fonksiyon_bul(algo_heuristic_hill_climbing, ['hill', 'heuristic', 'atama', 'main'])
        
        if func:
            res = func(st.session_state['ogrenciler'].copy(), st.session_state['firmalar'].copy(), iterasyon=3000, step_callback=step)
            st.session_state['ogrenciler'] = res[0] if isinstance(res, tuple) else res
            if isinstance(res, tuple): st.session_state['firmalar'] = res[1]
        else:
            st.error("Hill Climbing fonksiyonu modül içinde bulunamadı!")
            st.stop()
            
    except Exception as e:
        st.error(f"Hill Climbing Hatası: {e}")
        st.stop()
    
    bar.empty()
    sure = time.time() - t1
    islem_bitti = True

# 3. ANNEALING
elif btn_anneal:
    secilen_algo = "Simulated Annealing"
    t1 = time.time()
    bar = st.progress(0)
    
    def step(i):
        if i % 1000 == 0: bar.progress(min(i/10000, 1.0))
        
    try:
        # Fonksiyon adını dinamik bul
        func = dinamik_fonksiyon_bul(algo_heuristic_annealing, ['simulated', 'anneal', 'heuristic', 'atama'])
        
        if func:
            res = func(st.session_state['ogrenciler'].copy(), st.session_state['firmalar'].copy(), iterasyon=10000, step_callback=step)
            st.session_state['ogrenciler'] = res[0] if isinstance(res, tuple) else res
            if isinstance(res, tuple): st.session_state['firmalar'] = res[1]
        else:
            st.error("Annealing fonksiyonu modül içinde bulunamadı!")
            st.stop()
            
    except Exception as e:
        st.error(f"Annealing Hatası: {e}")
        st.stop()
    
    bar.empty()
    sure = time.time() - t1
    islem_bitti = True

# --- SONUÇLARI GÖSTER ---
if islem_bitti:
    df = st.session_state['ogrenciler']
    yerlesen = df['Yerleştiği_Firma'].count()
    basari = (yerlesen / len(df)) * 100
    puan = puan_hesapla(df)
    
    # Sonucu Kaydet
    st.session_state['analiz_sonuclari'][secilen_algo] = {"Puan": puan, "Yerleşen": yerlesen, "Süre": sure}
    
    st.success(f"✅ {secilen_algo} Tamamlandı!")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Yerleşen", f"{yerlesen}/{len(df)}")
    c2.metric("Başarı", f"%{basari:.1f}")
    c3.metric("Puan", f"{puan:,}".replace(",", "."))
    c4.metric("Süre", f"{sure:.3f}s")

# --- KIYASLAMA GRAFİĞİ ---
if btn_kiyasla:
    st.divider()
    st.subheader("📊 Analiz")
    res = st.session_state['analiz_sonuclari']
    
    if res:
        # Dict'ten DataFrame'e çevir
        data_list = []
        for k, v in res.items():
            row = v.copy()
            row['Algoritma'] = k
            data_list.append(row)
        
        df_res = pd.DataFrame(data_list)
        
        c1, c2 = st.columns([1, 1])
        
        with c1:
            st.dataframe(df_res[['Algoritma', 'Yerleşen', 'Puan', 'Süre']], hide_index=True, use_container_width=True)
            
            # En iyiyi göster
            best = df_res.loc[df_res['Puan'].idxmax()]
            st.info(f"🏆 En İyi Performans: **{best['Algoritma']}** ({int(best['Puan'])} Puan)")

        with c2:
            fig, ax = plt.subplots(figsize=(5, 3))
            colors = ['#FF4B4B', '#1C83E1', '#FFA500']
            bars = ax.bar(df_res['Algoritma'], df_res['Puan'], color=colors[:len(df_res)])
            ax.set_title("Memnuniyet Puanı Karşılaştırması")
            
            # Barların üstüne yazı ekle
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}', ha='center', va='bottom')
                
            st.pyplot(fig)
    else:
        st.warning("⚠️ Karşılaştırma için önce yukarıdan algoritmaları çalıştırın.")

# --- DETAYLI LİSTELER ---
st.divider()
t1, t2 = st.tabs(["👨‍🎓 Öğrenci Listesi", "🏢 Firma Listesi"])

with t1:
    df_ogr = st.session_state['ogrenciler']
    # Sütun filtreleme (Hata önleyici)
    cols = ['Öğrenci', 'GNO', 'Yerleştiği_Firma', 'Tercih1', 'Tercih2']
    # Veri setinde 'Ogrenci' varsa onu kullan
    cols = [c if c != 'Öğrenci' and 'Ogrenci' in df_ogr.columns else c for c in cols]
    
    # Sadece var olanları seç
    final_cols = [c for c in cols if c in df_ogr.columns]
    
    if final_cols:
        st.dataframe(df_ogr[final_cols], use_container_width=True)
    else:
        st.dataframe(df_ogr, use_container_width=True)

with t2:
    st.dataframe(st.session_state['firmalar'], use_container_width=True)