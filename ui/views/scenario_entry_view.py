# ew_platformasi/ui/views/scenario_entry_view.py

import qtawesome as qta
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
                               QLineEdit, QTextEdit, QPushButton, QComboBox, QListWidget,
                               QListWidgetItem, QGroupBox, QDateEdit, QDoubleSpinBox, QMessageBox)

from viewmodels.scenario_vm import ScenarioViewModel
from core.data_models import Senaryo, SONUC_NITEL


class ScenarioEntryView(QWidget):
    def __init__(self, view_model: ScenarioViewModel, parent=None):
        super().__init__(parent)
        self.vm = view_model
        self.current_scenario_id = None  # Düzenlenen senaryonun ID'sini tutmak için

        self._build_ui()
        self._connect_signals()
        self.refresh_lists()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.form_box = QGroupBox("Yeni Senaryo Kayıt Formu")  # Başlık dinamik olacak
        self.form_box.setMaximumWidth(800)
        form = QFormLayout(self.form_box)

        self.in_adi = QLineEdit()
        self.in_tarih = QDateEdit(calendarPopup=True, date=QDate.currentDate())
        self.dd_radar = QComboBox()
        self.list_teknik = QListWidget(selectionMode=QListWidget.SelectionMode.MultiSelection)
        self.in_sonuc = QComboBox();
        self.in_sonuc.addItems(SONUC_NITEL)

        self.in_js_db = QDoubleSpinBox(suffix=" dB", minimum=-50.0, maximum=50.0, decimals=1)
        self.in_js_db.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)

        self.in_mesafe_km = QDoubleSpinBox(suffix=" km", minimum=0.0, maximum=1000.0, decimals=1)
        self.in_mesafe_km.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)

        self.in_not = QTextEdit(fixedHeight=100)

        form.addRow("Senaryo Adı:", self.in_adi)
        form.addRow("Tarih:", self.in_tarih)
        form.addRow("Hedef Radar:", self.dd_radar)
        form.addRow("Uygulanan Teknikler:", self.list_teknik)

        numeric_layout = QHBoxLayout()
        numeric_layout.addWidget(QLabel("J/S Oranı:"))
        numeric_layout.addWidget(self.in_js_db)
        numeric_layout.addSpacing(20)
        numeric_layout.addWidget(QLabel("Mesafe:"))
        numeric_layout.addWidget(self.in_mesafe_km)
        numeric_layout.addStretch()
        form.addRow(numeric_layout)

        form.addRow("Nitel Sonuç:", self.in_sonuc)
        form.addRow("Notlar ve Açıklamalar:", self.in_not)

        button_layout = QHBoxLayout()
        self.btn_kaydet = QPushButton("Kaydet", icon=qta.icon('fa5s.save'))
        self.btn_temizle = QPushButton("Formu Temizle / Yeni Kayıt", icon=qta.icon('fa5s.eraser'))
        button_layout.addStretch()
        button_layout.addWidget(self.btn_kaydet)
        button_layout.addWidget(self.btn_temizle)

        layout.addWidget(self.form_box)
        layout.addLayout(button_layout)

    def _connect_signals(self):
        self.btn_kaydet.clicked.connect(self._save_scenario)
        self.btn_temizle.clicked.connect(self._clear_form)
        self.vm._data_manager.radarlar_changed.connect(self.refresh_lists)
        self.vm._data_manager.teknikler_changed.connect(self.refresh_lists)

    def refresh_lists(self):
        radars, teknikler = self.vm.get_available_radars_and_teknikler()

        self.dd_radar.clear()
        self.dd_radar.addItem("— Seçiniz —", userData=None)
        for r in radars:
            self.dd_radar.addItem(f"{r.adi} ({r.uretici})", userData=r.radar_id)

        self.list_teknik.clear()
        for t in teknikler:
            item = QListWidgetItem(f"{t.adi} [{t.kategori}]")
            item.setData(Qt.ItemDataRole.UserRole, t.teknik_id)
            self.list_teknik.addItem(item)

    def _save_scenario(self):
        if not self.in_adi.text().strip():
            QMessageBox.warning(self, "Eksik Bilgi", "Senaryo adı boş olamaz.")
            return

        selected_teknikler = [self.list_teknik.item(i).data(Qt.ItemDataRole.UserRole)
                              for i in range(self.list_teknik.count()) if self.list_teknik.item(i).isSelected()]

        js_db_value = self.in_js_db.value() if self.in_js_db.value() != 0.0 else None
        mesafe_km_value = self.in_mesafe_km.value() if self.in_mesafe_km.value() != 0.0 else None

        # Yeni senaryo nesnesini oluştur
        scenario_data = Senaryo(
            senaryo_id=self.current_scenario_id,  # Eğer düzenleme ise ID'yi koru, değilse None
            adi=self.in_adi.text().strip(),
            tarih_iso=self.in_tarih.date().toString("yyyy-MM-dd"),
            radar_id=self.dd_radar.currentData(),
            teknik_id_list=selected_teknikler,
            sonuc_nitel=self.in_sonuc.currentText(),
            js_db=js_db_value,
            mesafe_km=mesafe_km_value,
            notlar=self.in_not.toPlainText().strip()
        )

        # DataManager'a kaydet/güncelle
        self.vm.save_scenario(scenario_data)
        QMessageBox.information(self, "Başarılı", f"'{scenario_data.adi}' senaryosu kaydedildi.")
        self._clear_form()

    def _clear_form(self):
        """Formu temizler ve yeni kayıt moduna geçirir."""
        self.current_scenario_id = None
        self.form_box.setTitle("Yeni Senaryo Kayıt Formu")
        self.in_adi.clear()
        self.in_not.clear()
        self.in_tarih.setDate(QDate.currentDate())
        self.dd_radar.setCurrentIndex(0)
        self.list_teknik.clearSelection()
        self.in_sonuc.setCurrentIndex(0)
        self.in_js_db.setValue(0.0)
        self.in_mesafe_km.setValue(0.0)
        self.in_adi.setFocus()

    def load_scenario_for_edit(self, scenario: Senaryo):
        """Mevcut bir senaryoyu düzenlemek için formu doldurur."""
        self._clear_form()  # Önce formu temizle
        self.current_scenario_id = scenario.senaryo_id
        self.form_box.setTitle(f"Senaryo Düzenle: {scenario.adi}")

        self.in_adi.setText(scenario.adi)
        self.in_tarih.setDate(QDate.fromString(scenario.tarih_iso, "yyyy-MM-dd"))
        self.in_not.setPlainText(scenario.notlar)
        self.in_sonuc.setCurrentText(scenario.sonuc_nitel)
        self.in_js_db.setValue(scenario.js_db or 0.0)
        self.in_mesafe_km.setValue(scenario.mesafe_km or 0.0)

        # Radar ComboBox'ını ayarla
        radar_index = self.dd_radar.findData(scenario.radar_id)
        self.dd_radar.setCurrentIndex(radar_index if radar_index != -1 else 0)

        # Teknikler Listesini ayarla
        for i in range(self.list_teknik.count()):
            item = self.list_teknik.item(i)
            if item.data(Qt.ItemDataRole.UserRole) in scenario.teknik_id_list:
                item.setSelected(True)