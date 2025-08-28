import tkinter as tk
from tkinter import messagebox, simpledialog
import subprocess
import json
import os
import smtplib
from email.mime.text import MIMEText
from PIL import Image, ImageTk
import threading
import time
import webbrowser
import cv2  # Import OpenCV for video capturing

# Global variables
email_settings = {}
password = None  # Store the password for camera operations

# Function to load email settings and password from a configuration file
def load_email_settings():
    global email_settings, password
    if os.path.exists('email_config.json'):
        with open('email_config.json', 'r') as f:
            email_settings = json.load(f)
            password = email_settings.get('PASSWORD')  # Load the password from the config
    else:
        setup_email()

# Function to set up email and password at the start
def setup_email():
    global email_settings, password
    while True:
        email_address = simpledialog.askstring("Email Setup", "Enter your email address:")
        if email_address is None:
            continue

        email_password = simpledialog.askstring("Email Setup", "Enter your email password (or app password):", show="*")
        if email_password is None:
            continue

        recipient_email = simpledialog.askstring("Email Setup", "Enter the recipient email (optional):")
        if recipient_email is None:
            continue

        password = simpledialog.askstring("Password Setup", "Set a password for enabling/disabling the camera:", show="*")
        if password is None:
            continue

        email_settings = {
            'EMAIL_ADDRESS': email_address,
            'EMAIL_PASSWORD': email_password,
            'TO_EMAIL': recipient_email if recipient_email else email_address,
            'PASSWORD': password
        }
        save_email_settings()
        break

# Function to save email settings to a JSON file
def save_email_settings():
    global email_settings
    with open('email_config.json', 'w') as f:
        json.dump(email_settings, f)

# Function to send an email notification
def send_email(subject, message):
    global email_settings
    try:
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = email_settings['EMAIL_ADDRESS']
        msg['To'] = email_settings['TO_EMAIL']

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_settings['EMAIL_ADDRESS'], email_settings['EMAIL_PASSWORD'])
            server.send_message(msg)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send email: {str(e)}")

# Function to handle incorrect password attempts
def send_email_alert():
    subject = "Unauthorized Access Alert"
    message = "An incorrect password was entered."
    send_email(subject, message)

# Function to capture a 10-second video when incorrect password is entered
def capture_video():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('intrusion_video.avi', fourcc, 20.0, (640, 480))

    start_time = time.time()
    while int(time.time() - start_time) < 10:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
        else:
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

# Function to disable the camera using a batch file
def disable_camera():
    result = subprocess.run([r'disable_cam.bat'], shell=True)
    if result.returncode == 0:
        messagebox.showinfo("Success", "Camera disabled successfully.")
    else:
        messagebox.showerror("Error", "Failed to disable the camera.")

# Function to enable the camera using a batch file
def enable_camera():
    result = subprocess.run([r'enable_cam.bat'], shell=True)
    if result.returncode == 0:
        messagebox.showinfo("Success", "Camera enabled successfully.")
    else:
        messagebox.showerror("Error", "Failed to enable the camera.")

# Define the function to be executed when the disable button is clicked
def button1_clicked():
    password_window = tk.Toplevel(root)
    password_window.title("Enter Password")
    password_window.geometry("300x200")
    password_label = tk.Label(password_window, text="Enter Password:")
    password_label.pack()
    password_entry = tk.Entry(password_window, show="*")
    password_entry.pack()

    def ok_button():
        if password_entry.get() == password:
            disable_camera()
            password_window.destroy()
            success_label.config(text="Camera Disabled Successfully")
        else:
            error_label.config(text="Incorrect password. Please try again.")
            password_entry.delete(0, tk.END)
            send_email_alert()
            threading.Thread(target=capture_video).start()  # Start video capture in a separate thread

    ok_button = tk.Button(password_window, text="OK", command=ok_button)
    ok_button.pack()

    error_label = tk.Label(password_window, text="", font=("Arial", 12), bg="#f2f2f2", fg="#ff0000")
    error_label.pack()

# Define the function to be executed when the enable button is clicked
def button2_clicked():
    password_window = tk.Toplevel(root)
    password_window.title("Enter Password")
    password_window.geometry("300x200")
    password_label = tk.Label(password_window, text="Enter Password:")
    password_label.pack()
    password_entry = tk.Entry(password_window, show="*")
    password_entry.pack()

    def ok_button():
        if password_entry.get() == password:
            enable_camera()
            password_window.destroy()
            success_label.config(text="Camera Enabled Successfully")
        else:
            error_label.config(text="Incorrect password. Please try again.")
            password_entry.delete(0, tk.END)
            send_email_alert()
            threading.Thread(target=capture_video).start()  # Start video capture in a separate thread

    ok_button = tk.Button(password_window, text="OK", command=ok_button)
    ok_button.pack()

    error_label = tk.Label(password_window, text="", font=("Arial", 12), bg="#f2f2f2", fg="#ff0000")
    error_label.pack()

# Function to open the project information page in Chrome
def open_project_info():
    url = 'https://ibb.co/MCctmf8'
    webbrowser.open(url, new=2)

# Setup the main GUI
root = tk.Tk()
root.title("Webcam Spyware Security Tool")
root.geometry("500x400")

# Set custom icon for the window
try:
    root.iconbitmap('ico.ico')
except Exception as e:
    messagebox.showerror("Error", f"Icon file not found: {str(e)}")

# Background image setup
try:
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    bg_image = Image.open("back.png")
    bg_image = bg_image.resize((screen_width, screen_height), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    background_label = tk.Label(root, image=bg_photo)
    background_label.place(relwidth=1, relheight=1)
except FileNotFoundError:
    messagebox.showerror("Error", "Background image not found.")
    root.quit()

# Buttons for enabling and disabling the camera
button_font = ("Arial", 9, "bold")

disable_button = tk.Button(root, text="Disable Camera", command=button1_clicked, bg="red", fg="white", font=button_font, width=20, height=3)
disable_button.place(relx=0.4, rely=0.65, anchor=tk.CENTER)

enable_button = tk.Button(root, text="Enable Camera", command=button2_clicked, bg="green", fg="white", font=button_font, width=20, height=3)
enable_button.place(relx=0.6, rely=0.65, anchor=tk.CENTER)

# "Project Information" label that opens a webpage
project_label = tk.Label(root, text="Project Information", fg="Blue", cursor="hand2", font=("Arial", 14, "bold"))
project_label.place(relx=0.5, rely=0.75, anchor=tk.CENTER)

# Bind the click event to open the URL
project_label.bind("<Button-1>", lambda e: open_project_info())

# Load email settings
load_email_settings()

root.mainloop()
