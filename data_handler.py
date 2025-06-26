import json, os, csv
from constants import PYTHON_EXERCISES
from constants import DATA_SCIENCE_EXERCISES


def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}


def save_data(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


def import_csv_data(file_path, existing_data):
    with open(file_path) as csv_file:
        student_records = list(csv.DictReader(csv_file))

    sample_student = student_records[0]

    if "name" not in sample_student:
        raise ValueError("CSV file does not contain header `name`")

    if "email" not in sample_student:
        raise ValueError("CSV file does not contain header `email`")

    for student_info in student_records:
        name = student_info.get("name", "").strip()
        email = student_info.get("email", "").strip()

        if not name:
            raise ValueError("Name Cannot be empty. Please check csv file.")

        if not email:
            raise ValueError("Email Cannot be empty. Please check csv file.")

        if email in existing_data:
            raise ValueError(f"Email {email} already exists. Please check csv file.")
        
        if "data_science" in file_path:
            exercise_list = DATA_SCIENCE_EXERCISES
        else:
            exercise_list = PYTHON_EXERCISES 

        existing_data[email] = {
            "name": name,
            "exercises": {exercise_name: False for exercise_name in exercise_list},
        }
    return existing_data
