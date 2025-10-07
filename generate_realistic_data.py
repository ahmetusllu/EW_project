import os
import random
from datetime import date, timedelta

# Gerekli sınıfları ve modelleri projenizin içinden import edin
from core.data_models import (
    Radar, Teknik, Senaryo, Gorev,
    GurultuKaristirmaParams, MenzilAldatmaParams, AlmacGondermecAyarParametreleri, KaynakUretecAyarParametreleri,
    SONUC_NITEL, DARBE_MODULASYONLARI
)
from core.data_manager import DataManager


def generate_detailed_test_data():
    """
    Uygulama için daha gerçekçi, detaylı ve ilişkisel test verileri oluşturur.
    """
    print("Detaylı ve gerçekçi test verileri oluşturuluyor...")

    # --- 1. Gerçekçi Radarları Oluştur (10 Adet) ---
    # Not: Parametreler (PW, PRF, ERP vb.) halka açık kaynaklardan elde edilen
    # tipik ve temsili değerlerdir.
    radarlar = [
        Radar(adi="AN/SPY-1D(V)", uretici="Lockheed Martin", frekans_bandi="S", gorev_tipi="Hava Savunma",
              anten_tipi="PESA", pw_us=50.0, prf_hz=1000.0, pri_us=1000.0, erp_dbw=90.0,
              darbe_modulasyonu="Faz Kodlu (Barker, Frank vb.)", darbe_entegrasyonu="16-pulse coherent"),
        Radar(adi="ASELSAN ALP-300G", uretici="ASELSAN", frekans_bandi="S", gorev_tipi="Erken Uyarı", anten_tipi="AESA",
              pw_us=100.0, prf_hz=600.0, pri_us=1666.7, erp_dbw=85.0,
              darbe_modulasyonu="Lineer Frekans Mod. (LFM/Chirp)", darbe_entegrasyonu="32-pulse coherent"),
        Radar(adi="Thales APAR", uretici="Thales", frekans_bandi="X", gorev_tipi="Atış Kontrol", anten_tipi="AESA",
              pw_us=2.0, prf_hz=4000.0, pri_us=250.0, erp_dbw=70.0, darbe_modulasyonu="Normal Darbe (CW)",
              darbe_entegrasyonu="8-pulse doppler"),
        Radar(adi="SAAB Giraffe 4A", uretici="SAAB", frekans_bandi="S", gorev_tipi="Arama", anten_tipi="AESA",
              pw_us=10.0, prf_hz=2000.0, pri_us=500.0, erp_dbw=75.0, darbe_modulasyonu="Faz Kodlu (Barker, Frank vb.)",
              darbe_entegrasyonu="non-coherent"),
        Radar(adi="ELTA EL/M-2080 Green Pine", uretici="IAI", frekans_bandi="L", gorev_tipi="Atış Kontrol",
              anten_tipi="AESA", pw_us=250.0, prf_hz=400.0, pri_us=2500.0, erp_dbw=95.0,
              darbe_modulasyonu="Lineer Frekans Mod. (LFM/Chirp)", darbe_entegrasyonu="64-pulse coherent"),
        Radar(adi="92N6E 'Grave Stone'", uretici="Almaz-Antey", frekans_bandi="X", gorev_tipi="İzleme",
              anten_tipi="PESA", pw_us=5.0, prf_hz=5000.0, pri_us=200.0, erp_dbw=80.0,
              darbe_modulasyonu="Faz Kodlu (Barker, Frank vb.)", darbe_entegrasyonu="12-pulse MTI"),
        Radar(adi="AN/APG-81", uretici="Northrop Grumman", frekans_bandi="X", gorev_tipi="Atış Kontrol",
              anten_tipi="AESA", pw_us=1.0, prf_hz=10000.0, pri_us=100.0, erp_dbw=72.0,
              darbe_modulasyonu="Frekans Atlamalı (FH)", darbe_entegrasyonu="High PRF Doppler"),
        Radar(adi="Meteksan MİLDAR", uretici="Meteksan", frekans_bandi="Ka", gorev_tipi="Atış Kontrol",
              anten_tipi="Parabolik", pw_us=0.5, prf_hz=20000.0, pri_us=50.0, erp_dbw=60.0,
              darbe_modulasyonu="Normal Darbe (CW)", darbe_entegrasyonu="FMCW"),
        Radar(adi="ASELSAN Kalkan-II", uretici="ASELSAN", frekans_bandi="X", gorev_tipi="Hava Savunma",
              anten_tipi="AESA", pw_us=30.0, prf_hz=1500.0, pri_us=666.7, erp_dbw=78.0,
              darbe_modulasyonu="Lineer Frekans Mod. (LFM/Chirp)", darbe_entegrasyonu="24-pulse coherent"),
        Radar(adi="Hensoldt TRS-4D", uretici="Hensoldt", frekans_bandi="C", gorev_tipi="Arama", anten_tipi="AESA",
              pw_us=15.0, prf_hz=2200.0, pri_us=454.5, erp_dbw=82.0, darbe_modulasyonu="Faz Kodlu (Barker, Frank vb.)",
              darbe_entegrasyonu="non-coherent"),
    ]
    radar_ids = {r.adi: r.radar_id for r in radarlar}

    # --- 2. Gerçekçi EH Tekniklerini Oluştur (20 Adet) ---
    teknikler = [
        Teknik(adi="Geniş Bant Baraj Karıştırma (BBJ)", kategori="Gürültü Karıştırma",
               aciklama="Hedef radarın tüm olası frekans bandını geniş bir gürültü sinyaliyle bastırır.",
               parametreler=GurultuKaristirmaParams(tur="Barrage", bant_genisligi_mhz=500.0, guc_erp_dbw=60.0)),
        Teknik(adi="Noktasal Gürültü Karıştırma (Spot Noise)", kategori="Gürültü Karıştırma",
               aciklama="Tüm gücü, hedef radarın çalıştığı tek ve dar bir frekansa odaklar.",
               parametreler=GurultuKaristirmaParams(tur="Spot", bant_genisligi_mhz=20.0, guc_erp_dbw=75.0)),
        Teknik(adi="Süpürmeli Gürültü Karıştırma (Swept Noise)", kategori="Gürültü Karıştırma",
               aciklama="Gücü belirli bir frekans aralığında sürekli olarak gezdirir.",
               parametreler=GurultuKaristirmaParams(tur="Swept", bant_genisligi_mhz=100.0, guc_erp_dbw=70.0)),
        Teknik(adi="DRFM Tabanlı Akıllı Gürültü", kategori="Gürültü Karıştırma",
               aciklama="Radar sinyalini taklit eden ancak gürültüye gömülmüş akıllı sinyaller üretir.",
               parametreler=GurultuKaristirmaParams(tur="DRFM Noise", bant_genisligi_mhz=50.0, guc_erp_dbw=65.0)),
        Teknik(adi="Mesafe Kapısı Çekme - Dışarı (RGPO)", kategori="Menzil Aldatma",
               aciklama="Radar sinyalini kopyalayıp geciktirerek hedefin radardan daha uzakta görünmesini sağlar.",
               parametreler=MenzilAldatmaParams(teknik_tipi="RGPO", cekme_hizi_mps=2000.0, sahte_hedef_sayisi=1)),
        Teknik(adi="Mesafe Kapısı Çekme - İçeri (RGPI)", kategori="Menzil Aldatma",
               aciklama="Hedefin radara daha yakın veya üzerinde görünmesini sağlayarak füzeyi erken patlatmayı hedefler.",
               parametreler=MenzilAldatmaParams(teknik_tipi="RGPI", cekme_hizi_mps=-1000.0, sahte_hedef_sayisi=1)),
        Teknik(adi="Çoklu Sahte Hedef Üretimi", kategori="Menzil Aldatma",
               aciklama="Onlarca sahte hedef üreterek radar operatörünü ve sistemini satürasyona uğratır.",
               parametreler=MenzilAldatmaParams(teknik_tipi="RGPI", sahte_hedef_sayisi=20)),
        Teknik(adi="Hız Kapısı Çekme (VGPO)", kategori="Hız Aldatması",
               aciklama="Hedefin hızını Doppler kaymasını değiştirerek olduğundan farklı gösterir."),
        Teknik(adi="Ters Konik Tarama (Inverse Conical Scan)", kategori="Açı Aldatması",
               aciklama="Konik taramalı radarların açısal takip doğruluğunu bozar."),
        Teknik(adi="Yan Hüzme Karıştırması (Sidelobe Jamming)", kategori="Açı Aldatması",
               aciklama="Radar anteninin zayıf olan yan hüzmelerinden sisteme girerek yanlış yön bilgisi oluşturur."),
        Teknik(adi="Chirp Sinyal Üretimi", kategori="Kaynak Üreteç Ayarları",
               aciklama="Darbe sıkıştırma kullanan radarlara karşı etkili, frekansı zamanla değişen sinyal.",
               parametreler=KaynakUretecAyarParametreleri(dalga_formu_tipi="Testere Dişi",
                                                          baslangic_frekansi_mhz=9200.0, bitis_frekansi_mhz=9300.0,
                                                          darbe_genisligi_us=10.0)),
        Teknik(adi="Atım-Atım Frekans Atlamalı Sinyal", kategori="Kaynak Üreteç Ayarları",
               aciklama="Her darbeyi farklı bir frekansta göndererek takip ve karıştırmayı zorlaştırır.",
               parametreler=KaynakUretecAyarParametreleri(dalga_formu_tipi="Darbe", darbe_tekrarlama_araligi_us=500.0)),
        Teknik(adi="Yüksek Hızlı Örnekleme ve Yanıt", kategori="Alıcı/Gönderici Ayarları",
               aciklama="Gelen radar sinyalini çok hızlı örnekleyip anında değiştirerek geri gönderir.",
               parametreler=AlmacGondermecAyarParametreleri(on_ornekleme_frekansi_ghz=40.0, veri_hizi_mbps=1000.0)),
        Teknik(adi="Adaptif Güç Kontrolü", kategori="Alıcı/Gönderici Ayarları",
               aciklama="Hedef radardan gelen sinyal gücüne göre kendi çıkış gücünü anlık olarak ayarlar.",
               parametreler=AlmacGondermecAyarParametreleri(otomatik_kazanc_kontrolu_aktif=True,
                                                            gonderici_guc_dbm=40.0)),
        Teknik(adi="Chaff Koridoru Oluşturma", kategori="Diğer",
               aciklama="Uçakların güvenli geçişi için metalize fiber bulutları ile bir koridor oluşturur."),
        Teknik(adi="Harcanabilir Dekoy (Towed Decoy)", kategori="Diğer",
               aciklama="Uçaktan salınan ve radarı kendi üzerine çeken sahte hedef."),
        Teknik(adi="Blinking Jamming", kategori="Açı Aldatması",
               aciklama="İki farklı platformdan senkronize yapılan karıştırma ile hedefin ortada bir yerde görünmesini sağlar."),
        Teknik(adi="Cross-Eye Jamming", kategori="Açı Aldatması",
               aciklama="Monopulse radarların açısal doğruluğunu bozmak için hedefin iki ucundan sinyal gönderir."),
        Teknik(adi="Sessiz Kalma (Go-Silent)", kategori="Diğer",
               aciklama="Belirli bir süre tüm elektronik yayını keserek tespitten kaçınma."),
        Teknik(adi="Kybernetik Saldırı (Cyber Attack)", kategori="Diğer",
               aciklama="Radar ağının yazılımına sızarak yanlış bilgi göndermesini veya çökmesini sağlama."),
    ]
    teknik_ids = {t.adi: t.teknik_id for t in teknikler}

    # --- 3. Gerçekçi Senaryoları Oluştur (10 Adet) ---
    senaryolar = [
        Senaryo(adi="F-35'in APG-81'ine Karşı RGPO Uygulaması", tarih_iso="2024-10-21", radar_id=radar_ids["AN/APG-81"],
                teknik_id_list=[teknik_ids["Mesafe Kapısı Çekme - Dışarı (RGPO)"]], sonuc_nitel="Başarılı", js_db=15.0,
                mesafe_km=80.0, notlar="RGPO, AESA radarın takip kapısını başarıyla kırdı."),
        Senaryo(adi="AEGIS SPY-1D(V) Radarına Karşı Geniş Bant Karıştırma", tarih_iso="2025-01-15",
                radar_id=radar_ids["AN/SPY-1D(V)"], teknik_id_list=[teknik_ids["Geniş Bant Baraj Karıştırma (BBJ)"],
                                                                    teknik_ids["Harcanabilir Dekoy (Towed Decoy)"]],
                sonuc_nitel="Kısmen Başarılı", js_db=5.0, mesafe_km=150.0,
                notlar="BBJ radarın tespit menzilini %40 azalttı ancak dekoy erken fark edildi."),
        Senaryo(adi="ALP-300G Erken İhbar Radarının Bastırılması", tarih_iso="2025-03-02",
                radar_id=radar_ids["ASELSAN ALP-300G"],
                teknik_id_list=[teknik_ids["Süpürmeli Gürültü Karıştırma (Swept Noise)"],
                                teknik_ids["Yan Hüzme Karıştırması (Sidelobe Jamming)"]], sonuc_nitel="Başarılı",
                js_db=10.0, mesafe_km=250.0, notlar="Destek karıştırıcı, radarın ana sektörünü tamamen körleştirdi."),
        Senaryo(adi="S-400 92N6E Füze Takip Radarına Karşı Çoklu Aldatma", tarih_iso="2025-04-18",
                radar_id=radar_ids["92N6E 'Grave Stone'"],
                teknik_id_list=[teknik_ids["Hız Kapısı Çekme (VGPO)"], teknik_ids["Çoklu Sahte Hedef Üretimi"]],
                sonuc_nitel="Başarısız", js_db=-2.0, mesafe_km=60.0,
                notlar="Radar, filtreleme algoritmaları sayesinde sahte hedefleri ayırt etmeyi başardı."),
        Senaryo(adi="APAR Radarına Karşı Akıllı Gürültü Testi", tarih_iso="2025-05-25",
                radar_id=radar_ids["Thales APAR"], teknik_id_list=[teknik_ids["DRFM Tabanlı Akıllı Gürültü"]],
                sonuc_nitel="Başarılı", js_db=20.0, mesafe_km=50.0,
                notlar="DRFM, radarın darbe sıkıştırma kazancını etkisiz hale getirdi."),
        Senaryo(adi="Giraffe 4A Mobil Radar Tespiti ve Aldatması", tarih_iso="2025-06-11",
                radar_id=radar_ids["SAAB Giraffe 4A"],
                teknik_id_list=[teknik_ids["Noktasal Gürültü Karıştırma (Spot Noise)"]], sonuc_nitel="Kısmen Başarılı",
                js_db=8.0, mesafe_km=40.0,
                notlar="Karıştırıcı, radarın frekans atlama yeteneği nedeniyle sadece %60 oranında etkili olabildi."),
        Senaryo(adi="Green Pine Radarına Karşı Chaff Koridoru", tarih_iso="2025-07-30",
                radar_id=radar_ids["ELTA EL/M-2080 Green Pine"],
                teknik_id_list=[teknik_ids["Chaff Koridoru Oluşturma"]], sonuc_nitel="Değişken", js_db=None,
                mesafe_km=300.0,
                notlar="Rüzgar ve atmosferik koşullar, chaff bulutunun etkinliğini önemli ölçüde etkiledi."),
        Senaryo(adi="Kalkan-II Alçak İrtifa Tehdit Simülasyonu", tarih_iso="2025-08-05",
                radar_id=radar_ids["ASELSAN Kalkan-II"],
                teknik_id_list=[teknik_ids["Mesafe Kapısı Çekme - İçeri (RGPI)"]], sonuc_nitel="Başarılı", js_db=18.0,
                mesafe_km=35.0,
                notlar="RGPI, radarın mesafe kapısını başarıyla içeri çekerek sanal bir hedef oluşturdu."),
        Senaryo(adi="MİLDAR Helikopter Radarına Karşı Test", tarih_iso="2025-09-12",
                radar_id=radar_ids["Meteksan MİLDAR"], teknik_id_list=[teknik_ids["Adaptif Güç Kontrolü"]],
                sonuc_nitel="Kısmen Başarılı", js_db=12.0, mesafe_km=15.0,
                notlar="Adaptif güç, radarın LPI (düşük tespit olasılığı) özelliğini zorladı."),
        Senaryo(adi="AEGIS Radarına Karşı Cross-Eye Jamming", tarih_iso="2025-09-28",
                radar_id=radar_ids["AN/SPY-1D(V)"],
                teknik_id_list=[teknik_ids["Cross-Eye Jamming"], teknik_ids["Blinking Jamming"]],
                sonuc_nitel="Başarısız", js_db=3.0, mesafe_km=120.0,
                notlar="Radar, ECCM (elektronik karşı-karşı tedbir) modları sayesinde açısal aldatmayı büyük ölçüde filtreledi."),
    ]

    # --- 4. Görevleri Oluştur (2 Adet) ---
    gorevler = [
        Gorev(
            adi="Deniz Platformları Kendini Koruma Tatbikatı",
            sorumlu_personel="Kıdemli Yüzbaşı Efe Sancak",
            aciklama="Deniz unsurlarına yönelik hava savunma ve atış kontrol radarlarına karşı uygulanan kendini koruma (self-protection) EKT'lerinin etkinliğinin ölçülmesi.",
            senaryo_id_list=[senaryolar[1].senaryo_id, senaryolar[4].senaryo_id, senaryolar[6].senaryo_id,
                             senaryolar[9].senaryo_id]
        ),
        Gorev(
            adi="Hava Taarruzu Destek Karıştırma Operasyonu",
            sorumlu_personel="Kıdemli Üsteğmen Elif Öztürk",
            aciklama="Hava taarruz paketinin güvenliğini sağlamak amacıyla düşman erken ihbar ve takip radarlarına yönelik yapılan destek karıştırma (stand-off jamming) faaliyetleri.",
            senaryo_id_list=[senaryolar[0].senaryo_id, senaryolar[2].senaryo_id, senaryolar[3].senaryo_id,
                             senaryolar[5].senaryo_id, senaryolar[7].senaryo_id, senaryolar[8].senaryo_id]
        )
    ]

    # --- 5. Tüm Veriyi Tek Bir "Veri Seti" Dosyası Olarak Kaydet ---
    dm = DataManager()
    dm.radarlar = radarlar
    dm.teknikler = teknikler
    dm.senaryolar = senaryolar
    dm.gorevler = gorevler

    workspace_filename = "veri_seti_detayli.xml"
    dm.save_workspace(workspace_filename)

    print("\nDetaylı ve gerçekçi test verileri başarıyla oluşturuldu!")
    print(f"Tüm veriler '{workspace_filename}' dosyasına kaydedildi.")
    print(
        "Uygulamayı açtıktan sonra 'Dosya -> Veri Seti Aç...' menüsünden bu dosyayı seçerek tüm verileri yükleyebilirsiniz.")


if __name__ == "__main__":
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("schemas"):
        print("UYARI: 'schemas' klasörü bulunamadı. XML doğrulama yapılamayacak.")

    generate_detailed_test_data()