import sys
import os
import csv
import numpy as np
import PyQt5
from PyQt5 import QtWidgets
import ml
import json
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

import test_design


class App(QtWidgets.QMainWindow, test_design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.build_handlers()
        self.on_load_main_page()

    def build_handlers(self):
        self.loadConceptsButton.clicked.connect(self.on_load_concepts_button_click)
        self.determineClassButton.clicked.connect(self.on_determine_class_button_click)
        self.exportModelButton.clicked.connect(self.on_export_model_button_click)
        self.importModelButton.clicked.connect(self.on_load_model_button_click)
        self.clearFieldsButton.clicked.connect(self.on_clear_fields_button_click)

    def on_load_main_page(self):
        self.determineClassButton.setEnabled(False)
        with open(os.curdir + '/resources/characters_concepts.json', 'r') as f:
            data = json.loads(f.read())
        checkbox_list = refresh_scroll_area(data['concepts'], self.scrollArea)
        for checkbox in checkbox_list:
            checkbox.stateChanged.connect(self.on_checkbox_change_factory(checkbox_list))

        zero_model = np.zeros([len(checkbox_list), len(data['characters'].keys())])
        # zero_model = list(zero_model)
        fill_table(zero_model, self.modelTable)
        self.classesListWidget_2.itemSelectionChanged.connect(self.set_concepts_by_class(checkbox_list, data))
        self.refresh_list_view(data['characters'].keys())
        model = ml.import_model(os.curdir + "/resources/model_data.csv")
        fill_table(data=model, table=self.modelTable)

    def set_concepts_by_class(self, checkbox_list, data):
        def set_concepts():
            character = self.classesListWidget_2.currentItem().text()
            character = "{}{}".format(character[:1], character[1:].lower())
            concepts = data['characters'][character]
            for index, checkbox in enumerate(checkbox_list):
                if concepts[index] == 1:
                    checkbox.setChecked(True)
                else:
                    checkbox.setChecked(False)

        return set_concepts

    def refresh_list_view(self, data):
        for character in data:
            item = QtWidgets.QListWidgetItem(character.upper())
            icon = QtGui.QIcon(os.curdir + "/resources/characters_small/{}".format(character.lower()))
            item.setIcon(icon)

            self.classesListWidget_2.addItem(item)
        self.classesListWidget_2.setIconSize(QtCore.QSize(60, 60))

    def on_checkbox_change_factory(self, checkbox_list):
        def on_checkbox_change():
            flag = 0
            self.label.clear()
            self.characterNameLabel.clear()
            for checkbox in checkbox_list:
                if checkbox.isChecked():
                    flag = 1
                    self.determineClassButton.setEnabled(True)
            if flag == 0:
                self.determineClassButton.setEnabled(False)

        return on_checkbox_change

    def on_load_concepts_button_click(self):
        self.determineClassButton.setEnabled(False)
        try:
            filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Выберите файл с входными данными', filter="*.json")
            if filename:
                with open(filename[0], 'r') as f:
                    data = json.loads(f.read())
                checkbox_list = refresh_scroll_area(data['concepts'], self.scrollArea)
                for checkbox in checkbox_list:
                    checkbox.stateChanged.connect(self.on_checkbox_change_factory(checkbox_list))
        except FileNotFoundError:
            pass

    def on_clear_fields_button_click(self):
        checkbox_list = self.scrollArea.findChildren(QtWidgets.QCheckBox)
        for checkbox in checkbox_list:
            checkbox.setChecked(False)
        self.determineClassButton.setEnabled(False)
        self.label.clear()
        self.characterNameLabel.clear()

    def on_determine_class_button_click(self):
        with open(os.curdir + '/resources/characters_concepts.json', 'r') as f:
            data = json.loads(f.read())
        model = read_table(self.modelTable)

        checkbox_list = self.scrollArea.findChildren(QtWidgets.QCheckBox)
        input_concepts = [1 if box.isChecked() else 0 for box in checkbox_list]

        out_classes = ml.get_class(input_concepts, model, data['characters'])
        image_name = os.curdir + "/resources/characters_small/{}.png".format(out_classes[0].lower())
        self.label.setPixmap(QtGui.QPixmap(image_name))
        self.characterNameLabel.setText(out_classes[0].upper())

    def on_load_model_button_click(self):
        model = ml.import_model(os.curdir + "/resources/model_data.csv")
        fill_table(data=model, table=self.modelTable)

    def on_export_model_button_click(self):
        rows = self.modelTable.rowCount()
        cols = self.modelTable.columnCount()
        model = [[self.modelTable.item(row, col).text() for col in range(cols)] for row in range(rows)]
        filename = QtWidgets.QFileDialog.getSaveFileName(self, "Выберите место сохранения файла")
        if filename:
            ml.export_model(filename[0], model)


def refresh_scroll_area(data, scroll_area: QtWidgets.QScrollArea):
    layout = QtWidgets.QFormLayout()
    label_list = [QtWidgets.QLabel(concept) for concept in data]
    checkbox_list = [QtWidgets.QCheckBox() for i in range(len(label_list))]
    for i in range(len(label_list)):
        layout.addRow(label_list[i], checkbox_list[i])

    new_content = QtWidgets.QWidget()
    new_content.setLayout(layout)
    scroll_area.setWidget(new_content)
    return checkbox_list


def read_table(table: QtWidgets.QTableWidget):
    rows = table.rowCount()
    cols = table.columnCount()
    return [[float(table.item(row, col).text()) for col in range(cols)] for row in range(rows)]


def fill_table(data, table: QtWidgets.QTableWidget):
    table.setRowCount(len(data))
    table.setColumnCount(len(data[0]))
    for row in range(len(data)):
        for col in range(len(data[0])):
            table.setItem(row, col, QtWidgets.QTableWidgetItem(data[row][col]))


def main():
    dirname = os.path.dirname(PyQt5.__file__)
    plugin_path = os.path.join(dirname, 'plugins', 'platforms')
    os.environ[
        'QT_QPA_PLATFORM_PLUGIN_PATH'] = '/home/marcie/Рабочий стол/Study/MOI/Lab2/venv/lib/python3.6/site-packages/PyQt5/Qt/plugins/platforms'
    print(plugin_path)
    app = QtWidgets.QApplication(sys.argv)
    stylesheet = open('resources/styles.css').read()
    QtGui.QFontDatabase.addApplicationFont("resources/fonts/Overwatch Font.ttf")
    app.setStyleSheet(stylesheet)
    window = App()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
