import tkinter as tk
from tkinter import ttk
import psutil
import threading
import time
from plyer import notification
import os

# Function to format time nicely
def format_time(secs):
    if secs == psutil.POWER_TIME_UNLIMITED:
        return "Calculating..."
    elif secs == psutil.POWER_TIME_UNKNOWN:
        return "Unknown"
    else:
        hrs = secs // 3600
        mins = (secs % 3600) // 60
        return f"{hrs}h {mins}m"

# Function to animate charging label
def animate_charging_label():
    current_color = battery_label.cget("fg")
    new_color = "green" if current_color == "black" else "black"
    if charging_status.get().startswith("Charging"):
        battery_label.config(fg=new_color)
    else:
        battery_label.config(fg="green")  # Reset when not charging
    root.after(500, animate_charging_label)

# Charging icon animation (⚡ 🔌 🔋)
charging_icons = ["⚡", "🔌", "🔋"]
icon_index = 0
def animate_charging_icon():
    global icon_index
    if charging_status.get().startswith("Charging"):
        charging_icon.set(charging_icons[icon_index % len(charging_icons)])
        icon_index += 1
    else:
        charging_icon.set("🔋")
    root.after(700, animate_charging_icon)

# Open Battery Saver Settings
def open_battery_settings():
    os.system("start ms-settings:batterysaver")

# Battery monitor logic using root.after (safe in Tkinter)
def monitor_battery():
    notified_full = False
    notified_low = False

    def update_gui():
        nonlocal notified_full, notified_low

        battery = psutil.sensors_battery()
        percent = battery.percent
        plugged = battery.power_plugged
        secs = battery.secsleft

        battery_percent.set(f"{percent}%")
        battery_bar['value'] = percent
        charging_status.set("Charging ⚡" if plugged else "Not Charging 🔋")
        time_left.set(format_time(secs))

        # Notify when full
        if plugged and percent == 100 and not notified_full:
            notification.notify(
                title="Battery Full",
                message="Your battery is fully charged. You can unplug the charger.",
                timeout=5
            )
            notified_full = True

        

        # Notify when low
        if not plugged and percent <= 20 and not notified_low:
            notification.notify(
                title="Low Battery ⚠️",
                message="Battery is low. Consider enabling Battery Saver mode.",
                timeout=5
            )
            notified_low = True

        # Reset notifications
        if not plugged and percent > 20:
            notified_low = False
        if not plugged:
            notified_full = False

        root.after(5000, update_gui)

    update_gui()

# GUI Setup
root = tk.Tk()
root.title("Battery Charging Notifier ⚡")
root.geometry("370x320")
root.resizable(False, False)
root.configure(bg="#f0f0f0")

# Variables
battery_percent = tk.StringVar()
charging_status = tk.StringVar()
time_left = tk.StringVar()
charging_icon = tk.StringVar()

# GUI Elements
tk.Label(root, text="Battery Level", font=("Arial", 14, 'bold'), bg="#f0f0f0").pack(pady=(15, 5))
battery_label = tk.Label(root, textvariable=battery_percent, font=("Arial", 24), bg="#f0f0f0", fg="green")
battery_label.pack()

battery_bar = ttk.Progressbar(root, length=250, mode='determinate', maximum=100)
battery_bar.pack(pady=10)

tk.Label(root, textvariable=charging_status, font=("Arial", 12), bg="#f0f0f0").pack()
tk.Label(root, text="Estimated Time Left", font=("Arial", 12), bg="#f0f0f0").pack(pady=(10, 0))
tk.Label(root, textvariable=time_left, font=("Arial", 12, 'italic'), bg="#f0f0f0", fg="blue").pack()
tk.Label(root, textvariable=charging_icon, font=("Arial", 26), bg="#f0f0f0").pack(pady=(10, 0))

tk.Button(root, text="Open Battery Saver Settings", command=open_battery_settings).pack(pady=15)

# Start monitoring and animations
monitor_battery()
animate_charging_label()
animate_charging_icon()

root.mainloop()
