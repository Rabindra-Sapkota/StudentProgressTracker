import tkinter as tk
import constants

from tkinter import (
    ttk,
    messagebox,
    filedialog,
    Toplevel,
    Label,
    StringVar,
    Button,
    Frame,
    LEFT,
    BOTH,
    END,
    Checkbutton,
    BooleanVar,
)
from data_handler import load_data, save_data, import_csv_data
from dialogs import get_long_input
from email_utils import send_progress_email
from constants import EXERCISES
import os


class StudentTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()

        self.class_name = None
        self.selected_student = None
        self.data = {}
        self.select_class()

    def select_class(self):
        class_dialog = Toplevel()
        class_dialog.title("Select Class")
        class_dialog.geometry("400x200")
        class_dialog.grab_set()

        Label(class_dialog, text="Select or Create a Class", font=("Arial", 14)).pack(
            pady=10
        )

        class_files = [f[:-5] for f in os.listdir("classes") if f.endswith(".json")]
        class_var = StringVar()

        dropdown = ttk.Combobox(
            class_dialog, textvariable=class_var, values=class_files, state="readonly"
        )
        dropdown.pack(pady=10)

        def on_select():
            class_name = class_var.get()
            if class_name:
                self.class_name = class_name
                self.data_file = os.path.join("classes", f"{class_name}.json")
                class_dialog.destroy()
                self.finish_initialization()

        def on_create():
            new_class = get_long_input("New Class", "Enter new class name:")
            if new_class:
                self.class_name = new_class
                self.data_file = os.path.join("classes", f"{new_class}.json")
                class_dialog.destroy()
                self.finish_initialization()

        Button(class_dialog, text="Select Class", command=on_select).pack(pady=5)
        Button(class_dialog, text="Add New Class", command=on_create).pack(pady=5)

        class_dialog.wait_window()

    def finish_initialization(self):
        self.root.title(f"Progress Tracker - {self.class_name}")
        self.root.deiconify()
        self.data = load_data(self.data_file)
        self.setup_ui()
        self.refresh_student_list()

    def setup_ui(self):
        control_frame = Frame(self.root)
        control_frame.pack(pady=10)

        Button(control_frame, text="Enroll Student", command=self.add_student).pack(
            side=LEFT, padx=5
        )
        Button(control_frame, text="Edit Student", command=self.edit_student).pack(
            side=LEFT, padx=5
        )
        Button(control_frame, text="Remove Student", command=self.remove_student).pack(
            side=LEFT, padx=5
        )
        Button(
            control_frame,
            text="Check Exercise",
            command=self.mark_exercise_complete,
        ).pack(side=LEFT, padx=5)

        Button(control_frame, text="Send Message", command=self.send_mail).pack(
            side=LEFT, padx=5
        )
        Button(control_frame, text="Import from CSV", command=self.import_csv).pack(
            side=LEFT, padx=5
        )

        self.tree = ttk.Treeview(
            self.root,
            columns=("name", "email", "progress", "completed", "pending"),
            show="headings",
        )
        self.tree.heading("name", text="Name")
        self.tree.heading("email", text="Email Address")
        self.tree.heading("progress", text="Progress (%)")
        self.tree.heading("completed", text="Completed Exercises")
        self.tree.heading("pending", text="Pending Exercises")
        self.tree.pack(fill=BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def refresh_student_list(self):
        self.tree.delete(*self.tree.get_children())
        for email, info in self.data.items():
            progress, completed_exercises, incomplete_exercises = calculate_progress(
                info
            )
            self.tree.insert(
                "",
                END,
                iid=email,
                values=(
                    info["name"],
                    email,
                    progress,
                    completed_exercises,
                    incomplete_exercises,
                ),
            )

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.selected_student = selected[0]

    def add_student(self):
        name = get_long_input("Student Name", "Enter student's full name:")
        email = get_long_input("Email", "Enter student's email:")

        if not name:
            messagebox.showwarning("Missing Data", "Name is required.")
            return

        if not email:
            messagebox.showwarning("Missing Data", "Email is required.")
            return

        if email in self.data:
            messagebox.showerror("Duplicate", "Student already exists with same email.")
            return

        self.data[email] = {
            "name": name,
            "exercises": {exercise_name: False for exercise_name in EXERCISES},
        }
        save_data(self.data_file, self.data)
        self.refresh_student_list()

    def edit_student(self):
        if not self.selected_student:
            messagebox.showwarning("No Selection", "Select a student to edit.")
            return

        old_email = self.selected_student
        old_data = self.data[old_email]

        new_name = get_long_input(
            "Edit Name", "Edit student's name:", initial_value=old_data["name"]
        )

        new_email = get_long_input(
            "Edit Email", "Edit student's email:", initial_value=old_email
        )

        if not new_name or not new_email:
            messagebox.showwarning("Missing Data", "Both name and email are required.")
            return

        # If name changed and new name already exists
        if new_email != old_email and new_email in self.data:
            messagebox.showerror(
                "Duplicate", "Another student with this name already exists."
            )
            return

        # Update data
        if new_email != old_email:
            # Rename key
            self.data[new_email] = self.data.pop(old_email)
            self.selected_student = new_email  # Update selected student key

        self.data[new_email]["name"] = new_name

        save_data(self.data_file, self.data)
        self.refresh_student_list()

    def remove_student(self):
        if not self.selected_student:
            messagebox.showwarning("No Selection", "Select a student to remove.")
            return
        del self.data[self.selected_student]
        save_data(self.data_file, self.data)
        self.selected_student = None
        self.refresh_student_list()

    def mark_exercise_complete(self):
        if not self.selected_student:
            messagebox.showwarning("No Selection", "Select a student first.")
            return

        student = self.data[self.selected_student]
        window = Toplevel()
        window.title(f"Mark Tasks for {student.get("name")}")
        window.geometry("450x300")  # width x height
        window.grab_set()

        Label(
            window,
            text=f"Mark completed tasks for {student.get("name")}",
            font=("Arial", 14),
        ).pack(pady=10)

        check_vars = {}

        frame = Frame(window)
        frame.pack(padx=20, pady=10)

        # Exercises
        for i, (ex_name, done) in enumerate(student["exercises"].items()):
            var = BooleanVar(value=done)
            check_vars[ex_name] = var
            Checkbutton(
                frame,
                text=ex_name,
                variable=var,
            ).grid(
                row=i // 3,
                column=i % 3,
                sticky="w",
                pady=2,
            )

        def save_and_close():
            for key, var in check_vars.items():
                if key in student["exercises"]:
                    student["exercises"][key] = var.get()
                else:
                    student[key] = var.get()
            save_data(self.data_file, self.data)
            self.refresh_student_list()
            window.destroy()

        Button(window, text="Save", command=save_and_close).pack(pady=10)

    def send_mail(self):
        for student_email, student_detail in self.data.items():
            try:
                student_name = student_detail.get("name")
                progress, completed, pending = calculate_progress(student_detail)

                mail_body = constants.MAIL_BODY.format(
                    student_name=student_name,
                    progress=progress,
                    completed=completed,
                    incomplete=pending,
                )
                send_progress_email([student_email], constants.MAIL_SUBJECT, mail_body)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send email: {e}")
        messagebox.showinfo("Success", "Message sent successfully.")

    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not path:
            return
        try:
            updated_data = import_csv_data(path, self.data)
            self.data.update(updated_data)
            save_data(self.data_file, self.data)
            self.refresh_student_list()
            messagebox.showinfo("Import Successful", "Students imported from CSV.")
        except Exception as e:
            messagebox.showerror("Import Failed", str(e))


def calculate_progress(student):
    exercises = student["exercises"]
    progress = round((sum(exercises.values()) / len(exercises)) * 100, 2)

    completed_exercises = [
        exercise_name
        for exercise_name, is_completed in exercises.items()
        if is_completed
    ]
    incomplete_exercises = [
        exercise_name
        for exercise_name, is_completed in exercises.items()
        if not is_completed
    ]
    completed_exercises_name = ", ".join(completed_exercises)
    incomplete_exercises_name = ", ".join(incomplete_exercises)
    return progress, completed_exercises_name, incomplete_exercises_name
