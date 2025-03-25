import os
import subprocess
import tkinter as tk
from tkinter import messagebox

# Path to the batch files
batch_files = {
    "1": "Delete Temp Files.bat",
    "2": "Network Reset Utility.bat",
    "3": "System Health Check.bat",
    "4": "Task Slayer.bat"
}

# Function to execute a batch file
def execute_batch(batch_file):
    try:
        subprocess.run(batch_file, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"An error occurred while executing {batch_file}.\n{e}")
    else:
        messagebox.showinfo("Success", f"{batch_file} executed successfully!")

# Function to run all batch files
def run_all():
    for batch_file in batch_files.values():
        execute_batch(batch_file)

# Create the main window
root = tk.Tk()
root.title("Batch File Executor")

# Define window size and appearance
root.geometry("400x400")
root.config(bg="lightgray")

# Add a header label
header_label = tk.Label(root, text="Choose a Task", font=("Helvetica", 16), bg="lightgray")
header_label.pack(pady=20)

# Create buttons for each batch file
for key, batch_file in batch_files.items():
    button = tk.Button(root, text=f"Run Task {key}", width=20, height=2,
                       command=lambda batch=batch_file: execute_batch(batch))
    button.pack(pady=10)

# Button to run all batch files
run_all_button = tk.Button(root, text="Run All Tasks", width=20, height=2, command=run_all)
run_all_button.pack(pady=20)

# Start the Tkinter event loop
root.mainloop()
