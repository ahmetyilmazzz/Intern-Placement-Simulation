import pandas as pd

def greedy_atama(ogrenciler_df, firmalar_df):
    ogrenciler = ogrenciler_df.copy()
    firmalar = firmalar_df.copy()

    ogrenciler['Yerleştiği_Firma'] = None

    ogrenciler = ogrenciler.sort_values('GNO', ascending=False)
    # ogrenciler = ogrenciler.nlargest(len(ogrenciler), "GNO")

    bosta_olanlar = ogrenciler[ogrenciler['Yerleştiği_Firma'].isnull()]
    print(ogrenciler)

    for index, ogrenci in bosta_olanlar.iterrows():    # enumerate kullanılamaz pandas dataframede tek tek gezmek için iterrows kullanılır
        tercih_listesi = [ogrenci[f'Tercih{i}'] for i in range(1, 6)]
        for tercih_firma in tercih_listesi:
            firma_row = firmalar[firmalar['Firma'] == tercih_firma]

            firma_idx = firma_row.index[0]
            mevcut_kontenjan = firmalar.at[firma_idx, 'Kontenjan']

            if mevcut_kontenjan > 0:
                ogrenciler.at[index, 'Yerleştiği_Firma'] = tercih_firma
                firmalar.at[firma_idx, 'Kontenjan'] -= 1
                # ogrenciler.loc[index, 'Yerleştiği_Firma'] = tercih_firma
                # firmalar.loc[firma_idx, 'Kontenjan'] = mevcut_kontenjan - 1
                break

    return ogrenciler, firmalar


if __name__ == "__main__":
    data_ogrenci = {
        'Öğrenci': ['Ogrenci_1', 'Ogrenci_2', 'Ogrenci_3'],
        'GNO': [3.9, 2.5, 3.8],
        'Tercih1': ['Firma_1', 'Firma_1', 'Firma_2'],
        'Tercih2': ['Firma_2', 'Firma_2', 'Firma_1'],
        'Tercih3': ['Firma_3', 'Firma_3', 'Firma_3'],
        'Tercih4': ['Firma_4', 'Firma_4', 'Firma_4'],
        'Tercih5': ['Firma_5', 'Firma_5', 'Firma_5']
    }

    # Firma_1'in kontenjanı 1, Firma_2'nin kontenjanı 1 olsun
    data_firma = {
        'Firma': ['Firma_1', 'Firma_2', 'Firma_3', 'Firma_4', 'Firma_5'],
        'Kontenjan': [1, 1, 10, 10, 10]
    }

    df_ogr = pd.read_csv("proje_ogrenciler.csv")
    df_frm = pd.read_csv("proje_firmalar.csv")

    print("--- BAŞLANGIÇ DURUMU ---")
    print(df_ogr[['Öğrenci', 'GNO']])
    print(df_frm.head(2))

    sonuc_ogr, sonuc_frm = greedy_atama(df_ogr, df_frm)

    print("\n--- SONUÇ DURUMU ---")
    print(sonuc_ogr[['Öğrenci', 'GNO', 'Yerleştiği_Firma']])
    print("\nFirma Kontenjanları (Firma_1 ve Firma_2 0'a düşmeli):")
    print(sonuc_frm.head(2))

