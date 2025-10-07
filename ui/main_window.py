# ew_platformasi/ui/main_window.py

from PySide6.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QFileDialog
from PySide6.QtGui import QAction
import qtawesome as qta
import os

from core.data_manager import DataManager
from viewmodels.library_vm import LibraryViewModel
from viewmodels.scenario_vm import ScenarioViewModel
from viewmodels.gorev_vm import GorevViewModel
from ui.views.library_view import LibraryView
from ui.views.scenario_center_view import ScenarioCenterView
from ui.views.scenario_entry_view import ScenarioEntryView
from ui.views.gorev_center_view import GorevCenterView
from core.data_models import Senaryo


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Elektronik Harp Analiz Platformu v2.1")
        self.resize(1600, 900)

        self.current_workspace_path = None

        self.data_manager = DataManager()
        self.library_vm = LibraryViewModel(self.data_manager)
        self.scenario_vm = ScenarioViewModel(self.data_manager)
        self.gorev_vm = GorevViewModel(self.data_manager)

        self._build_ui()
        self._connect_signals()
        self.statusBar().showMessage("Platform hazır. Yeni bir veri seti oluşturun veya mevcut bir seti açın.")

    def _build_ui(self):
        self.tabs = QTabWidget()

        # View'ları oluştururken referanslarını saklayalım
        self.gorev_center_view = GorevCenterView(self.gorev_vm)
        self.scenario_center_view = ScenarioCenterView(self.scenario_vm)
        self.scenario_entry_view = ScenarioEntryView(self.scenario_vm)
        self.library_view = LibraryView(self.library_vm)

        self.tabs.addTab(self.gorev_center_view, qta.icon('fa5s.bullseye'), "Görev Merkezi")
        self.tabs.addTab(self.scenario_center_view, qta.icon('fa5s.archive'), "Senaryo Merkezi")
        self.tabs.addTab(self.scenario_entry_view, qta.icon('fa5s.pencil-alt'), "Senaryo Kayıt/Düzenleme")
        self.tabs.addTab(self.library_view, qta.icon('fa5s.book'), "Kütüphane Yönetimi")

        self.setCentralWidget(self.tabs)
        self._create_menu()

    def _connect_signals(self):
        self.library_vm.status_updated.connect(self.statusBar().showMessage)
        self.scenario_vm.status_updated.connect(self.statusBar().showMessage)
        self.gorev_vm.status_updated.connect(self.statusBar().showMessage)
        self.data_manager.status_updated.connect(self.statusBar().showMessage)

        # Düzenleme isteği sinyalini yakala
        self.scenario_vm.edit_scenario_requested.connect(self.handle_edit_request)

    def _create_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("Dosya")

        new_action = QAction(qta.icon('fa5s.file'), "Yeni Veri Seti", self)
        new_action.triggered.connect(self._new_workspace)

        open_action = QAction(qta.icon('fa5s.folder-open'), "Veri Seti Aç...", self)
        open_action.triggered.connect(self._open_workspace)

        save_action = QAction(qta.icon('fa5s.save'), "Veri Seti Kaydet", self)
        save_action.triggered.connect(self._save_workspace)

        save_as_action = QAction(qta.icon('fa5s.save', options=[{'scale_factor': 0.8, 'offset': (0.2, 0.2)}]),
                                 "Farklı Kaydet...", self)
        save_as_action.triggered.connect(self._save_workspace_as)

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addSeparator()

        import_package_action = QAction(qta.icon('fa5s.box'), "Görev Paketi İçe Aktar...", self)
        import_package_action.triggered.connect(self._import_gorev_package)
        file_menu.addAction(import_package_action)

        file_menu.addSeparator()
        exit_action = QAction(qta.icon('fa5s.sign-out-alt'), "Çıkış", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _new_workspace(self):
        self.data_manager.new_workspace()
        self.current_workspace_path = None
        self.setWindowTitle("İsimsiz Veri Seti - EH Analiz Platformu")

    def _open_workspace(self):
        path, _ = QFileDialog.getOpenFileName(self, "Veri Seti Aç", "", "EH Veri Seti Dosyaları (*.xml)")
        if path:
            self.data_manager.open_workspace(path)
            self.current_workspace_path = path
            self.setWindowTitle(f"{os.path.basename(path)} - EH Analiz Platformu")

    def _save_workspace(self):
        if self.current_workspace_path:
            self.data_manager.save_workspace(self.current_workspace_path)
        else:
            self._save_workspace_as()

    def _save_workspace_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Veri Setini Farklı Kaydet", "", "EH Veri Seti Dosyaları (*.xml)")
        if path:
            self.data_manager.save_workspace(path)
            self.current_workspace_path = path
            self.setWindowTitle(f"{os.path.basename(path)} - EH Analiz Platformu")

    def _import_gorev_package(self):
        path, _ = QFileDialog.getOpenFileName(self, "Görev Paketi İçe Aktar", "", "XML Paket Dosyaları (*.xml)")
        if path:
            self.gorev_vm.import_package(path)

    def handle_edit_request(self, scenario: Senaryo):
        """Senaryo düzenleme isteğini işler."""
        # Senaryo Kayıt/Düzenleme sekmesine geç
        self.tabs.setCurrentWidget(self.scenario_entry_view)
        # Seçili senaryoyu forma yükle
        self.scenario_entry_view.load_scenario_for_edit(scenario)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Çıkış', "Uygulamadan çıkmak istediğinizden emin misiniz?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()