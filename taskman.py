import sqlite3
from PySide6.QtWidgets import QApplication
from os import path

from UI.main_UI import TaskManUI

if __name__ == "__main__":
    # Creating a brand new database if the app can not find one.
    # I didn't use "try & except" because sqlite3.connect automatically -
    # creates a database if it can't find the name specified.
    if path.exists("TaskMan.db") is False:
        # Open database connection
        DB_CONNECTION = sqlite3.connect("TaskMan.db")
        DB_CURSOR = DB_CONNECTION.cursor()

        # Create and initialize the "Tasks" table.
        DB_CURSOR.execute(
            "CREATE TABLE Tasks(task_ID Integer, task_title TEXT, task_date TEXT)"
        )

        # Create and initialize the "Weights" table.
        DB_CURSOR.execute(
            "CREATE TABLE Weights(weight_ID Integer, weight_value REAL, weight_unit TEXT, weight_date TEXT)"
        )

        DB_CURSOR.close()
        DB_CONNECTION.close()

    APP = QApplication()
    WINDOW = TaskManUI(APP)
    WINDOW.show()
    APP.exec()
