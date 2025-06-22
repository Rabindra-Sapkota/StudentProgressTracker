import tkinter as tk


def get_long_input(title, prompt, initial_value=""):
    dialog = tk.Toplevel()
    dialog.title(title)
    dialog.geometry("400x150")
    dialog.grab_set()

    tk.Label(dialog, text=prompt, font=("Arial", 12)).pack(padx=20, pady=(20, 5))
    entry_var = tk.StringVar(value=initial_value)
    entry = tk.Entry(dialog, textvariable=entry_var, font=("Arial", 12), width=40)
    entry.pack(padx=20, pady=10)
    entry.focus()

    result = {}

    def on_submit():
        result["value"] = entry_var.get()
        dialog.destroy()

    tk.Button(dialog, text="OK", command=on_submit, width=10).pack(pady=10)
    dialog.wait_window()
    return result.get("value")
