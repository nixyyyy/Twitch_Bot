from enum import Enum

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import (QAbstractItemView, QMainWindow, QPushButton, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget, QLabel, QHBoxLayout)

import os
import json

# Constants
TITLE = 'Twitch Bot'
DEFAULT_COLOR = QColor(50, 50, 50)
SCREEN_WIDTH_FRACTION = 2/3
DEFAULT_COOLDOWN = 10

class Cols(Enum):
    COMMAND = 0
    COOLDOWN = 1
    RESPONSE = 2


class CustomTableWidget(QTableWidget):

    def __init__(self, parent=None):
        super(CustomTableWidget, self).__init__(parent)
        self.allow_auto_scroll = False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if self.state() != QAbstractItemView.EditingState:  # Check if we are not already editing
                current_item = self.currentItem()
                if current_item:
                    self.editItem(current_item)
        else:
            super().keyPressEvent(event)

    def scrollTo(self, index, hint=QAbstractItemView.EnsureVisible):
        if self.allow_auto_scroll:
            super().scrollTo(index, hint)


class CommandManager(QMainWindow):
    bot_process = None

    def __init__(self, config_file):
        super().__init__()
        self.config_file = config_file

        # Check if commands.json exists, if not, create and initialize it
        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w') as f:
                json.dump({}, f)

        # Load existing commands
        with open(self.config_file, 'r') as f:
            self.commands_config = json.load(f)

        # Set window properties
        self.setGeometry(300, 300, 400, 300)
        self.setWindowTitle(TITLE)

        # Create UI elements
        self.main_widget = QWidget(self)
        self.layout = QVBoxLayout(self.main_widget)

        label = QLabel('Command (variations separated by commas) | Cooldown (seconds) | Response')
        label_layout = QHBoxLayout()
        label_layout.addWidget(label)

        self.tableWidget = CustomTableWidget(self)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableWidget.setSelectionMode(QTableWidget.SingleSelection)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.setEditTriggers(QTableWidget.DoubleClicked)
        self.tableWidget.cellChanged.connect(self.on_cell_changed)

        for command, details in list(self.commands_config.items()):
            row_position = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_position)
            self.tableWidget.setItem(row_position, Cols.COMMAND.value, QTableWidgetItem(command))
            self.tableWidget.setItem(row_position, Cols.COOLDOWN.value, QTableWidgetItem(str(details['cooldown'])))  # Cooldown column
            self.tableWidget.setItem(row_position, Cols.RESPONSE.value, QTableWidgetItem(details['response']))

        self.tableWidget.resizeColumnToContents(Cols.COMMAND.value)
        self.tableWidget.resizeColumnToContents(Cols.COOLDOWN.value)

        self.add_new_row_button = QPushButton('Add Command', self.main_widget)
        self.add_new_row_button.clicked.connect(self.add_new_row)
        self.remove_button = QPushButton('Remove Command', self.main_widget)
        self.remove_button.clicked.connect(self.remove_command)

        self.layout.addLayout(label_layout)
        self.layout.addWidget(self.tableWidget)
        self.layout.addWidget(self.add_new_row_button)
        self.layout.addWidget(self.remove_button)
        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)


    def set_table_cell(self, row, col, text=None, color=DEFAULT_COLOR):
        item = self.tableWidget.item(row, col)
        if not item:
            item = QTableWidgetItem()
            self.tableWidget.setItem(row, col, item)
        if text is not None:
            item.setText(text)
        item.setBackground(QBrush(color))


    def resize_columns(self):
        for i in range(self.tableWidget.columnCount()):
            self.tableWidget.resizeColumnToContents(i)


    def add_new_row(self):
        row_position = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_position)

        for col in range(self.tableWidget.columnCount()):
            self.set_table_cell(row_position, col)


    def on_cell_changed(self, row, column):
        command = self.tableWidget.item(row, Cols.COMMAND.value)
        cooldown = self.tableWidget.item(row, Cols.COOLDOWN.value)
        response = self.tableWidget.item(row, Cols.RESPONSE.value)

        # Ensure all the items are valid before proceeding
        if command and command.text() and response and response.text():
            if cooldown and cooldown.text():
                try:
                    cooldown_value = int(cooldown.text())
                except ValueError:
                    # If conversion fails, it's not an integer. Revert/change the value.
                    cooldown.setText(str(DEFAULT_COOLDOWN))  # Set the cell content back to default value
                    cooldown_value = DEFAULT_COOLDOWN
            else:
                cooldown_value = DEFAULT_COOLDOWN
                cooldown.setText(str(DEFAULT_COOLDOWN))

            # Update the commands_config dictionary
            self.commands_config[command.text()] = {
                'response': response.text(),
                'cooldown': cooldown_value
            }
            self.save_commands()

        self.set_table_cell(row, column)
        self.resize_columns()


    def remove_command(self):
        selected_rows = self.tableWidget.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()  # Get the first selected row (there should only be one)
            command_to_remove = self.tableWidget.item(row, 0).text()

            # Remove from commands_config
            if command_to_remove in self.commands_config:
                del self.commands_config[command_to_remove]
                self.save_commands()

            self.tableWidget.removeRow(row)
            self.resize_columns()


    def save_commands(self):
        # Save to configuration file
        with open(self.config_file, 'w') as f:
            json.dump(self.commands_config, f, indent=4)


    def run_gui(self):
        self.show()


    def closeEvent(self, event):
        # Save the configuration file before closing
        self.save_commands()
        # Ensure bot process is terminated when GUI is closed
        if self.bot_process and self.bot_process.is_alive():
            self.bot_process.terminate()
        event.accept()
