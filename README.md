# Tkinter_system_monitor


### "Features included in this project" ###

🔋 Battery Monitoring Desktop App (Tkinter)
This is a desktop utility application built using Python Tkinter that monitors the system battery and provides real-time updates on the battery status. The project includes the following key features:

> Battery Monitoring:
Displays battery percentage,**charging status**, and power state using the psutil library.

> Brightness Control:
Allows users to adjust screen brightness through the app (using screen_brightness_control).

> System Notifications:
Sends battery low and full notifications using plyer.notification.(" also contain a voice notification feature")

> Notes & Database:
Provides a text area where users can write notes and save them to a MySQL database. Notes can also be emailed via the app.

> Temporary File Cleanup:
Includes functionality to clean temporary files to free up space.
---
# USER INTERFACE
                                     
   ![Screenshot 2025-06-17 232146](https://github.com/user-attachments/assets/4e85c1dd-4933-405f-a347-767021167a7a)

The main window contains features like VS Code launcher, mail access, and a temporary file clearing process to boost system speed and remove unnecessary cache files. The main purpose is to provide a battery level notifier to help improve battery life

# Second Window:
Features include:
- Send mail to friends and connect with the database
- Excel monitoring provided to view data analysis process
- Control screen brightness
- Monitor CPU temperature
- Display tips to improve cooling and system performance
                                    
---
# install all required package("From requirements.txt"):
  ```python
  pip install -r requirements.txt
  ```

# Config User Setting("config.ini file"):
  ```python
                      [database]
                     host = localhost      #user host name
                     user = your_mysql_username  
                     password = your_mysql_password  #my sql work env. password
                     database = your_database_name  

                      [email]
                     sender_email = "to"
                     receiver_email = "from"
                     password = "app password like umxxheedmcbwxpbs"
 ```

# .EXE Conversion (for Windows)
  ``` python   
                     pyinstaller \
                     --onedir \
                     --windowed \
                     --name "Battery_Assistant" \
                     --icon="assets/app_icon.ico" \
                     --add-data "assets:assets" \
                     --add-data "config.ini:." \
                     app.py
 ```
---
dependence file should be included.....
--- 

# Future Improvement:
Add an LLM (Large Language Model) integration with the Windows application to enable a chatbot that can perform system control tasks

