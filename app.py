import screen_brightness_control as sbc
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
import shutil
import tempfile
import queue
from tkinter import messagebox
import mysql.connector
import configparser
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)





# Initialize text-to-speech engine
engine = pyttsx3.init()

custom_frame = None



speech_queue = queue.Queue()

config = configparser.ConfigParser()
config.read(resource_path("config.ini"))


def save_note_to_db(note_text):
    try:
        conn = mysql.connector.connect(
        host=config["mysql"]["host"],
         user=config["mysql"]["user"],
         password=config["mysql"]["password"],
        database=config["mysql"]["database"]
       )
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notes (content) VALUES (%s)", (note_text,))
        conn.commit()
        cursor.close()
        conn.close()
        send_email("New Note Saved", f"Here is your saved note:\n\n{note_text}")
        speak("Note saved and email sent.")

        notification.notify(
            title="Note Saved",
            message="Note has been saved to database and emailed, chandru",
            timeout=4
        )
    except Exception as e:
        print("Failed to save note:", e)
        speak("Failed to save note.")

def speech_loop():
    while True:
        text = speech_queue.get()
        if text:
            engine.say(text)
            engine.runAndWait()
        speech_queue.task_done()

# Start the speech thread once
threading.Thread(target=speech_loop, daemon=True).start()

def speak(text):
    speech_queue.put(text)

def open_vscode():
    os.startfile(r"C:\\Users\\chanm\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Visual Studio Code\\Visual Studio Code.lnk")

def open_battery_settings():
    os.system("start ms-settings:batterysaver")

def open_mail():
    chrome_path = r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    webbrowser.get(f'"{chrome_path}" %s').open("https://mail.google.com")
def show_main_window():
    global custom_frame
    if custom_frame:
        custom_frame.destroy()
        custom_frame = None
    battery_widgets.pack()  # Show main content again

def open_custom_window():
    global custom_frame
    battery_widgets.pack_forget()  # Hide main content

    custom_frame = tk.Frame(content_frame, bg="#ffffff")
    custom_frame.pack(fill="both", expand=True, pady=10)

    # ----- Brightness Control -----
    def set_brightness(level):
        try:
            sbc.set_brightness(int(level))
        except Exception as e:
            print("Brightness error:", e)

    brightness_label = tk.Label(custom_frame, text="Adjust Brightness", font=("Arial", 12), bg="#ffffff")
    brightness_label.pack()

    try:
        current_brightness = sbc.get_brightness(display=0)[0]
    except:
        current_brightness = 50  # default if reading fails

    brightness_slider = tk.Scale(
        custom_frame, from_=0, to=100, orient=tk.HORIZONTAL,
        command=lambda val: set_brightness(val), bg="#ffffff", length=200
    )
    brightness_slider.set(current_brightness)
    brightness_slider.pack(pady=10)

    # Back button to return to main window
    back_btn = tk.Button(custom_frame, text="← Back", command=show_main_window, bg="#dddddd", font=("Arial", 10, "bold"))
    back_btn.place(x=180, y=400)
    note_label = tk.Label(custom_frame, text="Enter Note", font=("Arial", 12), bg="#ffffff")
    note_label.pack(pady=(10, 2))

    note_textbox = tk.Text(custom_frame, height=5, width=40)
    note_textbox.pack(pady=5)

    
    # Button to save note
    save_note_btn = tk.Button(
    custom_frame, text="Save Note", bg="#4CAF50", fg="white",
    font=("Arial", 10, "bold"),
    command=lambda: save_note_to_db(note_textbox.get("1.0", tk.END).strip())
)
    save_note_btn.pack(pady=10)


#def clear_cache_and_temp():
#    try:
#        temp_dir = tempfile.gettempdir()
#        shutil.rmtree(temp_dir, ignore_errors=True)
#        os.makedirs(temp_dir, exist_ok=True)
#        speak("Temporary and cache files cleared successfully.")
#        notification.notify(
#            title="Cache Cleared",
#            message="Temporary and cache files have been cleared.",
#            timeout=5
#        )
#    except Exception as e:
#        speak("Failed to clear cache.")
#        print("Cache clear error:", e)

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
    sender_email = config["email"]["sender_email"]
    receiver_email = config["email"]["receiver_email"]
    password = config["email"]["password"]


    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.send_message(msg)
            print("Email sent!")
    except Exception as e:
        print("Email failed:", e)

def clear_user_temp():
    temp_path = os.environ.get("TEMP", tempfile.gettempdir())
    deleted = 0
    for file in os.listdir(temp_path):
        path = os.path.join(temp_path, file)
        try:
            if os.path.isfile(path) or os.path.islink(path):
                os.remove(path)
                deleted += 1
            elif os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
                deleted += 1
        except Exception as e:
            print(f"User temp error: {e}")
    speak(f"{deleted} files removed from TEMP.")
    notification.notify(title="TEMP Cleaned 🚀", message=f"{deleted} TEMP files removed.", timeout=5)

def clear_percent_temp():
    percent_temp_path = tempfile.gettempdir()
    deleted = 0
    for file in os.listdir(percent_temp_path):
        path = os.path.join(percent_temp_path, file)
        try:
            if os.path.isfile(path) or os.path.islink(path):
                os.remove(path)
                deleted += 1
            elif os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
                deleted += 1
        except Exception as e:
            print(f"%TEMP% error: {e}")
    speak(f"{deleted} files removed from percent TEMP.")
    notification.notify(title="%TEMP% Cleaned 🚀", message=f"{deleted} %TEMP% files removed.", timeout=5)

def clear_prefetch():
    prefetch_path = r"C:\Windows\Prefetch"
    deleted = 0
    if os.path.exists(prefetch_path):
        for file in os.listdir(prefetch_path):
            path = os.path.join(prefetch_path, file)
            try:
                if path.endswith(".pf"):
                    os.remove(path)
                    deleted += 1
            except Exception as e:
                print(f"Prefetch error: {e}")
    speak(f"{deleted} Prefetch files cleared.")
    notification.notify(title="Prefetch Cleaned 🚀", message=f"{deleted} Prefetch files removed.", timeout=5)

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

        if plugged and percent == 95 and not notified_full:
            notification.notify(
                title="Battery Full 🔋",
                message="Your battery is fully charged. You can unplug the charger.",
                timeout=5
            )
            speak("Battery is full. You can unplug the charger.")
            send_email("Battery Full", "Your battery is fully charged.")
            notified_full = True

        if not plugged and percent <= 20 and not notified_low:
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
        if plugged and percent < 100:
            notified_full = False

        root.after(5000, update_gui)

    update_gui()

# Root window
root = tk.Tk()
root.title("Battery Charging Notifier ⚡")
root.geometry("400x500")
root.resizable(False, False)
root.configure(bg="#f0f0f0")
root.iconbitmap(resource_path("assets/app_icon.ico"))


# Content frame to replace window behavior
content_frame = tk.Frame(root, bg="#ffffff")
content_frame.place(x=0, y=0, relwidth=1, relheight=1)

# Variables
battery_percent = tk.StringVar()
charging_status = tk.StringVar()
time_left = tk.StringVar()
charging_icon = tk.StringVar()
charging_icons = ["⚡", "🔌", "🔋"]
icon_index = 0

# Battery UI
battery_widgets = tk.Frame(content_frame, bg="#f0f0f0")
battery_widgets.pack()

tk.Label(battery_widgets, text="Battery LeveL", font=("Arial", 14, 'bold'), bg="#f0f0f0").pack(pady=(15, 5))
battery_label = tk.Label(battery_widgets, textvariable=battery_percent, font=("Arial", 24), bg="#f0f0f0", fg="green")
battery_label.pack()

battery_bar = ttk.Progressbar(battery_widgets, length=250, mode='determinate', maximum=100)
battery_bar.pack(pady=10)

tk.Label(battery_widgets, textvariable=charging_status, font=("Arial", 12), bg="#f0f0f0").pack()
tk.Label(battery_widgets, text="Estimated Time Left", font=("Arial", 12,'bold'), bg="#f0f0f0").pack(pady=(10, 0))
tk.Label(battery_widgets, textvariable=time_left, font=("Arial", 12, 'italic'), bg="#f0f0f0", fg="blue").pack()
tk.Label(battery_widgets, textvariable=charging_icon, font=("Arial", 26), bg="#f0f0f0").pack(pady=(10, 0))

# Buttons
tk.Button(battery_widgets, text="Open Battery Saver Settings", command=open_battery_settings).pack(pady=10)
#tk.Button(battery_widgets, text="Clear Cache & Temp Files", command=clear_cache_and_temp).pack(pady=5)

# Horizontal Frame for Icons
icon_frame = tk.Frame(battery_widgets, bg="#f0f0f0")
icon_frame.pack(pady=10)

img = Image.open(resource_path("assets/icons8-visual-studio-code-48.png"))
vscode_icon = ImageTk.PhotoImage(img)
vscode_button = tk.Label(icon_frame, image=vscode_icon, bg="#f0f0f0", cursor="hand2", bd=0)
vscode_button.pack(side=tk.LEFT, padx=10)
vscode_button.bind("<Button-1>", lambda e: open_vscode())

mail_icon_img = Image.open(resource_path("assets/icons8-mail-48.png"))
mail_icon = ImageTk.PhotoImage(mail_icon_img)
mail_button = tk.Label(icon_frame, image=mail_icon, bg="#f0f0f0", cursor="hand2", bd=0)
mail_button.pack(side=tk.LEFT, padx=10)
mail_button.bind("<Button-1>", lambda e: open_mail())

custom_img = Image.open(resource_path("assets/icons8-setting-48.png"))
custom_icon = ImageTk.PhotoImage(custom_img)
custom_button = tk.Label(icon_frame, image=custom_icon, bg="#f0f0f0", cursor="hand2", bd=0)
custom_button.pack(side=tk.LEFT, padx=10)
custom_button.bind("<Button-1>", lambda e: open_custom_window())

# In icon_frame or your preferred frame
icon_frame = tk.Frame(battery_widgets, bg="#f0f0f0")
icon_frame.pack(pady=10)

# TEMP
temp_img = Image.open(resource_path("assets/icons8-manpower-48.png"))
temp_icon = ImageTk.PhotoImage(temp_img)
temp_button = tk.Label(icon_frame, image=temp_icon, bg="#f0f0f0", cursor="hand2")
temp_button.pack(side=tk.LEFT, padx=10)
temp_button.bind("<Button-1>", lambda e: clear_user_temp())

# %TEMP%
percent_temp_img = Image.open(resource_path("assets/icons8-temp-48.png"))
percent_temp_icon = ImageTk.PhotoImage(percent_temp_img)
percent_temp_button = tk.Label(icon_frame, image=percent_temp_icon, bg="#f0f0f0", cursor="hand2")
percent_temp_button.pack(side=tk.LEFT, padx=10)
percent_temp_button.bind("<Button-1>", lambda e: clear_percent_temp())

# Prefetch
prefetch_img = Image.open(resource_path("assets/icons8-cleaning-service-48.png"))
prefetch_icon = ImageTk.PhotoImage(prefetch_img)
prefetch_button = tk.Label(icon_frame, image=prefetch_icon, bg="#f0f0f0", cursor="hand2")
prefetch_button.pack(side=tk.LEFT, padx=10)
prefetch_button.bind("<Button-1>", lambda e: clear_prefetch())


monitor_battery()
animate_charging_label()
animate_charging_icon()

root.mainloop()
