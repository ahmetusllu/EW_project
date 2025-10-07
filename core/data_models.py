# ew_platformasi/core/data_models.py

import os
import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Literal, Union
from datetime import date

# --- Sabitler ve Kataloglar ---
FREKANS_BANDLARI = ["Bilinmiyor", "UHF", "VHF", "L", "S", "C", "X", "Ku", "K", "Ka"]
GOREV_TIPLERI = ["Bilinmiyor", "Hava Savunma", "Erken Uyarı", "Atış Kontrol", "Arama", "TWS", "İzleme"]
ANTEN_TIPLERI = ["Bilinmiyor", "AESA", "PESA", "Parabolik", "Phased ULA", "ESA"]
TEKNIK_KATEGORILERI = ["Gürültü Karıştırma", "Menzil Aldatma", "Alıcı/Gönderici Ayarları", "Kaynak Üreteç Ayarları", "Açı Aldatması", "Hız Aldatması", "Diğer"]
SONUC_NITEL = ["Bilinmiyor", "Başarılı", "Kısmen Başarılı", "Başarısız", "Değişken"]
DARBE_MODULASYONLARI = ["Bilinmiyor", "Normal Darbe (CW)", "Lineer Frekans Mod. (LFM/Chirp)", "Doğrusal Olmayan FM", "Faz Kodlu (Barker, Frank vb.)", "Frekans Atlamalı (FH)"]

# --- Depo Dosya Yolları ---
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(APP_DIR), "data")
SCHEMA_DIR = os.path.join(os.path.dirname(APP_DIR), "schemas")

TEKNIKLER_XML = os.path.join(DATA_DIR, "teknikler.xml")
RADARLAR_XML = os.path.join(DATA_DIR, "radarlar.xml")
SENARYOLAR_XML = os.path.join(DATA_DIR, "senaryolar.xml")
GOREVLER_XML = os.path.join(DATA_DIR, "gorevler.xml")

TEKNIKLER_XSD = os.path.join(SCHEMA_DIR, "teknik_schema.xsd")
RADARLAR_XSD = os.path.join(SCHEMA_DIR, "radar_schema.xsd")
SENARYOLAR_XSD = os.path.join(SCHEMA_DIR, "senaryo_schema.xsd")
GOREVLER_XSD = os.path.join(SCHEMA_DIR, "gorev_schema.xsd")

# --- Detaylı Teknik Parametre Sınıfları ---
@dataclass
class BaseTeknikParametreleri:
    pass

@dataclass
class GurultuKaristirmaParams(BaseTeknikParametreleri):
    tur: Literal["Barrage", "Spot", "Swept", "DRFM Noise"] = "Barrage"
    bant_genisligi_mhz: Optional[float] = None
    guc_erp_dbw: Optional[float] = None

@dataclass
class MenzilAldatmaParams(BaseTeknikParametreleri):
    teknik_tipi: Literal["RGPO", "RGPI"] = "RGPO"
    cekme_hizi_mps: Optional[float] = None
    sahte_hedef_sayisi: Optional[int] = None

@dataclass
class AlmacGondermecAyarParametreleri(BaseTeknikParametreleri):
    on_ornekleme_frekansi_ghz: Optional[float] = None
    rf_kazanc_db: Optional[float] = None
    if_kazanc_db: Optional[float] = None
    faz_kaydirma_derece: Optional[float] = None
    otomatik_kazanc_kontrolu_aktif: bool = False
    gonderici_guc_dbm: Optional[float] = None
    modulasyon_tipi: str = "QPSK"
    veri_hizi_mbps: Optional[float] = None

@dataclass
class KaynakUretecAyarParametreleri(BaseTeknikParametreleri):
    dalga_formu_tipi: str = "Sinus"
    baslangic_frekansi_mhz: Optional[float] = None
    bitis_frekansi_mhz: Optional[float] = None
    tarama_suresi_ms: Optional[float] = None
    darbe_genisligi_us: Optional[float] = None
    darbe_tekrarlama_araligi_us: Optional[float] = None
    faz_gurultusu_dbc_hz: Optional[float] = None
    harmonik_baski_db: Optional[float] = None


# --- Ana Veri Sınıfları ---
@dataclass
class Teknik:
    teknik_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    adi: str = "Yeni Teknik"
    kategori: str = TEKNIK_KATEGORILERI[0]
    aciklama: str = ""
    parametreler: Union[
        GurultuKaristirmaParams,
        MenzilAldatmaParams,
        AlmacGondermecAyarParametreleri,
        KaynakUretecAyarParametreleri,
        BaseTeknikParametreleri
    ] = field(default_factory=GurultuKaristirmaParams)

@dataclass
class Radar:
    radar_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    adi: str = "Yeni Radar"
    elnot: str = ""
    uretici: str = ""
    frekans_bandi: str = FREKANS_BANDLARI[0]
    gorev_tipi: str = GOREV_TIPLERI[0]
    anten_tipi: str = ANTEN_TIPLERI[0]
    pw_us: Optional[float] = None
    prf_hz: Optional[float] = None
    pri_us: Optional[float] = None
    erp_dbw: Optional[float] = None
    darbe_modulasyonu: str = DARBE_MODULASYONLARI[0]
    darbe_entegrasyonu: str = ""
    notlar: str = ""

@dataclass
class TeknikUygulama:
    """Senaryo içinde bir tekniğin uygulanma sırasını ve süresini tutar."""
    sira: int = 1
    teknik_id: str = ""
    sure_sn: float = 0.0

@dataclass
class Senaryo:
    senaryo_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    adi: str = "Yeni Senaryo"
    tarih_iso: str = "2025-01-01"
    konum: str = ""
    amac: str = ""
    et_sistem_ismi: str = ""
    manevra: bool = False
    radar_id: Optional[str] = None
    uygulanan_teknikler: List[TeknikUygulama] = field(default_factory=list) # DEĞİŞTİ
    sonuc_nitel: str = SONUC_NITEL[0]
    js_db: Optional[float] = None
    mesafe_km: Optional[float] = None
    notlar: str = ""

@dataclass
class Gorev:
    gorev_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    adi: str = "Yeni Görev"
    olusturma_tarihi_iso: str = field(default_factory=lambda: date.today().isoformat())
    sorumlu_personel: str = ""
    aciklama: str = ""
    senaryo_id_list: List[str] = field(default_factory=list)