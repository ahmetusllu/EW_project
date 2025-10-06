# ew_platformasi/ui/views/gorev_center_view.py

import qtawesome as qta
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QGroupBox,
                               QLineEdit, QTableView, QHeaderView, QLabel, QPushButton,
                               QFileDialog, QMessageBox, QListWidget, QFormLayout, QTextEdit,
                               QListWidgetItem, QDialog, QDialogButtonBox)
from viewmodels.gorev_vm import GorevViewModel
from core.data_models import Gorev


class SenaryoSelectionDialog(QDialog):
    """Göreve eklenecek senaryoları seçmek için kullanılan diyalog penceresi."""

    def __init__(self, all_senaryos, pre_selected_ids, parent=None):
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
    def __init__(self, view_model: GorevViewModel, parent=None):
        super().__init__(parent)
        self.vm = view_model
        self.current_gorev = None
        self._build_ui()
        self._connect_signals()
        self._clear_details()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Sol Panel: Görev Listesi
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        self.search_box = QLineEdit(placeholderText="Görev adı veya sorumlu personel ara...")
        self.table = QTableView()
        self.table.setModel(self.vm.proxy_model)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        left_layout.addWidget(self.search_box)
        left_layout.addWidget(self.table)

        # Sağ Panel: Görev Detayları
        right_panel = QGroupBox("Görev Detayları")
        self.right_layout = QVBoxLayout(right_panel)
        self._build_form()

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([700, 500])
        layout.addWidget(splitter)

    def _build_form(self):
        form = QFormLayout()
        self.in_adi = QLineEdit()
        self.in_tarih = QLineEdit(readOnly=True)
        self.in_sorumlu = QLineEdit()
        self.in_aciklama = QTextEdit()
        self.in_aciklama.setFixedHeight(100)
        self.list_senaryolar = QListWidget()

        form.addRow("Görev Adı:", self.in_adi)
        form.addRow("Oluşturma Tarihi:", self.in_tarih)
        form.addRow("Sorumlu Personel:", self.in_sorumlu)
        form.addRow("Açıklama:", self.in_aciklama)

        btn_layout = QHBoxLayout()
        self.btn_manage_senaryos = QPushButton("Senaryoları Yönet", icon=qta.icon('fa5s.tasks'))
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_manage_senaryos)

        self.right_layout.addLayout(form)
        self.right_layout.addWidget(QLabel("<b>Görevin Senaryoları:</b>"))
        self.right_layout.addWidget(self.list_senaryolar)
        self.right_layout.addLayout(btn_layout)
        self.right_layout.addStretch()

        op_btn_layout = QHBoxLayout()
        self.btn_yeni = QPushButton("Yeni Görev", icon=qta.icon('fa5s.plus-circle'))
        self.btn_kaydet = QPushButton("Kaydet", icon=qta.icon('fa5s.save'))
        self.btn_sil = QPushButton("Sil", icon=qta.icon('fa5s.trash-alt', color='red'))
        self.btn_export = QPushButton("Görevi Paketle", icon=qta.icon('fa5s.box-open'))

        op_btn_layout.addWidget(self.btn_yeni)
        op_btn_layout.addStretch()
        op_btn_layout.addWidget(self.btn_kaydet)
        op_btn_layout.addWidget(self.btn_sil)
        op_btn_layout.addWidget(self.btn_export)
        self.right_layout.addLayout(op_btn_layout)

    def _connect_signals(self):
        self.search_box.textChanged.connect(self.vm.set_filter)
        self.table.selectionModel().selectionChanged.connect(self._on_selection_changed)
        self.btn_yeni.clicked.connect(self._new_gorev)
        self.btn_kaydet.clicked.connect(self._save_gorev)
        self.btn_sil.clicked.connect(self._delete_gorev)
        self.btn_export.clicked.connect(self._export_package)
        self.btn_manage_senaryos.clicked.connect(self._manage_senaryos)

    def _on_selection_changed(self, selected, deselected):
        indexes = selected.indexes()
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
        self._update_senaryo_list(gorev)

        self.btn_kaydet.setEnabled(True)
        self.btn_sil.setEnabled(True)
        self.btn_export.setEnabled(True)
        self.btn_manage_senaryos.setEnabled(True)

    def _clear_details(self):
        self.current_gorev = None
        self.in_adi.clear()
        self.in_tarih.clear()
        self.in_sorumlu.clear()
        self.in_aciklama.clear()
        self.list_senaryolar.clear()
        self.in_adi.setFocus()

        self.btn_kaydet.setEnabled(False)
        self.btn_sil.setEnabled(False)
        self.btn_export.setEnabled(False)
        self.btn_manage_senaryos.setEnabled(False)

    def _update_senaryo_list(self, gorev):
        self.list_senaryolar.clear()
        senaryos_in_gorev = self.vm.get_senaryos_for_gorev(gorev)
        for s in senaryos_in_gorev:
            self.list_senaryolar.addItem(f"{s.adi} [{s.sonuc_nitel}]")

    def _new_gorev(self):
        self.table.clearSelection()
        self.current_gorev = Gorev()
        self._populate_details(self.current_gorev)
        self.in_adi.setFocus()

    def _save_gorev(self):
        if not self.current_gorev:
            QMessageBox.warning(self, "Uyarı", "Kaydedilecek bir görev seçili değil.")
            return
        if not self.in_adi.text().strip():
            QMessageBox.warning(self, "Eksik Bilgi", "Görev adı boş olamaz.")
            return

        self.current_gorev.adi = self.in_adi.text().strip()
        self.current_gorev.sorumlu_personel = self.in_sorumlu.text().strip()
        self.current_gorev.aciklama = self.in_aciklama.toPlainText().strip()

        self.vm.save_item(self.current_gorev)
        # Tablo seçimini korumak için, kaydettikten sonra yeniden seçtirme yapılabilir.
        # Şimdilik basit tutuyoruz.

    def _delete_gorev(self):
        if not self.current_gorev: return
        reply = QMessageBox.question(self, "Silme Onayı",
                                     f"'{self.current_gorev.adi}' görevini silmek istediğinizden emin misiniz?")
        if reply == QMessageBox.StandardButton.Yes:
            self.vm.delete_item(self.current_gorev)
            self._clear_details()

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
            self._update_senaryo_list(self.current_gorev)
            QMessageBox.information(self, "Bilgi",
                                    "Senaryo listesi güncellendi. Değişiklikleri kalıcı hale getirmek için 'Kaydet' butonuna tıklayınız.")