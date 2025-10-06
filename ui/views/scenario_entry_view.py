# ew_platformasi/ui/views/scenario_entry_view.py

import qtawesome as qta
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QLineEdit, QTextEdit, QPushButton, QComboBox, QListWidget,
                               QGroupBox, QDateEdit, QMessageBox)
from viewmodels.scenario_vm import ScenarioViewModel
from core.data_models import Senaryo, SONUC_NITEL

class ScenarioEntryView(QWidget):
    def __init__(self, view_model: ScenarioViewModel, parent=None):
        super().__init__(parent)
        self.vm = view_model
        self._build_ui()
        self._connect_signals()
        self.refresh_lists()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        form_box = QGroupBox("Yeni Senaryo Kayıt Formu")
        form_box.setMaximumWidth(800)
        form = QFormLayout(form_box)
        self.in_adi = QLineEdit()
        self.in_tarih = QDateEdit(calendarPopup=True, date=QDate.currentDate())
        self.dd_radar = QComboBox()
        self.list_teknik = QListWidget(selectionMode=QListWidget.SelectionMode.MultiSelection)
        self.in_sonuc = QComboBox(); self.in_sonuc.addItems(SONUC_NITEL)
        self.in_not = QTextEdit(); self.in_not.setFixedHeight(100)
        form.addRow("Senaryo Adı:", self.in_adi)
        form.addRow("Tarih:", self.in_tarih)
        form.addRow("Hedef Radar:", self.dd_radar)
        form.addRow("Uygulanan Teknikler:", self.list_teknik)
        form.addRow("Nitel Sonuç:", self.in_sonuc)
        form.addRow("Notlar ve Açıklamalar:", self.in_not)
        button_layout = QHBoxLayout()
        self.btn_kaydet = QPushButton("Kaydet", icon=qta.icon('fa5s.save'))
        self.btn_temizle = QPushButton("Formu Temizle", icon=qta.icon('fa5s.eraser'))
        button_layout.addStretch()
        button_layout.addWidget(self.btn_kaydet)
        button_layout.addWidget(self.btn_temizle)
        layout.addWidget(form_box)
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
        for r in radars: self.dd_radar.addItem(f"{r.adi} ({r.uretici})", userData=r.radar_id)
        self.list_teknik.clear()
        for t in teknikler:
            item = self.list_teknik.addItem(f"{t.adi} [{t.kategori}]")
            # setData metodunda bir hata var. Bu şekilde düzeltilmeli
            # item.setData(Qt.ItemDataRole.UserRole, t.teknik_id)

    def _save_scenario(self):
        if not self.in_adi.text().strip():
            QMessageBox.warning(self, "Eksik Bilgi", "Senaryo adı boş olamaz.")
            return
        selected_teknikler = [self.list_teknik.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.list_teknik.count()) if self.list_teknik.item(i).isSelected()]
        new_scenario = Senaryo(
            adi=self.in_adi.text().strip(),
            tarih_iso=self.in_tarih.date().toString("yyyy-MM-dd"),
            radar_id=self.dd_radar.currentData(),
            teknik_id_list=selected_teknikler,
            sonuc_nitel=self.in_sonuc.currentText(),
            notlar=self.in_not.toPlainText().strip()
        )
        self.vm.save_scenario(new_scenario)
        self._clear_form()

    def _clear_form(self):
        self.in_adi.clear()
        self.in_not.clear()
        self.in_tarih.setDate(QDate.currentDate())
        self.dd_radar.setCurrentIndex(0)
        self.list_teknik.clearSelection()
        self.in_sonuc.setCurrentIndex(0)
        self.in_adi.setFocus()