import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QTableWidget,
                             QTableWidgetItem, QHeaderView, QMessageBox, QTabWidget)
from PyQt5.QtCore import Qt

# Diğer dosyalarından fonksiyonları çağırıyoruz
try:
    from veri_olustur import veri_seti_olustur
    from algo_greedy import greedy_atama
    from algo_heuristic import heuristic_atama, memnuniyet_skoru_hesapla
except ImportError as e:
    print(f"Hata: Modüller bulunamadı. Lütfen dosya isimlerini kontrol edin.\n{e}")


class ProjeArayuz(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stajyer Yerleştirme Simülatörü - 2025/2026")
        self.setGeometry(100, 100, 1000, 700)

        # Veri saklama değişkenleri
        self.df_ogrenciler = None
        self.df_firmalar = None
        self.sonuc_ogrenciler = None
        self.sonuc_firmalar = None

        self.init_ui()

    def init_ui(self):
        # Ana Widget ve Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Üst Panel: Butonlar ve Bilgi
        btn_layout = QHBoxLayout()

        self.btn_veri_uret = QPushButton("1. Veri Seti Oluştur")
        self.btn_veri_uret.clicked.connect(self.veri_uret_tikla)
        self.btn_veri_uret.setStyleSheet("background-color: #d1e7dd; padding: 10px;")

        self.btn_greedy = QPushButton("2. Greedy Çalıştır")
        self.btn_greedy.clicked.connect(self.greedy_calistir)
        self.btn_greedy.setEnabled(False)  # Veri olmadan çalışmasın

        self.btn_heuristic = QPushButton("3. Heuristic İyileştir")
        self.btn_heuristic.clicked.connect(self.heuristic_calistir)
        self.btn_heuristic.setEnabled(False)  # Greedy çalışmadan çalışmasın

        btn_layout.addWidget(self.btn_veri_uret)
        btn_layout.addWidget(self.btn_greedy)
        btn_layout.addWidget(self.btn_heuristic)

        main_layout.addLayout(btn_layout)

        # Bilgi Etiketi (Skorlar vs.)
        self.lbl_info = QLabel("Sistem Hazır. Lütfen veri seti oluşturun.")
        self.lbl_info.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        self.lbl_info.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.lbl_info)

        # Tablo Alanı (Sekmeli Yapı)
        self.tabs = QTabWidget()
        self.tab_ogrenci = QWidget()
        self.tab_firma = QWidget()

        self.tabs.addTab(self.tab_ogrenci, "Öğrenci Listesi")
        self.tabs.addTab(self.tab_firma, "Firma Kontenjanları")

        # Tablo Layoutları
        self.layout_tab1 = QVBoxLayout()
        self.table_ogrenci = QTableWidget()
        self.layout_tab1.addWidget(self.table_ogrenci)
        self.tab_ogrenci.setLayout(self.layout_tab1)

        self.layout_tab2 = QVBoxLayout()
        self.table_firma = QTableWidget()
        self.layout_tab2.addWidget(self.table_firma)
        self.tab_firma.setLayout(self.layout_tab2)

        main_layout.addWidget(self.tabs)

    def tabloyu_doldur(self, df, tablo_widget):
        if df is None: return

        tablo_widget.setRowCount(df.shape[0])
        tablo_widget.setColumnCount(df.shape[1])
        tablo_widget.setHorizontalHeaderLabels(df.columns)

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                deger = str(df.iloc[i, j])
                item = QTableWidgetItem(deger)
                tablo_widget.setItem(i, j, item)

        tablo_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def veri_uret_tikla(self):
        try:
            # Varsayılan değerlerle veri üret
            self.df_firmalar, self.df_ogrenciler = veri_seti_olustur(ogrenci_sayisi=150, firma_sayisi=40)

            self.lbl_info.setText("Veri seti oluşturuldu! Greedy algoritmasını çalıştırabilirsiniz.")
            self.tabloyu_doldur(self.df_ogrenciler, self.table_ogrenci)
            self.tabloyu_doldur(self.df_firmalar, self.table_firma)

            self.btn_greedy.setEnabled(True)
            self.btn_heuristic.setEnabled(False)
            self.sonuc_ogrenciler = None  # Önceki sonuçları temizle

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Veri üretilirken hata oluştu:\n{str(e)}")

    def greedy_calistir(self):
        if self.df_ogrenciler is None: return

        try:
            # Orijinal veriyi bozmamak için kopyalıyoruz
            ogr_copy = self.df_ogrenciler.copy()
            frm_copy = self.df_firmalar.copy()

            # Greedy algoritmasını çağır
            self.sonuc_ogrenciler, self.sonuc_firmalar = greedy_atama(ogr_copy, frm_copy)

            skor = memnuniyet_skoru_hesapla(self.sonuc_ogrenciler)
            yerlesen_sayisi = self.sonuc_ogrenciler['Yerleştiği_Firma'].notna().sum()

            self.lbl_info.setText(f"Greedy Tamamlandı. Yerleşen: {yerlesen_sayisi}/150 | Memnuniyet Skoru: {skor}")
            self.lbl_info.setStyleSheet("color: blue; font-size: 14px; font-weight: bold;")

            self.tabloyu_doldur(self.sonuc_ogrenciler, self.table_ogrenci)
            self.tabloyu_doldur(self.sonuc_firmalar, self.table_firma)

            self.btn_heuristic.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Greedy çalışırken hata oluştu:\n{str(e)}")

    def heuristic_calistir(self):
        if self.sonuc_ogrenciler is None: return

        try:
            self.lbl_info.setText("Heuristic çalışıyor, lütfen bekleyin...")
            QApplication.processEvents()  # Arayüzün donmasını engeller

            # Heuristic algoritmasını çağır (Greedy sonuçları üzerinden devam eder)
            h_ogr, h_frm = heuristic_atama(self.sonuc_ogrenciler, self.sonuc_firmalar, iterasyon=2000)

            skor = memnuniyet_skoru_hesapla(h_ogr)
            yerlesen_sayisi = h_ogr['Yerleştiği_Firma'].notna().sum()

            self.lbl_info.setText(f"Heuristic Tamamlandı! Yerleşen: {yerlesen_sayisi}/150 | YENİ SKOR: {skor}")
            self.lbl_info.setStyleSheet("color: green; font-size: 14px; font-weight: bold;")

            self.tabloyu_doldur(h_ogr, self.table_ogrenci)
            self.tabloyu_doldur(h_frm, self.table_firma)

            # Sonuçları güncelle
            self.sonuc_ogrenciler = h_ogr
            self.sonuc_firmalar = h_frm

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Heuristic çalışırken hata oluştu:\n{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProjeArayuz()
    window.show()
    sys.exit(app.exec_())