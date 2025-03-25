import subprocess
import tkinter as tk
from tkinter import messagebox
import os
import threading

# Path to the batch files
batch_files = {
    "1": "Delete Temp Files.bat",
    "2": "Network Reset Utility.bat",
    "3": "System Health Check.bat",
    "4": "Task Slayer.bat"
}

# Task names for UI (without .bat suffix)
task_names_ui = {
    "1": "Delete Temp Files",
    "2": "Network Reset Utility",
    "3": "System Health Check",
    "4": "Task Slayer"
}

# Function to execute a batch file with elevated privileges using PowerShell
def execute_batch(batch_file, task_name):
    if not os.path.exists(batch_file):
        messagebox.showerror("Error", f"{task_name} is missing or not found.")
        return

    try:
        # Use PowerShell to run the batch file as administrator
        command = f"PowerShell Start-Process cmd.exe -ArgumentList '/c {batch_file}' -Verb RunAs"
        result = subprocess.run(command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)

        if result.returncode == 0:
            messagebox.showinfo("Success", f"{task_name} completed successfully!")
        else:
            messagebox.showerror("Error", f"An error occurred while executing {task_name}. The task may not be working properly.\n{result.stderr.decode()}")
    except subprocess.TimeoutExpired:
        messagebox.showerror("Error", f"{task_name} took too long to complete and was terminated.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error while executing {task_name}. \n{e}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

# Function to run all batch files (in separate threads)
def run_all():
    for batch_file, task_name in zip(batch_files.values(), task_names_ui.values()):
        thread = threading.Thread(target=execute_batch, args=(batch_file, task_name))
        thread.start()

# Create the main window
root = tk.Tk()
root.title("Ultimate System Tuner")

# Define window size and appearance
window_width = 500
window_height = 600

# Get screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculate the position to center the window
x_position = int(screen_width / 2 - window_width / 2)
y_position = int(screen_height / 2 - window_height / 2)

# Set the window position and size
root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
root.config(bg="lightgray")

# Add a header label with some style
header_label = tk.Label(root, text="Choose a Task", font=("Arial", 20, "bold"), bg="lightgray")
header_label.pack(pady=20)

# Create a frame for buttons to add some padding around them
button_frame = tk.Frame(root, bg="lightgray")
button_frame.pack(pady=30)

# Function to create buttons with style
def create_button(task_key, task_name):
    button = tk.Button(button_frame, text=task_name, width=20, height=2, font=("Arial", 14), bg="#4CAF50", fg="white",
                       relief="solid", bd=3, command=lambda batch=batch_files[task_key], name=task_name: execute_batch(batch, name))
    button.grid(row=int(task_key)-1, column=0, pady=10, padx=10)
    return button

# Create buttons for each batch file
buttons = {}
for key, name in task_names_ui.items():
    buttons[key] = create_button(key, name)

# Button to run all batch files
run_all_button = tk.Button(root, text="Run All Tasks", width=20, height=2, font=("Arial", 14), bg="#2196F3", fg="white",
                           relief="solid", bd=3, command=run_all)
run_all_button.pack(pady=20)

# Bind numpad keys (1-4) to the corresponding buttons
def on_numpad_key(event, key):
    buttons[key].invoke()  # Simulate button click

# Fix numpad key bindings
root.bind("<KP_1>", lambda event: on_numpad_key(event, "1"))
root.bind("<KP_2>", lambda event: on_numpad_key(event, "2"))
root.bind("<KP_3>", lambda event: on_numpad_key(event, "3"))
root.bind("<KP_4>", lambda event: on_numpad_key(event, "4"))

# Start the Tkinter event loop
root.mainloop()
