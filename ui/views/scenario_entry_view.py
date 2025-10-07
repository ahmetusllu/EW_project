# ew_platformasi/ui/views/scenario_entry_view.py
from __future__ import annotations

import qtawesome as qta
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
                               QLineEdit, QTextEdit, QPushButton, QComboBox, QListWidget,
                               QListWidgetItem, QGroupBox, QDateEdit, QDoubleSpinBox, QMessageBox,
                               QTableWidget, QAbstractItemView, QHeaderView, QDialog, QDialogButtonBox,
                               QSpinBox, QTableWidgetItem)

from viewmodels.scenario_vm import ScenarioViewModel
from core.data_models import Senaryo, SONUC_NITEL, Teknik, TeknikUygulama


class TeknikSecimDialog(QDialog):
    """Mevcut teknikler arasından seçim yapmak için kullanılan diyalog."""
    def __init__(self, teknikler: list[Teknik], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Teknik Seç")
        self.list_widget = QListWidget()
        for t in teknikler:
            item = QListWidgetItem(f"{t.adi} [{t.kategori}]")
            item.setData(Qt.ItemDataRole.UserRole, t)
            self.list_widget.addItem(item)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Eklemek için bir teknik seçin:"))
        layout.addWidget(self.list_widget)
        layout.addWidget(buttons)

    def get_selected_teknik(self) -> Teknik | None:
        if self.list_widget.currentItem():
            return self.list_widget.currentItem().data(Qt.ItemDataRole.UserRole)
        return None


class ScenarioEntryView(QWidget):
    form_saved = Signal()

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

        self.in_adi = QLineEdit()
        self.in_tarih = QDateEdit(calendarPopup=True, date=QDate.currentDate())
        self.dd_radar = QComboBox()

        # Teknikler için QListWidget yerine QTableWidget kullanacağız
        self._build_teknik_table_ui()

        self.in_sonuc = QComboBox()
        self.in_sonuc.addItems(SONUC_NITEL)
        self.in_js_db = QDoubleSpinBox(suffix=" dB", minimum=-50.0, maximum=50.0, decimals=1, value=0.0)
        self.in_js_db.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        self.in_mesafe_km = QDoubleSpinBox(suffix=" km", minimum=0.0, maximum=1000.0, decimals=1, value=0.0)
        self.in_mesafe_km.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        self.in_not = QTextEdit(fixedHeight=100)
        self.in_konum = QLineEdit()
        self.in_amac = QTextEdit(fixedHeight=80)

        form.addRow("Senaryo Adı:", self.in_adi)
        form.addRow("Tarih:", self.in_tarih)
        form.addRow("Konum:", self.in_konum)
        form.addRow("Amaç:", self.in_amac)
        form.addRow("Hedef Radar:", self.dd_radar)
        form.addRow(self.teknik_group)  # Teknik grubunu form'a ekle

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
        self.btn_kaydet = QPushButton("Kaydet ve Kapat", icon=qta.icon('fa5s.save'))
        self.btn_temizle = QPushButton("Formu Temizle / Yeni Kayıt", icon=qta.icon('fa5s.eraser'))
        button_layout.addStretch()
        button_layout.addWidget(self.btn_temizle)
        button_layout.addWidget(self.btn_kaydet)

        layout.addWidget(self.form_box)
        layout.addLayout(button_layout)

    def _build_teknik_table_ui(self):
        self.teknik_group = QGroupBox("Uygulanan Teknikler Sırası ve Süreleri")
        teknik_layout = QHBoxLayout(self.teknik_group)
        self.teknik_table = QTableWidget()
        self.teknik_table.setColumnCount(4)
        self.teknik_table.setHorizontalHeaderLabels(["Sıra", "Teknik Adı", "Süre (sn)", "ID"])
        self.teknik_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.teknik_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.teknik_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.teknik_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.teknik_table.setColumnHidden(3, True) # ID sütununu gizle
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
        self.vm._data_manager.radarlar_changed.connect(self.refresh_lists)
        self.vm._data_manager.teknikler_changed.connect(self.refresh_lists)

        self.btn_teknik_ekle.clicked.connect(self._add_teknik)
        self.btn_teknik_sil.clicked.connect(self._remove_teknik)
        self.btn_teknik_yukari.clicked.connect(lambda: self._move_teknik(-1))
        self.btn_teknik_asagi.clicked.connect(lambda: self._move_teknik(1))

    def refresh_lists(self):
        radars, _ = self.vm.get_available_radars_and_teknikler()
        self.dd_radar.clear()
        self.dd_radar.addItem("— Seçiniz —", userData=None)
        for r in radars:
            self.dd_radar.addItem(f"{r.adi} ({r.uretici})", userData=r.radar_id)

    def _add_teknik(self):
        _, teknikler = self.vm.get_available_radars_and_teknikler()
        dialog = TeknikSecimDialog(teknikler, self)
        if dialog.exec():
            secilen_teknik = dialog.get_selected_teknik()
            if secilen_teknik:
                row_pos = self.teknik_table.rowCount()
                self.teknik_table.insertRow(row_pos)

                sira_item = QTableWidgetItem(str(row_pos + 1))
                sira_item.setFlags(sira_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                ad_item = QTableWidgetItem(secilen_teknik.adi)
                ad_item.setFlags(ad_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                sure_spinbox = QDoubleSpinBox(decimals=1, minimum=0.1, value=10.0)

                id_item = QTableWidgetItem(secilen_teknik.teknik_id)

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
            # Satır içeriğini al
            items = [self.teknik_table.takeItem(row, col) for col in [0,1,3]]
            widget = self.teknik_table.cellWidget(row, 2)
            # Satırı sil ve yeni yere ekle
            self.teknik_table.removeRow(row)
            self.teknik_table.insertRow(new_row)
            # İçeriği geri koy
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

        uygulanan_teknikler = []
        for row in range(self.teknik_table.rowCount()):
            uygulanan_teknikler.append(TeknikUygulama(
                sira=int(self.teknik_table.item(row, 0).text()),
                teknik_id=self.teknik_table.item(row, 3).text(),
                sure_sn=self.teknik_table.cellWidget(row, 2).value()
            ))

        scenario_data = Senaryo(
            senaryo_id=self.current_scenario_id,
            adi=self.in_adi.text().strip(),
            tarih_iso=self.in_tarih.date().toString("yyyy-MM-dd"),
            konum=self.in_konum.text().strip(),
            amac=self.in_amac.toPlainText().strip(),
            radar_id=self.dd_radar.currentData(),
            uygulanan_teknikler=uygulanan_teknikler,
            sonuc_nitel=self.in_sonuc.currentText(),
            js_db=self.in_js_db.value() if self.in_js_db.value() != 0.0 else None,
            mesafe_km=self.in_mesafe_km.value() if self.in_mesafe_km.value() != 0.0 else None,
            notlar=self.in_not.toPlainText().strip()
        )
        self.vm.save_scenario(scenario_data)
        self.form_saved.emit()

    def _clear_form(self):
        self.current_scenario_id = None
        self.form_box.setTitle("Yeni Senaryo Kayıt Formu")
        self.in_adi.clear()
        self.in_not.clear()
        self.in_konum.clear()
        self.in_amac.clear()
        self.in_tarih.setDate(QDate.currentDate())
        self.dd_radar.setCurrentIndex(0)
        self.teknik_table.setRowCount(0)
        self.in_sonuc.setCurrentIndex(0)
        self.in_js_db.setValue(0.0)
        self.in_mesafe_km.setValue(0.0)
        self.in_adi.setFocus()

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
        self.in_js_db.setValue(scenario.js_db or 0.0)
        self.in_mesafe_km.setValue(scenario.mesafe_km or 0.0)

        radar_index = self.dd_radar.findData(scenario.radar_id)
        self.dd_radar.setCurrentIndex(radar_index if radar_index != -1 else 0)

        # Teknik tablosunu doldur
        self.teknik_table.setRowCount(0)
        _, teknikler_list = self.vm.get_available_radars_and_teknikler()
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