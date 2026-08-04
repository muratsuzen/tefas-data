import os
import glob
import json
import pandas as pd

def process_excel():
    os.makedirs("data", exist_ok=True)
    json_path = "data/latest_funds.json"

    # data/ klasöründeki .xlsx dosyalarını ara
    excel_files = glob.glob("data/*.xlsx")
    
    if not excel_files:
        print("HATA: data/ klasöründe herhangi bir .xlsx dosyası bulunamadı!")
        return

    # En son yüklenen/güncellenen Excel dosyasını seç
    target_excel = sorted(excel_files, key=os.path.getmtime, reverse=True)[0]
    print(f"İşlenen Excel Dosyası: {target_excel}")

    # skiprows=4: İlk 4 satırı (Rapor Bilgileri vs.) atlar, 5. satırı (Fon Kodu, Fon Adı...) başlık yapar
    df = pd.read_excel(target_excel, skiprows=4)

    # Sütun isimlerini standart Next.js / API formatına eşliyoruz
    df.columns = [
        'fonKodu', 
        'fonUnvan', 
        'tarih', 
        'fiyat', 
        'tedPaySayisi', 
        'kisiSayisi', 
        'portfoyBuyukluk'
    ]

    # Başlık satırının veya boş satırların kalmasını engelle
    df = df.dropna(subset=['fonKodu'])
    df = df[df['fonKodu'].astype(str).str.strip() != 'Fon Kodu']

    # Tarihi standart hale getir (Metin olarak alır, gerekirse DD.MM.YYYY yapar)
    df['tarih'] = pd.to_datetime(df['tarih'], errors='coerce').dt.strftime('%d.%m.%Y')

    # Sayısal alanları temizleme (Gerekirse)
    df['fiyat'] = pd.to_numeric(df['fiyat'], errors='coerce')
    df['kisiSayisi'] = pd.to_numeric(df['kisiSayisi'], errors='coerce')

    # Dict dizisine dönüştür
    funds_data = df.to_dict(orient="records")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(funds_data, f, ensure_ascii=False, indent=2)

    print(f"✅ BAŞARILI: {len(funds_data)} adet fon verisi {json_path} dosyasına yazıldı!")

if __name__ == "__main__":
    process_excel()