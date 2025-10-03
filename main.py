# ew_platformasi/main.py

import sys
from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from ui.main_window import MainWindow


def main():
    """Uygulamayı başlatır."""
    app = QApplication(sys.argv)

    # Modern bir tema uygula (örn: dark_teal.xml, light_blue.xml)
    apply_stylesheet(app, theme='dark_blue.xml')

    # Ana pencereyi oluştur ve göster
    window = MainWindow()
    window.show()

    # Uygulamanın olay döngüsünü başlat
    sys.exit(app.exec())


if __name__ == "__main__":
    main()