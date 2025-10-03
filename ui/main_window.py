# ew_platformasi/ui/main_window.py

from PySide6.QtWidgets import QMainWindow, QTabWidget, QMessageBox
from PySide6.QtGui import QAction
import qtawesome as qta

from core.data_manager import DataManager
from viewmodels.library_vm import LibraryViewModel
from viewmodels.scenario_vm import ScenarioViewModel
from ui.views.library_view import LibraryView
from ui.views.scenario_center_view import ScenarioCenterView
from ui.views.scenario_entry_view import ScenarioEntryView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Elektronik Harp Analiz Platformu v1.1")
        self.resize(1600, 900)

        self.data_manager = DataManager()

        # --- ViewModelleri Oluştur ---
        self.library_vm = LibraryViewModel(self.data_manager)
        self.scenario_vm = ScenarioViewModel(self.data_manager)

        self._build_ui()
        self._connect_signals()
        self.statusBar().showMessage("Platform hazır.")

    def _build_ui(self):
        self.tabs = QTabWidget()

        # --- Arayüzleri (View) Oluştur ve Sekmelere Ekle ---
        scenario_center_view = ScenarioCenterView(self.scenario_vm)
        scenario_entry_view = ScenarioEntryView(self.scenario_vm)
        library_view = LibraryView(self.library_vm)

        self.tabs.addTab(scenario_center_view, qta.icon('fa5s.archive'), "Senaryo Merkezi")
        self.tabs.addTab(scenario_entry_view, qta.icon('fa5s.plus'), "Yeni Senaryo Kaydı")
        self.tabs.addTab(library_view, qta.icon('fa5s.book'), "Kütüphane Yönetimi")

        self.setCentralWidget(self.tabs)
        self._create_menu()

    def _connect_signals(self):
        # ViewModellerden gelen status mesajlarını statusBar'da göster
        self.scenario_vm.status_updated.connect(self.statusBar().showMessage)

    def _create_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("Dosya")
        exit_action = QAction("Çıkış", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Çıkış', "Uygulamadan çıkmak istediğinizden emin misiniz?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()