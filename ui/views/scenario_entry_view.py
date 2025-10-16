# ew_platformasi/ui/views/scenario_entry_view.py
from __future__ import annotations
import qtawesome as qta
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
                               QLineEdit, QTextEdit, QPushButton, QComboBox, QListWidget,
                               QListWidgetItem, QGroupBox, QDateEdit, QDoubleSpinBox, QMessageBox,
                               QTableWidget, QAbstractItemView, QHeaderView, QDialog, QDialogButtonBox,
                               QTableWidgetItem)

from viewmodels.scenario_vm import ScenarioViewModel
from core.data_models import Senaryo, Teknik, TeknikUygulama, ETPlatformu, Radar, SONUC_NITEL
from ui.views.library_view import TeknikFormWidget


class TeknikEntryDialog(QDialog):
    def __init__(self, vm: ScenarioViewModel, parent=None):
        super().__init__(parent)
        self.vm = vm
        self.setWindowTitle("Yeni EH Tekniği Oluştur (Detaylı)")
        self.setMinimumWidth(600)
        self.yeni_teknik = None

        layout = QVBoxLayout(self)
        self.form_widget = TeknikFormWidget(is_dialog=True)
        platforms = self.vm.get_available_data()[0]
        self.form_widget.update_platform_list(platforms)
        layout.addWidget(self.form_widget)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        try:
            self.yeni_teknik = self.form_widget.get_data_from_form()
            if not self.yeni_teknik.adi:
                QMessageBox.warning(self, "Eksik Bilgi", "Teknik adı boş olamaz.")
                return
            if not self.yeni_teknik.platform_id:
                QMessageBox.warning(self, "Eksik Bilgi", "Lütfen bir platform seçin.")
                return
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Teknik kaydedilirken bir hata oluştu: {e}")


class TeknikSecimDialog(QDialog):
    def __init__(self, vm: ScenarioViewModel, platform_id: str, parent=None):
        super().__init__(parent)
        self.vm = vm
        self.platform_id = platform_id
        self.setWindowTitle("Teknik Seç")
        self.secilen_teknik = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Eklemek için bir teknik seçin veya yeni bir tane oluşturun:"))
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        self.refresh_teknik_list()

        self.btn_yeni_teknik = QPushButton("Yeni Teknik Oluştur...", icon=qta.icon('fa5s.plus'))
        self.btn_yeni_teknik.clicked.connect(self.create_new_teknik)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_yeni_teknik)
        btn_layout.addStretch()
        btn_layout.addWidget(button_box)
        layout.addLayout(btn_layout)

    def refresh_teknik_list(self, select_id: str | None = None):
        self.list_widget.clear()
        teknikler = self.vm.get_teknikler_for_platform(self.platform_id)
        for t in sorted(teknikler, key=lambda x: x.adi):
            item = QListWidgetItem(f"{t.adi} [{t.kategori}]")
            item.setData(Qt.ItemDataRole.UserRole, t)
            self.list_widget.addItem(item)
            if t.teknik_id == select_id:
                self.list_widget.setCurrentItem(item)

    def create_new_teknik(self):
        dialog = TeknikEntryDialog(self.vm, self)
        if dialog.exec() and dialog.yeni_teknik:
            self.vm.save_teknik(dialog.yeni_teknik)
            self.refresh_teknik_list(select_id=dialog.yeni_teknik.teknik_id)

    def accept(self):
        if self.list_widget.currentItem():
            self.secilen_teknik = self.list_widget.currentItem().data(Qt.ItemDataRole.UserRole)
        super().accept()


class ScenarioEntryView(QWidget):
    form_saved = Signal(Senaryo)

    def __init__(self, view_model: ScenarioViewModel, parent=None):
        super().__init__(parent)
        self.vm = view_model
        self.current_scenario_id = None
        self._build_ui()
        self._connect_signals()
        self.refresh_lists()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.form_box = QGroupBox("Yeni Senaryo Kayıt Formu")

        form = QFormLayout(self.form_box)
        self.dd_platform = QComboBox()
        self.in_adi = QLineEdit()
        self.in_tarih = QDateEdit(calendarPopup=True, date=QDate.currentDate())
        self.dd_radar = QComboBox()
        self._build_teknik_table_ui()
        self.in_sonuc = QComboBox()
        self.in_sonuc.addItems(SONUC_NITEL)
        self.in_mesafe_km = QDoubleSpinBox(suffix=" km", minimum=0.0, maximum=1000.0, decimals=1, value=0.0)
        self.in_mesafe_km.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        self.in_not = QTextEdit(fixedHeight=100)
        self.in_konum = QLineEdit()
        self.in_amac = QTextEdit(fixedHeight=80)

        form.addRow("ET Platformu:", self.dd_platform)
        form.addRow("Senaryo Adı:", self.in_adi)
        form.addRow("Tarih:", self.in_tarih)
        form.addRow("Konum:", self.in_konum)
        form.addRow("Amaç:", self.in_amac)
        form.addRow("Hedef Radar:", self.dd_radar)
        form.addRow(self.teknik_group)

        numeric_layout = QHBoxLayout()
        numeric_layout.addWidget(QLabel("Mesafe:"))
        numeric_layout.addWidget(self.in_mesafe_km)
        numeric_layout.addStretch()
        form.addRow(numeric_layout)

        form.addRow("Nitel Sonuç:", self.in_sonuc)
        form.addRow("Notlar ve Açıklamalar:", self.in_not)

        button_layout = QHBoxLayout()
        self.btn_kaydet = QPushButton("Kaydet ve Kapat", icon=qta.icon('fa5s.save'))
        self.btn_temizle = QPushButton("Formu Temizle / Yeni Kayıt", icon=qta.icon('fa5s.eraser'))
        button_layout.addStretch()
        button_layout.addWidget(self.btn_temizle)
        button_layout.addWidget(self.btn_kaydet)

        layout.addWidget(self.form_box)
        layout.addLayout(button_layout)

    def _build_teknik_table_ui(self):
        self.teknik_group = QGroupBox("Uygulanan Teknikler Sırası ve Süreleri")
        self.teknik_group.setEnabled(False)  # Başlangıçta pasif
        teknik_layout = QHBoxLayout(self.teknik_group)
        self.teknik_table = QTableWidget()
        self.teknik_table.setColumnCount(4)
        self.teknik_table.setHorizontalHeaderLabels(["Sıra", "Teknik Adı", "Süre (sn)", "ID"])
        self.teknik_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.teknik_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.teknik_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.teknik_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.teknik_table.setColumnHidden(3, True)
        self.teknik_table.setFixedWidth(500)

        teknik_buttons_layout = QVBoxLayout()
        self.btn_teknik_ekle = QPushButton(qta.icon('fa5s.plus'), "")
        self.btn_teknik_sil = QPushButton(qta.icon('fa5s.trash-alt'), "")
        self.btn_teknik_yukari = QPushButton(qta.icon('fa5s.arrow-up'), "")
        self.btn_teknik_asagi = QPushButton(qta.icon('fa5s.arrow-down'), "")
        teknik_buttons_layout.addWidget(self.btn_teknik_ekle)
        teknik_buttons_layout.addWidget(self.btn_teknik_sil)
        teknik_buttons_layout.addStretch()
        teknik_buttons_layout.addWidget(self.btn_teknik_yukari)
        teknik_buttons_layout.addWidget(self.btn_teknik_asagi)

        teknik_layout.addWidget(self.teknik_table)
        teknik_layout.addLayout(teknik_buttons_layout)

    def _connect_signals(self):
        self.btn_kaydet.clicked.connect(self._save_scenario)
        self.btn_temizle.clicked.connect(self._clear_form)
        self.vm._data_manager.platformlar_changed.connect(self.refresh_lists)
        self.vm._data_manager.radarlar_changed.connect(self.refresh_lists)
        self.vm._data_manager.teknikler_changed.connect(self.refresh_lists)

        self.dd_platform.currentIndexChanged.connect(self._on_platform_changed)
        self.btn_teknik_ekle.clicked.connect(self._add_teknik)
        self.btn_teknik_sil.clicked.connect(self._remove_teknik)
        self.btn_teknik_yukari.clicked.connect(lambda: self._move_teknik(-1))
        self.btn_teknik_asagi.clicked.connect(lambda: self._move_teknik(1))

    def refresh_lists(self):
        platforms, radars, _ = self.vm.get_available_data()

        current_platform = self.dd_platform.currentData()
        self.dd_platform.clear()
        self.dd_platform.addItem("— Önce Platform Seçiniz —", userData=None)
        for p in sorted(platforms, key=lambda x: x.adi):
            self.dd_platform.addItem(p.adi, userData=p.platform_id)
        new_platform_index = self.dd_platform.findData(current_platform)
        if new_platform_index != -1: self.dd_platform.setCurrentIndex(new_platform_index)

        current_radar = self.dd_radar.currentData()
        self.dd_radar.clear()
        self.dd_radar.addItem("— Seçiniz —", userData=None)
        for r in sorted(radars, key=lambda x: x.adi):
            self.dd_radar.addItem(f"{r.adi} ({r.uretici})", userData=r.radar_id)
        new_radar_index = self.dd_radar.findData(current_radar)
        if new_radar_index != -1: self.dd_radar.setCurrentIndex(new_radar_index)

    def _on_platform_changed(self, index):
        platform_secili = self.dd_platform.currentData() is not None
        self.teknik_group.setEnabled(platform_secili)
        if self.teknik_table.rowCount() > 0:
            QMessageBox.warning(self, "Uyarı", "Platform değiştirildiği için mevcut teknik listesi temizlendi.")
            self.teknik_table.setRowCount(0)

    def _add_teknik(self):
        platform_id = self.dd_platform.currentData()
        if not platform_id:
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen önce bir ET Platformu seçin.")
            return

        dialog = TeknikSecimDialog(self.vm, platform_id, self)
        if dialog.exec() and dialog.secilen_teknik:
            secilen_teknik = dialog.secilen_teknik
            row_pos = self.teknik_table.rowCount()
            self.teknik_table.insertRow(row_pos)
            sira_item = QTableWidgetItem(str(row_pos + 1))
            ad_item = QTableWidgetItem(secilen_teknik.adi)
            sure_spinbox = QDoubleSpinBox(decimals=1, minimum=0.1, value=10.0)
            id_item = QTableWidgetItem(secilen_teknik.teknik_id)

            for item in [sira_item, ad_item]:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            self.teknik_table.setItem(row_pos, 0, sira_item)
            self.teknik_table.setItem(row_pos, 1, ad_item)
            self.teknik_table.setCellWidget(row_pos, 2, sure_spinbox)
            self.teknik_table.setItem(row_pos, 3, id_item)
            self._update_sira()

    def _remove_teknik(self):
        current_row = self.teknik_table.currentRow()
        if current_row >= 0:
            self.teknik_table.removeRow(current_row)
            self._update_sira()

    def _move_teknik(self, direction):
        row = self.teknik_table.currentRow()
        if row < 0: return
        new_row = row + direction
        if 0 <= new_row < self.teknik_table.rowCount():
            items = [self.teknik_table.takeItem(row, col) for col in [0, 1, 3]]
            widget = self.teknik_table.cellWidget(row, 2)
            self.teknik_table.removeRow(row)
            self.teknik_table.insertRow(new_row)
            self.teknik_table.setItem(new_row, 0, items[0])
            self.teknik_table.setItem(new_row, 1, items[1])
            self.teknik_table.setCellWidget(new_row, 2, widget)
            self.teknik_table.setItem(new_row, 3, items[2])
            self.teknik_table.selectRow(new_row)
            self._update_sira()

    def _update_sira(self):
        for row in range(self.teknik_table.rowCount()):
            self.teknik_table.item(row, 0).setText(str(row + 1))

    def _save_scenario(self):
        if not self.in_adi.text().strip():
            QMessageBox.warning(self, "Eksik Bilgi", "Senaryo adı boş olamaz.")
            return
        if not self.dd_platform.currentData():
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen bir ET Platformu seçin.")
            return

        uygulanan_teknikler = [TeknikUygulama(
            sira=int(self.teknik_table.item(row, 0).text()),
            teknik_id=self.teknik_table.item(row, 3).text(),
            sure_sn=self.teknik_table.cellWidget(row, 2).value()
        ) for row in range(self.teknik_table.rowCount())]

        scenario_data = Senaryo(
            senaryo_id=self.current_scenario_id,
            adi=self.in_adi.text().strip(),
            tarih_iso=self.in_tarih.date().toString("yyyy-MM-dd"),
            konum=self.in_konum.text().strip(),
            amac=self.in_amac.toPlainText().strip(),
            et_platformu_id=self.dd_platform.currentData(),
            radar_id=self.dd_radar.currentData(),
            uygulanan_teknikler=uygulanan_teknikler,
            sonuc_nitel=self.in_sonuc.currentText(),
            mesafe_km=self.in_mesafe_km.value() if self.in_mesafe_km.value() != 0.0 else None,
            notlar=self.in_not.toPlainText().strip()
        )
        saved_scenario = self.vm.save_scenario(scenario_data)
        self.form_saved.emit(saved_scenario)

    def _clear_form(self):
        self.current_scenario_id = None
        self.form_box.setTitle("Yeni Senaryo Kayıt Formu")
        self.in_adi.clear()
        self.in_not.clear()
        self.in_konum.clear()
        self.in_amac.clear()
        self.in_tarih.setDate(QDate.currentDate())
        self.dd_platform.setCurrentIndex(0)
        self.dd_radar.setCurrentIndex(0)
        self.teknik_table.setRowCount(0)
        self.in_sonuc.setCurrentIndex(0)
        self.in_mesafe_km.setValue(0.0)
        self.dd_platform.setFocus()

    def load_scenario_for_edit(self, scenario: Senaryo):
        self._clear_form()
        self.current_scenario_id = scenario.senaryo_id
        self.form_box.setTitle(f"Senaryo Düzenle: {scenario.adi}")

        self.in_adi.setText(scenario.adi)
        self.in_tarih.setDate(QDate.fromString(scenario.tarih_iso, "yyyy-MM-dd"))
        self.in_konum.setText(scenario.konum)
        self.in_amac.setPlainText(scenario.amac)
        self.in_not.setPlainText(scenario.notlar)
        self.in_sonuc.setCurrentText(scenario.sonuc_nitel)
        self.in_mesafe_km.setValue(scenario.mesafe_km or 0.0)

        platform_index = self.dd_platform.findData(scenario.et_platformu_id)
        self.dd_platform.setCurrentIndex(platform_index if platform_index != -1 else 0)

        radar_index = self.dd_radar.findData(scenario.radar_id)
        self.dd_radar.setCurrentIndex(radar_index if radar_index != -1 else 0)

        self.teknik_table.setRowCount(0)
        teknikler_list = self.vm.get_teknikler_for_platform(scenario.et_platformu_id)
        teknik_map = {t.teknik_id: t for t in teknikler_list}
        for uygulama in sorted(scenario.uygulanan_teknikler, key=lambda x: x.sira):
            teknik = teknik_map.get(uygulama.teknik_id)
            if teknik:
                row_pos = self.teknik_table.rowCount()
                self.teknik_table.insertRow(row_pos)
                sira_item = QTableWidgetItem(str(uygulama.sira))
                ad_item = QTableWidgetItem(teknik.adi)
                sure_spinbox = QDoubleSpinBox(decimals=1, minimum=0.1, value=uygulama.sure_sn)
                id_item = QTableWidgetItem(teknik.teknik_id)
                self.teknik_table.setItem(row_pos, 0, sira_item)
                self.teknik_table.setItem(row_pos, 1, ad_item)
                self.teknik_table.setCellWidget(row_pos, 2, sure_spinbox)
                self.teknik_table.setItem(row_pos, 3, id_item)
        self._update_sira()