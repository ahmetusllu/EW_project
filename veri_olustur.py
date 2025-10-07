import os
import random
from datetime import date

from core.data_models import (
    Radar, Teknik, Senaryo, Gorev,
    GurultuKaristirmaParams, MenzilAldatmaParams,
    SONUC_NITEL, DARBE_MODULASYONLARI
)
from core.data_manager import DataManager


def generate_comprehensive_test_data():
    """
    Uygulamanın tüm özelliklerini test etmek için kapsamlı ve ilişkisel
    bir test veri seti oluşturur.
    """
    print("Kapsamlı test veri seti oluşturuluyor...")

    # --- Radarlar ---
    # Radar_A: Faaliyet geçmişi dolu olan ana test radarı
    # Radar_B: Faaliyet geçmişi daha az olan radar
    # Radar_C: Hiç faaliyeti olmayan, silme ve düzenleme testi için radar
    radarlar = [
        Radar(adi="AN/SPY-1D(V) AEGIS", uretici="Lockheed Martin", frekans_bandi="S", gorev_tipi="Hava Savunma",
              anten_tipi="PESA", pw_us=50.0, prf_hz=1000.0, erp_dbw=90.0,
              darbe_modulasyonu="Faz Kodlu (Barker, Frank vb.)"),
        Radar(adi="Thales APAR", uretici="Thales", frekans_bandi="X", gorev_tipi="Atış Kontrol", anten_tipi="AESA",
              pw_us=2.0, prf_hz=4000.0, erp_dbw=70.0, darbe_modulasyonu="Normal Darbe (CW)"),
        Radar(adi="Hensoldt TRS-3D", uretici="Hensoldt", frekans_bandi="C", gorev_tipi="Arama", anten_tipi="PESA",
              pw_us=15.0, prf_hz=2200.0, erp_dbw=82.0),
    ]
    radar_map = {r.adi: r.radar_id for r in radarlar}

    # --- Teknikler ---
    # Birkaç farklı kategoriden, senaryolarda kullanılacak teknikler
    teknikler = [
        Teknik(adi="Geniş Bant Baraj Karıştırma (BBJ)", kategori="Gürültü Karıştırma",
               parametreler=GurultuKaristirmaParams(tur="Barrage", bant_genisligi_mhz=500.0)),
        Teknik(adi="Mesafe Kapısı Çekme - Dışarı (RGPO)", kategori="Menzil Aldatma",
               parametreler=MenzilAldatmaParams(teknik_tipi="RGPO", cekme_hizi_mps=2000.0)),
        Teknik(adi="Hız Kapısı Çekme (VGPO)", kategori="Hız Aldatması"),
        Teknik(adi="Yan Hüzme Karıştırması (SLJ)", kategori="Açı Aldatması"),
        Teknik(adi="Harcanabilir Dekoy (Towed Decoy)", kategori="Diğer"),
    ]
    teknik_map = {t.adi: t.teknik_id for t in teknikler}

    # --- Senaryolar ---
    # Senaryo 1-3: Radar_A'ya karşı, Görev 1 için
    # Senaryo 4: Radar_B'ye karşı, Görev 1 için
    # Senaryo 5: Radar_A'ya karşı, Görev 2 için
    # Senaryo 6: Hiçbir göreve dahil olmayan, bağımsız senaryo
    senaryolar = [
        Senaryo(adi="S-01: AEGIS BBJ Testi", tarih_iso="2024-10-21", radar_id=radar_map["AN/SPY-1D(V) AEGIS"],
                teknik_id_list=[teknik_map["Geniş Bant Baraj Karıştırma (BBJ)"]], sonuc_nitel="Kısmen Başarılı",
                js_db=5.0, mesafe_km=150.0),
        Senaryo(adi="S-02: AEGIS RGPO Testi", tarih_iso="2024-11-05", radar_id=radar_map["AN/SPY-1D(V) AEGIS"],
                teknik_id_list=[teknik_map["Mesafe Kapısı Çekme - Dışarı (RGPO)"],
                                teknik_map["Harcanabilir Dekoy (Towed Decoy)"]], sonuc_nitel="Başarılı", js_db=15.0,
                mesafe_km=80.0),
        Senaryo(adi="S-03: AEGIS VGPO Başarısız Test", tarih_iso="2024-12-10", radar_id=radar_map["AN/SPY-1D(V) AEGIS"],
                teknik_id_list=[teknik_map["Hız Kapısı Çekme (VGPO)"]], sonuc_nitel="Başarısız", js_db=-5.0,
                mesafe_km=100.0),
        Senaryo(adi="S-04: APAR Yan Hüzme Testi", tarih_iso="2025-01-20", radar_id=radar_map["Thales APAR"],
                teknik_id_list=[teknik_map["Yan Hüzme Karıştırması (SLJ)"]], sonuc_nitel="Başarılı", js_db=10.0,
                mesafe_km=40.0),
        Senaryo(adi="S-05: AEGIS Kombine Aldatma", tarih_iso="2025-02-15", radar_id=radar_map["AN/SPY-1D(V) AEGIS"],
                teknik_id_list=[teknik_map["Mesafe Kapısı Çekme - Dışarı (RGPO)"],
                                teknik_map["Hız Kapısı Çekme (VGPO)"]], sonuc_nitel="Değişken", js_db=8.0,
                mesafe_km=90.0),
        Senaryo(adi="S-06: Bağımsız TRS-3D Testi", tarih_iso="2025-03-01", radar_id=radar_map["Hensoldt TRS-3D"],
                teknik_id_list=[teknik_map["Geniş Bant Baraj Karıştırma (BBJ)"]], sonuc_nitel="Kısmen Başarılı",
                js_db=7.5, mesafe_km=110.0),
    ]

    # --- Görevler ---
    gorevler = [
        Gorev(
            adi="Tatbikat-2025/1 Öz Koruma Faaliyeti",
            sorumlu_personel="Yzb. Efe Sancak",
            aciklama="Deniz platformlarına yönelik tehdit radarlarına karşı kendini koruma EKT'lerinin testi.",
            senaryo_id_list=[senaryolar[0].senaryo_id, senaryolar[1].senaryo_id, senaryolar[2].senaryo_id,
                             senaryolar[3].senaryo_id]
        ),
        Gorev(
            adi="Operasyon Gözcü-2 Destek Karıştırma",
            sorumlu_personel="Ütğm. Elif Öztürk",
            aciklama="Hava unsurlarının güvenliği için düşman hava savunma radarlarına yönelik destek karıştırma.",
            senaryo_id_list=[senaryolar[4].senaryo_id]
        )
    ]

    # --- Veri Seti Olarak Kaydetme ---
    dm = DataManager()
    dm.radarlar = radarlar
    dm.teknikler = teknikler
    dm.senaryolar = senaryolar
    dm.gorevler = gorevler

    workspace_filename = "veri_seti_kapsamli_test.xml"
    dm.save_workspace(workspace_filename)

    print(f"\nKapsamlı test verileri başarıyla '{workspace_filename}' dosyasına kaydedildi.")
    print("Uygulamayı açıp 'Dosya -> Veri Seti Aç...' menüsünden bu dosyayı seçerek teste başlayabilirsiniz.")


if __name__ == "__main__":
    generate_comprehensive_test_data()