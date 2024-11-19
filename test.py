import tkinter as tk
from tkinter import filedialog
import tkintermapview # type: ignore

def animate_text(text, label, index=0):
    if index < len(text):
        label.config(text=label.cget("text") + text[index])
        root.after(100, animate_text, text, label, index + 1)

def show_main_window():
    root.destroy()
    main_window = tk.Tk()
    main_window.title("Main Application")
    main_window.geometry("800x600")
    main_window.configure(bg="black")

    # Create menu
    menubar = tk.Menu(main_window)
    main_window.config(menu=menubar)

    # File menu
    file_menu = tk.Menu(menubar, tearoff=0, bg="black", fg="#39FF14")
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Upload File", command=lambda: upload_file(main_window))

    # Create a frame to hold the map
    map_frame = tk.Frame(main_window, bg="black")
    map_frame.pack(pady=20, padx=20, fill="both", expand=True)

    # Create the map widget
    map_widget = tkintermapview.TkinterMapView(map_frame, width=700, height=500, corner_radius=0)
    map_widget.pack()

    # Set the position to Manchester, UK
    map_widget.set_position(53.4808, -2.2426)  # Latitude and Longitude of Manchester
    map_widget.set_zoom(12)  # Adjust the zoom level as needed

    main_window.mainloop()

def upload_file(window):
    file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
    if file_path:
        tk.messagebox.showinfo("File Uploaded", f"File uploaded: {file_path}", parent=window)

# Create the welcome window
root = tk.Tk()
root.title("Welcome")
root.geometry("400x200")
root.configure(bg="black")

# Create a label for the animated text
animated_label = tk.Label(root, text="", font=("Arial", 20, "bold"), fg="#39FF14", bg="black")
animated_label.pack(expand=True)

# Create and pack a frame to hold the buttons
frame = tk.Frame(root, bg="black")
frame.pack(expand=True)

# Create OK button
ok_button = tk.Button(frame, text="OK", command=show_main_window, width=10, fg="#39FF14", bg="black")
ok_button.pack(side=tk.LEFT, padx=10)

# Create Cancel button
cancel_button = tk.Button(frame, text="Cancel", command=root.quit, width=10, fg="#39FF14", bg="black")
cancel_button.pack(side=tk.LEFT, padx=10)

# Start the text animation
welcome_text = "Welcome to the Application!"
root.after(100, animate_text, welcome_text, animated_label)

# Start the main event loop
root.mainloop()
