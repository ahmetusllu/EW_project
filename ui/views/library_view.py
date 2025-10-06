# ew_platformasi/ui/views/library_view.py

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QStackedWidget,
                               QTableView, QGroupBox, QLabel, QFormLayout, QLineEdit, QComboBox, QTextEdit,
                               QPushButton, QDoubleSpinBox, QSpinBox, QHeaderView, QMessageBox, QSplitter, QCheckBox)

from core.data_models import (Radar, Teknik, GurultuKaristirmaParams, MenzilAldatmaParams, BaseTeknikParametreleri,
                              AlmacGondermecAyarParametreleri, KaynakUretecAyarParametreleri,
                              FREKANS_BANDLARI, GOREV_TIPLERI, ANTEN_TIPLERI, TEKNIK_KATEGORILERI)
from viewmodels.library_vm import LibraryViewModel

class LibraryView(QWidget):
    def __init__(self, view_model: LibraryViewModel, parent=None):
        super().__init__(parent)
        self.vm = view_model
        self.current_item = None
        self._build_ui()
        self._connect_signals()
        self.category_list.setCurrentRow(0)

    def _build_ui(self):
        main_layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.category_list = QListWidget()
        self.category_list.setFixedWidth(200)
        self.category_list.addItem(QListWidgetItem(qta.icon('fa5s.broadcast-tower', color='lightblue'), "Radarlar"))
        self.category_list.addItem(QListWidgetItem(qta.icon('fa5s.wave-square', color='lightgreen'), "EH Teknikleri"))
        middle_panel = self._create_middle_panel()
        self.form_stack = self._create_right_panel()
        splitter.addWidget(self.category_list)
        splitter.addWidget(middle_panel)
        splitter.addWidget(self.form_stack)
        splitter.setSizes([200, 500, 500])
        main_layout.addWidget(splitter)

    def _create_middle_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        top_bar_layout = QHBoxLayout()
        self.search_box = QLineEdit(placeholderText="Listede ara...")
        self.btn_yeni = QPushButton("Yeni Ekle", icon=qta.icon('fa5s.plus-circle'))
        top_bar_layout.addWidget(self.search_box)
        top_bar_layout.addWidget(self.btn_yeni)
        self.table_stack = QStackedWidget()
        for model in [self.vm.radars_proxy_model, self.vm.teknikler_proxy_model]:
            table = QTableView()
            table.setModel(model)
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
        placeholder_layout.addWidget(QLabel("İşlem yapmak için bir kayıt seçin veya 'Yeni Ekle' butonunu kullanın."), 0, Qt.AlignmentFlag.AlignCenter)
        placeholder_layout.addStretch()
        stack.addWidget(self.placeholder_form)
        stack.addWidget(self._create_radar_form())
        stack.addWidget(self._create_teknik_form())
        return stack

    def _connect_signals(self):
        self.category_list.currentRowChanged.connect(self._on_category_changed)
        self.search_box.textChanged.connect(self._on_search_changed)
        self.btn_yeni.clicked.connect(self._on_new_item_clicked)
        self.radars_table().selectionModel().selectionChanged.connect(lambda s, d: self._on_item_selected(s, d, self.vm.radars_proxy_model))
        self.teknikler_table().selectionModel().selectionChanged.connect(lambda s, d: self._on_item_selected(s, d, self.vm.teknikler_proxy_model))
        self.radar_btn_kaydet.clicked.connect(self._save_radar)
        self.radar_btn_sil.clicked.connect(self._delete_current_item)
        self.radar_btn_cogalt.clicked.connect(self._duplicate_current_item)
        self.teknik_btn_kaydet.clicked.connect(self._save_teknik)
        self.teknik_btn_sil.clicked.connect(self._delete_current_item)
        self.teknik_btn_cogalt.clicked.connect(self._duplicate_current_item)
        self.teknik_in_kategori.currentIndexChanged.connect(self._on_teknik_kategori_changed)

    def radars_table(self): return self.table_stack.widget(0)
    def teknikler_table(self): return self.table_stack.widget(1)

    def _on_category_changed(self, index):
        self.table_stack.setCurrentIndex(index)
        self.search_box.clear()
        self._clear_forms_and_selection()

    def _on_search_changed(self, text):
        if self.category_list.currentRow() == 0: self.vm.set_radar_filter(text)
        else: self.vm.set_teknik_filter(text)

    def _on_item_selected(self, selected, deselected, proxy_model):
        if not selected.indexes():
            self._clear_forms_and_selection()
            return
        self.current_item = self.vm.get_item_from_proxy_index(selected.indexes()[0], proxy_model)
        if isinstance(self.current_item, Radar):
            self.form_stack.setCurrentWidget(self.radar_form)
            self._populate_radar_form(self.current_item)
        elif isinstance(self.current_item, Teknik):
            self.form_stack.setCurrentWidget(self.teknik_form)
            self._populate_teknik_form(self.current_item)

    def _on_new_item_clicked(self):
        self._clear_forms_and_selection(clear_table_selection=False)
        if self.category_list.currentRow() == 0:
            self.current_item = Radar()
            self.form_stack.setCurrentWidget(self.radar_form)
            self._populate_radar_form(self.current_item)
        else:
            self.current_item = Teknik()
            self.form_stack.setCurrentWidget(self.teknik_form)
            self._populate_teknik_form(self.current_item)

    def _delete_current_item(self):
        if self.current_item:
            reply = QMessageBox.question(self, "Silme Onayı", f"'{self.current_item.adi}' kaydını silmek istediğinizden emin misiniz?")
            if reply == QMessageBox.StandardButton.Yes:
                self.vm.delete_item(self.current_item)
                self._clear_forms_and_selection()

    def _duplicate_current_item(self):
        if self.current_item: self.vm.duplicate_item(self.current_item)

    def _clear_forms_and_selection(self, clear_table_selection=True):
        self.current_item = None
        if clear_table_selection:
            self.radars_table().clearSelection()
            self.teknikler_table().clearSelection()
        self.form_stack.setCurrentWidget(self.placeholder_form)
        self._populate_radar_form(Radar())
        self._populate_teknik_form(Teknik())

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

    def _create_radar_form(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        form_group = QGroupBox("Radar Detayları")
        layout.addWidget(form_group)
        form = QFormLayout(form_group)
        self.radar_in_adi = QLineEdit()
        self.radar_in_uretici = QLineEdit()
        self.radar_in_bant = QComboBox(); self.radar_in_bant.addItems(FREKANS_BANDLARI)
        self.radar_in_gorev = QComboBox(); self.radar_in_gorev.addItems(GOREV_TIPLERI)
        self.radar_in_anten = QComboBox(); self.radar_in_anten.addItems(ANTEN_TIPLERI)
        self.radar_in_not = QTextEdit(); self.radar_in_not.setFixedHeight(120)
        form.addRow("Adı:", self.radar_in_adi)
        form.addRow("Üretici:", self.radar_in_uretici)
        form.addRow("Frekans Bandı:", self.radar_in_bant)
        form.addRow("Görev Tipi:", self.radar_in_gorev)
        form.addRow("Anten Tipi:", self.radar_in_anten)
        form.addRow("Notlar:", self.radar_in_not)
        layout.addStretch()
        self.radar_btn_kaydet, self.radar_btn_cogalt, self.radar_btn_sil, btn_layout = self._create_form_buttons()
        layout.addLayout(btn_layout)
        self.radar_form = panel
        return panel

    def _populate_radar_form(self, radar: Radar):
        self.radar_in_adi.setText(radar.adi)
        self.radar_in_uretici.setText(radar.uretici)
        self.radar_in_bant.setCurrentText(radar.frekans_bandi)
        self.radar_in_gorev.setCurrentText(radar.gorev_tipi)
        self.radar_in_anten.setCurrentText(radar.anten_tipi)
        self.radar_in_not.setPlainText(radar.notlar)
        is_new = not hasattr(radar, 'radar_id') or not self.vm.item_exists(radar.radar_id, Radar)
        self.radar_btn_cogalt.setEnabled(not is_new)
        self.radar_btn_sil.setEnabled(not is_new)

    def _save_radar(self):
        if self.current_item and isinstance(self.current_item, Radar):
            self.current_item.adi = self.radar_in_adi.text()
            self.current_item.uretici = self.radar_in_uretici.text()
            self.current_item.frekans_bandi = self.radar_in_bant.currentText()
            self.current_item.gorev_tipi = self.radar_in_gorev.currentText()
            self.current_item.anten_tipi = self.radar_in_anten.currentText()
            self.current_item.notlar = self.radar_in_not.toPlainText()
            self.vm.save_item(self.current_item)
            QMessageBox.information(self, "Başarılı", f"'{self.current_item.adi}' radarı kaydedildi.")

    def _create_teknik_form(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        form_group = QGroupBox("Teknik Detayları")
        layout.addWidget(form_group)
        form = QFormLayout(form_group)
        self.teknik_in_adi = QLineEdit()
        self.teknik_in_kategori = QComboBox(); self.teknik_in_kategori.addItems(TEKNIK_KATEGORILERI)
        self.teknik_in_aciklama = QTextEdit(); self.teknik_in_aciklama.setFixedHeight(120)
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
        param_layout.addWidget(self.teknik_params_stack)
        layout.addWidget(param_group)
        layout.addStretch()
        self.teknik_btn_kaydet, self.teknik_btn_cogalt, self.teknik_btn_sil, btn_layout = self._create_form_buttons()
        layout.addLayout(btn_layout)
        self.teknik_form = panel
        return panel

    def _create_gurultu_params_form(self):
        widget = QWidget()
        form = QFormLayout(widget)
        self.p_gurultu_tur = QComboBox(); self.p_gurultu_tur.addItems(["Barrage", "Spot", "Swept", "DRFM Noise"])
        self.p_gurultu_bant = QDoubleSpinBox(suffix=" MHz", maximum=100000)
        self.p_gurultu_guc = QDoubleSpinBox(suffix=" dBW", minimum=-100, maximum=100)
        form.addRow("Tür:", self.p_gurultu_tur)
        form.addRow("Bant Genişliği:", self.p_gurultu_bant)
        form.addRow("Güç (ERP):", self.p_gurultu_guc)
        self.teknik_params_stack.addWidget(widget)

    def _create_menzil_params_form(self):
        widget = QWidget()
        form = QFormLayout(widget)
        self.p_menzil_tip = QComboBox(); self.p_menzil_tip.addItems(["RGPO", "RGPI"])
        self.p_menzil_hiz = QDoubleSpinBox(suffix=" m/s", maximum=10000)
        self.p_menzil_sayi = QSpinBox(maximum=100)
        form.addRow("Teknik Tipi:", self.p_menzil_tip)
        form.addRow("Çekme Hızı:", self.p_menzil_hiz)
        form.addRow("Sahte Hedef Sayısı:", self.p_menzil_sayi)
        self.teknik_params_stack.addWidget(widget)

    def _create_ag_params_form(self):
        widget = QWidget()
        form = QFormLayout(widget)
        self.p_ag_ornek_freq = QDoubleSpinBox(suffix=" GHz", maximum=100)
        self.p_ag_rf_kazanc = QDoubleSpinBox(suffix=" dB", minimum=-20, maximum=80)
        self.p_ag_if_kazanc = QDoubleSpinBox(suffix=" dB", minimum=-20, maximum=80)
        self.p_ag_faz_kaydirma = QDoubleSpinBox(suffix=" °", maximum=360)
        self.p_ag_agc_aktif = QCheckBox("Aktif")
        self.p_ag_gonderici_guc = QDoubleSpinBox(suffix=" dBm", minimum=-50, maximum=50)
        self.p_ag_mod_tipi = QComboBox(); self.p_ag_mod_tipi.addItems(["BPSK", "QPSK", "16-QAM", "64-QAM"])
        self.p_ag_veri_hizi = QDoubleSpinBox(suffix=" Mbps", maximum=1000)
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
        self.p_ku_dalga_formu = QComboBox(); self.p_ku_dalga_formu.addItems(["Sinus", "Kare", "Testere Dişi", "Darbe"])
        self.p_ku_bas_freq = QDoubleSpinBox(suffix=" MHz", maximum=100000)
        self.p_ku_bit_freq = QDoubleSpinBox(suffix=" MHz", maximum=100000)
        self.p_ku_tarama_sure = QDoubleSpinBox(suffix=" ms", maximum=10000)
        self.p_ku_darbe_gen = QDoubleSpinBox(suffix=" µs", maximum=1000)
        self.p_ku_dta = QDoubleSpinBox(suffix=" µs", maximum=10000)
        self.p_ku_faz_gurultu = QDoubleSpinBox(suffix=" dBc/Hz", minimum=-200, maximum=0)
        self.p_ku_harmonik = QDoubleSpinBox(suffix=" dB", minimum=-100, maximum=0)
        form.addRow("Dalga Formu Tipi:", self.p_ku_dalga_formu)
        form.addRow("Başlangıç Frekansı:", self.p_ku_bas_freq)
        form.addRow("Bitiş Frekansı:", self.p_ku_bit_freq)
        form.addRow("Tarama Süresi:", self.p_ku_tarama_sure)
        form.addRow("Darbe Genişliği:", self.p_ku_darbe_gen)
        form.addRow("Darbe Tekrarlama Aralığı:", self.p_ku_dta)
        form.addRow("Faz Gürültüsü:", self.p_ku_faz_gurultu)
        form.addRow("Harmonik Baskı:", self.p_ku_harmonik)
        self.teknik_params_stack.addWidget(widget)

    def _on_teknik_kategori_changed(self, index):
        kategori_map = {
            "Gürültü Karıştırma": 0, "Menzil Aldatma": 1,
            "Alıcı/Gönderici Ayarları": 2, "Kaynak Üreteç Ayarları": 3
        }
        self.teknik_params_stack.setCurrentIndex(kategori_map.get(self.teknik_in_kategori.itemText(index), 0))

    def _populate_teknik_form(self, teknik: Teknik):
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
            self.p_ag_agc_aktif.setChecked(params.otomatik_kazanc_kontrolu_aktif)
            self.p_ag_gonderici_guc.setValue(params.gonderici_guc_dbm or 0)
            self.p_ag_mod_tipi.setCurrentText(params.modulasyon_tipi)
            self.p_ag_veri_hizi.setValue(params.veri_hizi_mbps or 0)
        elif isinstance(params, KaynakUretecAyarParametreleri):
            self.p_ku_dalga_formu.setCurrentText(params.dalga_formu_tipi)
            self.p_ku_bas_freq.setValue(params.baslangic_frekansi_mhz or 0)
            self.p_ku_bit_freq.setValue(params.bitis_frekansi_mhz or 0)
            self.p_ku_tarama_sure.setValue(params.tarama_suresi_ms or 0)
            self.p_ku_darbe_gen.setValue(params.darbe_genisligi_us or 0)
            self.p_ku_dta.setValue(params.darbe_tekrarlama_araligi_us or 0)
            self.p_ku_faz_gurultu.setValue(params.faz_gurultusu_dbc_hz or 0)
            self.p_ku_harmonik.setValue(params.harmonik_baski_db or 0)
        is_new = not hasattr(teknik, 'teknik_id') or not self.vm.item_exists(teknik.teknik_id, Teknik)
        self.teknik_btn_cogalt.setEnabled(not is_new)
        self.teknik_btn_sil.setEnabled(not is_new)

    def _save_teknik(self):
        if not (self.current_item and isinstance(self.current_item, Teknik)): return
        teknik = self.current_item
        teknik.adi = self.teknik_in_adi.text()
        teknik.kategori = self.teknik_in_kategori.currentText()
        teknik.aciklama = self.teknik_in_aciklama.toPlainText()
        kategori = teknik.kategori
        if kategori == "Gürültü Karıştırma":
            teknik.parametreler = GurultuKaristirmaParams(
                tur=self.p_gurultu_tur.currentText(),
                bant_genisligi_mhz=self.p_gurultu_bant.value() or None,
                guc_erp_dbw=self.p_gurultu_guc.value() or None)
        elif kategori == "Menzil Aldatma":
            teknik.parametreler = MenzilAldatmaParams(
                teknik_tipi=self.p_menzil_tip.currentText(),
                cekme_hizi_mps=self.p_menzil_hiz.value() or None,
                sahte_hedef_sayisi=self.p_menzil_sayi.value() or None)
        elif kategori == "Alıcı/Gönderici Ayarları":
            teknik.parametreler = AlmacGondermecAyarParametreleri(
                on_ornekleme_frekansi_ghz=self.p_ag_ornek_freq.value() or None,
                rf_kazanc_db=self.p_ag_rf_kazanc.value() or None,
                if_kazanc_db=self.p_ag_if_kazanc.value() or None,
                faz_kaydirma_derece=self.p_ag_faz_kaydirma.value() or None,
                otomatik_kazanc_kontrolu_aktif=self.p_ag_agc_aktif.isChecked(),
                gonderici_guc_dbm=self.p_ag_gonderici_guc.value() or None,
                modulasyon_tipi=self.p_ag_mod_tipi.currentText(),
                veri_hizi_mbps=self.p_ag_veri_hizi.value() or None)
        elif kategori == "Kaynak Üreteç Ayarları":
            teknik.parametreler = KaynakUretecAyarParametreleri(
                dalga_formu_tipi=self.p_ku_dalga_formu.currentText(),
                baslangic_frekansi_mhz=self.p_ku_bas_freq.value() or None,
                bitis_frekansi_mhz=self.p_ku_bit_freq.value() or None,
                tarama_suresi_ms=self.p_ku_tarama_sure.value() or None,
                darbe_genisligi_us=self.p_ku_darbe_gen.value() or None,
                darbe_tekrarlama_araligi_us=self.p_ku_dta.value() or None,
                faz_gurultusu_dbc_hz=self.p_ku_faz_gurultu.value() or None,
                harmonik_baski_db=self.p_ku_harmonik.value() or None)
        else:
            teknik.parametreler = BaseTeknikParametreleri()
        self.vm.save_item(teknik)
        QMessageBox.information(self, "Başarılı", f"'{teknik.adi}' tekniği kaydedildi.")