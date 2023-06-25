from typing_extensions import override
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QMessageBox,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QTabWidget,
    QApplication,
)
from PySide6.QtCore import Qt, QEvent

from UI.task_input_section_UI import TaskInputSection
from UI.weight_input_section_UI import WeightInputSection


class TaskManUI(QMainWindow):
    def __init__(self, app: QApplication) -> None:
        """This function will lay out the basic skeleton of the program"""

        super().__init__()
        self.APP = app  # Keeping a reference to the APP varibale in TaskMan.py

        # Creating the QMainWindow's central widget and customizing the window.
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.setWindowTitle("Task Man")
        self.resize(500, 400)

        # Creating the top menu bar of the application.
        self.app_menu_bar = self.menuBar()
        self.file_menu_bar = self.app_menu_bar.addMenu("&File")
        self.file_menu_bar_exit_action = self.file_menu_bar.addAction("Exit")
        self.file_menu_bar_exit_action.triggered.connect(lambda: self.APP.quit())

        # This is the parent vertical layout of the program.
        self.main_v_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_v_layout)

        # This is the header horizontal layout.
        # It currently only contains a title (QLabel)
        # There will be other widgets in this layout soon in future updates.
        self.header_h_layout = QHBoxLayout()
        self.header_title_label = QLabel("Task Man")
        self.header_title_label.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.header_h_layout.addWidget(self.header_title_label)

        # This is the application's body vertical layout.
        self.body_v_layout = QVBoxLayout()

        # This is the app's main tab widget.
        # It includes a "Tasks" and a "Weight" section
        self.main_tab_widget = QTabWidget()

        self.tasks_tab_widget = TaskInputSection()  # Custom class
        self.weight_tab_widget = WeightInputSection()  # Custom class

        self.main_tab_widget.addTab(self.tasks_tab_widget, "Tasks")
        self.main_tab_widget.addTab(self.weight_tab_widget, "Weight")

        # Adding the different section layouts (Header & Body) -
        # to the main vertical layout of the app.
        self.main_v_layout.addLayout(self.header_h_layout)
        self.body_v_layout.addWidget(self.main_tab_widget)
        self.main_v_layout.addLayout(self.body_v_layout)

    @override
    def closeEvent(self, event: QEvent) -> None:
        """This funtion is an override of the closeEvent function
        in QMainApplication.

        This function asks the user for confirmation before quiting

        It is run generally when the OS tries to terminate the app; for example:
        - User presses ALT + F4
        - User presses X button
        - User presses "Exit" from menu bar
        - Functions within the app trying to terminate the app (!)
        """

        exit_confirmation = QMessageBox.warning(
            self,
            "Task Man",
            "Are you sure you want to exit the application?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if exit_confirmation == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
