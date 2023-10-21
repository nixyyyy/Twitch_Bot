from multiprocessing import Process, freeze_support
from bot import run_bot
from command_manager import CommandManager
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtCore import Qt
import sys


def set_dark_theme(app):
    dark_palette = QPalette()

    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(dark_palette)
    app.setStyleSheet("""
    QToolTip {
        color: #ffffff;
        background-color: #2a82da;
        border: 1px solid white;
    }

    QPushButton {
        background-color: #333333;
        color: #e0e0e0;
        border: 1px solid #555555;
        padding: 5px;
    }

    QPushButton:hover {
        background-color: #555555;
    }

    QPushButton:pressed {
        background-color: #222222;
    }

    QTableWidget QTableCornerButton::section {
    background-color: #444;
    border: 1px solid #555;
    }

    QTableWidget QHeaderView::section {
    background-color: #444;
    color: #e0e0e0;
    padding: 5px;
    border: 1px solid #555;
    border-top-left-radius: 5px;  /* Optional: if you want rounded corners */
    border-top-right-radius: 5px; /* Optional: if you want rounded corners */
    }

    QTableWidget QHeaderView {
        background-color: #444;  /* Set background color for the header view */
    }

    QTableWidget::item:selected {
        background-color: #666;
        color: white
    }

    QTableWidget QLineEdit {
    background-color: #333;
    color: #e0e0e0;
    border: 1px solid #555;
    }
    """)


def main():
    # This is necessary when using multiprocessing in a frozen application, as per the Python documentation.
    freeze_support()

    # Start bot as a separate process
    bot_process = Process(target=run_bot)
    bot_process.start()

    # Initialize GUI application
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('bot.ico'))

    set_dark_theme(app)

    # Start the manager process
    manager = CommandManager('commands.json')
    manager.bot_process = bot_process
    manager.run_gui()

    try:
        sys.exit(app.exec_())
    finally:
        bot_process.terminate()
        bot_process.join()


if __name__ == '__main__':
    main()
