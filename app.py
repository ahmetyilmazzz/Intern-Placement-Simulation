import streamlit as st
import pandas as pd
import time

# Sayfa Ayarları
st.set_page_config(page_title="Stajyer Simülasyonu", layout="wide", page_icon="🎓")

# Başlık
st.title("🎓 Stajyer Yerleştirme Simülasyonu (Online)")
st.info("Bu proje; Greedy, Hill Climbing ve Simulated Annealing algoritmalarını karşılaştırır.")

# --- SENİN DOSYALARINI İÇERİ ALIYORUZ ---
try:
    import veri_olustur
    import algo_greedy
    import algo_heuristic_hill_climbing
    import algo_heuristic_annealing
except ImportError:
    st.error("Hata: Algoritma dosyaları bulunamadı! Lütfen dosya isimlerini kontrol et.")
    st.stop()

# --- HAFIZA (Session State) ---
# Web sayfası yenilendiğinde veriler kaybolmasın diye
if 'ogrenciler' not in st.session_state:
    st.session_state['ogrenciler'] = pd.DataFrame()
if 'firmalar' not in st.session_state:
    st.session_state['firmalar'] = pd.DataFrame()
if 'sonuc_mesaji' not in st.session_state:
    st.session_state['sonuc_mesaji'] = ""

# --- SOL MENÜ ---
with st.sidebar:
    st.header("⚙️ Ayarlar")
    ogr_sayisi = st.slider("Öğrenci Sayısı", 50, 500, 150)
    firma_sayisi = st.slider("Firma Sayısı", 10, 100, 40)

    if st.button("🔄 Yeni Veri Seti Oluştur", type="primary"):
        # Senin veri_olustur fonksiyonunu çağırıyoruz
        st.session_state['ogrenciler'], st.session_state['firmalar'] = veri_olustur.veri_seti_olustur(ogr_sayisi,
                                                                                                      firma_sayisi)
        st.success("Veriler oluşturuldu!")

    st.divider()
    st.subheader("Algoritma Seç")

    # Butonlar
    col1, col2 = st.columns(2)
    run_greedy = st.button("🚀 Greedy")
    run_hill = st.button("⛰️ Hill Climb")
    run_anneal = st.button("🔥 Annealing")

# --- ÇALIŞTIRMA MANTIĞI ---
if not st.session_state['ogrenciler'].empty:
    start_time = 0
    end_time = 0
    algo_name = ""

    if run_greedy:
        algo_name = "Greedy (Açgözlü)"
        start_time = time.time()
        # Senin greedy fonksiyonunu çağırıyoruz
        algo_greedy.greedy_atama(st.session_state['ogrenciler'], st.session_state['firmalar'])
        end_time = time.time()

    elif run_hill:
        algo_name = "Hill Climbing"
        start_time = time.time()
        # Senin hill climbing fonksiyonunu çağırıyoruz
        algo_heuristic_hill_climbing.hill_climbing_main(st.session_state['ogrenciler'], st.session_state['firmalar'])
        end_time = time.time()

    elif run_anneal:
        algo_name = "Simulated Annealing"
        start_time = time.time()
        # Senin annealing fonksiyonunu çağırıyoruz
        algo_heuristic_annealing.simulated_annealing_main(st.session_state['ogrenciler'], st.session_state['firmalar'])
        end_time = time.time()

    # Sonuç Gösterme
    if algo_name:
        sure = end_time - start_time
        # Basit bir skor hesaplama (Senin kodunda varsa onu kullanabiliriz)
        yerlesen = st.session_state['ogrenciler']['Yerleştiği_Firma'].count()
        toplam = len(st.session_state['ogrenciler'])
        basari = (yerlesen / toplam) * 100

        st.success(f"✅ {algo_name} Tamamlandı!")

        # Metrikler (Kutucuklar)
        m1, m2, m3 = st.columns(3)
        m1.metric("Yerleşen Öğrenci", f"{yerlesen} / {toplam}")
        m2.metric("Başarı Oranı", f"%{basari:.1f}")
        m3.metric("Süre", f"{sure:.4f} sn")

# --- TABLO VE GRAFİKLER ---
tab1, tab2 = st.tabs(["📋 Liste", "📊 Grafikler"])

with tab1:
    if not st.session_state['ogrenciler'].empty:
        st.dataframe(st.session_state['ogrenciler'][['Öğrenci', 'GNO', 'Yerleştiği_Firma', 'Tercih1']],
                     use_container_width=True)
    else:
        st.warning("Lütfen sol menüden veri oluşturun.")

with tab2:
    if not st.session_state['ogrenciler'].empty:
        # Basit bir GNO grafiği
        st.bar_chart(st.session_state['ogrenciler']['GNO'])