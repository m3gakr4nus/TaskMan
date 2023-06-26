import sqlite3
from PySide6.QtWidgets import (
    QPushButton,
    QLineEdit,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QDateEdit,
    QSizePolicy,
    QScrollArea,
)
from PySide6.QtCore import Qt, QDate
from os.path import dirname, join
from playsound import playsound

from populate_scroll_area import PopulateScrollArea


class TaskInputSection(QWidget):
    def __init__(self) -> None:
        """This funtion creates and implements everything needed
        for the task input section of the app.
        """
        super().__init__()

        # This is the main vertical layout for the input section.
        self.main_v_layout = QVBoxLayout()
        self.main_v_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Simply a title for this section
        self.tab_title = QLabel("New Task")
        self.tab_title.setAlignment(Qt.AlignHCenter)

        # This is where user enteres a new task's name/title.
        # User input validation -> A Maximum of 70 characters allowed
        # After user presses "Enter", act as if they pressed the "Add" button.
        self.new_task_input = QLineEdit()
        self.new_task_input.setMaxLength(70)
        self.new_task_input.setClearButtonEnabled(True)
        self.new_task_input.returnPressed.connect(self.save_to_DB)

        # This is where user can choose the date for their new task.
        # User input validation -> make sure no tasks can be added before today.
        # Let the user choose with a calandar rather than typing/spinning.
        # Change the active tasks date so the user see's the tasks for that day.
        self.new_task_date = QDateEdit(QDate.currentDate())
        self.new_task_date.setMinimumDate(QDate.currentDate())
        self.new_task_date.setDisplayFormat("dd.MM.yyyy")
        self.new_task_date.setCalendarPopup(True)
        self.new_task_date.dateChanged.connect(self.update_active_tasks_date)

        # Pressing this butto will save the task into DB and refresh the UI.
        self.new_task_add_button = QPushButton("Add")
        self.new_task_add_button.clicked.connect(self.save_to_DB)

        # Adding all input elements to one layout.
        # This horizontal layout contains the input widgets.
        # Putting them in one layout helps keep them in one line.
        self.input_section_h_layout = QHBoxLayout()
        self.input_section_h_layout.addWidget(self.new_task_input)
        self.input_section_h_layout.addWidget(self.new_task_date)
        self.input_section_h_layout.addWidget(self.new_task_add_button)

        # Simple a label for the active tasks section
        self.current_active_tasks_label = QLabel("Current Active Tasks")
        self.current_active_tasks_label.setAlignment(Qt.AlignHCenter)

        # User can choose to see a certain date's active tasks.
        # Every time the date is changed the tasks list is refreshed.
        self.active_tasks_date = QDateEdit(QDate.currentDate())
        self.active_tasks_date.setDisplayFormat("dd.MM.yyyy")
        self.active_tasks_date.setCalendarPopup(True)
        self.active_tasks_date.setAlignment(Qt.AlignCenter)
        self.active_tasks_date.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        self.active_tasks_date.dateChanged.connect(self.load_from_DB)

        # These button will helps the user navigate faster.
        # Increase or decrease 1 day from whatever the current date is.
        self.previous_day_button = QPushButton("<")
        self.previous_day_button.clicked.connect(
            lambda: self.active_tasks_date.setDate(
                self.active_tasks_date.date().addDays(-1)
            )
        )
        self.next_day_button = QPushButton(">")
        self.next_day_button.clicked.connect(
            lambda: self.active_tasks_date.setDate(
                self.active_tasks_date.date().addDays(1)
            )
        )

        # Creating the HLayout for the last and next day inclidung the date picker.
        # Adding the buttons and the date picker in one horizontal layout.
        self.active_tasks_date_selection_h_layout = QHBoxLayout()
        self.active_tasks_date_selection_h_layout.addWidget(self.previous_day_button)
        self.active_tasks_date_selection_h_layout.addWidget(self.active_tasks_date)
        self.active_tasks_date_selection_h_layout.addWidget(self.next_day_button)

        # Creating a scroll area so that if there are too many tasks -
        # the UI wouldn't grow too much.
        self.tasks_scroll_area = QScrollArea()
        self.tasks_scroll_area.setWidgetResizable(True)
        self.tasks_scroll_area.setAlignment(Qt.AlignTop)

        # Finally adding everything to the main vertical layout in order.
        self.main_v_layout.addWidget(self.tab_title)
        self.main_v_layout.addLayout(self.input_section_h_layout)
        self.main_v_layout.addWidget(self.current_active_tasks_label)
        self.main_v_layout.addLayout(self.active_tasks_date_selection_h_layout)
        self.main_v_layout.addWidget(self.tasks_scroll_area)
        self.setLayout(self.main_v_layout)

        # Loading tasks from DB once everything is set.
        self.load_from_DB()

    def update_active_tasks_date(self, dateChangedTo: QDate) -> None:
        """This function will update the active tasks section date picker to
        match the new task's date picker. This way even before the user has
        added a task, they can see the active tasks for that day.
        """

        self.active_tasks_date.setDate(dateChangedTo)

    def save_to_DB(self) -> None:
        """This function will open a connection to the database and if the input
        if valid, it will get saved. This will also play a short sound after
        completion.
        """

        # User input validation -> If input field has value
        if self.new_task_input.text():
            """If user has changed the current active tasks date manually and
            adds a task in a separate date, this will update the view.
            """
            if self.new_task_date.date() != self.active_tasks_date.date():
                self.update_active_tasks_date(self.new_task_date.date())

            task_title = self.new_task_input.text()
            task_date = self.new_task_date.date().toString(Qt.RFC2822Date)
            task_ID = 1

            # Opening the database connection.
            DB_CONNECTION = sqlite3.connect("TaskMan.db")
            DB_CURSOR = DB_CONNECTION.cursor()

            # Checking for the last task ID saved in the DB.
            # TO-DO: Only select task_id from DB (no need to get everything)
            DB_CURSOR.execute(f"SELECT * FROM Tasks WHERE task_date = '{task_date}'")
            tasks = DB_CURSOR.fetchall()

            # Simply trying to find the last ID saved in the DB
            # TO-DO: can be easily done with something like:
            # if empty -> ID = 1 | if not empty -> ID = tasks[-1][0] + 1
            for task in tasks:
                if task[0] > task_ID:
                    task_ID = task[0]
                if task[0] == task_ID:
                    task_ID += 1

            # Finally saving the new task in the DB.
            DB_CURSOR.execute(
                f"INSERT INTO Tasks VALUES('{task_ID}', '{task_title}', '{task_date}')"
            )

            # This will commit the changes before closing the connection.
            DB_CONNECTION.commit()

            # Close the DB connection.
            DB_CURSOR.close()
            DB_CONNECTION.close()

            # Clearing the input field after completion.
            self.new_task_input.clear()

            # Refreshing the UI so the newly added task shows up.
            self.load_from_DB()

            # Play a completion notification sound
            current_path = dirname(__file__)
            playsound(
                join(
                    current_path,
                    "../Resources/Sounds/taskAddedNotificationSound_V0.2.wav",
                ),
                block=False,
            )

    def load_from_DB(self) -> None:
        """This function will completely destroy the tasks list widgets if they
        exist and re-generate them.
        The function will load the tasks from the chosen date by the user.
        """

        # Load tasks from this date
        date = self.active_tasks_date.date().toString(Qt.RFC2822Date)

        try:
            if self.tasks_scroll_area_widget:
                # If the widget already exists destroy first before re-generating.
                self.generate_tasks_list_UI(already_exists=False)

        except AttributeError:
            # If it does not exist, simply generate it.

            self.generate_tasks_list_UI()

    def generate_tasks_list_UI(self, already_exists: bool = False) -> None:
        """This function will create a new object of my custom class.
        The class will return a QWidget populated with items from the DB.
        """

        # Load tasks from this date
        date = self.active_tasks_date.date().toString(Qt.RFC2822Date)

        # If the widget already exists destroy first before re-generating.
        if already_exists:
            self.tasks_scroll_area_widget.destroy()

        # Creating a widget filled with tasks from the DB with checkboxes
        self.tasks_scroll_area_widget = PopulateScrollArea()  # Custom class
        self.tasks_scroll_area_widget.get_task_widget(date)

        # Set the object as the Scroll Area's widget
        self.tasks_scroll_area.setWidget(self.tasks_scroll_area_widget)
