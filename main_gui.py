import sys
import time
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QTableWidget,
                             QTableWidgetItem, QHeaderView, QMessageBox, QTabWidget,
                             QFrame, QProgressBar, QStatusBar, QGraphicsDropShadowEffect,
                             QTextEdit, QLineEdit)  # <--- QLineEdit eklendi
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QIntValidator  # <--- QIntValidator eklendi

# --- Import Kontrolü ---
try:
    from veri_olustur import veri_seti_olustur
    from algo_greedy import greedy_atama, simulasyon_dongusu
    from algo_heuristic import heuristic_atama, memnuniyet_skoru_hesapla
except ImportError as e:
    def veri_seti_olustur(*args, **kwargs):
        return pd.DataFrame(), pd.DataFrame()


    def greedy_atama(*args, **kwargs):
        return pd.DataFrame(), pd.DataFrame()


    def simulasyon_dongusu(*args, **kwargs):
        return pd.DataFrame(), pd.DataFrame(), []


    def heuristic_atama(*args, **kwargs):
        return pd.DataFrame(), pd.DataFrame()


    def memnuniyet_skoru_hesapla(*args):
        return 0


# --- 1. GİRİŞ PENCERESİ ---
class GirisPenceresi(QWidget):
    pencere_gecis_sinyali = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sisteme Giriş")
        self.setFixedSize(450, 320)
        self.setStyleSheet("""
            QWidget { background-color: #2c3e50; }
            QLabel { color: white; }
            QPushButton { 
                background-color: #f1c40f; color: #2c3e50; border-radius: 6px; 
                font-size: 15px; font-weight: bold; padding: 12px; 
            }
            QPushButton:hover { background-color: #f39c12; }
        """)
        layout = QVBoxLayout()
        layout.addStretch()
        lbl_baslik = QLabel("STAJYER YERLEŞTİRME\nSİMÜLATÖRÜ")
        lbl_baslik.setAlignment(Qt.AlignCenter)
        lbl_baslik.setFont(QFont("Segoe UI", 20, QFont.Bold))
        lbl_alt = QLabel("2025-2026 Dönem Projesi")
        lbl_alt.setAlignment(Qt.AlignCenter)
        lbl_alt.setFont(QFont("Segoe UI", 11))
        lbl_alt.setStyleSheet("color: #bdc3c7;")
        self.btn_baslat = QPushButton("UYGULAMAYI BAŞLAT")
        self.btn_baslat.setCursor(Qt.PointingHandCursor)
        self.btn_baslat.setFixedWidth(220)
        self.btn_baslat.clicked.connect(self.tiklandi)
        layout.addWidget(lbl_baslik, alignment=Qt.AlignCenter)
        layout.addWidget(lbl_alt, alignment=Qt.AlignCenter)
        layout.addSpacing(25)
        layout.addWidget(self.btn_baslat, alignment=Qt.AlignCenter)
        layout.addStretch()
        self.setLayout(layout)

    def tiklandi(self):
        self.pencere_gecis_sinyali.emit()
        self.close()


# --- 2. ANA ARAYÜZ ---
class ModernProjeArayuz(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("InternPlacement v4.0 - Parametrik")
        self.setGeometry(50, 50, 1400, 850)

        self.df_ogrenciler = None
        self.df_firmalar = None
        self.sonuc_ogrenciler = None
        self.sonuc_firmalar = None
        self.greedy_skor = 0
        self.greedy_sure = 0
        self.heuristic_skor = 0
        self.heuristic_sure = 0

        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ================= SOL MENÜ (INPUTLAR BURAYA EKLENDİ) =================
        left_panel = QFrame()
        left_panel.setObjectName("LeftPanel")
        left_panel.setFixedWidth(260)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(15, 40, 15, 20)
        left_layout.setSpacing(15)

        lbl_baslik = QLabel("STAJYER\nSİMÜLATÖRÜ")
        lbl_baslik.setObjectName("MenuTitle")
        lbl_baslik.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(lbl_baslik)

        lbl_yil = QLabel("2025 - 2026")
        lbl_yil.setObjectName("MenuSubtitle")
        lbl_yil.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(lbl_yil)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: rgba(255,255,255,0.2);")
        left_layout.addWidget(line)

        # --- YENİ INPUT ALANLARI ---
        input_style = """
            QLineEdit { 
                background-color: rgba(255, 255, 255, 0.1); 
                color: white; 
                border: 1px solid rgba(255, 255, 255, 0.3); 
                border-radius: 4px; 
                padding: 5px; 
                font-weight: bold;
            }
            QLabel { color: #bdc3c7; font-size: 12px; font-weight: bold; }
        """

        # Öğrenci Sayısı Input
        lbl_ogr = QLabel("Öğrenci Sayısı:")
        lbl_ogr.setStyleSheet(input_style)
        self.txt_ogrenci_sayisi = QLineEdit()
        self.txt_ogrenci_sayisi.setText("150")  # Varsayılan
        self.txt_ogrenci_sayisi.setValidator(QIntValidator(1, 10000))  # Sadece sayı
        self.txt_ogrenci_sayisi.setStyleSheet(input_style)

        # Firma Sayısı Input
        lbl_frm = QLabel("Firma Sayısı:")
        lbl_frm.setStyleSheet(input_style)
        self.txt_firma_sayisi = QLineEdit()
        self.txt_firma_sayisi.setText("40")  # Varsayılan
        self.txt_firma_sayisi.setValidator(QIntValidator(1, 1000))
        self.txt_firma_sayisi.setStyleSheet(input_style)

        # Inputları Layout'a ekle
        left_layout.addWidget(lbl_ogr)
        left_layout.addWidget(self.txt_ogrenci_sayisi)
        left_layout.addWidget(lbl_frm)
        left_layout.addWidget(self.txt_firma_sayisi)

        left_layout.addSpacing(10)  # Biraz boşluk

        # Butonlar
        self.btn_veri = self.create_button("🎲  Veri Seti Oluştur", self.veri_uret_tikla)
        self.btn_greedy = self.create_button("🚀  Greedy Algoritması", self.greedy_calistir, False)
        self.btn_heuristic = self.create_button("🧠  Heuristic İyileştirme", self.heuristic_calistir, False)
        self.btn_analiz = self.create_button("📊  Simülasyon & Analiz", self.analiz_sayfasini_ac, False)
        self.btn_reset = self.create_button("🔄  Sistemi Sıfırla", self.sistemi_sifirla)

        left_layout.addWidget(self.btn_veri)
        left_layout.addWidget(self.btn_greedy)
        left_layout.addWidget(self.btn_heuristic)
        left_layout.addWidget(self.btn_analiz)
        left_layout.addStretch()
        left_layout.addWidget(self.btn_reset)
        main_layout.addWidget(left_panel)

        # ================= SAĞ PANEL (AYNI) =================
        right_container = QWidget()
        right_container.setStyleSheet("background-color: #f4f6f9;")
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: white; border-bottom: 1px solid #dcdcdc;")
        header_frame.setFixedHeight(60)
        header_frame.setGraphicsEffect(self.get_shadow())
        h_layout = QHBoxLayout(header_frame)
        h_layout.setContentsMargins(30, 0, 30, 0)
        self.lbl_page_title = QLabel("Kontrol Paneli")
        self.lbl_page_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.lbl_page_title.setStyleSheet("color: #2c3e50; border: none;")
        self.lbl_status = QLabel("Durum: Bekleniyor")
        self.lbl_status.setStyleSheet("color: #7f8c8d;")
        h_layout.addWidget(self.lbl_page_title)
        h_layout.addStretch()
        h_layout.addWidget(self.lbl_status)
        right_layout.addWidget(header_frame)

        # Tabs
        self.tabs_main = QTabWidget()
        self.tabs_main.tabBar().setVisible(False)

        self.page_dashboard = QWidget()
        self.setup_dashboard_page(self.page_dashboard)
        self.tabs_main.addTab(self.page_dashboard, "Dashboard")

        self.page_analiz = QWidget()
        self.setup_analiz_page(self.page_analiz)
        self.tabs_main.addTab(self.page_analiz, "Analiz")

        right_layout.addWidget(self.tabs_main)

        self.pbar = QProgressBar()
        self.pbar.setFixedHeight(5)
        self.pbar.setTextVisible(False)
        self.pbar.setStyleSheet(
            "QProgressBar {border:none; background:#e0e0e0;} QProgressBar::chunk {background:#27ae60;}")
        right_layout.addWidget(self.pbar)

        main_layout.addWidget(right_container)
        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def setup_dashboard_page(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        dash_layout = QHBoxLayout()
        self.card_total = self.create_card("Toplam Öğrenci", "0", "#3498db")
        self.card_placed = self.create_card("Yerleşen", "0", "#27ae60")
        self.card_score = self.create_card("Memnuniyet Puanı", "0", "#f39c12")
        self.card_time = self.create_card("İşlem Süresi", "0 sn", "#9b59b6")
        dash_layout.addWidget(self.card_total)
        dash_layout.addWidget(self.card_placed)
        dash_layout.addWidget(self.card_score)
        dash_layout.addWidget(self.card_time)
        layout.addLayout(dash_layout)

        self.tabs_data = QTabWidget()
        self.tabs_data.setStyleSheet(self.get_tab_style())
        self.tab_ogrenci = QTableWidget()
        self.tab_firma = QTableWidget()
        self.setup_table(self.tab_ogrenci)
        self.setup_table(self.tab_firma)
        self.tabs_data.addTab(self.tab_ogrenci, "📄 Öğrenci Listesi")
        self.tabs_data.addTab(self.tab_firma, "🏢 Firmalar ve Yerleşenler")
        layout.addWidget(self.tabs_data)

    def setup_analiz_page(self, parent):
        layout = QHBoxLayout(parent)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Simülasyon
        left_frame = QFrame()
        left_frame.setStyleSheet("background: white; border-radius: 8px;")
        left_frame.setGraphicsEffect(self.get_shadow())
        l_layout = QVBoxLayout(left_frame)
        lbl_sim = QLabel("🔄 Simülasyon Döngüsü")
        lbl_sim.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl_sim.setStyleSheet("color: #2c3e50; border:none;")
        l_layout.addWidget(lbl_sim)
        self.btn_sim_baslat = QPushButton("Simülasyonu Başlat")
        self.btn_sim_baslat.setStyleSheet(
            "background-color: #e67e22; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")
        self.btn_sim_baslat.clicked.connect(self.simulasyon_baslat)
        l_layout.addWidget(self.btn_sim_baslat)
        self.table_sim = QTableWidget()
        self.table_sim.setColumnCount(5)
        self.table_sim.setHorizontalHeaderLabels(["Tur", "Yerleşen", "Reddedilen", "Kalan Kont.", "Detaylar"])
        self.setup_table(self.table_sim)
        self.table_sim.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        l_layout.addWidget(self.table_sim)
        layout.addWidget(left_frame, 60)

        # Karşılaştırma
        right_frame = QFrame()
        right_frame.setStyleSheet("background: white; border-radius: 8px;")
        right_frame.setGraphicsEffect(self.get_shadow())
        r_layout = QVBoxLayout(right_frame)
        lbl_kars = QLabel("🆚 Yöntem Karşılaştırması")
        lbl_kars.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl_kars.setStyleSheet("color: #2c3e50; border:none;")
        r_layout.addWidget(lbl_kars)
        self.table_comp = QTableWidget()
        self.table_comp.setColumnCount(3)
        self.table_comp.setRowCount(2)
        self.table_comp.setHorizontalHeaderLabels(["Kriter", "Greedy", "Heuristic"])
        self.table_comp.setItem(0, 0, QTableWidgetItem("Memnuniyet Skoru"))
        self.table_comp.setItem(1, 0, QTableWidgetItem("Çözüm Süresi"))
        self.setup_table(self.table_comp)
        r_layout.addWidget(self.table_comp)
        self.txt_sonuc = QTextEdit()
        self.txt_sonuc.setReadOnly(True)
        self.txt_sonuc.setStyleSheet("background: #f8f9fa; border: 1px solid #ddd; padding: 10px; color: #333;")
        r_layout.addWidget(self.txt_sonuc)
        layout.addWidget(right_frame, 40)

    # --- YARDIMCI METOTLAR ---
    def get_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 4)
        return shadow

    def get_tab_style(self):
        return """
            QTabWidget::pane { border: 1px solid #dcdcdc; background: white; border-radius: 5px; }
            QTabBar::tab { background: #ecf0f1; padding: 8px 20px; margin-right: 2px; border-top-left-radius: 5px; border-top-right-radius: 5px; }
            QTabBar::tab:selected { background: white; border-bottom: 3px solid #3498db; color: #3498db; font-weight: bold; }
        """

    def create_button(self, text, func, enabled=True):
        btn = QPushButton(text)
        btn.clicked.connect(func)
        btn.setEnabled(enabled)
        btn.setFixedHeight(50)
        btn.setCursor(Qt.PointingHandCursor)
        return btn

    def create_card(self, title, value, color):
        frame = QFrame()
        frame.setStyleSheet(f"background-color: white; border-left: 5px solid {color}; border-radius: 8px;")
        frame.setGraphicsEffect(self.get_shadow())
        l = QVBoxLayout(frame)
        lbl_t = QLabel(title)
        lbl_t.setStyleSheet("color: #7f8c8d; font-weight: bold; border:none;")
        lbl_v = QLabel(value)
        lbl_v.setObjectName("CardValue")
        lbl_v.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: 800; border:none;")
        l.addWidget(lbl_t)
        l.addWidget(lbl_v)
        return frame

    def setup_table(self, table):
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setStyleSheet(
            "QTableWidget { background-color: white; border: none; gridline-color: #ecf0f1; } QHeaderView::section { background-color: #34495e; color: white; padding: 5px; }")

    def update_card(self, card, val):
        for lbl in card.findChildren(QLabel):
            if lbl.objectName() == "CardValue": lbl.setText(str(val))

    def tabloyu_doldur(self, df, table):
        if df is None: return
        table.setRowCount(df.shape[0])
        table.setColumnCount(df.shape[1])
        table.setHorizontalHeaderLabels(df.columns)
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                table.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #f4f6f9; }
            #LeftPanel { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2c3e50, stop:1 #34495e); }
            #MenuTitle { color: #f1c40f; font-size: 18px; font-weight: 900; letter-spacing: 1px; margin-bottom: 5px; } 
            #MenuSubtitle { color: #bdc3c7; font-size: 13px; margin-bottom: 15px; }
            QPushButton { background-color: rgba(255, 255, 255, 0.05); color: white; border: none; padding-left: 15px; text-align: left; border-radius: 6px; font-size: 14px; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.15); border-left: 4px solid #f1c40f; }
            QPushButton:disabled { color: #7f8c8d; }
        """)

    # --- AKSİYONLAR ---
    def veri_uret_tikla(self):
        try:
            # Kullanıcının girdiği sayıları al (GÜNCELLENDİ)
            str_ogr = self.txt_ogrenci_sayisi.text()
            str_frm = self.txt_firma_sayisi.text()

            if not str_ogr or not str_frm:
                QMessageBox.warning(self, "Uyarı", "Lütfen öğrenci ve firma sayısı giriniz.")
                return

            ogrenci_sayisi = int(str_ogr)
            firma_sayisi = int(str_frm)

            # Parametrik fonksiyonu çağır
            self.df_firmalar, self.df_ogrenciler = veri_seti_olustur(ogrenci_sayisi, firma_sayisi)

            self.update_card(self.card_total, len(self.df_ogrenciler))
            self.tabloyu_doldur(self.df_ogrenciler, self.tab_ogrenci)
            self.tabloyu_doldur(self.df_firmalar, self.tab_firma)

            self.btn_greedy.setEnabled(True)
            self.btn_analiz.setEnabled(True)
            self.lbl_status.setText(f"Durum: {ogrenci_sayisi} Öğrenci, {firma_sayisi} Firma Hazır")
            self.tabs_main.setCurrentIndex(0)

        except ValueError as ve:
            QMessageBox.critical(self, "Veri Hatası",
                                 f"Lütfen geçerli sayılar giriniz.\nFirma sayısı öğrenci sayısından büyük olamaz.\n{ve}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def greedy_calistir(self):
        self.lbl_status.setText("Durum: Greedy Çalışıyor...")
        QApplication.processEvents()
        t1 = time.time()
        try:
            self.sonuc_ogrenciler, self.sonuc_firmalar = greedy_atama(self.df_ogrenciler, self.df_firmalar)
            t2 = time.time()
            self.greedy_sure = t2 - t1
            self.greedy_skor = memnuniyet_skoru_hesapla(self.sonuc_ogrenciler)

            yerlesen = self.sonuc_ogrenciler['Yerleştiği_Firma'].notna().sum()
            self.update_card(self.card_placed, yerlesen)
            self.update_card(self.card_score, self.greedy_skor)
            self.update_card(self.card_time, f"{self.greedy_sure:.4f} sn")

            self.tabloyu_doldur(self.sonuc_ogrenciler, self.tab_ogrenci)
            self.tabloyu_doldur(self.sonuc_firmalar, self.tab_firma)

            self.btn_heuristic.setEnabled(True)
            self.lbl_status.setText("Durum: Greedy Tamamlandı")
            self.tabs_main.setCurrentIndex(0)
            self.update_karsilastirma_tablosu()
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def heuristic_calistir(self):
        self.lbl_status.setText("Durum: Heuristic Çalışıyor...")
        self.btn_heuristic.setEnabled(False)
        self.pbar.setValue(0)
        QApplication.processEvents()
        t1 = time.time()

        def progress(s):
            self.pbar.setValue(int((s / 3000) * 100))
            QApplication.processEvents()

        try:
            try:
                h_ogr, h_frm = heuristic_atama(self.sonuc_ogrenciler, self.sonuc_firmalar, iterasyon=3000,
                                               step_callback=progress)
            except:
                h_ogr, h_frm = heuristic_atama(self.sonuc_ogrenciler, self.sonuc_firmalar, iterasyon=3000)

            t2 = time.time()
            self.heuristic_sure = t2 - t1
            self.heuristic_skor = memnuniyet_skoru_hesapla(h_ogr)
            self.sonuc_ogrenciler = h_ogr
            self.sonuc_firmalar = h_frm

            yerlesen = h_ogr['Yerleştiği_Firma'].notna().sum()
            self.update_card(self.card_placed, yerlesen)
            self.update_card(self.card_score, self.heuristic_skor)
            self.update_card(self.card_time, f"{self.heuristic_sure:.2f} sn")

            self.tabloyu_doldur(h_ogr, self.tab_ogrenci)
            self.tabloyu_doldur(h_frm, self.tab_firma)

            self.pbar.setValue(100)
            self.lbl_status.setText("Durum: Heuristic Bitti")
            self.update_karsilastirma_tablosu()
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))
        self.btn_heuristic.setEnabled(True)

    def analiz_sayfasini_ac(self):
        self.lbl_page_title.setText("Simülasyon & Analiz Paneli")
        self.tabs_main.setCurrentIndex(1)
        self.update_karsilastirma_tablosu()

    def simulasyon_baslat(self):
        if self.df_ogrenciler is None: return
        self.table_sim.setRowCount(0)
        self.lbl_status.setText("Durum: Simülasyon Döngüsü Çalışıyor...")
        QApplication.processEvents()

        try:
            _, _, logs = simulasyon_dongusu(self.df_ogrenciler, self.df_firmalar)
            self.table_sim.setRowCount(len(logs))
            for i, log in enumerate(logs):
                self.table_sim.setItem(i, 0, QTableWidgetItem(str(log['Tur'])))
                self.table_sim.setItem(i, 1, QTableWidgetItem(str(log['Yerleşen'])))
                self.table_sim.setItem(i, 2, QTableWidgetItem(str(log['Reddedilen'])))
                self.table_sim.setItem(i, 3, QTableWidgetItem(str(log['Kalan_Kontenjan'])))
                self.table_sim.setItem(i, 4, QTableWidgetItem(str(log['Red_Detay'])))
            self.lbl_status.setText("Durum: Simülasyon Tamamlandı")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Simülasyon Hatası: {e}")

    def update_karsilastirma_tablosu(self):
        self.table_comp.setItem(0, 1, QTableWidgetItem(str(self.greedy_skor)))
        self.table_comp.setItem(0, 2, QTableWidgetItem(str(self.heuristic_skor)))
        self.table_comp.setItem(1, 1, QTableWidgetItem(f"{self.greedy_sure:.4f} sn"))
        self.table_comp.setItem(1, 2, QTableWidgetItem(f"{self.heuristic_sure:.2f} sn"))

        if self.heuristic_skor > 0:
            fark = self.heuristic_skor - self.greedy_skor
            yuzde = (fark / self.greedy_skor) * 100 if self.greedy_skor > 0 else 0
            yorum = (f"SONUÇ ANALİZİ:\n"
                     f"Heuristic yöntem, Greedy yöntemine göre memnuniyet skorunu {fark} puan "
                     f"(%{yuzde:.1f}) artırmıştır.\n"
                     f"Ancak işlem süresi {self.heuristic_sure / (self.greedy_sure + 0.0001):.1f} kat daha uzundur.")
            self.txt_sonuc.setText(yorum)

    def sistemi_sifirla(self):
        self.df_ogrenciler = None
        self.tab_ogrenci.setRowCount(0)
        self.table_sim.setRowCount(0)
        self.update_card(self.card_total, "0")
        self.update_card(self.card_placed, "0")
        self.update_card(self.card_score, "0")
        self.update_card(self.card_time, "0 sn")
        self.btn_greedy.setEnabled(False)
        self.btn_heuristic.setEnabled(False)
        self.pbar.setValue(0)
        self.tabs_main.setCurrentIndex(0)
        self.lbl_page_title.setText("Kontrol Paneli")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    giris_penceresi = GirisPenceresi()
    ana_arayuz = ModernProjeArayuz()


    def ana_ekrani_goster():
        ana_arayuz.show()


    giris_penceresi.pencere_gecis_sinyali.connect(ana_ekrani_goster)
    giris_penceresi.show()
    sys.exit(app.exec_())