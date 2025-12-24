import pandas as pd
import numpy as np


def greedy_atama(ogrenciler_df, firmalar_df):
    ogrenciler = ogrenciler_df.copy().reset_index(drop=True)
    firmalar = firmalar_df.copy().reset_index(drop=True)

    # Yeni sütunları başlat
    ogrenciler['Yerleştiği_Firma'] = None
    ogrenciler['Tercih_Sırası'] = "-"  # <--- YENİ SÜTUN (Kaçıncı tercih?)
    firmalar['Yerlesenler'] = None

    sirali_ogrenciler = ogrenciler.sort_values('GNO', ascending=False)

    for idx, ogrenci in sirali_ogrenciler.iterrows():
        # 1'den 5'e kadar tercihleri dönüyoruz
        for i in range(1, 6):
            tercih_firma = ogrenci[f'Tercih{i}']

            firma_row = firmalar[firmalar['Firma'] == tercih_firma]
            if firma_row.empty: continue

            firma_idx = firma_row.index[0]
            if firmalar.at[firma_idx, 'Kontenjan'] > 0:
                ogrenciler.at[idx, 'Yerleştiği_Firma'] = tercih_firma
                ogrenciler.at[idx, 'Tercih_Sırası'] = i  # <--- YENİ: Tercih sırasını kaydet
                firmalar.at[firma_idx, 'Kontenjan'] -= 1
                break

    # Firmalara yerleşenleri yazma işlemi
    yerlesen_grup = ogrenciler[ogrenciler['Yerleştiği_Firma'].notna()].groupby('Yerleştiği_Firma')['Öğrenci'].apply(
        lambda x: ", ".join(x))
    firmalar['Yerlesenler'] = firmalar['Firma'].map(yerlesen_grup).fillna("-")

    return ogrenciler, firmalar


def simulasyon_dongusu(ogrenciler_df, firmalar_df):
    ogr = ogrenciler_df.copy().reset_index(drop=True)
    frm = firmalar_df.copy().reset_index(drop=True)

    ogr['Yerleştiği_Firma'] = None
    ogr['Tercih_Sırası'] = "-"  # <--- YENİ
    frm['Yerlesenler'] = None

    gecmis_log = []
    max_tur = 10

    for tur in range(1, max_tur + 1):
        # 1. Greedy Yerleştirme
        bostakiler = ogr[ogr['Yerleştiği_Firma'].isnull()].sort_values('GNO', ascending=False)
        yerlesen_bu_tur = 0

        for idx, ogrenci in bostakiler.iterrows():
            for i in range(1, 6):
                tercih = ogrenci[f'Tercih{i}']
                f_idx = frm[frm['Firma'] == tercih].index

                if not f_idx.empty and frm.at[f_idx[0], 'Kontenjan'] > 0:
                    ogr.at[idx, 'Yerleştiği_Firma'] = tercih
                    ogr.at[idx, 'Tercih_Sırası'] = i  # <--- YENİ
                    frm.at[f_idx[0], 'Kontenjan'] -= 1
                    yerlesen_bu_tur += 1
                    break

        if yerlesen_bu_tur == 0:
            break

        # 2. Red Simülasyonu
        reddedilen_sayisi = 0
        red_listesi_text = []
        yeni_yerlesenler = ogr[ogr['Yerleştiği_Firma'].notna()]

        for idx, row in yeni_yerlesenler.iterrows():
            if np.random.rand() < 0.10:
                firma = row['Yerleştiği_Firma']
                ogr.at[idx, 'Yerleştiği_Firma'] = None
                ogr.at[idx, 'Tercih_Sırası'] = "-"  # <--- YENİ: Atılınca sırası da silinir

                f_idx = frm[frm['Firma'] == firma].index[0]
                frm.at[f_idx, 'Kontenjan'] += 1
                reddedilen_sayisi += 1
                red_listesi_text.append(f"{firma}->{row['Öğrenci']}")

        kalan_kontenjan = frm['Kontenjan'].sum()
        gecmis_log.append({
            "Tur": tur,
            "Yerleşen": yerlesen_bu_tur,
            "Reddedilen": reddedilen_sayisi,
            "Kalan_Kontenjan": kalan_kontenjan,
            "Red_Detay": ", ".join(red_listesi_text[:3])
        })

    yerlesen_grup = ogr[ogr['Yerleştiği_Firma'].notna()].groupby('Yerleştiği_Firma')['Öğrenci'].apply(
        lambda x: ", ".join(x))
    frm['Yerlesenler'] = frm['Firma'].map(yerlesen_grup).fillna("-")

    return ogr, frm, gecmis_log