# ew_platformasi/core/data_manager.py

import os
import uuid
import xml.etree.ElementTree as ET
from dataclasses import fields, is_dataclass, asdict
from typing import List, Type, TypeVar, get_origin, get_args, Union, Optional
from lxml import etree
from PySide6.QtCore import QObject, Signal

from core.data_models import (
    Teknik, Radar, Senaryo, BaseTeknikParametreleri, GurultuKaristirmaParams, MenzilAldatmaParams,
    TEKNIKLER_XML, RADARLAR_XML, SENARYOLAR_XML,
    TEKNIKLER_XSD, RADARLAR_XSD, SENARYOLAR_XSD, DATA_DIR
)

# Generic Type for return types
T = TypeVar('T')


class DataManager(QObject):
    # Bu sinyaller, veri değiştiğinde arayüzü otomatik olarak güncellemek için kullanılacak
    radarlar_changed = Signal()
    teknikler_changed = Signal()
    senaryolar_changed = Signal()

    def __init__(self):
        super().__init__()
        self._param_class_map = {
            "GurultuKaristirmaParams": GurultuKaristirmaParams,
            "MenzilAldatmaParams": MenzilAldatmaParams,
            "BaseTeknikParametreleri": BaseTeknikParametreleri
        }
        self._ensure_data_files_exist()

        # Uygulama başlangıcında tüm veriyi belleğe yükle
        self.radarlar: List[Radar] = self._load_all(RADARLAR_XML, RADARLAR_XSD, "Radar", Radar)
        self.teknikler: List[Teknik] = self._load_all(TEKNIKLER_XML, TEKNIKLER_XSD, "Teknik", Teknik)
        self.senaryolar: List[Senaryo] = self._load_all(SENARYOLAR_XML, SENARYOLAR_XSD, "Senaryo", Senaryo)

    # --- XML <-> Dataclass Dönüşüm Metotları ---

    def _element_to_dataclass(self, element: ET.Element, cls: Type[T]) -> T:
        """Bir XML elementini ilgili dataclass'a çevirir."""
        data = {}
        for field_info in fields(cls):
            field_name_pascal = field_info.name.replace('_', ' ').title().replace(' ', '')
            child_element = element.find(field_name_pascal)

            if child_element is None: continue

            # Polimorfik parametreleri handle et (Teknik sınıfı için)
            if field_info.name == "parametreler":
                # Parametreler elementi içindeki ilk ve tek elementi al (örn: <GurultuKaristirmaParams>)
                param_element = child_element[0]
                param_cls_name = param_element.tag
                param_cls = self._param_class_map.get(param_cls_name, BaseTeknikParametreleri)
                data[field_info.name] = self._element_to_dataclass(param_element, param_cls)
                continue

            # ID listelerini handle et (Senaryo sınıfı için)
            if field_info.name == "teknik_id_list":
                data[field_info.name] = [item.text for item in child_element.findall("TeknikID")]
                continue

            # Diğer normal alanlar
            text_val = child_element.text
            if text_val is None or text_val == 'None':
                data[field_info.name] = None
            else:
                field_type = field_info.type
                origin_type = get_origin(field_type)
                type_args = get_args(field_type)

                # Optional[int] gibi tipleri handle et
                if origin_type is Union and type(None) in type_args:
                    base_type = next(t for t in type_args if t is not type(None))
                    try:
                        data[field_info.name] = base_type(text_val)
                    except (ValueError, TypeError):
                        data[field_info.name] = None
                else:
                    try:
                        data[field_info.name] = field_type(text_val)
                    except (ValueError, TypeError):
                        data[field_info.name] = text_val

        # ID'yi attribute'dan al
        id_attr = element.attrib.get("id")
        id_field_name = f"{cls.__name__.lower()}_id"
        if id_attr and hasattr(cls, id_field_name):
            data[id_field_name] = id_attr

        return cls(**data)

    # DOĞRU KOD
    def _dataclass_to_element(self, instance) -> ET.Element:
        """Bir dataclass örneğini XML elementine çevirir."""
        class_name = instance.__class__.__name__
        id_field_name = f"{class_name.lower()}_id"

        # Sadece ana nesnelerin (Teknik, Radar, Senaryo) ID'si vardır.
        # Parametre nesnelerinin yoktur. Bu yüzden ID'nin varlığını kontrol et.
        if hasattr(instance, id_field_name):
            instance_id = getattr(instance, id_field_name)
            element = ET.Element(class_name, attrib={"id": instance_id})
        else:
            # ID'si olmayan iç içe nesneler (parametreler gibi) için
            element = ET.Element(class_name)

        for field_info in fields(instance):
            # ID alanını tekrar işlememek için atla
            if field_info.name == id_field_name:
                continue

            field_name_pascal = field_info.name.replace('_', ' ').title().replace(' ', '')
            child_element = ET.SubElement(element, field_name_pascal)
            value = getattr(instance, field_info.name)

            if is_dataclass(value):
                # İç içe dataclass'ları (parametreler gibi) ekle
                param_element = self._dataclass_to_element(value)
                child_element.append(param_element)
            elif isinstance(value, list):
                # ID listelerini (teknik_id_list gibi) ekle
                for item in value:
                    ET.SubElement(child_element, "TeknikID").text = str(item)
            elif value is not None:
                child_element.text = str(value)

        return element

    # --- XML Dosya İşlemleri ve Doğrulama (Validation) ---

    def _validate_xml(self, xml_path: str, xsd_path: str) -> bool:
        """Bir XML dosyasını XSD şemasına göre doğrular."""
        try:
            xmlschema_doc = etree.parse(xsd_path)
            xmlschema = etree.XMLSchema(xmlschema_doc)
            xml_doc = etree.parse(xml_path)
            xmlschema.assertValid(xml_doc)
            return True
        except etree.XMLSchemaError as e:
            print(f"XSD Şema Hatası: {xsd_path} - {e}")
            return False
        except etree.DocumentInvalid as e:
            print(f"XML Doğrulama Hatası: {xml_path} - {e}")
            return False
        except FileNotFoundError:
            return True  # Dosya yoksa, geçerli sayılır (yeni oluşturulacak)
        except Exception as e:
            print(f"Bilinmeyen XML hatası: {e}")
            return False

    def _load_all(self, xml_path: str, xsd_path: str, item_tag: str, cls: Type[T]) -> List[T]:
        """Bir XML dosyasını okur, doğrular ve dataclass listesine çevirir."""
        if not os.path.exists(xml_path) or not self._validate_xml(xml_path, xsd_path):
            return []
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            return [self._element_to_dataclass(el, cls) for el in root.findall(item_tag)]
        except ET.ParseError as e:
            print(f"XML Parse Hatası: {xml_path} - {e}")
            return []

    def _save_all(self, data_list: List, xml_path: str, xsd_path: str, root_tag: str):
        """Bir dataclass listesini XML'e yazar ve doğrular."""
        root = ET.Element(root_tag)
        for item in data_list:
            element = self._dataclass_to_element(item)
            root.append(element)

        # Geçici dosyaya yaz ve doğrula, sonra asıl dosyanın üzerine yaz
        temp_path = xml_path + ".tmp"
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ", level=0)
        tree.write(temp_path, encoding="utf-8", xml_declaration=True)

        if self._validate_xml(temp_path, xsd_path):
            os.replace(temp_path, xml_path)
        else:
            print(f"HATA: Kaydedilen dosya {xml_path} şemaya uymuyor. Kayıt iptal edildi.")
            os.remove(temp_path)

    # --- Public CRUD (Create, Read, Update, Delete) Metotları ---

    def save_item(self, item):
        """Verilen bir öğeyi (Radar, Teknik, veya Senaryo) kaydeder veya günceller."""
        item_type = type(item)
        if item_type is Radar:
            list_ref, save_func, signal = self.radarlar, lambda: self._save_all(self.radarlar, RADARLAR_XML,
                                                                                RADARLAR_XSD,
                                                                                "Radarlar"), self.radarlar_changed
        elif item_type is Teknik:
            list_ref, save_func, signal = self.teknikler, lambda: self._save_all(self.teknikler, TEKNIKLER_XML,
                                                                                 TEKNIKLER_XSD,
                                                                                 "Teknikler"), self.teknikler_changed
        elif item_type is Senaryo:
            list_ref, save_func, signal = self.senaryolar, lambda: self._save_all(self.senaryolar, SENARYOLAR_XML,
                                                                                  SENARYOLAR_XSD,
                                                                                  "Senaryolar"), self.senaryolar_changed
        else:
            return

        id_field = f"{item_type.__name__.lower()}_id"
        item_id = getattr(item, id_field)

        idx = next((i for i, x in enumerate(list_ref) if getattr(x, id_field) == item_id), None)
        if idx is not None:
            list_ref[idx] = item
        else:
            list_ref.append(item)

        save_func()
        signal.emit()

    def delete_item_by_id(self, item_id: str, item_type: Type[T]):
        """Verilen ID ve tipe göre öğeyi siler."""
        if item_type is Radar:
            list_ref, save_func, signal = self.radarlar, lambda: self._save_all(self.radarlar, RADARLAR_XML,
                                                                                RADARLAR_XSD,
                                                                                "Radarlar"), self.radarlar_changed
        elif item_type is Teknik:
            list_ref, save_func, signal = self.teknikler, lambda: self._save_all(self.teknikler, TEKNIKLER_XML,
                                                                                 TEKNIKLER_XSD,
                                                                                 "Teknikler"), self.teknikler_changed
        elif item_type is Senaryo:
            list_ref, save_func, signal = self.senaryolar, lambda: self._save_all(self.senaryolar, SENARYOLAR_XML,
                                                                                  SENARYOLAR_XSD,
                                                                                  "Senaryolar"), self.senaryolar_changed
        else:
            return

        id_field = f"{item_type.__name__.lower()}_id"
        initial_len = len(list_ref)
        list_ref[:] = [item for item in list_ref if getattr(item, id_field) != item_id]

        if len(list_ref) < initial_len:
            save_func()
            signal.emit()

    # DOĞRU KOD
    def _ensure_data_files_exist(self):
        """Gerekli data klasörünü ve boş XML dosyalarını oluşturur."""
        os.makedirs(DATA_DIR, exist_ok=True)
        # files_to_check bir sözlük olmalı, yani { ile başlamalı ve } ile bitmeli.
        files_to_check = {
            RADARLAR_XML: "<Radarlar></Radarlar>",
            TEKNIKLER_XML: "<Teknikler></Teknikler>",
            SENARYOLAR_XML: "<Senaryolar></Senaryolar>"
        }
        for path, content in files_to_check.items():
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)