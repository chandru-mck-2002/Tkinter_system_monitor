import tkinter as tk
from tkinter import ttk
import psutil
import threading
import time
from plyer import notification
from PIL import Image, ImageTk
import os
import pyttsx3
import smtplib
from email.mime.text import MIMEText
import webbrowser

# Initialize text-to-speech engine
engine = pyttsx3.init()

def speak(text):
    def run():
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=run).start()

def open_vscode():
    os.startfile(r"C:\Users\chanm\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Visual Studio Code\Visual Studio Code.lnk")

def open_battery_settings():
    os.system("start ms-settings:batterysaver")

def open_mail():
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    webbrowser.get(f'"{chrome_path}" %s').open("https://mail.google.com")

def open_custom_window():
    new_window = tk.Toplevel(root)
    new_window.title("New Window")
    new_window.geometry("300x200")
    new_window.configure(bg="#ffffff")
    tk.Label(new_window, text="This is a new window", font=("Arial", 14), bg="#ffffff").pack(expand=True)

def format_time(secs, plugged):
    if secs in [psutil.POWER_TIME_UNLIMITED, psutil.POWER_TIME_UNKNOWN] or secs < 0 or secs > 86400:
        return "Estimating..." if plugged else "Unknown"
    hrs = secs // 3600
    mins = (secs % 3600) // 60
    return f"{hrs}h {mins}m until full" if plugged else f"{hrs}h {mins}m remaining"

def animate_charging_label():
    current_color = battery_label.cget("fg")
    new_color = "green" if current_color == "black" else "black"
    if charging_status.get().startswith("Charging"):
        battery_label.config(fg=new_color)
    else:
        battery_label.config(fg="green")
    root.after(500, animate_charging_label)

def animate_charging_icon():
    global icon_index
    if charging_status.get().startswith("Charging"):
        charging_icon.set(charging_icons[icon_index % len(charging_icons)])
        icon_index += 1
    else:
        charging_icon.set("🔋")
    root.after(700, animate_charging_icon)

def send_email(subject, message):
    sender_email = "your_email@example.com"
    receiver_email = "receiver_email@example.com"
    password = "your_email_password"

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.send_message(msg)
    except Exception as e:
        print("Email failed:", e)

def monitor_battery():
    notified_full = False
    notified_low = False
    previous_plugged = None

    def update_gui():
        nonlocal notified_full, notified_low, previous_plugged

        battery = psutil.sensors_battery()
        percent = battery.percent
        plugged = battery.power_plugged
        secs = battery.secsleft

        battery_percent.set(f"{percent}%")
        battery_bar['value'] = percent
        charging_status.set("Charging ⚡" if plugged else "Not Charging 🔋")
        time_left.set(format_time(secs, plugged))

        if previous_plugged is not None:
            if plugged and not previous_plugged:
                speak("Chandru, power has been plugged in.")
                send_email("Power Plugged", "Chandru, power has been plugged in.")
            elif not plugged and previous_plugged:
                speak("Chandru, power has been unplugged.")
                send_email("Power Unplugged", "Chandru, power has been unplugged.")
        previous_plugged = plugged

        if plugged and percent == 100 and not notified_full:
            notification.notify(
                title="Battery Full 🔋",
                message="Your battery is fully charged. You can unplug the charger.",
                timeout=5
            )
            speak("Battery is full. You can unplug the charger.")
            send_email("Battery Full", "Your battery is fully charged.")
            notified_full = True

        if not plugged and percent <= 30 and not notified_low:
            if plugged:
                pass
            else:
                notification.notify(
                    title="Low Battery ⚠️",
                    message="Battery is low. Consider enabling Battery Saver mode.",
                    timeout=5
                )
                speak("Battery is low. Please plug in the charger.")
                send_email("Low Battery Warning", "Battery is low. Please plug in the charger.")
                notified_low = True

        if not plugged and percent > 20:
            notified_low = False
        if not plugged:
            notified_full = False

        root.after(5000, update_gui)

    update_gui()

# Root window
root = tk.Tk()
root.title("Battery Charging Notifier ⚡")
root.geometry("400x460")
root.resizable(False, False)
root.configure(bg="#f0f0f0")

# Variables
battery_percent = tk.StringVar()
charging_status = tk.StringVar()
time_left = tk.StringVar()
charging_icon = tk.StringVar()
charging_icons = ["⚡", "🔌", "🔋"]
icon_index = 0

# Battery UI
tk.Label(root, text="Battery Level", font=("Arial", 14, 'bold'), bg="#f0f0f0").pack(pady=(15, 5))
battery_label = tk.Label(root, textvariable=battery_percent, font=("Arial", 24), bg="#f0f0f0", fg="green")
battery_label.pack()

battery_bar = ttk.Progressbar(root, length=250, mode='determinate', maximum=100)
battery_bar.pack(pady=10)

tk.Label(root, textvariable=charging_status, font=("Arial", 12), bg="#f0f0f0").pack()
tk.Label(root, text="Estimated Time Left", font=("Arial", 12), bg="#f0f0f0").pack(pady=(10, 0))
tk.Label(root, textvariable=time_left, font=("Arial", 12, 'italic'), bg="#f0f0f0", fg="blue").pack()
tk.Label(root, textvariable=charging_icon, font=("Arial", 26), bg="#f0f0f0").pack(pady=(10, 0))

# Buttons
tk.Button(root, text="Open Battery Saver Settings", command=open_battery_settings).pack(pady=10)

# Horizontal Frame for Icons
icon_frame = tk.Frame(root, bg="#f0f0f0")
icon_frame.pack(pady=10)

img = Image.open(r"C:\Users\chanm\OneDrive\Desktop\tkinterproject\image\icons8-visual-studio-code-48.png")
vscode_icon = ImageTk.PhotoImage(img)
vscode_button = tk.Label(icon_frame, image=vscode_icon, bg="#f0f0f0", cursor="hand2", bd=0)
vscode_button.pack(side=tk.LEFT, padx=10)
vscode_button.bind("<Button-1>", lambda e: open_vscode())

mail_icon_img = Image.open(r"C:\Users\chanm\OneDrive\Desktop\tkinterproject\image\icons8-mail-48.png")
mail_icon = ImageTk.PhotoImage(mail_icon_img)
mail_button = tk.Label(icon_frame, image=mail_icon, bg="#f0f0f0", cursor="hand2", bd=0)
mail_button.pack(side=tk.LEFT, padx=10)
mail_button.bind("<Button-1>", lambda e: open_mail())

# New Image Button for opening a new window
custom_img = Image.open(r"C:\Users\chanm\OneDrive\Desktop\tkinterproject\image\icons8-setting-48.png")
custom_icon = ImageTk.PhotoImage(custom_img)
custom_button = tk.Label(icon_frame, image=custom_icon, bg="#f0f0f0", cursor="hand2", bd=0)
custom_button.pack(side=tk.LEFT, padx=10)
custom_button.bind("<Button-1>", lambda e: open_custom_window())

# Start monitoring
monitor_battery()
animate_charging_label()
animate_charging_icon()

root.mainloop()
