import os
import uuid

# Projenizin 'core' paketindeki ilgili modülleri import ediyoruz.
# Bu betiği projenin kök dizininden çalıştırmalısınız.
from core.data_models import (
    Teknik,
    GurultuKaristirmaParams,
    MenzilAldatmaParams,
    AlmacGondermecAyarParametreleri,
    KaynakUretecAyarParametreleri
)
from core.data_manager import DataManager


def generate_teknik_test_files():
    """
    İçeri aktarma özelliğini test etmek için örnek EKT'ler içeren
    XML dosyaları oluşturur.
    """
    print("Örnek teknik (EKT) test dosyaları oluşturuluyor...")

    # --- 1. XML Dosyası İçin Teknikler (Gürültü Karıştırma Teknikleri) ---
    teknikler_gurultu = [
        Teknik(
            adi="Geniş Bant Baraj Karıştırma (Test)",
            kategori="Gürültü Karıştırma",
            aciklama="Hedef radarın tüm olası frekans bandını geniş bir gürültü sinyaliyle bastırır.",
            parametreler=GurultuKaristirmaParams(tur="Barrage", bant_genisligi_mhz=500.0, guc_erp_dbw=60.0)
        ),
        Teknik(
            adi="Noktasal Gürültü (Test)",
            kategori="Gürültü Karıştırma",
            aciklama="Tüm gücü, hedef radarın çalıştığı tek ve dar bir frekansa odaklar.",
            parametreler=GurultuKaristirmaParams(tur="Spot", bant_genisligi_mhz=20.0, guc_erp_dbw=75.0)
        )
    ]

    # --- 2. XML Dosyası İçin Teknikler (Aldatma Teknikleri) ---
    teknikler_aldatma = [
        Teknik(
            adi="Mesafe Kapısı Dışarı Çekme (RGPO) (Test)",
            kategori="Menzil Aldatma",
            aciklama="Radar sinyalini kopyalayıp geciktirerek hedefin radardan daha uzakta görünmesini sağlar.",
            parametreler=MenzilAldatmaParams(teknik_tipi="RGPO", cekme_hizi_mps=2000.0, sahte_hedef_sayisi=1)
        ),
        Teknik(
            adi="Hız Kapısı Aldatması (VGPO) (Test)",
            kategori="Hız Aldatması",
            aciklama="Hedefin hızını Doppler kaymasını değiştirerek olduğundan farklı gösterir."
        ),
        Teknik(
            adi="Yan Hüzme Karıştırması (Test)",
            kategori="Açı Aldatması",
            aciklama="Radar anteninin zayıf olan yan hüzmelerinden sisteme girerek yanlış yön bilgisi oluşturur."
        )
    ]

    # --- 3. XML Dosyası İçin Teknikler (Diğer Teknikler) ---
    teknikler_diger = [
        Teknik(
            adi="Chirp Sinyal Üretimi (Test)",
            kategori="Kaynak Üreteç Ayarları",
            aciklama="Darbe sıkıştırma kullanan radarlara karşı etkili, frekansı zamanla değişen sinyal.",
            parametreler=KaynakUretecAyarParametreleri(
                dalga_formu_tipi="Testere Dişi",
                baslangic_frekansi_mhz=9200.0,
                bitis_frekansi_mhz=9300.0,
                darbe_genisligi_us=10.0
            )
        ),
        Teknik(
            adi="Harcanabilir Dekoy (Towed Decoy) (Test)",
            kategori="Diğer",
            aciklama="Uçaktan salınan ve radarı kendi üzerine çeken sahte hedef."
        )
    ]

    # DataManager'ın dışa aktarma fonksiyonunu kullanmak için bir örnek oluşturuyoruz.
    dm = DataManager()

    # Test dosyalarının kaydedileceği klasörü oluştur.
    output_dir = "teknik_test_dosyalari"
    os.makedirs(output_dir, exist_ok=True)
    print(f"'{output_dir}' klasörü oluşturuldu/kontrol edildi.")

    # Her bir teknik listesini ayrı bir XML dosyasına kaydet.
    try:
        path1 = os.path.join(output_dir, "gurultu_teknikleri.xml")
        dm.export_teknikler_to_xml(teknikler_gurultu, path1)
        print(f" - '{path1}' oluşturuldu.")

        path2 = os.path.join(output_dir, "aldatma_teknikleri.xml")
        dm.export_teknikler_to_xml(teknikler_aldatma, path2)
        print(f" - '{path2}' oluşturuldu.")

        path3 = os.path.join(output_dir, "diger_teknikler.xml")
        dm.export_teknikler_to_xml(teknikler_diger, path3)
        print(f" - '{path3}' oluşturuldu.")

        print(f"\nTest dosyaları '{output_dir}' klasörüne başarıyla oluşturuldu.")
        print("Uygulamadaki 'İçeri Aktar' butonu ile bu dosyaları seçebilirsiniz.")

    except Exception as e:
        print(f"\nBir hata oluştu: {e}")
        print("Lütfen betiği projenin ana klasöründen çalıştırdığınızdan emin olun.")


if __name__ == "__main__":
    generate_teknik_test_files()