import sqlite3
from PySide6.QtWidgets import QLabel, QCheckBox, QHBoxLayout, QGridLayout
from PySide6.QtCore import Qt
from os.path import dirname, join

from playsound import playsound

"""This file contains 2 classes.
One is for populating tasks and the other for weights.
Each class a has child/nested class inside of it.
The nested class allows each task/weight record to be their own object.
The outer class allows the layout in which these records lie to be its own object.

I did it this way solely because of code organization and readability.
Might change this in the future.
"""


class PopulateTasks(QGridLayout):
    def __init__(self, date: str) -> None:
        """This initializer will createa a QGridLayout and populate it with
        layout objects which include records from the DB.
        These layouts are taken from the nested/child class.
        """
        # Create QGridLayout
        super().__init__()

        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.DATE = date

        # Prepare records to be passed onto the nested class.
        self.initialize_task_item_class()

    def initialize_task_item_class(self) -> None:
        """This function will grab the records from the database and pass them
        onto the child class. The child class will then create a layout filled
        with database records as widgets.
        """

        DB_CONNECTION = sqlite3.connect("TaskMan.db")
        DB_CURSOR = DB_CONNECTION.cursor()

        # Grab all tasks on the specified date.
        DB_CURSOR.execute(f"SELECT * FROM Tasks WHERE task_date = '{self.DATE}'")
        tasks = DB_CURSOR.fetchall()

        # Cycle through loaded records from the DB and make objects of each one.
        # Pass 'self' to the child class as a pointer to this class (Parent).
        for task in tasks:
            next_rowIndex = self.rowCount()
            PopulateTasks.TaskItem(self, task[0], task[1], task[2], next_rowIndex)

        # Close database connection
        DB_CURSOR.close()
        DB_CONNECTION.close()

    def destroy(self) -> None:
        """This function will cycle through added layouts in the QGridLayout
        and delete them including their widgets.

        It will finally self-destruct.
        """

        # Start removing from bottom up because the after removing -
        # the count gets updated.
        for _layout in reversed(range(self.count())):
            currentLayout = self.takeAt(_layout)
            # Destroy the widgets inside this layout.
            for _widget in reversed(range(currentLayout.count())):
                childWidget = currentLayout.takeAt(_widget).widget()
                childWidget.deleteLater()
            # Destroy the layout itself.
            currentLayout.deleteLater()
        # Self-destruct
        self.deleteLater()

    class TaskItem(QHBoxLayout):
        def __init__(
            self,
            outer_class_instance: object,
            task_ID: int,
            task_title: str,
            task_date: str,
            next_row: int,
        ) -> None:
            """This function will create a QHBoxLayout and add a single task record
            to it as a checkbox.

            This QHBoxLayout will then be added to the parent class (QGridLayout).
            """

            # Create a QHBoxLayout
            super().__init__()

            # Initialize class variables
            self.OUTER_CLASS_INSTANCE = outer_class_instance
            self.TASK_TITLE = task_title
            self.TASK_ID = task_ID
            self.TASK_DATE = task_date

            # Create a checkbox out of the DB record
            # When the user activates/checks the checkbox, the task will -
            # be removed from the DB and the UI will be refreshed.
            self.task_checkbox = QCheckBox(self.TASK_TITLE)
            self.task_checkbox.stateChanged.connect(self.task_completed)

            # Add the checkbox to the QHBoxLayout
            self.addWidget(self.task_checkbox)

            # Add the QHBoxLayout to the parent class (QGridLayout)
            self.OUTER_CLASS_INSTANCE.addLayout(self, next_row, 1)

        def task_completed(self) -> None:
            """This function will run when the user activates/checks the
            task checkbox. Doing this indicates that the task is completed and
            so it will be removed from the Database.
            """

            # Set state to false so the user can not make any changes
            self.task_checkbox.setEnabled(False)

            # Open database connection
            DB_CONNECTION = sqlite3.connect("TaskMan.db")
            DB_CURSOR = DB_CONNECTION.cursor()

            # Remove the task from the DB
            DB_CURSOR.execute(
                f"DELETE FROM Tasks WHERE task_date = '{self.TASK_DATE}' AND task_ID = {self.TASK_ID}"
            )

            # Commit the changes.
            DB_CONNECTION.commit()

            # Close database connection.
            DB_CURSOR.close()
            DB_CONNECTION.close()

            # Delete the checkbox from the UI and then delete the QHBoxLayout
            self.task_checkbox.deleteLater()
            self.deleteLater()

            # Play a sound after completion
            current_path = dirname(__file__)
            playsound(
                join(
                    current_path,
                    "Resources/Sounds/taskCompletedNotificationSound_V0.07.wav",
                ),
                block=False,
            )


class PopulateWeight(QGridLayout):
    def __init__(self, unit_choice: str, weight_changes_label: QLabel):
        """This initializer will createa a QGridLayout and populate it with
        layout objects which include records from the DB.
        These layouts are taken from the nested/child class.
        """

        # Create the QGridLayout
        super().__init__()
        self.setAlignment(Qt.AlignTop)

        self.USER_UNIT = unit_choice
        self.weight_changes_label = weight_changes_label

        # Prepare records to be passed onto the nested class.
        self.initialize_weight_item_class()

    def initialize_weight_item_class(self) -> None:
        """This function will grab the records from the database and pass them
        onto the child class. The child class will then create a layout filled
        with database records as widgets.
        """

        # Open database connection.
        DB_CONNECTION = sqlite3.connect("TaskMan.db")
        DB_CURSOR = DB_CONNECTION.cursor()

        # Grab all the data from the "Weight" table.
        DB_CURSOR.execute("SELECT * FROM Weights")
        weights = DB_CURSOR.fetchall()

        # Pass to funtion to update the weight changes label.
        self.update_weight_changes(weights)

        # Cycle through loaded records from the DB and make objects of each one.
        # Check if the user has selected "lb" as unit. if so, then convert values.
        # Pass 'self' to the child class as a pointer to this class (Parent).
        for weight in weights:
            next_rowIndex = self.rowCount()
            weight_value = weight[1]

            # If user sets unit to lb, convert KG value to lb
            if self.USER_UNIT == "lb":
                weight_value = round(weight[1] / 0.45359237, 2)

            PopulateWeight.WeightItem(
                self, weight[0], weight_value, self.USER_UNIT, weight[3], next_rowIndex
            )

        # Close database connection.
        DB_CURSOR.close()
        DB_CONNECTION.close()

    def update_weight_changes(self, weights: list[tuple[int, float, str, str]]):
        """This function will grab the last two saved records in the database and
        look for changes between them. Then it will update the weight changes label
        so that the user can see if they have gained or lost weight since last time.
        """
        # If there are more than 1 records saved the the DB.
        if len(weights) > 1:
            # Grab the last two records
            old_weight = weights[len(weights) - 2][1]
            new_weight = weights[len(weights) - 1][1]

            # If the user has selected "lb" as unit, convert the values first.
            if self.USER_UNIT == "lb":
                old_weight = round(old_weight / 0.45359237, 2)
                new_weight = round(new_weight / 0.45359237, 2)

            difference = round(old_weight - new_weight, 2)

            # If value is a positive number, that means the user has lost weight.
            # Example: 90 KG - 85 KG : 5 KG
            if difference > 0:
                self.weight_changes_label.setText(
                    f"Weight Changes:  -{str(difference)}"
                )
            # If the value is a negative number, that means the user has gained weight.
            # Example: 90 KG - 95 KG : -5 KG
            elif difference < 0:
                self.weight_changes_label.setText(
                    f"Weight Changes:  +{str(abs(difference))}"
                )
            # If both values are the same, there has been no progress since last time.
            else:
                self.weight_changes_label.setText("Weight Changes:  No progress")

    def destroy(self) -> None:
        """This function will cycle through added layouts in the QGridLayout
        and delete them including their widgets.

        It will finally self-destruct.
        """

        # Start removing from bottom up because the after removing -
        # the widgets shift in position.
        for _layout in reversed(range(self.count())):
            currentLayout = self.takeAt(_layout)
            # Destroy the widgets inside this layout.
            for _widget in reversed(range(currentLayout.count())):
                childWidget = currentLayout.takeAt(_widget).widget()
                childWidget.deleteLater()
            # Destroy the layout itself.
            currentLayout.deleteLater()
        # Self-destruct
        self.deleteLater()

    class WeightItem(QHBoxLayout):
        def __init__(
            self,
            outer_class_instance: object,
            weight_ID: int,
            weight_value: float,
            weight_unit: str,
            weight_date: str,
            next_row: int,
        ) -> None:
            """This function will create a QHBoxLayout and add a single task record
            to it as a checkbox.

            This QHBoxLayout will then be added to the parent class (QGridLayout).
            """

            # Create the QHBoxLayout
            super().__init__()

            # Initialize class variables
            self.OUTER_CLASS_INSTANCE = outer_class_instance
            self.WEIGHT_VALUE = weight_value
            self.WEIGHT_UNIT = weight_unit
            self.WEIGHT_DATE = weight_date
            self.WEIGHT_ID = weight_ID

            # Combine the weight value and its unit.
            # Create a QLabel out of both of them.
            self.weight_value_and_unit_label = QLabel(
                str(self.WEIGHT_VALUE) + " " + self.WEIGHT_UNIT
            )
            self.weight_value_and_unit_label.setAlignment(Qt.AlignLeft)

            # A QLabel for the task's date.
            self.weightDateLabel = QLabel(self.WEIGHT_DATE)
            self.weightDateLabel.setAlignment(Qt.AlignRight)

            # Add both QLabels to the QHBoxLayout (self)
            self.addWidget(self.weight_value_and_unit_label)
            self.addWidget(self.weightDateLabel)

            # Add the layout to the QGridLayout (parent class)
            self.OUTER_CLASS_INSTANCE.addLayout(self, next_row, 1)
