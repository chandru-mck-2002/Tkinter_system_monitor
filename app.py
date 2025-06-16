import tkinter as tk
from tkinter import ttk
import psutil
import threading
import time
from plyer import notification

# Function to update battery status
def monitor_battery():
    notified_full = False
    while True:
        battery = psutil.sensors_battery()
        percent = battery.percent
        plugged = battery.power_plugged
        secs = battery.secsleft

        # Update progress bar and label
        battery_percent.set(f"{percent}%")
        battery_bar['value'] = percent

        status = "Charging ⚡" if plugged else "Not Charging 🔋"
        charging_status.set(status)
        time_left.set("Time Left: " + format_time(secs))


        # Show notification when battery is full
        if plugged and percent == 100 and not notified_full:
            notification.notify(
                title="Battery Full",
                message="Your battery is fully charged. You can unplug the charger.",
                timeout=5
            )
            notified_full = True

        if not plugged:
            notified_full = False

        time.sleep(5)  # Refresh every 5 seconds
def format_time(secs):
    if secs == psutil.POWER_TIME_UNLIMITED:
        return "Calculating..."
    elif secs == psutil.POWER_TIME_UNKNOWN:
        return "Unknown"
    else:
        hrs = secs // 3600
        mins = (secs % 3600) // 60
        return f"{hrs}h {mins}m"


# Setup Tkinter window
root = tk.Tk()
root.title("Battery Charging Notifier")
root.geometry("350x200")
root.resizable(False, False)
root.configure(bg="#f0f0f0")

# Variables
battery_percent = tk.StringVar()
charging_status = tk.StringVar()
time_left = tk.StringVar()


# Battery label
tk.Label(root, text="Battery Level", font=("Arial", 14, 'bold'), bg="#f0f0f0").pack(pady=(20, 5))
battery_label = tk.Label(root, textvariable=battery_percent, font=("Arial", 24), bg="#f0f0f0", fg="green")
battery_label.pack()

# Progress bar
battery_bar = ttk.Progressbar(root, length=250, mode='determinate', maximum=100)
battery_bar.pack(pady=10)

# Charging status
status_label = tk.Label(root, textvariable=charging_status, font=("Arial", 12), bg="#f0f0f0")
status_label.pack()
tk.Label(root, textvariable=time_left, font=("Arial", 12), bg="#f0f0f0").pack(pady=(5, 0))

# Start monitoring in background
threading.Thread(target=monitor_battery, daemon=True).start()

root.mainloop()
