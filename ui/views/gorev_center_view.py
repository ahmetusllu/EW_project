# ew_platformasi/ui/views/gorev_center_view.py
from __future__ import annotations

import qtawesome as qta
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QGroupBox,
                               QLineEdit, QTableView, QHeaderView, QLabel, QPushButton,
                               QFileDialog, QMessageBox, QListWidget, QFormLayout, QTextEdit,
                               QListWidgetItem, QDialog, QDialogButtonBox, QAbstractItemView, QTabWidget)

from viewmodels.gorev_vm import GorevViewModel
from viewmodels.scenario_vm import ScenarioViewModel
from ui.views.scenario_entry_view import ScenarioEntryView
from core.data_models import Gorev, Senaryo


class ScenarioEntryDialog(QDialog):
    """Senaryo giriş formunu sarmalayan diyalog penceresi."""
    form_saved = Signal()

    def __init__(self, vm: ScenarioViewModel, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Senaryo Kayıt/Düzenleme")
        self.setMinimumSize(800, 700)
        self.view = ScenarioEntryView(vm)
        layout = QVBoxLayout(self)
        layout.addWidget(self.view)

        # View içindeki sinyali diyalogun kapanmasına bağla
        self.view.form_saved.connect(self.accept)

    def load_scenario(self, scenario: Senaryo | None):
        if scenario:
            self.view.load_scenario_for_edit(scenario)
        else:
            self.view._clear_form()


class SenaryoSelectionDialog(QDialog):
    def __init__(self, all_senaryos: list[Senaryo], pre_selected_ids: list[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Senaryo Seçimi")
        self.setMinimumSize(400, 500)

        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        layout.addWidget(self.list_widget)

        for senaryo in all_senaryos:
            item = QListWidgetItem(f"{senaryo.adi} ({senaryo.tarih_iso})")
            item.setData(Qt.ItemDataRole.UserRole, senaryo.senaryo_id)
            self.list_widget.addItem(item)
            if senaryo.senaryo_id in pre_selected_ids:
                item.setSelected(True)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_selected_ids(self) -> list[str]:
        return [self.list_widget.item(i).data(Qt.ItemDataRole.UserRole)
                for i in range(self.list_widget.count()) if self.list_widget.item(i).isSelected()]


class GorevCenterView(QWidget):
    def __init__(self, gorev_vm: GorevViewModel, scenario_vm: ScenarioViewModel, parent=None):
        super().__init__(parent)
        self.vm = gorev_vm
        self.scenario_vm = scenario_vm
        self.current_gorev = None
        self.current_scenario = None

        # Senaryo giriş formunu içeren diyalog penceresini oluştur
        self.scenario_entry_dialog = ScenarioEntryDialog(self.scenario_vm, self)

        self._build_ui()
        self._connect_signals()
        self._clear_details()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Sol Panel: Görev Listesi
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        self.gorev_search_box = QLineEdit(placeholderText="Görev adı veya sorumlu personel ara...")
        self.gorev_table = QTableView()
        self.gorev_table.setModel(self.vm.proxy_model)
        self.gorev_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.gorev_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.gorev_table.setSortingEnabled(True)
        self.gorev_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        left_layout.addWidget(self.gorev_search_box)
        left_layout.addWidget(self.gorev_table)

        # Sağ Panel: Artık sekmeli bir yapı
        right_panel = QTabWidget()
        self.gorev_details_tab = QWidget()
        self.senaryo_yonetim_tab = QWidget()

        right_panel.addTab(self.gorev_details_tab, "Görev Detayları")
        right_panel.addTab(self.senaryo_yonetim_tab, "Tüm Senaryoları Yönet")

        self._build_gorev_details_tab()
        self._build_senaryo_yonetim_tab()

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([700, 600])
        layout.addWidget(splitter)

    def _build_gorev_details_tab(self):
        """Görev detaylarının ve atanmış senaryoların olduğu ilk sekmeyi oluşturur."""
        layout = QVBoxLayout(self.gorev_details_tab)
        form_group = QGroupBox("Seçili Görev Bilgileri")
        form = QFormLayout(form_group)

        self.in_adi = QLineEdit()
        self.in_tarih = QLineEdit(readOnly=True)
        self.in_sorumlu = QLineEdit()
        self.in_aciklama = QTextEdit(fixedHeight=80)

        form.addRow("Görev Adı:", self.in_adi)
        form.addRow("Oluşturma Tarihi:", self.in_tarih)
        form.addRow("Sorumlu Personel:", self.in_sorumlu)
        form.addRow("Açıklama:", self.in_aciklama)
        layout.addWidget(form_group)

        senaryo_group = QGroupBox("Göreve Atanmış Senaryolar")
        senaryo_layout = QVBoxLayout(senaryo_group)
        self.senaryo_table = QTableView()
        self.senaryo_table.setModel(self.vm.senaryo_details_model)
        self.senaryo_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.senaryo_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.senaryo_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.senaryo_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.senaryo_table.setWordWrap(True)
        senaryo_layout.addWidget(self.senaryo_table)

        btn_layout = QHBoxLayout()
        self.btn_manage_senaryos = QPushButton("Görev Senaryolarını Yönet", icon=qta.icon('fa5s.tasks'))
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_manage_senaryos)
        senaryo_layout.addLayout(btn_layout)
        layout.addWidget(senaryo_group)

        op_btn_layout = QHBoxLayout()
        self.btn_yeni_gorev = QPushButton("Yeni Görev", icon=qta.icon('fa5s.plus-circle'))
        self.btn_kaydet_gorev = QPushButton("Görevi Kaydet", icon=qta.icon('fa5s.save'))
        self.btn_sil_gorev = QPushButton("Görevi Sil", icon=qta.icon('fa5s.trash-alt', color='red'))
        self.btn_export = QPushButton("Görevi Paketle", icon=qta.icon('fa5s.box-open'))

        op_btn_layout.addWidget(self.btn_yeni_gorev)
        op_btn_layout.addStretch()
        op_btn_layout.addWidget(self.btn_kaydet_gorev)
        op_btn_layout.addWidget(self.btn_sil_gorev)
        op_btn_layout.addWidget(self.btn_export)
        layout.addLayout(op_btn_layout)

    def _build_senaryo_yonetim_tab(self):
        """Tüm senaryoların yönetildiği ikinci sekmeyi oluşturur."""
        layout = QVBoxLayout(self.senaryo_yonetim_tab)

        top_bar = QHBoxLayout()
        self.senaryo_search_box = QLineEdit(placeholderText="Senaryo adı, sonuç veya konumda ara...")
        top_bar.addWidget(self.senaryo_search_box)
        layout.addLayout(top_bar)

        self.all_senaryo_table = QTableView()
        self.all_senaryo_table.setModel(self.scenario_vm.proxy_model)
        self.all_senaryo_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.all_senaryo_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.all_senaryo_table.setSortingEnabled(True)
        self.all_senaryo_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.all_senaryo_table)

        op_btn_layout = QHBoxLayout()
        self.btn_yeni_senaryo = QPushButton("Yeni Senaryo", icon=qta.icon('fa5s.plus-circle'))
        self.btn_duzenle_senaryo = QPushButton("Düzenle", icon=qta.icon('fa5s.edit'))
        self.btn_cogalt_senaryo = QPushButton("Çoğalt", icon=qta.icon('fa5s.copy'))
        self.btn_sil_senaryo = QPushButton("Sil", icon=qta.icon('fa5s.trash-alt', color='red'))

        op_btn_layout.addWidget(self.btn_yeni_senaryo)
        op_btn_layout.addStretch()
        op_btn_layout.addWidget(self.btn_duzenle_senaryo)
        op_btn_layout.addWidget(self.btn_cogalt_senaryo)
        op_btn_layout.addWidget(self.btn_sil_senaryo)
        layout.addLayout(op_btn_layout)

    def _connect_signals(self):
        # Görev Sinyalleri
        self.gorev_search_box.textChanged.connect(self.vm.set_filter)
        self.gorev_table.selectionModel().selectionChanged.connect(self._on_gorev_selection_changed)
        self.btn_yeni_gorev.clicked.connect(self._new_gorev)
        self.btn_kaydet_gorev.clicked.connect(self._save_gorev)
        self.btn_sil_gorev.clicked.connect(self._delete_gorev)
        self.btn_export.clicked.connect(self._export_package)
        self.btn_manage_senaryos.clicked.connect(self._manage_senaryos)

        # Senaryo Sinyalleri
        self.senaryo_search_box.textChanged.connect(self.scenario_vm.set_filter)
        self.all_senaryo_table.selectionModel().selectionChanged.connect(self._on_scenario_selection_changed)
        self.btn_yeni_senaryo.clicked.connect(self._new_scenario)
        self.btn_duzenle_senaryo.clicked.connect(self._edit_scenario)
        self.btn_cogalt_senaryo.clicked.connect(self._duplicate_scenario)
        self.btn_sil_senaryo.clicked.connect(self._delete_scenario)

    # --- GÖREV METOTLARI ---
    def _on_gorev_selection_changed(self, selected, deselected):
        indexes = self.gorev_table.selectionModel().selectedRows()
        if not indexes:
            self._clear_details()
            return
        self.current_gorev = self.vm.get_item_from_proxy_index(indexes[0])
        if self.current_gorev:
            self._populate_details(self.current_gorev)

    def _populate_details(self, gorev):
        self.in_adi.setText(gorev.adi)
        self.in_tarih.setText(gorev.olusturma_tarihi_iso)
        self.in_sorumlu.setText(gorev.sorumlu_personel)
        self.in_aciklama.setPlainText(gorev.aciklama)
        self.vm.update_senaryo_details_for_gorev(gorev)

        self.btn_kaydet_gorev.setEnabled(True)
        self.btn_sil_gorev.setEnabled(True)
        self.btn_export.setEnabled(True)
        self.btn_manage_senaryos.setEnabled(True)

    def _clear_details(self):
        self.gorev_table.clearSelection()
        self.current_gorev = None
        self.in_adi.clear()
        self.in_tarih.clear()
        self.in_sorumlu.clear()
        self.in_aciklama.clear()
        self.vm.update_senaryo_details_for_gorev(None)

        self.btn_kaydet_gorev.setEnabled(False)
        self.btn_sil_gorev.setEnabled(False)
        self.btn_export.setEnabled(False)
        self.btn_manage_senaryos.setEnabled(False)

    def _new_gorev(self):
        self._clear_details()
        self.current_gorev = Gorev()
        self._populate_details(self.current_gorev)
        self.in_adi.setFocus()

    def _save_gorev(self):
        if not self.current_gorev:
            return
        if not self.in_adi.text().strip():
            QMessageBox.warning(self, "Eksik Bilgi", "Görev adı boş olamaz.")
            return

        self.current_gorev.adi = self.in_adi.text().strip()
        self.current_gorev.sorumlu_personel = self.in_sorumlu.text().strip()
        self.current_gorev.aciklama = self.in_aciklama.toPlainText().strip()

        self.vm.save_item(self.current_gorev)
        self.vm.status_updated.emit(f"'{self.current_gorev.adi}' görevi kaydedildi.")

    def _delete_gorev(self):
        if not self.current_gorev: return
        reply = QMessageBox.question(self, "Silme Onayı",
                                     f"'{self.current_gorev.adi}' görevini silmek istediğinizden emin misiniz?")
        if reply == QMessageBox.StandardButton.Yes:
            gorev_adi = self.current_gorev.adi
            self.vm.delete_item(self.current_gorev)
            self._clear_details()
            self.vm.status_updated.emit(f"'{gorev_adi}' görevi silindi.")

    def _export_package(self):
        if not self.current_gorev: return
        path, _ = QFileDialog.getSaveFileName(self, "Görev Paketini Dışa Aktar", f"{self.current_gorev.adi}_paketi.xml",
                                              "XML Paket Dosyaları (*.xml)")
        if path:
            self.vm.export_package(self.current_gorev.gorev_id, path)

    def _manage_senaryos(self):
        if not self.current_gorev: return

        all_senaryos = self.vm.get_available_senaryos()
        pre_selected_ids = self.current_gorev.senaryo_id_list

        dialog = SenaryoSelectionDialog(all_senaryos, pre_selected_ids, self)
        if dialog.exec():
            self.current_gorev.senaryo_id_list = dialog.get_selected_ids()
            self.vm.update_senaryo_details_for_gorev(self.current_gorev)
            QMessageBox.information(self, "Bilgi",
                                    "Senaryo listesi güncellendi. Değişiklikleri kalıcı hale getirmek için 'Görevi Kaydet' butonuna tıklayınız.")

    # --- SENARYO METOTLARI ---
    def _on_scenario_selection_changed(self, selected, deselected):
        indexes = self.all_senaryo_table.selectionModel().selectedRows()
        if not indexes:
            self.current_scenario = None
            self.btn_duzenle_senaryo.setEnabled(False)
            self.btn_cogalt_senaryo.setEnabled(False)
            self.btn_sil_senaryo.setEnabled(False)
            return

        self.current_scenario = self.scenario_vm.get_item_from_proxy_index(indexes[0])
        self.btn_duzenle_senaryo.setEnabled(True)
        self.btn_cogalt_senaryo.setEnabled(True)
        self.btn_sil_senaryo.setEnabled(True)

    def _new_scenario(self):
        self.scenario_entry_dialog.load_scenario(None)
        self.scenario_entry_dialog.exec()

    def _edit_scenario(self):
        if self.current_scenario:
            self.scenario_entry_dialog.load_scenario(self.current_scenario)
            self.scenario_entry_dialog.exec()

    def _duplicate_scenario(self):
        if self.current_scenario:
            self.scenario_vm.duplicate_scenario(self.current_scenario)

    def _delete_scenario(self):
        if not self.current_scenario: return
        reply = QMessageBox.question(self, "Silme Onayı",
                                     f"'{self.current_scenario.adi}' senaryosunu silmek istediğinizden emin misiniz?")
        if reply == QMessageBox.StandardButton.Yes:
            self.scenario_vm.delete_scenario(self.current_scenario)