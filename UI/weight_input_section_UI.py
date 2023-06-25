import sqlite3
from PySide6.QtWidgets import (
    QPushButton,
    QDoubleSpinBox,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QDateEdit,
    QComboBox,
    QSizePolicy,
    QScrollArea,
)
from PySide6.QtCore import Qt, QDate
from simpleaudio import WaveObject

from populate_scroll_area import PopulateScrollArea


class WeightInputSection(QWidget):
    def __init__(self) -> None:
        """This funtion creates and implements everything needed
        for the weight input section of the app.
        """

        super().__init__()

        # This is the main vertical layout for the input section.
        self.main_v_layout = QVBoxLayout()
        self.main_v_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Simply a title for this section
        self.tab_title = QLabel("Current Weight")
        self.tab_title.setAlignment(Qt.AlignHCenter)

        # This is where user can either type or scroll through weight values.
        # I chose to use a QDoubleSpinBox because of more control rather than a QLineEdit
        # User input validation -> Minimum 5.0 KG/lbs | Maximum 999.999 KG/lbs
        # User can scroll through values with +5 or -5 steps.
        # Default value starts a 60 (Average world weight in KG for faster value selection)
        # TO-DO: Set default value to last DB input if available
        self.new_weight_input = QDoubleSpinBox()
        self.new_weight_input.setMinimum(5.0)
        self.new_weight_input.setMaximum(999.999)
        self.new_weight_input.setSingleStep(5)
        self.new_weight_input.setValue(60.00)
        self.new_weight_input.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        self.new_weight_input.setAlignment(Qt.AlignHCenter)

        # This combox box lets the user choose between kilograms or pounds.
        # Everytime the value changes, the UI refreshes the values and -
        # converts them to user selected Unit.
        self.weight_unit_combobox = QComboBox()
        self.weight_unit_combobox.addItem("KG")
        self.weight_unit_combobox.addItem("lb")
        self.weight_unit_combobox.currentTextChanged.connect(
            self.update_weight_input_suffix
        )

        # Setting the default QDoubleSpinBox suffix to the default Combobox value.
        self.new_weight_input.setSuffix(f" {self.weight_unit_combobox.currentText()}")

        # This is where the user chooses the date for their new weight input.
        # User input validation -> set maximum available date to today.
        # Let the user choose date from a calandar rather than typing/scrolling
        self.new_weight_date = QDateEdit(QDate.currentDate())
        self.new_weight_date.setMaximumDate(QDate.currentDate())
        self.new_weight_date.setDisplayFormat("dd.MM.yyyy")
        self.new_weight_date.setCalendarPopup(True)

        # Pressing this butto will save the weight into DB and refresh the UI.
        self.new_weight_add_button = QPushButton("Add")
        self.new_weight_add_button.clicked.connect(self.save_to_DB)

        # Adding all input elements to one layout.
        # This horizontal layout contains the input widgets.
        # Putting them in one layout helps keep them in one line.
        self.input_section_h_layout = QHBoxLayout()
        self.input_section_h_layout.addWidget(self.new_weight_input)
        self.input_section_h_layout.addWidget(self.weight_unit_combobox)
        self.input_section_h_layout.addWidget(self.new_weight_date)
        self.input_section_h_layout.addWidget(self.new_weight_add_button)

        # This section shows how much progress the user has had since the last
        # entry. (Not from the first entry but rather from the previous one)
        # TO-DO: Let this show overall progress since the first entry ever
        self.weight_changes_label = QLabel("Weight Changes: No progress")
        self.weight_changes_label.setAlignment(Qt.AlignHCenter)
        self.weight_changes_label.setToolTip("Weight changes since the first entry")

        # Creating a scroll area so that if there are too many tasks -
        # the UI wouldn't grow too much.
        self.weights_scroll_area = QScrollArea()
        self.weights_scroll_area.setWidgetResizable(True)
        self.weights_scroll_area.setAlignment(Qt.AlignTop)

        # Finally adding everything to the main vertical layout in order.
        self.main_v_layout.addWidget(self.tab_title)
        self.main_v_layout.addLayout(self.input_section_h_layout)
        self.main_v_layout.addWidget(self.weight_changes_label)
        self.main_v_layout.addWidget(self.weights_scroll_area)
        self.setLayout(self.main_v_layout)

        # Loading weights from DB once everything is set.
        self.load_from_DB()

    def update_weight_input_suffix(self, currentUnit: str) -> None:
        """This function will run when user changes the weight unit.
        It will destroy the UI first and re-generate it with converted values.

        By default, this app stores weight values in KG.
        This means if the user saves a new entry as lbs, it will first be -
        converted to KG then stored in the DB. This make the convertion -
        process easier and faster.
        """

        # Set the suffix to whatever the user changed the unti to.
        self.new_weight_input.setSuffix(f" {currentUnit}")

        # Destroy the UI first and re-generate it with converted values.
        self.generate_weights_list_UI(already_exists=True)

    def save_to_DB(self) -> None:
        """This function will convert any values that was entered as lb to KG.
        Then it will open a connection to the DB and save it there.
        Finally, it will play a short sound after completion.
        """

        if self.new_weight_input.text():
            weight_value = self.new_weight_input.value()
            weight_unit = self.weight_unit_combobox.currentText()
            weight_date = self.new_weight_date.date().toString(Qt.RFC2822Date)
            weight_ID = 1

            # Only save Kilogram values in the Database.
            # If the user chooses "lb", the program will convert the values.
            # If not, the values will simply be shown straight from the DB.
            if weight_unit == "lb":
                weight_value = round(weight_value * 0.45359237, 2)
                weight_unit = "KG"

            # Opening the database connection.
            DB_CONNECTION = sqlite3.connect("TaskMan.db")
            DB_CURSOR = DB_CONNECTION.cursor()

            # Checking for the last task ID saved in the DB.
            # TO-DO: Only select weight_id from DB (no need to get everything)
            DB_CURSOR.execute("SELECT * FROM Weights")
            weights = DB_CURSOR.fetchall()

            # Simply trying to find the last ID saved in the DB
            # TO-DO: can be easily done with something like:
            # if empty -> ID = 1 | if not empty -> ID = weights[-1][0] + 1
            for weight in weights:
                if weight[0] > weight_ID:
                    weight_ID = weight[0]
                if weight[0] == weight_ID:
                    weight_ID += 1

            # Finally saving the new weight in the DB.
            DB_CURSOR.execute(
                f"INSERT INTO Weights VALUES('{weight_ID}', '{weight_value}', '{weight_unit}', '{weight_date}')"
            )

            # This will commit the changes before closing the connection.
            DB_CONNECTION.commit()

            # Close the DB connection.
            DB_CURSOR.close()
            DB_CONNECTION.close()

            # Refreshing the UI so the newly added weight shows up.
            self.load_from_DB()

            # Play a completion notification sound
            notification_sound = WaveObject.from_wave_file(
                "./Resources/Sounds/taskAddedNotificationSound_V0.2.wav"
            )
            notification_sound.play()

    def load_from_DB(self) -> None:
        """This function will completely destroy the weights list widgets if they
        exist and re-generate them.
        The function will load (all) records saved by the user.
        """

        try:
            if self.weights_scroll_area:
                self.generate_weights_list_UI(already_exists=True)

        except AttributeError:
            self.generate_weights_list_UI()

    def generate_weights_list_UI(self, already_exists: bool = False) -> None:
        """This function will create a new object of my custom class.
        The class will return a QWidget populated with items from the DB.
        """

        # If the widgets exist, destroy them first before re-generating.
        if already_exists:
            self.weights_scroll_area.destroy()

        # Creating a widget filled with weight records from the DB.
        # This is a custom class created by me.
        self.weights_scroll_area_widget = PopulateScrollArea()
        self.weights_scroll_area_widget.get_weight_widget(
            self.weight_unit_combobox.currentText(), self.weight_changes_label
        )

        # Set the object as the Scroll Area's widget
        self.weights_scroll_area.setWidget(self.weights_scroll_area_widget)
