# ew_platformasi/ui/views/library_view.py

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QStackedWidget,
                               QTableView, QGroupBox, QLabel, QFormLayout, QLineEdit, QComboBox, QTextEdit,
                               QPushButton, QDoubleSpinBox, QSpinBox, QHeaderView, QMessageBox, QSplitter, QCheckBox,
                               QMenu, QFileDialog, QAbstractItemView)

from ..dialogs.radar_history_dialog import RadarHistoryDialog
from core.data_models import (ETPlatformu, Radar, Teknik, GurultuKaristirmaParams, MenzilAldatmaParams,
                              BaseTeknikParametreleri,
                              AlmacGondermecAyarParametreleri, KaynakUretecAyarParametreleri,
                              FREKANS_BANDLARI, GOREV_TIPLERI, ANTEN_TIPLERI, TEKNIK_KATEGORILERI, DARBE_MODULASYONLARI)
from viewmodels.library_vm import LibraryViewModel
from typing import List


class TeknikFormWidget(QWidget):
    def __init__(self, is_dialog=False, parent=None):
        super().__init__(parent)
        self.is_dialog = is_dialog
        self.platforms: List[ETPlatformu] = []
        self._build_teknik_form()

    def _build_teknik_form(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        form_group = QGroupBox("Teknik Detayları")
        layout.addWidget(form_group)

        form = QFormLayout(form_group)
        self.teknik_in_platform = QComboBox()
        self.teknik_in_adi = QLineEdit()
        self.teknik_in_kategori = QComboBox()
        self.teknik_in_kategori.addItems(TEKNIK_KATEGORILERI)
        self.teknik_in_aciklama = QTextEdit()
        self.teknik_in_aciklama.setFixedHeight(120)

        form.addRow("İlişkili Platform:", self.teknik_in_platform)
        form.addRow("Adı:", self.teknik_in_adi)
        form.addRow("Kategori:", self.teknik_in_kategori)
        form.addRow("Açıklama:", self.teknik_in_aciklama)

        param_group = QGroupBox("Tekniğe Özel Parametreler")
        param_layout = QVBoxLayout(param_group)
        self.teknik_params_stack = QStackedWidget()
        self._create_gurultu_params_form()
        self._create_menzil_params_form()
        self._create_ag_params_form()
        self._create_ku_params_form()
        self._create_base_params_form()  # Diğer kategoriler için boş form
        param_layout.addWidget(self.teknik_params_stack)
        layout.addWidget(param_group)

        if not self.is_dialog:
            layout.addStretch()

        self.teknik_in_kategori.currentIndexChanged.connect(self._on_teknik_kategori_changed)

    def _create_gurultu_params_form(self):
        widget = QWidget()
        form = QFormLayout(widget)
        self.p_gurultu_tur = QComboBox()
        self.p_gurultu_tur.addItems(["Barrage", "Spot", "Swept", "DRFM Noise"])
        self.p_gurultu_bant = QDoubleSpinBox(suffix=" MHz", maximum=100000, decimals=1)
        self.p_gurultu_guc = QDoubleSpinBox(suffix=" dBW", minimum=-100, maximum=100, decimals=1)
        form.addRow("Tür:", self.p_gurultu_tur)
        form.addRow("Bant Genişliği:", self.p_gurultu_bant)
        form.addRow("Güç (ERP):", self.p_gurultu_guc)
        self.teknik_params_stack.addWidget(widget)

    def _create_menzil_params_form(self):
        widget = QWidget()
        form = QFormLayout(widget)
        self.p_menzil_tip = QComboBox()
        self.p_menzil_tip.addItems(["RGPO", "RGPI"])
        self.p_menzil_hiz = QDoubleSpinBox(suffix=" m/s", maximum=10000, decimals=1)
        self.p_menzil_sayi = QSpinBox(maximum=100)
        form.addRow("Teknik Tipi:", self.p_menzil_tip)
        form.addRow("Çekme Hızı:", self.p_menzil_hiz)
        form.addRow("Sahte Hedef Sayısı:", self.p_menzil_sayi)
        self.teknik_params_stack.addWidget(widget)

    def _create_ag_params_form(self):
        widget = QWidget()
        form = QFormLayout(widget)
        self.p_ag_ornek_freq = QDoubleSpinBox(suffix=" GHz", maximum=100, decimals=2)
        self.p_ag_rf_kazanc = QDoubleSpinBox(suffix=" dB", minimum=-20, maximum=80, decimals=1)
        self.p_ag_if_kazanc = QDoubleSpinBox(suffix=" dB", minimum=-20, maximum=80, decimals=1)
        self.p_ag_faz_kaydirma = QDoubleSpinBox(suffix=" °", maximum=360, decimals=1)
        self.p_ag_agc_aktif = QCheckBox("Aktif")
        self.p_ag_gonderici_guc = QDoubleSpinBox(suffix=" dBm", minimum=-50, maximum=50, decimals=1)
        self.p_ag_mod_tipi = QComboBox()
        self.p_ag_mod_tipi.addItems(["BPSK", "QPSK", "16-QAM", "64-QAM"])
        self.p_ag_veri_hizi = QDoubleSpinBox(suffix=" Mbps", maximum=1000, decimals=1)
        form.addRow("Ön Örnekleme Frekansı:", self.p_ag_ornek_freq)
        form.addRow("RF Kazancı:", self.p_ag_rf_kazanc)
        form.addRow("IF Kazancı:", self.p_ag_if_kazanc)
        form.addRow("Faz Kaydırma:", self.p_ag_faz_kaydirma)
        form.addRow("Otomatik Kazanç Kontrolü:", self.p_ag_agc_aktif)
        form.addRow("Gönderici Gücü:", self.p_ag_gonderici_guc)
        form.addRow("Modülasyon Tipi:", self.p_ag_mod_tipi)
        form.addRow("Veri Hızı:", self.p_ag_veri_hizi)
        self.teknik_params_stack.addWidget(widget)

    def _create_ku_params_form(self):
        widget = QWidget()
        form = QFormLayout(widget)
        self.p_ku_dalga_formu = QComboBox()
        self.p_ku_dalga_formu.addItems(["Sinus", "Kare", "Testere Dişi", "Darbe"])
        self.p_ku_bas_freq = QDoubleSpinBox(suffix=" MHz", maximum=100000, decimals=2)
        self.p_ku_bit_freq = QDoubleSpinBox(suffix=" MHz", maximum=100000, decimals=2)
        self.p_ku_tarama_sure = QDoubleSpinBox(suffix=" ms", maximum=10000, decimals=2)
        self.p_ku_darbe_gen = QDoubleSpinBox(suffix=" µs", maximum=1000, decimals=2)
        self.p_ku_dta = QDoubleSpinBox(suffix=" µs", maximum=10000, decimals=2)
        self.p_ku_faz_gurultu = QDoubleSpinBox(suffix=" dBc/Hz", minimum=-200, maximum=0, decimals=1)
        self.p_ku_harmonik = QDoubleSpinBox(suffix=" dB", minimum=-100, maximum=0, decimals=1)
        form.addRow("Dalga Formu Tipi:", self.p_ku_dalga_formu)
        form.addRow("Başlangıç Frekansı:", self.p_ku_bas_freq)
        form.addRow("Bitiş Frekansı:", self.p_ku_bit_freq)
        form.addRow("Tarama Süresi:", self.p_ku_tarama_sure)
        form.addRow("Darbe Genişliği:", self.p_ku_darbe_gen)
        form.addRow("Darbe Tekrarlama Aralığı:", self.p_ku_dta)
        form.addRow("Faz Gürültüsü:", self.p_ku_faz_gurultu)
        form.addRow("Harmonik Baskı:", self.p_ku_harmonik)
        self.teknik_params_stack.addWidget(widget)

    def _create_base_params_form(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Bu kategori için özel parametre bulunmamaktadır."), 0, Qt.AlignmentFlag.AlignCenter)
        self.teknik_params_stack.addWidget(widget)

    def _on_teknik_kategori_changed(self, index):
        kategori_map = {
            "Gürültü Karıştırma": 0, "Menzil Aldatma": 1,
            "Alıcı/Gönderici Ayarları": 2, "Kaynak Üreteç Ayarları": 3
        }
        kategori_text = self.teknik_in_kategori.itemText(index)
        # Eşleşme yoksa sonuncu (boş) widget'ı göster
        self.teknik_params_stack.setCurrentIndex(kategori_map.get(kategori_text, 4))

    def update_platform_list(self, platforms: List[ETPlatformu]):
        self.platforms = platforms
        current_selection = self.teknik_in_platform.currentData()
        self.teknik_in_platform.clear()
        self.teknik_in_platform.addItem("— Seçiniz —", userData=None)
        for p in sorted(platforms, key=lambda x: x.adi):
            self.teknik_in_platform.addItem(p.adi, userData=p.platform_id)

        new_index = self.teknik_in_platform.findData(current_selection)
        if new_index != -1:
            self.teknik_in_platform.setCurrentIndex(new_index)

    def populate_form(self, teknik: Teknik):
        platform_index = self.teknik_in_platform.findData(teknik.platform_id)
        self.teknik_in_platform.setCurrentIndex(platform_index if platform_index != -1 else 0)
        self.teknik_in_adi.setText(teknik.adi)
        self.teknik_in_kategori.setCurrentText(teknik.kategori)
        self.teknik_in_aciklama.setText(teknik.aciklama)
        params = teknik.parametreler
        if isinstance(params, GurultuKaristirmaParams):
            self.p_gurultu_tur.setCurrentText(params.tur)
            self.p_gurultu_bant.setValue(params.bant_genisligi_mhz or 0)
            self.p_gurultu_guc.setValue(params.guc_erp_dbw or 0)
        elif isinstance(params, MenzilAldatmaParams):
            self.p_menzil_tip.setCurrentText(params.teknik_tipi)
            self.p_menzil_hiz.setValue(params.cekme_hizi_mps or 0)
            self.p_menzil_sayi.setValue(params.sahte_hedef_sayisi or 0)
        elif isinstance(params, AlmacGondermecAyarParametreleri):
            self.p_ag_ornek_freq.setValue(params.on_ornekleme_frekansi_ghz or 0)
            self.p_ag_rf_kazanc.setValue(params.rf_kazanc_db or 0)
            self.p_ag_if_kazanc.setValue(params.if_kazanc_db or 0)
            self.p_ag_faz_kaydirma.setValue(params.faz_kaydirma_derece or 0)
            self.p_ag_agc_aktif.setChecked(params.otomatik_kazanc_kontrolu_aktif or False)
            self.p_ag_gonderici_guc.setValue(params.gonderici_guc_dbm or 0)
            self.p_ag_mod_tipi.setCurrentText(params.modulasyon_tipi or "QPSK")
            self.p_ag_veri_hizi.setValue(params.veri_hizi_mbps or 0)
        elif isinstance(params, KaynakUretecAyarParametreleri):
            self.p_ku_dalga_formu.setCurrentText(params.dalga_formu_tipi or "Sinus")
            self.p_ku_bas_freq.setValue(params.baslangic_frekansi_mhz or 0)
            self.p_ku_bit_freq.setValue(params.bitis_frekansi_mhz or 0)
            self.p_ku_tarama_sure.setValue(params.tarama_suresi_ms or 0)
            self.p_ku_darbe_gen.setValue(params.darbe_genisligi_us or 0)
            self.p_ku_dta.setValue(params.darbe_tekrarlama_araligi_us or 0)
            self.p_ku_faz_gurultu.setValue(params.faz_gurultusu_dbc_hz or 0)
            self.p_ku_harmonik.setValue(params.harmonik_baski_db or 0)

    def get_data_from_form(self) -> Teknik:
        teknik = Teknik()
        teknik.platform_id = self.teknik_in_platform.currentData()
        teknik.adi = self.teknik_in_adi.text()
        teknik.kategori = self.teknik_in_kategori.currentText()
        teknik.aciklama = self.teknik_in_aciklama.toPlainText()
        kategori = teknik.kategori
        if kategori == "Gürültü Karıştırma":
            teknik.parametreler = GurultuKaristirmaParams(tur=self.p_gurultu_tur.currentText(),
                                                          bant_genisligi_mhz=self.p_gurultu_bant.value() or None,
                                                          guc_erp_dbw=self.p_gurultu_guc.value() or None)
        elif kategori == "Menzil Aldatma":
            teknik.parametreler = MenzilAldatmaParams(teknik_tipi=self.p_menzil_tip.currentText(),
                                                      cekme_hizi_mps=self.p_menzil_hiz.value() or None,
                                                      sahte_hedef_sayisi=self.p_menzil_sayi.value() or None)
        elif kategori == "Alıcı/Gönderici Ayarları":
            teknik.parametreler = AlmacGondermecAyarParametreleri(
                on_ornekleme_frekansi_ghz=self.p_ag_ornek_freq.value() or None,
                rf_kazanc_db=self.p_ag_rf_kazanc.value() or None, if_kazanc_db=self.p_ag_if_kazanc.value() or None,
                faz_kaydirma_derece=self.p_ag_faz_kaydirma.value() or None,
                otomatik_kazanc_kontrolu_aktif=self.p_ag_agc_aktif.isChecked(),
                gonderici_guc_dbm=self.p_ag_gonderici_guc.value() or None,
                modulasyon_tipi=self.p_ag_mod_tipi.currentText(), veri_hizi_mbps=self.p_ag_veri_hizi.value() or None)
        elif kategori == "Kaynak Üreteç Ayarları":
            teknik.parametreler = KaynakUretecAyarParametreleri(dalga_formu_tipi=self.p_ku_dalga_formu.currentText(),
                                                                baslangic_frekansi_mhz=self.p_ku_bas_freq.value() or None,
                                                                bitis_frekansi_mhz=self.p_ku_bit_freq.value() or None,
                                                                tarama_suresi_ms=self.p_ku_tarama_sure.value() or None,
                                                                darbe_genisligi_us=self.p_ku_darbe_gen.value() or None,
                                                                darbe_tekrarlama_araligi_us=self.p_ku_dta.value() or None,
                                                                faz_gurultusu_dbc_hz=self.p_ku_faz_gurultu.value() or None,
                                                                harmonik_baski_db=self.p_ku_harmonik.value() or None)
        else:
            teknik.parametreler = BaseTeknikParametreleri()
        return teknik


class LibraryView(QWidget):
    def __init__(self, view_model: LibraryViewModel, parent=None):
        super().__init__(parent)
        self.vm = view_model
        self.current_item = None
        self._build_ui()
        self._connect_signals()
        self._update_button_states()

    def _build_ui(self):
        main_layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.category_list = QListWidget()
        self.category_list.setFixedWidth(200)
        self.category_list.addItem(QListWidgetItem(qta.icon('fa5s.fighter-jet', color='orange'), "ET Platformları"))
        self.category_list.addItem(QListWidgetItem(qta.icon('fa5s.broadcast-tower', color='lightblue'), "Radarlar"))
        self.category_list.addItem(QListWidgetItem(qta.icon('fa5s.wave-square', color='lightgreen'), "EH Teknikleri"))

        middle_panel = self._create_middle_panel()
        self.form_stack = self._create_right_panel()

        splitter.addWidget(self.category_list)
        splitter.addWidget(middle_panel)
        splitter.addWidget(self.form_stack)
        splitter.setSizes([200, 600, 500])
        main_layout.addWidget(splitter)

        self.category_list.setCurrentRow(0)

    def _create_middle_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        top_bar_layout = QHBoxLayout()
        self.search_box = QLineEdit(placeholderText="Listede ara...")

        self.btn_yeni = QPushButton("Yeni Ekle", icon=qta.icon('fa5s.plus-circle'))
        self.btn_import = QPushButton("İçeri Aktar", icon=qta.icon('fa5s.file-import'))
        self.btn_export = QPushButton("Dışarı Aktar", icon=qta.icon('fa5s.file-export'))

        top_bar_layout.addWidget(self.search_box)
        top_bar_layout.addWidget(self.btn_yeni)
        top_bar_layout.addWidget(self.btn_import)
        top_bar_layout.addWidget(self.btn_export)

        self.table_stack = QStackedWidget()
        platformlar_table = QTableView()
        platformlar_table.setModel(self.vm.platformlar_proxy_model)
        radars_table = QTableView()
        radars_table.setModel(self.vm.radars_proxy_model)
        radars_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        teknikler_table = QTableView()
        teknikler_table.setModel(self.vm.teknikler_proxy_model)

        for table in [platformlar_table, radars_table, teknikler_table]:
            table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
            table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
            table.setSortingEnabled(True)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.table_stack.addWidget(table)

        layout.addLayout(top_bar_layout)
        layout.addWidget(self.table_stack)
        return panel

    def _create_right_panel(self):
        stack = QStackedWidget()
        self.placeholder_form = QWidget()
        placeholder_layout = QVBoxLayout(self.placeholder_form)
        placeholder_layout.addStretch()
        placeholder_layout.addWidget(QLabel("İşlem yapmak için bir kayıt seçin veya 'Yeni Ekle' butonunu kullanın."), 0,
                                     Qt.AlignmentFlag.AlignCenter)
        placeholder_layout.addStretch()
        stack.addWidget(self.placeholder_form)
        stack.addWidget(self._create_platform_form())
        stack.addWidget(self._create_radar_form())
        stack.addWidget(self._create_teknik_panel())
        return stack

    def _connect_signals(self):
        self.category_list.currentRowChanged.connect(self._on_category_changed)
        self.search_box.textChanged.connect(self._on_search_changed)
        self.btn_yeni.clicked.connect(self._on_new_item_clicked)
        self.btn_import.clicked.connect(self._import_teknikler)
        self.btn_export.clicked.connect(self._export_teknikler)

        self.platformlar_table().selectionModel().selectionChanged.connect(
            lambda s, d: self._on_item_selected(s, d, self.vm.platformlar_proxy_model))
        self.radars_table().customContextMenuRequested.connect(self._show_radar_context_menu)
        self.radars_table().selectionModel().selectionChanged.connect(
            lambda s, d: self._on_item_selected(s, d, self.vm.radars_proxy_model))
        self.teknikler_table().selectionModel().selectionChanged.connect(
            lambda s, d: self._on_item_selected(s, d, self.vm.teknikler_proxy_model))
        self.teknikler_table().selectionModel().selectionChanged.connect(self._update_button_states)

        self.platform_btn_kaydet.clicked.connect(self._save_platform)
        self.platform_btn_sil.clicked.connect(self._delete_current_item)
        self.platform_btn_cogalt.clicked.connect(self._duplicate_current_item)

        self.radar_btn_kaydet.clicked.connect(self._save_radar)
        self.radar_btn_sil.clicked.connect(self._delete_current_item)
        self.radar_btn_cogalt.clicked.connect(self._duplicate_current_item)
        self.radar_in_prf.editingFinished.connect(self._update_pri_from_prf)
        self.radar_in_pri.editingFinished.connect(self._update_prf_from_pri)

        self.teknik_btn_kaydet.clicked.connect(self._save_teknik)
        self.teknik_btn_sil.clicked.connect(self._delete_current_item)
        self.teknik_btn_cogalt.clicked.connect(self._duplicate_current_item)

    def _import_teknikler(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Teknik XML Dosyalarını İçe Aktar", "", "XML Dosyaları (*.xml)")
        if paths:
            self.vm.import_teknikler(paths)

    def _export_teknikler(self):
        selected_indexes = self.teknikler_table().selectionModel().selectedRows()
        if not selected_indexes:
            QMessageBox.warning(self, "Seçim Yapılmadı", "Dışa aktarmak için listeden en az bir teknik seçin.")
            return

        teknik_ids = [self.vm.get_item_from_proxy_index(index, self.vm.teknikler_proxy_model).teknik_id
                      for index in selected_indexes]

        path, _ = QFileDialog.getSaveFileName(
            self, "Seçili Teknikleri Dışa Aktar", "EKT_Paketi.xml", "XML Dosyaları (*.xml)")
        if path:
            self.vm.export_teknikler(teknik_ids, path)

    def _update_button_states(self):
        is_teknik_category = self.category_list.currentRow() == 2
        self.btn_import.setVisible(is_teknik_category)
        self.btn_export.setVisible(is_teknik_category)
        if is_teknik_category:
            self.btn_export.setEnabled(self.teknikler_table().selectionModel().hasSelection())

    def platformlar_table(self):
        return self.table_stack.widget(0)

    def radars_table(self):
        return self.table_stack.widget(1)

    def teknikler_table(self):
        return self.table_stack.widget(2)

    def _on_category_changed(self, index):
        self.table_stack.setCurrentIndex(index)
        self.search_box.clear()
        self._clear_forms_and_selection()
        self._update_button_states()

    def _on_search_changed(self, text):
        current_row = self.category_list.currentRow()
        if current_row == 0:
            self.vm.set_filter(text, "platform")
        elif current_row == 1:
            self.vm.set_filter(text, "radar")
        else:
            self.vm.set_filter(text, "teknik")

    def _on_item_selected(self, selected, deselected, proxy_model):
        table_map = {
            self.vm.platformlar_proxy_model: self.platformlar_table(),
            self.vm.radars_proxy_model: self.radars_table(),
            self.vm.teknikler_proxy_model: self.teknikler_table(),
        }
        table_view = table_map.get(proxy_model)
        if not table_view: return

        selected_indexes = table_view.selectionModel().selectedRows()
        if len(selected_indexes) == 1:
            self.current_item = self.vm.get_item_from_proxy_index(selected_indexes[0], proxy_model)
            if isinstance(self.current_item, ETPlatformu):
                self.form_stack.setCurrentWidget(self.platform_form)
                self._populate_platform_form(self.current_item)
            elif isinstance(self.current_item, Radar):
                self.form_stack.setCurrentWidget(self.radar_form)
                self._populate_radar_form(self.current_item)
            elif isinstance(self.current_item, Teknik):
                self.form_stack.setCurrentWidget(self.teknik_panel)
                self._populate_teknik_form(self.current_item)
        else:
            self._clear_forms_and_selection(clear_table_selection=False)

    def _on_new_item_clicked(self):
        current_row = self.category_list.currentRow()
        if current_row == 0:
            self.platformlar_table().clearSelection()
            self.current_item = ETPlatformu()
            self.form_stack.setCurrentWidget(self.platform_form)
            self._populate_platform_form(self.current_item)
        elif current_row == 1:
            self.radars_table().clearSelection()
            self.current_item = Radar()
            self.form_stack.setCurrentWidget(self.radar_form)
            self._populate_radar_form(self.current_item)
        else:
            self.teknikler_table().clearSelection()
            self.current_item = Teknik()
            self.form_stack.setCurrentWidget(self.teknik_panel)
            self._populate_teknik_form(self.current_item)

    def _delete_current_item(self):
        if self.current_item:
            reply = QMessageBox.question(self, "Silme Onayı",
                                         f"'{self.current_item.adi}' kaydını silmek istediğinizden emin misiniz?")
            if reply == QMessageBox.StandardButton.Yes:
                self.vm.delete_item(self.current_item)
                self._clear_forms_and_selection()

    def _duplicate_current_item(self):
        if self.current_item: self.vm.duplicate_item(self.current_item)

    def _clear_forms_and_selection(self, clear_table_selection=True):
        self.current_item = None
        if clear_table_selection:
            self.platformlar_table().clearSelection()
            self.radars_table().clearSelection()
            self.teknikler_table().clearSelection()
        self.form_stack.setCurrentWidget(self.placeholder_form)
        self._populate_platform_form(ETPlatformu())
        self._populate_radar_form(Radar())
        self._populate_teknik_form(Teknik())

    def _show_radar_context_menu(self, position):
        indexes = self.radars_table().selectionModel().selectedRows()
        if not indexes: return
        menu = QMenu()
        history_action = menu.addAction(qta.icon('fa5s.history'), "Faaliyet Geçmişini Göster")
        action = menu.exec(self.radars_table().viewport().mapToGlobal(position))
        if action == history_action:
            proxy_index = indexes[0]
            radar_item = self.vm.get_item_from_proxy_index(proxy_index, self.vm.radars_proxy_model)
            if radar_item:
                self._show_radar_history(radar_item)

    def _show_radar_history(self, radar):
        related_senaryos = self.vm.get_senaryos_for_radar(radar.radar_id)
        if not related_senaryos:
            QMessageBox.information(self, "Bilgi", f"'{radar.adi}' radarına karşı kaydedilmiş bir faaliyet bulunamadı.")
            return
        dialog = RadarHistoryDialog(radar.adi, related_senaryos, self)
        dialog.exec()

    def _create_form_buttons(self):
        kaydet = QPushButton("Kaydet", icon=qta.icon('fa5s.save'))
        cogalt = QPushButton("Çoğalt", icon=qta.icon('fa5s.copy'))
        sil = QPushButton("Sil", icon=qta.icon('fa5s.trash-alt', color='red'))
        layout = QHBoxLayout()
        layout.addStretch()
        layout.addWidget(kaydet)
        layout.addWidget(cogalt)
        layout.addWidget(sil)
        return kaydet, cogalt, sil, layout

    def _create_platform_form(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        form_group = QGroupBox("Platform Detayları")
        layout.addWidget(form_group)
        form = QFormLayout(form_group)
        self.platform_in_adi = QLineEdit()
        self.platform_in_aciklama = QTextEdit(fixedHeight=120)
        form.addRow("Platform Adı:", self.platform_in_adi)
        form.addRow("Açıklama:", self.platform_in_aciklama)
        layout.addStretch()
        self.platform_btn_kaydet, self.platform_btn_cogalt, self.platform_btn_sil, btn_layout = self._create_form_buttons()
        layout.addLayout(btn_layout)
        self.platform_form = panel
        return panel

    def _populate_platform_form(self, platform: ETPlatformu):
        is_new = not self.vm.item_exists(platform.platform_id, ETPlatformu)
        self.platform_btn_cogalt.setEnabled(not is_new)
        self.platform_btn_sil.setEnabled(not is_new)
        self.platform_in_adi.setText(platform.adi)
        self.platform_in_aciklama.setPlainText(platform.aciklama)

    def _save_platform(self):
        if not (self.current_item and isinstance(self.current_item, ETPlatformu)): return
        if not self.platform_in_adi.text().strip():
            QMessageBox.warning(self, "Eksik Bilgi", "Platform adı boş olamaz.")
            return
        self.current_item.adi = self.platform_in_adi.text().strip()
        self.current_item.aciklama = self.platform_in_aciklama.toPlainText().strip()
        self.vm.save_item(self.current_item)
        QMessageBox.information(self, "Başarılı", f"'{self.current_item.adi}' platformu güncellendi.")

    def _create_radar_form(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        form_group = QGroupBox("Radar Detayları")
        layout.addWidget(form_group)
        form = QFormLayout(form_group)
        self.radar_in_adi = QLineEdit()
        self.radar_in_elnot = QLineEdit()
        self.radar_in_uretici = QLineEdit()
        self.radar_in_bant = QComboBox();
        self.radar_in_bant.addItems(FREKANS_BANDLARI)
        self.radar_in_gorev = QComboBox();
        self.radar_in_gorev.addItems(GOREV_TIPLERI)
        self.radar_in_anten = QComboBox();
        self.radar_in_anten.addItems(ANTEN_TIPLERI)
        form.addRow("Adı:", self.radar_in_adi)
        form.addRow("ELNOT:", self.radar_in_elnot)
        form.addRow("Üretici:", self.radar_in_uretici)
        form.addRow("Frekans Bandı:", self.radar_in_bant)
        form.addRow("Görev Tipi:", self.radar_in_gorev)
        form.addRow("Anten Tipi:", self.radar_in_anten)
        params_group = QGroupBox("Teknik Parametreler")
        params_layout = QFormLayout(params_group)
        double_validator = QDoubleValidator();
        double_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.radar_in_erp = QLineEdit(validator=double_validator, placeholderText="dBW")
        self.radar_in_pw = QLineEdit(validator=double_validator, placeholderText="µs")
        self.radar_in_prf = QLineEdit(validator=double_validator, placeholderText="Hz")
        self.radar_in_pri = QLineEdit(validator=double_validator, placeholderText="µs")
        self.radar_in_modulasyon = QComboBox();
        self.radar_in_modulasyon.addItems(DARBE_MODULASYONLARI)
        self.radar_in_entegrasyon = QLineEdit(placeholderText="Örn: 10-pulse coherent")
        params_layout.addRow("ERP (Efektif Yayılan Güç):", self.radar_in_erp)
        params_layout.addRow("PW (Darbe Genişliği):", self.radar_in_pw)
        params_layout.addRow("PRF (Darbe Tekrarlama Frek.):", self.radar_in_prf)
        params_layout.addRow("PRI (Darbe Tekrarlama Aralığı):", self.radar_in_pri)
        params_layout.addRow("Darbe Modülasyonu:", self.radar_in_modulasyon)
        params_layout.addRow("Darbe Entegrasyonu:", self.radar_in_entegrasyon)
        form.addRow(params_group)
        self.radar_in_not = QTextEdit(fixedHeight=80)
        form.addRow("Notlar:", self.radar_in_not)
        layout.addStretch()
        self.radar_btn_kaydet, self.radar_btn_cogalt, self.radar_btn_sil, btn_layout = self._create_form_buttons()
        layout.addLayout(btn_layout)
        self.radar_form = panel
        return panel

    def _populate_radar_form(self, radar: Radar):
        is_new = not self.vm.item_exists(radar.radar_id, Radar)
        self.radar_btn_cogalt.setEnabled(not is_new)
        self.radar_btn_sil.setEnabled(not is_new)
        self.radar_in_adi.setText(radar.adi)
        self.radar_in_elnot.setText(radar.elnot)
        self.radar_in_uretici.setText(radar.uretici)
        self.radar_in_bant.setCurrentText(radar.frekans_bandi)
        self.radar_in_gorev.setCurrentText(radar.gorev_tipi)
        self.radar_in_anten.setCurrentText(radar.anten_tipi)
        self.radar_in_not.setPlainText(radar.notlar)
        self.radar_in_erp.setText(str(radar.erp_dbw) if radar.erp_dbw is not None else "")
        self.radar_in_pw.setText(str(radar.pw_us) if radar.pw_us is not None else "")
        self.radar_in_prf.setText(str(radar.prf_hz) if radar.prf_hz is not None else "")
        self.radar_in_pri.setText(str(radar.pri_us) if radar.pri_us is not None else "")
        self.radar_in_modulasyon.setCurrentText(radar.darbe_modulasyonu or DARBE_MODULASYONLARI[0])
        self.radar_in_entegrasyon.setText(radar.darbe_entegrasyonu or "")

    def _save_radar(self):
        if not (self.current_item and isinstance(self.current_item, Radar)): return
        if not self.radar_in_adi.text().strip():
            QMessageBox.warning(self, "Eksik Bilgi", "Radar adı boş olamaz.")
            return

        def get_float(widget: QLineEdit):
            text = widget.text().strip().replace(',', '.')
            return float(text) if text else None

        self.current_item.adi = self.radar_in_adi.text().strip()
        self.current_item.elnot = self.radar_in_elnot.text().strip()
        self.current_item.uretici = self.radar_in_uretici.text().strip()
        self.current_item.frekans_bandi = self.radar_in_bant.currentText()
        self.current_item.gorev_tipi = self.radar_in_gorev.currentText()
        self.current_item.anten_tipi = self.radar_in_anten.currentText()
        self.current_item.notlar = self.radar_in_not.toPlainText().strip()
        self.current_item.erp_dbw = get_float(self.radar_in_erp)
        self.current_item.pw_us = get_float(self.radar_in_pw)
        self.current_item.prf_hz = get_float(self.radar_in_prf)
        self.current_item.pri_us = get_float(self.radar_in_pri)
        self.current_item.darbe_modulasyonu = self.radar_in_modulasyon.currentText()
        self.current_item.darbe_entegrasyonu = self.radar_in_entegrasyon.text().strip()
        self.vm.save_item(self.current_item)
        QMessageBox.information(self, "Başarılı", f"'{self.current_item.adi}' radarı güncellendi.")

    def _update_pri_from_prf(self):
        try:
            prf_hz = float(self.radar_in_prf.text().replace(',', '.'))
            if prf_hz > 0: self.radar_in_pri.setText(f"{(1 / prf_hz) * 1_000_000:.4f}")
        except (ValueError, ZeroDivisionError):
            pass

    def _update_prf_from_pri(self):
        try:
            pri_us = float(self.radar_in_pri.text().replace(',', '.'))
            if pri_us > 0: self.radar_in_prf.setText(f"{1 / (pri_us / 1_000_000):.2f}")
        except (ValueError, ZeroDivisionError):
            pass

    def _create_teknik_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        self.teknik_form_widget = TeknikFormWidget()
        layout.addWidget(self.teknik_form_widget)
        self.teknik_btn_kaydet, self.teknik_btn_cogalt, self.teknik_btn_sil, btn_layout = self._create_form_buttons()
        layout.addLayout(btn_layout)
        self.teknik_panel = panel
        return panel

    def _populate_teknik_form(self, teknik: Teknik):
        platforms = self.vm.get_all_platforms()
        self.teknik_form_widget.update_platform_list(platforms)
        self.teknik_form_widget.populate_form(teknik)
        is_new = not self.vm.item_exists(teknik.teknik_id, Teknik)
        self.teknik_btn_cogalt.setEnabled(not is_new)
        self.teknik_btn_sil.setEnabled(not is_new)

    def _save_teknik(self):
        if not (self.current_item and isinstance(self.current_item, Teknik)): return
        try:
            updated_teknik = self.teknik_form_widget.get_data_from_form()
            if not updated_teknik.adi:
                QMessageBox.warning(self, "Eksik Bilgi", "Teknik adı boş olamaz.")
                return
            if not updated_teknik.platform_id:
                QMessageBox.warning(self, "Eksik Bilgi", "Lütfen teknik için bir platform seçin.")
                return

            updated_teknik.teknik_id = self.current_item.teknik_id
            self.current_item = updated_teknik
            self.vm.save_item(self.current_item)
            QMessageBox.information(self, "Başarılı", f"'{self.current_item.adi}' tekniği kaydedildi.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Teknik kaydedilirken bir hata oluştu: {e}")