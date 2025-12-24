import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QTableWidget,
                             QTableWidgetItem, QHeaderView, QMessageBox, QTabWidget,
                             QFrame, QProgressBar, QSplitter, QStatusBar)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor

# --- Import Kontrolü ---
try:
    from veri_olustur import veri_seti_olustur
    from algo_greedy import greedy_atama
    from algo_heuristic import heuristic_atama, memnuniyet_skoru_hesapla
except ImportError as e:
    print(f"KRİTİK HATA: Modüller bulunamadı! {e}")
    # Hata olsa bile arayüzün açılması için dummy fonksiyonlar (gerekirse)
    pass


class ModernProjeArayuz(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("InternPlacement v2.0 - Stajyer Yerleştirme Simülasyonu")
        self.setGeometry(100, 100, 1280, 800)

        # Veri Değişkenleri
        self.df_ogrenciler = None
        self.df_firmalar = None
        self.sonuc_ogrenciler = None
        self.sonuc_firmalar = None

        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        # Ana Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- 1. SOL PANEL (MENÜ) ---
        left_panel = QFrame()
        left_panel.setObjectName("LeftPanel")
        left_panel.setFixedWidth(250)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 40, 20, 20)
        left_layout.setSpacing(20)

        # Başlık
        lbl_baslik = QLabel("STAJYER\nSİMÜLATÖRÜ")
        lbl_baslik.setObjectName("MenuTitle")
        lbl_baslik.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(lbl_baslik)

        # Çizgi
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("MenuLine")
        left_layout.addWidget(line)

        # Butonlar
        self.btn_veri = self.create_menu_button("🎲  Veri Seti Oluştur", self.veri_uret_tikla)
        self.btn_greedy = self.create_menu_button("🚀  Greedy Algoritması", self.greedy_calistir, enabled=False)
        self.btn_heuristic = self.create_menu_button("🧠  Heuristic İyileştirme", self.heuristic_calistir, enabled=False)
        self.btn_reset = self.create_menu_button("🔄  Sıfırla", self.sistemi_sifirla)

        left_layout.addWidget(self.btn_veri)
        left_layout.addWidget(self.btn_greedy)
        left_layout.addWidget(self.btn_heuristic)
        left_layout.addStretch()  # Boşluk bırak
        left_layout.addWidget(self.btn_reset)

        # Öğrenci Bilgisi (Footer gibi)
        lbl_footer = QLabel("Grup: Python Projesi\n2025-2026")
        lbl_footer.setObjectName("MenuFooter")
        lbl_footer.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(lbl_footer)

        main_layout.addWidget(left_panel)

        # --- 2. SAĞ PANEL (İÇERİK) ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(20)

        # DASHBOARD (Kartlar)
        dash_layout = QHBoxLayout()
        self.card_total = self.create_info_card("Toplam Öğrenci", "0", "#3498db")
        self.card_placed = self.create_info_card("Yerleşen", "0", "#27ae60")
        self.card_score = self.create_info_card("Memnuniyet Skoru", "0", "#f39c12")

        dash_layout.addWidget(self.card_total)
        dash_layout.addWidget(self.card_placed)
        dash_layout.addWidget(self.card_score)
        right_layout.addLayout(dash_layout)

        # TABLOLAR
        self.tabs = QTabWidget()
        self.tab_ogrenci = QTableWidget()
        self.tab_firma = QTableWidget()

        self.setup_table(self.tab_ogrenci)
        self.setup_table(self.tab_firma)

        self.tabs.addTab(self.tab_ogrenci, "📄 Öğrenci Listesi & Atamalar")
        self.tabs.addTab(self.tab_firma, "🏢 Firma Kontenjan Durumu")

        right_layout.addWidget(self.tabs)

        # PROGRESS BAR (Heuristic için)
        self.pbar = QProgressBar()
        self.pbar.setValue(0)
        self.pbar.setTextVisible(False)
        self.pbar.setFixedHeight(10)
        self.pbar.setStyleSheet(
            "QProgressBar {border:0px; background-color: #ecf0f1; border-radius: 5px;} QProgressBar::chunk {background-color: #3498db; border-radius: 5px;}")
        right_layout.addWidget(self.pbar)

        main_layout.addWidget(right_panel)

        # DURUM ÇUBUĞU
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Sistem Hazır. Lütfen veri seti oluşturun.")

    def create_menu_button(self, text, func, enabled=True):
        btn = QPushButton(text)
        btn.clicked.connect(func)
        btn.setEnabled(enabled)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(50)
        return btn

    def create_info_card(self, title, value, color):
        frame = QFrame()
        frame.setObjectName("InfoCard")
        frame.setStyleSheet(
            f"#InfoCard {{ background-color: white; border-left: 5px solid {color}; border-radius: 8px; }}")

        layout = QVBoxLayout(frame)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #7f8c8d; font-size: 14px;")

        lbl_value = QLabel(value)
        lbl_value.setObjectName("CardValue")  # ID for updating later
        lbl_value.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold;")

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        return frame

    def setup_table(self, table):
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QTableWidget.NoEditTriggers)  # Salt okunur
        table.setSelectionBehavior(QTableWidget.SelectRows)

    def apply_styles(self):
        style = """
        QMainWindow { background-color: #ecf0f1; }
        #LeftPanel { background-color: #2c3e50; border: none; }
        #MenuTitle { color: white; font-size: 20px; font-weight: bold; margin-bottom: 10px; }
        #MenuLine { color: #34495e; }
        #MenuFooter { color: #95a5a6; font-size: 12px; margin-top: 20px; }

        QPushButton {
            background-color: #34495e;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 14px;
            text-align: left;
            padding-left: 20px;
        }
        QPushButton:hover { background-color: #2980b9; }
        QPushButton:pressed { background-color: #1abc9c; }
        QPushButton:disabled { background-color: #7f8c8d; color: #bdc3c7; }

        QTabWidget::pane { border: 1px solid #bdc3c7; background: white; border-radius: 5px; }
        QTabBar::tab { background: #ecf0f1; padding: 10px 20px; margin-right: 2px; border-top-left-radius: 5px; border-top-right-radius: 5px; }
        QTabBar::tab:selected { background: white; border-bottom: 2px solid #3498db; font-weight: bold; }

        QStatusBar { background: #ffffff; color: #2c3e50; }
        """
        self.setStyleSheet(style)

    # --- FONKSİYONLAR ---
    def update_card(self, card, new_value):
        # Card içindeki Value label'ını bulup güncelle
        labels = card.findChildren(QLabel)
        for lbl in labels:
            if lbl.objectName() == "CardValue":
                lbl.setText(str(new_value))

    def tabloyu_doldur(self, df, tablo_widget):
        if df is None: return
        tablo_widget.setRowCount(df.shape[0])
        tablo_widget.setColumnCount(df.shape[1])
        tablo_widget.setHorizontalHeaderLabels(df.columns)

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                item = QTableWidgetItem(str(df.iloc[i, j]))
                tablo_widget.setItem(i, j, item)

    def veri_uret_tikla(self):
        self.status.showMessage("Veri seti oluşturuluyor...")
        try:
            self.df_firmalar, self.df_ogrenciler = veri_seti_olustur(ogrenci_sayisi=150, firma_sayisi=40)

            self.update_card(self.card_total, len(self.df_ogrenciler))
            self.update_card(self.card_placed, "0")
            self.update_card(self.card_score, "0")

            self.tabloyu_doldur(self.df_ogrenciler, self.tab_ogrenci)
            self.tabloyu_doldur(self.df_firmalar, self.tab_firma)

            self.btn_greedy.setEnabled(True)
            self.btn_heuristic.setEnabled(False)
            self.status.showMessage("Veri seti hazır! Greedy algoritmasını çalıştırabilirsiniz.", 5000)

        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def greedy_calistir(self):
        self.status.showMessage("Greedy Algoritması çalışıyor...")
        try:
            ogr_copy = self.df_ogrenciler.copy()
            frm_copy = self.df_firmalar.copy()

            self.sonuc_ogrenciler, self.sonuc_firmalar = greedy_atama(ogr_copy, frm_copy)

            # İstatistikleri Güncelle
            skor = memnuniyet_skoru_hesapla(self.sonuc_ogrenciler)
            yerlesen = self.sonuc_ogrenciler['Yerleştiği_Firma'].notna().sum()

            self.update_card(self.card_placed, f"{yerlesen}")
            self.update_card(self.card_score, f"{skor}")

            self.tabloyu_doldur(self.sonuc_ogrenciler, self.tab_ogrenci)
            self.tabloyu_doldur(self.sonuc_firmalar, self.tab_firma)

            self.btn_heuristic.setEnabled(True)
            self.status.showMessage("Greedy tamamlandı. Sonuçları inceleyebilirsiniz.", 5000)

        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def heuristic_calistir(self):
        self.status.showMessage("Heuristic optimizasyon başladı... Bu işlem biraz sürebilir.")
        self.btn_heuristic.setEnabled(False)  # Tekrar basılmasın
        self.pbar.setValue(10)
        QApplication.processEvents()

        try:
            # Algoritmayı çalıştır
            h_ogr, h_frm = heuristic_atama(self.sonuc_ogrenciler, self.sonuc_firmalar, iterasyon=3000)
            self.pbar.setValue(90)

            skor = memnuniyet_skoru_hesapla(h_ogr)
            yerlesen = h_ogr['Yerleştiği_Firma'].notna().sum()

            self.update_card(self.card_placed, f"{yerlesen}")
            self.update_card(self.card_score, f"{skor}")

            self.tabloyu_doldur(h_ogr, self.tab_ogrenci)
            self.tabloyu_doldur(h_frm, self.tab_firma)

            self.sonuc_ogrenciler = h_ogr
            self.sonuc_firmalar = h_frm

            self.pbar.setValue(100)
            self.status.showMessage("Heuristic İyileştirme Tamamlandı! Skor arttırıldı.", 5000)

        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))
            self.btn_heuristic.setEnabled(True)
            self.pbar.setValue(0)

    def sistemi_sifirla(self):
        self.df_ogrenciler = None
        self.df_firmalar = None
        self.tab_ogrenci.setRowCount(0)
        self.tab_firma.setRowCount(0)
        self.update_card(self.card_total, "0")
        self.update_card(self.card_placed, "0")
        self.update_card(self.card_score, "0")
        self.btn_greedy.setEnabled(False)
        self.btn_heuristic.setEnabled(False)
        self.pbar.setValue(0)
        self.status.showMessage("Sistem sıfırlandı.")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Font Ayarı (Opsiyonel: Sistem fontunu biraz büyütebiliriz)
    font = QFont("Segoe UI", 9)
    app.setFont(font)

    window = ModernProjeArayuz()
    window.show()
    sys.exit(app.exec_())