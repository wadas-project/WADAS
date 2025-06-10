"""Module that simulates a road sign actuator"""

import requests
import urllib3

from tkinter import Frame, Label, PhotoImage, Tk

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://localhost:8443/api/v1/actuators/"
ACTUATOR_ID = "A98DB973KWL8XP1L"

count = 0
flag = False


def check_update():
    global count, flag

    if count == 10:
        traffic_sign.config(fg="black")
        count = 0
        flag = False

    try:
        response = requests.get(f"{URL}{ACTUATOR_ID}", verify=False)
        if (
            response.status_code == 200
            and "display" in response.json()
            and response.json()["display"]
        ):
            count = 0
            flag = True
            traffic_sign.config(fg="#d84b20")
    except requests.exceptions.ConnectionError:
        print("Failed to establish connection")

    count += flag
    root.after(5000, check_update)


root = Tk()
root.title("WADAS TRAFFIC SIGN")
# root.maxsize(1000, 1000)
root.config(bg="white")

# Create frames
upper_frame = Frame(root, width=600, height=300, bg="white")
lower_frame = Frame(root, width=600, height=300, bg="grey")

# Create main label
upper_label = Label(upper_frame, text="WADAS", bg="white", font=("Sans-Serif", 24, "bold"))
upper_label.pack()

# Add road sign image to the frame
image = PhotoImage(file="road_sign.png")
new_image = image.zoom(2, 2)
final_image = new_image.subsample(3, 3)
image_label = Label(upper_frame, image=final_image)
image_label.pack(fill="x", expand=True)

# Add road sign text to the frame
traffic_sign = Label(
    lower_frame,
    text="ATTENZIONE ANIMALI\nIN CARREGGIATA",
    bg="black",
    fg="black",
    font=("Sans-Serif", 32, "bold"),
)
traffic_sign.pack(padx=10, pady=10)
upper_frame.pack(side="top", fill="both", expand=True)
lower_frame.pack(side="bottom", pady=(5, 30), padx=10)

# Start periodic checks
root.after(5000, check_update)

root.mainloop()
