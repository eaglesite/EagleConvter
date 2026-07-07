#!/usr/bin/env python3
import sys
import os


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


sys.path.insert(0, resource_path(""))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile
from PySide6.QtGui import QIcon
from ui.main_window import MainWindow


def load_styles(app):
    qss_path = resource_path(os.path.join("resources", "styles.qss"))
    f = QFile(qss_path)
    if f.open(QFile.ReadOnly | QFile.Text):
        app.setStyleSheet(f.readAll().data().decode())
        f.close()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("EagleConvter")
    app.setOrganizationName("EagleConvter")
    icon_path = resource_path(os.path.join("resources", "app.png"))
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    load_styles(app)

    win = MainWindow()
    win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
