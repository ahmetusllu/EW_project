# ew_platformasi/core/data_manager.py

import os
import uuid
import copy
import xml.etree.ElementTree as ET
from dataclasses import fields, is_dataclass
from typing import List, Type, TypeVar, get_origin, get_args, Union
from lxml import etree
from PySide6.QtCore import QObject, Signal

from core.data_models import (
    Teknik, Radar, Senaryo, Gorev, BaseTeknikParametreleri, GurultuKaristirmaParams, MenzilAldatmaParams,
    AlmacGondermecAyarParametreleri, KaynakUretecAyarParametreleri, TeknikUygulama,
    TEKNIKLER_XML, RADARLAR_XML, SENARYOLAR_XML, GOREVLER_XML,
    TEKNIKLER_XSD, RADARLAR_XSD, SENARYOLAR_XSD, GOREVLER_XSD, DATA_DIR
)

T = TypeVar('T')


class DataManager(QObject):
    radarlar_changed = Signal()
    teknikler_changed = Signal()
    senaryolar_changed = Signal()
    gorevler_changed = Signal()
    status_updated = Signal(str)

    def __init__(self):
        super().__init__()
        self._param_class_map = {
            "GurultuKaristirmaParams": GurultuKaristirmaParams,
            "MenzilAldatmaParams": MenzilAldatmaParams,
            "AlmacGondermecAyarParametreleri": AlmacGondermecAyarParametreleri,
            "KaynakUretecAyarParametreleri": KaynakUretecAyarParametreleri,
            "BaseTeknikParametreleri": BaseTeknikParametreleri
        }
        self._ensure_data_files_exist()

        self.radarlar: List[Radar] = []
        self.teknikler: List[Teknik] = []
        self.senaryolar: List[Senaryo] = []
        self.gorevler: List[Gorev] = []

    def new_workspace(self):
        """Tüm mevcut veriyi temizler ve yeni bir çalışma alanı başlatır."""
        self.radarlar.clear()
        self.teknikler.clear()
        self.senaryolar.clear()
        self.gorevler.clear()
        self._emit_all_changed_signals()
        self.status_updated.emit("Yeni veri seti oluşturuldu. Alanlar temizlendi.")

    def save_workspace(self, path: str):
        """Mevcut tüm veriyi tek bir XML dosyasına kaydeder."""
        try:
            root = ET.Element("EWVeriSeti")
            for tag, data_list in [
                ("Radarlar", self.radarlar),
                ("Teknikler", self.teknikler),
                ("Senaryolar", self.senaryolar),
                ("Gorevler", self.gorevler)
            ]:
                sub_root = ET.SubElement(root, tag)
                for item in data_list:
                    sub_root.append(self._dataclass_to_element(item))

            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ", level=0)
            tree.write(path, encoding="utf-8", xml_declaration=True)
            self.status_updated.emit(f"Veri seti başarıyla '{os.path.basename(path)}' dosyasına kaydedildi.")
        except Exception as e:
            self.status_updated.emit(f"Hata: Veri seti kaydedilemedi - {e}")

    def open_workspace(self, path: str):
        """Bir XML dosyasından tüm veri setini yükler. Mevcut veri silinir."""
        try:
            self.new_workspace()
            root = ET.parse(path).getroot()

            item_map = {
                "Radarlar/Radar": (Radar, self.radarlar),
                "Teknikler/Teknik": (Teknik, self.teknikler),
                "Senaryolar/Senaryo": (Senaryo, self.senaryolar),
                "Gorevler/Gorev": (Gorev, self.gorevler)
            }

            for path_str, (cls, data_list) in item_map.items():
                for elem in root.findall(path_str):
                    item = self._element_to_dataclass(elem, cls)
                    data_list.append(item)

            self._emit_all_changed_signals()
            self.status_updated.emit(f"'{os.path.basename(path)}' veri seti başarıyla yüklendi.")
        except Exception as e:
            self.new_workspace()
            self.status_updated.emit(f"Hata: Veri seti yüklenemedi - {e}")

    def export_teknikler_to_xml(self, teknikler: List[Teknik], path: str):
        """Verilen teknik listesini belirtilen yola XML olarak kaydeder."""
        try:
            root = ET.Element("Teknikler")
            for item in teknikler:
                root.append(self._dataclass_to_element(item))
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ", level=0)
            tree.write(path, encoding="utf-8", xml_declaration=True)
            self.status_updated.emit(
                f"{len(teknikler)} teknik başarıyla '{os.path.basename(path)}' dosyasına aktarıldı.")
        except Exception as e:
            self.status_updated.emit(f"Hata: Teknikler dışa aktarılamadı - {e}")

    def import_teknikler_from_xml(self, path: str) -> List[Teknik]:
        """Bir XML dosyasından teknikleri okur ve bir liste olarak döndürür."""
        try:
            root = ET.parse(path).getroot()
            if root.tag != "Teknikler":
                self.status_updated.emit(f"Hata: '{os.path.basename(path)}' geçerli bir teknik dosyası değil.")
                return []

            imported_teknikler = []
            for elem in root.findall("Teknik"):
                item = self._element_to_dataclass(elem, Teknik)
                imported_teknikler.append(item)

            existing_ids = {t.teknik_id for t in self.teknikler}
            new_teknikler = []
            updated_count = 0

            for teknik in imported_teknikler:
                if teknik.teknik_id in existing_ids:
                    self.save_item(teknik)
                    updated_count += 1
                else:
                    new_teknikler.append(teknik)

            if new_teknikler:
                self.teknikler.extend(new_teknikler)

            if new_teknikler or updated_count > 0:
                self.teknikler_changed.emit()
                self.status_updated.emit(
                    f"'{os.path.basename(path)}' dosyasından {len(new_teknikler)} yeni teknik eklendi, {updated_count} teknik güncellendi.")

            return imported_teknikler
        except Exception as e:
            self.status_updated.emit(f"Hata: Teknikler içe aktarılamadı - {e}")
            return []

    def _emit_all_changed_signals(self):
        self.radarlar_changed.emit()
        self.teknikler_changed.emit()
        self.senaryolar_changed.emit()
        self.gorevler_changed.emit()

    def _element_to_dataclass(self, element: ET.Element, cls: Type[T]) -> T:
        data = {}
        cls_fields = {f.name for f in fields(cls)}

        for field_info in fields(cls):
            field_name_pascal = field_info.name.replace('_', ' ').title().replace(' ', '')
            child_element = element.find(field_name_pascal)
            if child_element is None: continue

            if field_info.name == "parametreler":
                if len(child_element) > 0:
                    param_element = child_element[0]
                    param_cls_name = param_element.tag
                    param_cls = self._param_class_map.get(param_cls_name, BaseTeknikParametreleri)
                    data[field_info.name] = self._element_to_dataclass(param_element, param_cls)
            elif field_info.name == "senaryo_id_list":
                data[field_info.name] = [item.text for item in child_element.findall("SenaryoID")]
            # YENİ: `uygulanan_teknikler` listesini işlemek için
            elif field_info.name == "uygulanan_teknikler":
                data[field_info.name] = [self._element_to_dataclass(item, TeknikUygulama)
                                         for item in child_element.findall("TeknikUygulama")]
            else:
                text_val = child_element.text
                if text_val is not None and text_val != 'None':
                    field_type = field_info.type
                    origin_type = get_origin(field_type)
                    type_args = get_args(field_type)

                    try:
                        if origin_type is Union and type(None) in type_args:
                            base_type = next(t for t in type_args if t is not type(None))
                            data[field_info.name] = base_type(text_val)
                        elif field_type is bool:
                            data[field_info.name] = text_val.lower() in ('true', '1')
                        else:
                            data[field_info.name] = field_type(text_val)
                    except (ValueError, TypeError):
                        data[field_info.name] = text_val

        id_attr = element.attrib.get("id")
        id_field_name = f"{cls.__name__.lower()}_id"
        if id_attr and hasattr(cls, id_field_name):
            data[id_field_name] = id_attr

        return cls(**{k: v for k, v in data.items() if k in cls_fields})

    def _dataclass_to_element(self, instance) -> ET.Element:
        class_name = instance.__class__.__name__
        id_field_name = f"{class_name.lower()}_id"
        attribs = {}
        if hasattr(instance, id_field_name) and getattr(instance, id_field_name):
            attribs["id"] = getattr(instance, id_field_name)

        element = ET.Element(class_name, attrib=attribs)

        for field_info in fields(instance):
            if field_info.name == id_field_name: continue

            field_name_pascal = field_info.name.replace('_', ' ').title().replace(' ', '')
            child_element = ET.SubElement(element, field_name_pascal)
            value = getattr(instance, field_info.name)

            if is_dataclass(value):
                child_element.append(self._dataclass_to_element(value))
            elif isinstance(value, list):
                # YENİ: Liste elemanlarının dataclass olup olmadığını kontrol et
                if field_info.name == "senaryo_id_list":
                    for item in value: ET.SubElement(child_element, "SenaryoID").text = str(item)
                elif field_info.name == "uygulanan_teknikler":
                    for item in value:
                        child_element.append(self._dataclass_to_element(item))
            elif value is not None:
                child_element.text = str(value)
        return element

    def _validate_xml(self, xml_path: str, xsd_path: str) -> bool:
        if not os.path.exists(xsd_path): return True
        try:
            xmlschema_doc = etree.parse(xsd_path)
            xmlschema = etree.XMLSchema(xmlschema_doc)
            xml_doc = etree.parse(xml_path)
            xmlschema.assertValid(xml_doc)
            return True
        except (etree.XMLSchemaError, etree.DocumentInvalid, FileNotFoundError, OSError) as e:
            self.status_updated.emit(f"XML doğrulama hatası: {e}")
            return False

    def _get_list_ref(self, item_type: Type[T]):
        if item_type is Radar:
            return self.radarlar, self.radarlar_changed
        elif item_type is Teknik:
            return self.teknikler, self.teknikler_changed
        elif item_type is Senaryo:
            return self.senaryolar, self.senaryolar_changed
        elif item_type is Gorev:
            return self.gorevler, self.gorevler_changed
        return None, None

    def save_item(self, item):
        list_ref, signal = self._get_list_ref(type(item))
        if list_ref is None: return

        id_field = f"{type(item).__name__.lower()}_id"
        item_id = getattr(item, id_field, None)

        if not item_id or not self.item_exists(item_id, type(item)):
            if not item_id:
                setattr(item, id_field, str(uuid.uuid4()))
            list_ref.append(item)
        else:
            idx = next((i for i, x in enumerate(list_ref) if getattr(x, id_field) == item_id), None)
            if idx is not None:
                list_ref[idx] = item
        signal.emit()

    def item_exists(self, item_id: str, item_type: Type[T]) -> bool:
        list_ref, _ = self._get_list_ref(item_type)
        if list_ref is None: return False
        id_field = f"{item_type.__name__.lower()}_id"
        return any(getattr(item, id_field) == item_id for item in list_ref)

    def delete_item_by_id(self, item_id: str, item_type: Type[T]):
        list_ref, signal = self._get_list_ref(item_type)
        if list_ref is None: return
        id_field = f"{item_type.__name__.lower()}_id"
        original_len = len(list_ref)
        list_ref[:] = [item for item in list_ref if getattr(item, id_field) != item_id]
        if len(list_ref) < original_len:
            signal.emit()

    def duplicate_item(self, item):
        try:
            new_item = copy.deepcopy(item)
            item_type = type(item)
            id_field = f"{item_type.__name__.lower()}_id"
            setattr(new_item, id_field, str(uuid.uuid4()))
            new_item.adi = f"{new_item.adi} (Kopya)"
            self.save_item(new_item)
            self.status_updated.emit(f"'{item.adi}' kopyalandı ve '{new_item.adi}' olarak kaydedildi.")
        except Exception as e:
            self.status_updated.emit(f"Hata: Kayıt kopyalanamadı - {e}")

    def export_gorev_package(self, gorev_id: str, path: str):
        gorev = next((g for g in self.gorevler if g.gorev_id == gorev_id), None)
        if not gorev:
            self.status_updated.emit("Hata: Dışa aktarılacak görev bulunamadı.")
            return

        related_senaryos = [s for s in self.senaryolar if s.senaryo_id in gorev.senaryo_id_list]
        related_teknik_ids = {uygulama.teknik_id for s in related_senaryos for uygulama in s.uygulanan_teknikler}
        related_tekniks = [t for t in self.teknikler if t.teknik_id in related_teknik_ids]

        root = ET.Element("EHGorevPaketi")
        root.append(self._dataclass_to_element(gorev))
        senaryolar_root = ET.SubElement(root, "IlgiliSenaryolar")
        for item in related_senaryos: senaryolar_root.append(self._dataclass_to_element(item))
        teknikler_root = ET.SubElement(root, "IlgiliTeknikler")
        for item in related_tekniks: teknikler_root.append(self._dataclass_to_element(item))

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ", level=0)
        tree.write(path, encoding="utf-8", xml_declaration=True)
        self.status_updated.emit(f"'{gorev.adi}' görevi ve ilgili veriler başarıyla paketlendi.")

    def import_gorev_package(self, path: str):
        try:
            root = ET.parse(path).getroot()

            existing_teknik_ids = {t.teknik_id for t in self.teknikler}
            existing_senaryo_ids = {s.senaryo_id for s in self.senaryolar}
            existing_gorev_ids = {g.gorev_id for g in self.gorevler}

            for elem in root.findall("IlgiliTeknikler/Teknik"):
                item = self._element_to_dataclass(elem, Teknik)
                if item.teknik_id not in existing_teknik_ids: self.teknikler.append(item)
            for elem in root.findall("IlgiliSenaryolar/Senaryo"):
                item = self._element_to_dataclass(elem, Senaryo)
                if item.senaryo_id not in existing_senaryo_ids: self.senaryolar.append(item)
            gorev_elem = root.find("Gorev")
            if gorev_elem is not None:
                item = self._element_to_dataclass(gorev_elem, Gorev)
                if item.gorev_id not in existing_gorev_ids: self.gorevler.append(item)

            self._emit_all_changed_signals()
            self.status_updated.emit(f"Görev paketi '{os.path.basename(path)}' dosyasından başarıyla içe aktarıldı.")
        except Exception as e:
            self.status_updated.emit(f"Hata: Görev paketi içe aktarılamadı - {e}")

    def _ensure_data_files_exist(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        files_to_check = {
            RADARLAR_XML: "<Radarlar></Radarlar>",
            TEKNIKLER_XML: "<Teknikler></Teknikler>",
            SENARYOLAR_XML: "<Senaryolar></Senaryolar>",
            GOREVLER_XML: "<Gorevler></Gorevler>"
        }
        for path, content in files_to_check.items():
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f: f.write(content)