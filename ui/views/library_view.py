# ew_platformasi/ui/views/library_view.py

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QStackedWidget,
                               QTableView, QGroupBox, QLabel, QFormLayout, QLineEdit, QComboBox, QTextEdit,
                               QPushButton, QDoubleSpinBox, QSpinBox, QHeaderView, QMessageBox, QSplitter)

from core.data_models import (Radar, Teknik, GurultuKaristirmaParams, MenzilAldatmaParams, BaseTeknikParametreleri,
                              FREKANS_BANDLARI, GOREV_TIPLERI, ANTEN_TIPLERI, TEKNIK_KATEGORILERI)
from viewmodels.library_vm import LibraryViewModel


class LibraryView(QWidget):
    def __init__(self, view_model: LibraryViewModel, parent=None):
        super().__init__(parent)
        self.vm = view_model
        self.current_item = None

        self._build_ui()
        self._connect_signals()
        self.category_list.setCurrentRow(0)  # Başlangıçta Radarları göster

    def _build_ui(self):
        main_layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- 1. Sol Panel: Kategori Navigasyonu ---
        self.category_list = QListWidget()
        self.category_list.setFixedWidth(200)
        self.category_list.addItem(QListWidgetItem(qta.icon('fa5s.broadcast-tower', color='lightblue'), "Radarlar"))
        self.category_list.addItem(QListWidgetItem(qta.icon('fa5s.wave-square', color='lightgreen'), "EH Teknikleri"))

        # --- 2. Orta Panel: Kayıt Listesi ve Filtreleme ---
        middle_panel = self._create_middle_panel()

        # --- 3. Sağ Panel: Detay/Düzenleme Formu ---
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

        # Arama ve "Yeni Ekle" Butonu
        top_bar_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Listede ara...")
        self.btn_yeni = QPushButton("Yeni Ekle", icon=qta.icon('fa5s.plus-circle'))
        top_bar_layout.addWidget(self.search_box)
        top_bar_layout.addWidget(self.btn_yeni)

        # Tabloları içeren Stacked Widget
        self.table_stack = QStackedWidget()

        self.radars_table = QTableView()
        self.radars_table.setModel(self.vm.radars_proxy_model)  # Proxy modele bağlan
        self.radars_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.radars_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.radars_table.setSortingEnabled(True)
        self.radars_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.teknikler_table = QTableView()
        self.teknikler_table.setModel(self.vm.teknikler_proxy_model)  # Proxy modele bağlan
        self.teknikler_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.teknikler_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.teknikler_table.setSortingEnabled(True)
        self.teknikler_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.table_stack.addWidget(self.radars_table)
        self.table_stack.addWidget(self.teknikler_table)

        layout.addLayout(top_bar_layout)
        layout.addWidget(self.table_stack)
        return panel

    def _create_right_panel(self):
        stack = QStackedWidget()

        # Boş Panel
        self.placeholder_form = QWidget()
        placeholder_layout = QVBoxLayout(self.placeholder_form)
        placeholder_layout.addStretch()
        placeholder_layout.addWidget(QLabel(
            "İncelemek veya düzenlemek için bir kayıt seçin.\nYeni kayıt eklemek için 'Yeni Ekle' butonunu kullanın."),
                                     0, Qt.AlignmentFlag.AlignCenter)
        placeholder_layout.addStretch()

        self.radar_form = self._create_radar_form()
        self.teknik_form = self._create_teknik_form()

        stack.addWidget(self.placeholder_form)
        stack.addWidget(self.radar_form)
        stack.addWidget(self.teknik_form)

        return stack

    def _connect_signals(self):
        self.category_list.currentRowChanged.connect(self._on_category_changed)
        self.search_box.textChanged.connect(self._on_search_changed)
        self.btn_yeni.clicked.connect(self._on_new_item_clicked)

        # Tablo seçim sinyalleri
        self.radars_table.selectionModel().selectionChanged.connect(
            lambda s, d: self._on_item_selected(s, d, self.vm.radars_proxy_model))
        self.teknikler_table.selectionModel().selectionChanged.connect(
            lambda s, d: self._on_item_selected(s, d, self.vm.teknikler_proxy_model))

        # Form buton sinyalleri
        self.radar_btn_kaydet.clicked.connect(self._save_radar)
        self.radar_btn_sil.clicked.connect(self._delete_current_item)
        self.teknik_btn_kaydet.clicked.connect(self._save_teknik)
        self.teknik_btn_sil.clicked.connect(self._delete_current_item)
        self.teknik_in_kategori.currentIndexChanged.connect(self.teknik_params_stack.setCurrentIndex)

    def _on_category_changed(self, index):
        """Sol menüde kategori değiştiğinde orta ve sağ panelleri günceller."""
        self.table_stack.setCurrentIndex(index)
        self.search_box.clear()
        self._clear_forms_and_selection()

    def _on_search_changed(self, text):
        """Arama kutusu değiştiğinde ilgili ViewModel'deki filtreyi tetikler."""
        if self.category_list.currentRow() == 0:
            self.vm.set_radar_filter(text)
        else:
            self.vm.set_teknik_filter(text)

    def _on_item_selected(self, selected, deselected, proxy_model):
        """Tablolardan bir öğe seçildiğinde sağdaki formu doldurur."""
        indexes = selected.indexes()
        if not indexes:
            self._clear_forms_and_selection()
            return

        self.current_item = self.vm.get_item_from_proxy_index(indexes[0], proxy_model)

        if isinstance(self.current_item, Radar):
            self.form_stack.setCurrentWidget(self.radar_form)
            self._populate_radar_form(self.current_item)
        elif isinstance(self.current_item, Teknik):
            self.form_stack.setCurrentWidget(self.teknik_form)
            self._populate_teknik_form(self.current_item)

    def _on_new_item_clicked(self):
        """'Yeni Ekle' butonu, seçimi temizler ve sağdaki formu yeni giriş için hazırlar."""
        self._clear_forms_and_selection()
        if self.category_list.currentRow() == 0:
            self.current_item = Radar()  # Boş bir nesne oluştur
            self.form_stack.setCurrentWidget(self.radar_form)
            self._populate_radar_form(self.current_item)
        else:
            self.current_item = Teknik()
            self.form_stack.setCurrentWidget(self.teknik_form)
            self._populate_teknik_form(self.current_item)

    def _delete_current_item(self):
        """Seçili olan öğeyi siler."""
        if self.current_item:
            item_name = self.current_item.adi
            reply = QMessageBox.question(self, "Silme Onayı",
                                         f"'{item_name}' kaydını silmek istediğinizden emin misiniz?")
            if reply == QMessageBox.StandardButton.Yes:
                self.vm.delete_item(self.current_item)
                self._clear_forms_and_selection()

    def _clear_forms_and_selection(self):
        """Tüm formları ve tablo seçimlerini temizler."""
        self.current_item = None
        self.radars_table.clearSelection()
        self.teknikler_table.clearSelection()
        self.form_stack.setCurrentWidget(self.placeholder_form)
        # Formları da temizle (opsiyonel ama iyi pratik)
        self._populate_radar_form(Radar())
        self._populate_teknik_form(Teknik())

    # --- RADAR FORM METOTLARI ---
    def _create_radar_form(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        form_group = QGroupBox("Radar Detayları")
        layout.addWidget(form_group)
        form = QFormLayout(form_group)

        self.radar_in_adi = QLineEdit()
        self.radar_in_uretici = QLineEdit()
        self.radar_in_bant = QComboBox();
        self.radar_in_bant.addItems(FREKANS_BANDLARI)
        self.radar_in_gorev = QComboBox();
        self.radar_in_gorev.addItems(GOREV_TIPLERI)
        self.radar_in_anten = QComboBox();
        self.radar_in_anten.addItems(ANTEN_TIPLERI)
        self.radar_in_not = QTextEdit();
        self.radar_in_not.setFixedHeight(120)

        form.addRow("Adı:", self.radar_in_adi)
        form.addRow("Üretici:", self.radar_in_uretici)
        form.addRow("Frekans Bandı:", self.radar_in_bant)
        form.addRow("Görev Tipi:", self.radar_in_gorev)
        form.addRow("Anten Tipi:", self.radar_in_anten)
        form.addRow("Notlar:", self.radar_in_not)
        layout.addStretch()

        button_layout = QHBoxLayout()
        self.radar_btn_kaydet = QPushButton("Kaydet", icon=qta.icon('fa5s.save'))
        self.radar_btn_sil = QPushButton("Sil", icon=qta.icon('fa5s.trash-alt'))
        button_layout.addStretch();
        button_layout.addWidget(self.radar_btn_kaydet);
        button_layout.addWidget(self.radar_btn_sil)
        layout.addLayout(button_layout)
        return panel

    def _populate_radar_form(self, radar: Radar):
        self.radar_in_adi.setText(radar.adi)
        self.radar_in_uretici.setText(radar.uretici)
        self.radar_in_bant.setCurrentText(radar.frekans_bandi)
        self.radar_in_gorev.setCurrentText(radar.gorev_tipi)
        self.radar_in_anten.setCurrentText(radar.anten_tipi)
        self.radar_in_not.setPlainText(radar.notlar)

    def _save_radar(self):
        if self.current_item and isinstance(self.current_item, Radar):
            self.current_item.adi = self.radar_in_adi.text()
            self.current_item.uretici = self.radar_in_uretici.text()
            self.current_item.frekans_bandi = self.radar_in_bant.currentText()
            self.current_item.gorev_tipi = self.radar_in_gorev.currentText()
            self.current_item.anten_tipi = self.radar_in_anten.currentText()
            self.current_item.notlar = self.radar_in_not.toPlainText()
            self.vm.save_item(self.current_item)
            QMessageBox.information(self, "Başarılı", f"'{self.current_item.adi}' radarı güncellendi.")

    # --- TEKNİK FORM METOTLARI ---
    def _create_teknik_form(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        form_group = QGroupBox("Teknik Detayları")
        layout.addWidget(form_group)
        form = QFormLayout(form_group)

        self.teknik_in_adi = QLineEdit()
        self.teknik_in_kategori = QComboBox();
        self.teknik_in_kategori.addItems(TEKNIK_KATEGORILERI)
        self.teknik_in_aciklama = QTextEdit();
        self.teknik_in_aciklama.setFixedHeight(120)

        form.addRow("Adı:", self.teknik_in_adi)
        form.addRow("Kategori:", self.teknik_in_kategori)
        form.addRow("Açıklama:", self.teknik_in_aciklama)

        param_group = QGroupBox("Tekniğe Özel Parametreler")
        param_layout = QVBoxLayout(param_group)
        self.teknik_params_stack = QStackedWidget()
        gurultu_widget = QWidget()
        gurultu_form = QFormLayout(gurultu_widget)
        self.p_gurultu_tur = QComboBox();
        self.p_gurultu_tur.addItems(["Barrage", "Spot", "Swept", "DRFM Noise"])
        self.p_gurultu_bant = QDoubleSpinBox(suffix=" MHz")
        self.p_gurultu_guc = QDoubleSpinBox(suffix=" dBW")
        gurultu_form.addRow("Tür:", self.p_gurultu_tur)
        gurultu_form.addRow("Bant Genişliği:", self.p_gurultu_bant)
        gurultu_form.addRow("Güç (ERP):", self.p_gurultu_guc)

        menzil_widget = QWidget()
        menzil_form = QFormLayout(menzil_widget)
        self.p_menzil_tip = QComboBox();
        self.p_menzil_tip.addItems(["RGPO", "RGPI"])
        self.p_menzil_hiz = QDoubleSpinBox(suffix=" m/s")
        self.p_menzil_sayi = QSpinBox()
        menzil_form.addRow("Teknik Tipi:", self.p_menzil_tip)
        menzil_form.addRow("Çekme Hızı:", self.p_menzil_hiz)
        menzil_form.addRow("Sahte Hedef Sayısı:", self.p_menzil_sayi)

        self.teknik_params_stack.addWidget(gurultu_widget)  # Index 0
        self.teknik_params_stack.addWidget(menzil_widget)  # Index 1
        # Diğerleri eklenecek...

        param_layout.addWidget(self.teknik_params_stack)
        layout.addWidget(param_group)
        layout.addStretch()

        button_layout = QHBoxLayout()
        self.teknik_btn_kaydet = QPushButton("Kaydet", icon=qta.icon('fa5s.save'))
        self.teknik_btn_sil = QPushButton("Sil", icon=qta.icon('fa5s.trash-alt'))
        button_layout.addStretch();
        button_layout.addWidget(self.teknik_btn_kaydet);
        button_layout.addWidget(self.teknik_btn_sil)
        layout.addLayout(button_layout)
        return panel

    def _populate_teknik_form(self, teknik: Teknik):
        self.teknik_in_adi.setText(teknik.adi)
        self.teknik_in_kategori.setCurrentText(teknik.kategori)
        self.teknik_in_aciklama.setText(teknik.aciklama)

        if isinstance(teknik.parametreler, GurultuKaristirmaParams):
            self.teknik_in_kategori.setCurrentText("Gürültü Karıştırma")
            self.p_gurultu_tur.setCurrentText(teknik.parametreler.tur)
            self.p_gurultu_bant.setValue(teknik.parametreler.bant_genisligi_mhz or 0)
            self.p_gurultu_guc.setValue(teknik.parametreler.guc_erp_dbw or 0)
        elif isinstance(teknik.parametreler, MenzilAldatmaParams):
            self.teknik_in_kategori.setCurrentText("Menzil Aldatma")
            self.p_menzil_tip.setCurrentText(teknik.parametreler.teknik_tipi)
            self.p_menzil_hiz.setValue(teknik.parametreler.cekme_hizi_mps or 0)
            self.p_menzil_sayi.setValue(teknik.parametreler.sahte_hedef_sayisi or 0)

    def _save_teknik(self):
        if self.current_item and isinstance(self.current_item, Teknik):
            teknik = self.current_item
            teknik.adi = self.teknik_in_adi.text()
            teknik.kategori = self.teknik_in_kategori.currentText()
            teknik.aciklama = self.teknik_in_aciklama.toPlainText()

            if teknik.kategori == "Gürültü Karıştırma":
                teknik.parametreler = GurultuKaristirmaParams(
                    tur=self.p_gurultu_tur.currentText(),
                    bant_genisligi_mhz=self.p_gurultu_bant.value() or None,
                    guc_erp_dbw=self.p_gurultu_guc.value() or None)
            elif teknik.kategori == "Menzil Aldatma":
                teknik.parametreler = MenzilAldatmaParams(
                    teknik_tipi=self.p_menzil_tip.currentText(),
                    cekme_hizi_mps=self.p_menzil_hiz.value() or None,
                    sahte_hedef_sayisi=self.p_menzil_sayi.value() or None)
            else:
                teknik.parametreler = BaseTeknikParametreleri()

            self.vm.save_item(teknik)
            QMessageBox.information(self, "Başarılı", f"'{teknik.adi}' tekniği güncellendi.")