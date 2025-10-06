# ew_platformasi/ui/main_window.py

from PySide6.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QFileDialog
from PySide6.QtGui import QAction
import qtawesome as qta

from core.data_manager import DataManager
from viewmodels.library_vm import LibraryViewModel
from viewmodels.scenario_vm import ScenarioViewModel
from viewmodels.gorev_vm import GorevViewModel
from ui.views.library_view import LibraryView
from ui.views.scenario_center_view import ScenarioCenterView
from ui.views.scenario_entry_view import ScenarioEntryView
from ui.views.gorev_center_view import GorevCenterView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Elektronik Harp Analiz Platformu v2.0")
        self.resize(1600, 900)

        self.data_manager = DataManager()

        self.library_vm = LibraryViewModel(self.data_manager)
        self.scenario_vm = ScenarioViewModel(self.data_manager)
        self.gorev_vm = GorevViewModel(self.data_manager)

        self._build_ui()
        self._connect_signals()
        self.statusBar().showMessage("Platform hazır.")

    def _build_ui(self):
        self.tabs = QTabWidget()

        gorev_center_view = GorevCenterView(self.gorev_vm)
        scenario_center_view = ScenarioCenterView(self.scenario_vm)
        scenario_entry_view = ScenarioEntryView(self.scenario_vm)
        library_view = LibraryView(self.library_vm)

        self.tabs.addTab(gorev_center_view, qta.icon('fa5s.bullseye'), "Görev Merkezi")
        self.tabs.addTab(scenario_center_view, qta.icon('fa5s.archive'), "Senaryo Merkezi")
        self.tabs.addTab(scenario_entry_view, qta.icon('fa5s.plus'), "Yeni Senaryo Kaydı")
        self.tabs.addTab(library_view, qta.icon('fa5s.book'), "Kütüphane Yönetimi")

        self.setCentralWidget(self.tabs)
        self._create_menu()

    def _connect_signals(self):
        self.scenario_vm.status_updated.connect(self.statusBar().showMessage)
        self.library_vm.status_updated.connect(self.statusBar().showMessage)
        self.gorev_vm.status_updated.connect(self.statusBar().showMessage)
        self.data_manager.status_updated.connect(self.statusBar().showMessage)

    def _create_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("Dosya")

        import_package_action = QAction(qta.icon('fa5s.box'), "Görev Paketi Yükle...", self)
        import_package_action.triggered.connect(self._import_gorev_package)
        file_menu.addAction(import_package_action)

        file_menu.addSeparator()

        exit_action = QAction(qta.icon('fa5s.sign-out-alt'), "Çıkış", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _import_gorev_package(self):
        path, _ = QFileDialog.getOpenFileName(self, "Görev Paketi İçe Aktar", "", "XML Paket Dosyaları (*.xml)")
        if path:
            self.gorev_vm.import_package(path)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Çıkış', "Uygulamadan çıkmak istediğinizden emin misiniz?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()