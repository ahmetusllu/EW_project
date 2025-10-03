# ew_platformasi/core/data_models.py

import os
import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Literal, Union

# --- Sabitler ve Kataloglar ---
FREKANS_BANDLARI = ["Bilinmiyor", "UHF", "VHF", "L", "S", "C", "X", "Ku", "K", "Ka"]
GOREV_TIPLERI = ["Bilinmiyor", "Hava Savunma", "Erken Uyarı", "Atış Kontrol", "Arama", "TWS", "İzleme"]
ANTEN_TIPLERI = ["Bilinmiyor", "AESA", "PESA", "Parabolik", "Phased ULA", "ESA"]
TEKNIK_KATEGORILERI = ["Gürültü Karıştırma", "Menzil Aldatma", "Açı Aldatması", "Hız Aldatması", "Diğer"]
SONUC_NITEL = ["Bilinmiyor", "Başarılı", "Kısmen Başarılı", "Başarısız", "Değişken"]

# --- Depo Dosya Yolları ---
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(APP_DIR), "data")
SCHEMA_DIR = os.path.join(os.path.dirname(APP_DIR), "schemas")

TEKNIKLER_XML = os.path.join(DATA_DIR, "teknikler.xml")
RADARLAR_XML = os.path.join(DATA_DIR, "radarlar.xml")
SENARYOLAR_XML = os.path.join(DATA_DIR, "senaryolar.xml")

TEKNIKLER_XSD = os.path.join(SCHEMA_DIR, "teknik_schema.xsd")
RADARLAR_XSD = os.path.join(SCHEMA_DIR, "radar_schema.xsd")
SENARYOLAR_XSD = os.path.join(SCHEMA_DIR, "senaryo_schema.xsd")

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

# --- Ana Veri Sınıfları ---
@dataclass
class Teknik:
    teknik_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    adi: str = "Yeni Teknik"
    kategori: str = TEKNIK_KATEGORILERI[0]
    aciklama: str = ""
    parametreler: Union[GurultuKaristirmaParams, MenzilAldatmaParams, BaseTeknikParametreleri] = field(default_factory=GurultuKaristirmaParams)

@dataclass
class Radar:
    radar_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    adi: str = "Yeni Radar"
    uretici: str = ""
    frekans_bandi: str = FREKANS_BANDLARI[0]
    gorev_tipi: str = GOREV_TIPLERI[0]
    anten_tipi: str = ANTEN_TIPLERI[0]
    pw_us: Optional[float] = None
    prf_hz: Optional[int] = None
    notlar: str = ""

@dataclass
class Senaryo:
    senaryo_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    adi: str = "Yeni Senaryo"
    tarih_iso: str = "2025-01-01"
    konum: str = ""
    amac: str = ""
    radar_id: Optional[str] = None
    teknik_id_list: List[str] = field(default_factory=list)
    sonuc_nitel: str = SONUC_NITEL[0]
    js_db: Optional[float] = None
    mesafe_km: Optional[float] = None
    notlar: str = ""