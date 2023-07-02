from PySide6.QtWidgets import QWidget, QLabel

from populate_grid import PopulateTasks, PopulateWeight


class PopulateScrollArea(QWidget):
    def __init__(self) -> None:
        # Create a new QWidget
        super().__init__()

    def get_task_widget(self, date: str) -> None:
        """This function will use my custom class to retrive a
        horizontal layout which contains a checkbox with the task name.

        The layout will then be set as the QWidget's layout of this class.
        """

        self.populated_grid_layout = PopulateTasks(date)
        self.setLayout(self.populated_grid_layout)

    def get_weight_widget(self, unit_choice: str, weight_changes_label: QLabel) -> None:
        """This function will use my custom class to retrive a
        horizontal layout which contains 2 QLabels.
        One is the weight value and the other is the saved date of the value.

        The layout will then be set as the QWidget's layout of this class.
        """

        # Pass the unit choice to know if conversion should happen.
        # Pass the weight changes QLabel to apply updates.
        self.populated_grid_layout = PopulateWeight(unit_choice, weight_changes_label)
        self.setLayout(self.populated_grid_layout)

    def destroy(self) -> None:
        """This function will call the layout's destroy function to remove all
        widgets inside it and then delete itself.

        This function will finally delete the QWidget of this class as well.
        """
        self.populated_grid_layout.destroy()
        self.deleteLater()
