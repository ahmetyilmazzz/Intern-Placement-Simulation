import pandas as pd
import numpy as np

def veri_seti_olustur(ogrenci_sayisi, firma_sayisi, tercih_sayisi=5, seed=46, prefix="proje"):
    if firma_sayisi > ogrenci_sayisi:
        raise ValueError("firma_sayisi, ogrenci_sayisi'ndan büyük olamaz (her firmaya en az 1 kontenjan veriyorsun).")
    if firma_sayisi < tercih_sayisi:
        raise ValueError("firma_sayisi, tercih_sayisi'ndan küçük olamaz (replace=False seçim yapıyorsun).")

    rng = np.random.default_rng(seed)

    firma_isimleri = [f"Firma_{i+1}" for i in range(firma_sayisi)]

    kontenjanlar = np.ones(firma_sayisi, dtype=int)
    kalan = ogrenci_sayisi - firma_sayisi
    if kalan > 0:
        secimler = rng.integers(0, firma_sayisi, size=kalan)
        kontenjanlar += np.bincount(secimler, minlength=firma_sayisi)

    df_firmalar = pd.DataFrame({
        "Firma": firma_isimleri,
        "Kontenjan": kontenjanlar
    })

    ogrenciler = []
    for i in range(ogrenci_sayisi):
        isim = f"Ogrenci_{i+1}"
        gno = np.round(rng.uniform(2.0, 4.0), 2)
        tercihler = rng.choice(firma_isimleri, size=tercih_sayisi, replace=False)
        ogrenciler.append([isim, gno, *tercihler])

    df_ogrenciler = pd.DataFrame(
        ogrenciler,
        columns=["Öğrenci", "GNO"] + [f"Tercih{j}" for j in range(1, tercih_sayisi + 1)]
    )

    df_firmalar.to_csv("proje_firmalar.csv", index=False, encoding="utf-8-sig")
    df_ogrenciler.to_csv("proje_ogrenciler.csv", index=False, encoding="utf-8-sig")

    print("Oluşturuldu: proje_firmalar.csv ve proje_ogrenciler.csv\n" + "Toplam kontenjan:", int(df_firmalar["Kontenjan"].sum()))

    return df_firmalar, df_ogrenciler

if __name__ == "__main__":
    veri_seti_olustur(ogrenci_sayisi=150, firma_sayisi=40)