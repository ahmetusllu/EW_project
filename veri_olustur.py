import os
import random
from datetime import date, timedelta

# Önemli: Bu betiği çalıştırmadan önce, core paketinin Python tarafından
# bulunabildiğinden emin olun. Genellikle betiği projenin kök dizininden
# çalıştırmak yeterlidir.
from core.data_models import (
    Radar, Teknik, Senaryo, Gorev,
    GurultuKaristirmaParams, MenzilAldatmaParams, AlmacGondermecAyarParametreleri, KaynakUretecAyarParametreleri,
    FREKANS_BANDLARI, GOREV_TIPLERI, ANTEN_TIPLERI, TEKNIK_KATEGORILERI, SONUC_NITEL
)
from core.data_manager import DataManager


def generate_test_data():
    """
    Uygulama için test verileri oluşturur ve XML dosyalarına kaydeder.
    """
    print("Test verileri oluşturuluyor...")

    # --- 1. Radarları Oluştur (10 Adet) ---
    radarlar = [
        Radar(adi="ASELSAN Kalkan-G", uretici="ASELSAN", frekans_bandi="X", gorev_tipi="Atış Kontrol",
              anten_tipi="AESA"),
        Radar(adi="TAI Gözcü-S", uretici="TAI", frekans_bandi="S", gorev_tipi="Arama", anten_tipi="PESA"),
        Radar(adi="Meteksan MİLDAR", uretici="Meteksan", frekans_bandi="Ka", gorev_tipi="Atış Kontrol",
              anten_tipi="Parabolik"),
        Radar(adi="HAVELSAN EİRS", uretici="HAVELSAN", frekans_bandi="L", gorev_tipi="Erken Uyarı", anten_tipi="AESA"),
        Radar(adi="Thales SMART-L", uretici="Thales", frekans_bandi="L", gorev_tipi="Erken Uyarı", anten_tipi="ESA"),
        Radar(adi="Raytheon AN/SPY-6", uretici="Raytheon", frekans_bandi="S", gorev_tipi="Hava Savunma",
              anten_tipi="AESA"),
        Radar(adi="SAAB Giraffe 4A", uretici="SAAB", frekans_bandi="S", gorev_tipi="Arama", anten_tipi="AESA"),
        Radar(adi="IAI EL/M-2080 Green Pine", uretici="IAI", frekans_bandi="L", gorev_tipi="Atış Kontrol",
              anten_tipi="AESA"),
        Radar(adi="NPP Salyut 30N6E", uretici="NPP Salyut", frekans_bandi="X", gorev_tipi="İzleme", anten_tipi="PESA"),
        Radar(adi="Lockheed Martin AN/TPQ-53", uretici="Lockheed Martin", frekans_bandi="S", gorev_tipi="Arama",
              anten_tipi="AESA"),
    ]
    radar_ids = [r.radar_id for r in radarlar]

    # --- 2. EH Tekniklerini Oluştur (20 Adet) ---
    teknikler = [
        Teknik(adi="Yoğun Sis Perdesi", kategori="Gürültü Karıştırma",
               parametreler=GurultuKaristirmaParams(tur="Barrage", bant_genisligi_mhz=100.0, guc_erp_dbw=50.0)),
        Teknik(adi="Noktasal Karartma", kategori="Gürültü Karıştırma",
               parametreler=GurultuKaristirmaParams(tur="Spot", bant_genisligi_mhz=10.0, guc_erp_dbw=65.0)),
        Teknik(adi="DRFM Tabanlı Gürültü", kategori="Gürültü Karıştırma",
               parametreler=GurultuKaristirmaParams(tur="DRFM Noise", bant_genisligi_mhz=50.0, guc_erp_dbw=55.0)),
        Teknik(adi="Süpürmeli Gürültü", kategori="Gürültü Karıştırma",
               parametreler=GurultuKaristirmaParams(tur="Swept", bant_genisligi_mhz=20.0, guc_erp_dbw=60.0)),

        Teknik(adi="Hassas RGPO Menzil Çekmesi", kategori="Menzil Aldatma",
               parametreler=MenzilAldatmaParams(teknik_tipi="RGPO", cekme_hizi_mps=1500.0, sahte_hedef_sayisi=1)),
        Teknik(adi="Çoklu Sahte Hedef (RGPI)", kategori="Menzil Aldatma",
               parametreler=MenzilAldatmaParams(teknik_tipi="RGPI", sahte_hedef_sayisi=8)),
        Teknik(adi="Mesafe Kapısı İleri Çekme", kategori="Menzil Aldatma",
               parametreler=MenzilAldatmaParams(teknik_tipi="RGPI", cekme_hizi_mps=500.0, sahte_hedef_sayisi=2)),

        Teknik(adi="Yüksek Kazançlı RF Ayarı", kategori="Alıcı/Gönderici Ayarları",
               parametreler=AlmacGondermecAyarParametreleri(rf_kazanc_db=70.0, gonderici_guc_dbm=30.0)),
        Teknik(adi="Geniş Bant Örnekleme Modu", kategori="Alıcı/Gönderici Ayarları",
               parametreler=AlmacGondermecAyarParametreleri(on_ornekleme_frekansi_ghz=20.0, modulasyon_tipi="64-QAM")),
        Teknik(adi="Otomatik Kazanç Kontrol Kapatma", kategori="Alıcı/Gönderici Ayarları",
               parametreler=AlmacGondermecAyarParametreleri(otomatik_kazanc_kontrolu_aktif=False, if_kazanc_db=40.0)),

        Teknik(adi="Hızlı Frekans Atlamalı Sinyal", kategori="Kaynak Üreteç Ayarları",
               parametreler=KaynakUretecAyarParametreleri(baslangic_frekansi_mhz=8000.0, bitis_frekansi_mhz=12000.0,
                                                          tarama_suresi_ms=10.0)),
        Teknik(adi="Kısa Darbe Modülasyonu", kategori="Kaynak Üreteç Ayarları",
               parametreler=KaynakUretecAyarParametreleri(dalga_formu_tipi="Darbe", darbe_genisligi_us=0.5,
                                                          darbe_tekrarlama_araligi_us=100.0)),
        Teknik(adi="Düşük Faz Gürültülü Osilatör", kategori="Kaynak Üreteç Ayarları",
               parametreler=KaynakUretecAyarParametreleri(faz_gurultusu_dbc_hz=-110.0)),

        Teknik(adi="Karşı Açı Aldatması", kategori="Açı Aldatması"),
        Teknik(adi="Yan Hüzme Karıştırması", kategori="Açı Aldatması"),

        Teknik(adi="Hız Kapısı Çekme (VGPO)", kategori="Hız Aldatması"),
        Teknik(adi="Yanlış Doppler Üretimi", kategori="Hız Aldatması"),

        Teknik(adi="Darbe Tekrarlama Frekansı (PRF) Değişimi", kategori="Diğer"),
        Teknik(adi="Akıllı Hedef Aldatma", kategori="Diğer"),
        Teknik(adi="Ağ Merkezli EH Saldırısı", kategori="Diğer"),
    ]
    teknik_ids = [t.teknik_id for t in teknikler]

    # --- 3. Senaryoları Oluştur (10 Adet) ---
    senaryolar = []
    today = date.today()
    for i in range(10):
        senaryo_tarihi = today - timedelta(days=random.randint(5, 365))
        secilen_radar_id = random.choice(radar_ids)
        secilen_teknik_sayisi = random.randint(1, 4)
        secilen_teknik_idler = random.sample(teknik_ids, secilen_teknik_sayisi)

        s = Senaryo(
            adi=f"Test Senaryosu-{i + 1:02d}",
            tarih_iso=senaryo_tarihi.isoformat(),
            konum=random.choice(["Doğu Akdeniz", "Ege Denizi", "Konya Test Sahası", "Karadeniz Açıkları"]),
            radar_id=secilen_radar_id,
            teknik_id_list=secilen_teknik_idler,
            sonuc_nitel=random.choice(SONUC_NITEL),
            js_db=round(random.uniform(-5.0, 25.0), 1),
            mesafe_km=round(random.uniform(20.0, 250.0), 1)
        )
        senaryolar.append(s)
    senaryo_ids = [s.senaryo_id for s in senaryolar]

    # --- 4. Görevleri Oluştur (2 Adet) ---
    gorevler = [
        Gorev(
            adi="Hava Savunma Radarlarını Test Etme Görevi",
            sorumlu_personel="Ahmet Yılmaz",
            aciklama="Çeşitli HSR sistemlerine karşı menzil ve açı aldatma tekniklerinin etkinliği test edilmiştir.",
            senaryo_id_list=senaryo_ids[:5]  # İlk 5 senaryo bu göreve ait
        ),
        Gorev(
            adi="Erken Uyarı Sistemlerini Değerlendirme Görevi",
            sorumlu_personel="Ayşe Kaya",
            aciklama="Uzun menzilli arama radarlarına karşı uygulanan gürültü karıştırma senaryoları.",
            senaryo_id_list=senaryo_ids[5:]  # Son 5 senaryo bu göreve ait
        )
    ]

    # --- 5. Verileri XML Dosyalarına Kaydet ---
    # Not: Bu kısım, normalde DataManager'ın içindeki _save_all metodunu kullanır.
    # Burada doğrudan DataManager'ın listelerini doldurup kaydetme işlemini tetikliyoruz.

    dm = DataManager()

    # Oluşturulan verileri DataManager'a yükle
    dm.radarlar = radarlar
    dm.teknikler = teknikler
    dm.senaryolar = senaryolar
    dm.gorevler = gorevler

    # DataManager'ın kaydetme metodunu kullanarak dosyaları oluştur
    # (Bu metotlar private olsa da test betiği için kullanıyoruz)
    print("radarlar.xml oluşturuluyor...")
    dm._save_all(dm.radarlar, "data/radarlar.xml", "schemas/radar_schema.xsd", "Radarlar")

    print("teknikler.xml oluşturuluyor...")
    dm._save_all(dm.teknikler, "data/teknikler.xml", "schemas/teknik_schema.xsd", "Teknikler")

    print("senaryolar.xml oluşturuluyor...")
    dm._save_all(dm.senaryolar, "data/senaryolar.xml", "schemas/senaryo_schema.xsd", "Senaryolar")

    print("gorevler.xml oluşturuluyor...")
    dm._save_all(dm.gorevler, "data/gorevler.xml", "schemas/gorev_schema.xsd", "Gorevler")

    print("\nTest verileri başarıyla oluşturuldu!")
    print("Oluşturulan dosyalar: data/radarlar.xml, data/teknikler.xml, data/senaryolar.xml, data/gorevler.xml")
    print("\nUygulamayı açıp test etmek için bu verileri içeren bir 'Veri Seti' olarak kaydedebilirsiniz.")
    print("Bunun için önce 'veri_seti.xml' adında bir dosya oluşturalım.")

    # Tüm veriyi tek bir "Veri Seti" dosyası olarak da kaydedelim
    dm.save_workspace("veri_seti.xml")
    print("\nTüm veriler 'veri_seti.xml' dosyasına da kaydedildi.")
    print(
        "Uygulamayı açtıktan sonra 'Dosya -> Veri Seti Aç...' menüsünden bu dosyayı seçerek tüm verileri yükleyebilirsiniz.")


if __name__ == "__main__":
    # 'data' ve 'schemas' klasörlerinin var olduğundan emin ol
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("schemas"):
        print("UYARI: 'schemas' klasörü bulunamadı. XML doğrulama yapılmayacak.")

    generate_test_data()