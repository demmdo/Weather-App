import requests
import customtkinter as ctk
import threading
import json
import os



app = ctk.CTk()

def toggleAppearanceMode():
    if changeAppearanceMode.get() == 0:
        mode = "dark"
        ctk.set_appearance_mode(mode)


    else:
        mode = "light"
        ctk.set_appearance_mode(mode)


    try:
        with open("config/config.json", "r") as f:
            config = json.load(f)
    except:
        config = {}

    config["appearance"] = mode

    with open("config/config.json", "w") as f:
        json.dump(config, f, indent=4)


    ErrorFrame.configure(
        fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
    )


def toggleFromMetric():
    global system
    global degrees
    if changeFromMetric.get() == 0:
        system = "metric"

    if changeFromMetric.get() == 1:
        system = "imperial"

    checkSystem()

    try:
        with open("config/config.json", "r") as f:
            config = json.load(f)
    except:
        config = {}

    config["system"] = system

    with open("config/config.json", "w") as f:
        json.dump(config, f, indent=4)

    if resultPage.winfo_ismapped():
        doSearch()


switchFrame = ctk.CTkFrame(app, fg_color="transparent")
switchFrame.pack(anchor="ne")

changeAppearanceMode = ctk.CTkSwitch(switchFrame, text="Light Mode", command=toggleAppearanceMode)
changeAppearanceMode.pack(anchor="w", padx=10, pady=5)

changeFromMetric = ctk.CTkSwitch(switchFrame, text="Change to Imperial System", command=toggleFromMetric)
changeFromMetric.pack(anchor="w", padx=10, pady=5)

if os.path.exists("config/config.json"):
    with open("config/config.json", "r") as f:
        config = json.load(f)
        mode = config.get("appearance")
    if mode == "light":
        changeAppearanceMode.set(True)
    else:
        changeAppearanceMode.set(False)


ctk.set_appearance_mode(mode)

app.title("Weather App")
app.geometry("1800x900")




popup = None
mode = None
APIKey = None
system = "metric"
degrees = "°C"


def glow_effect(widget, steps=25, start_rgb=(239, 68, 68), delay=30):
    theme_color = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]

    if ctk.get_appearance_mode() == "Dark":
        end_color = theme_color[1]
    else:
        end_color = theme_color[0]


    r16, g16, b16 = app.winfo_rgb(end_color)
    end_rgb = (r16 // 256, g16 // 256, b16 // 256)

    for i in range(steps + 1):
        r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * (i / steps))
        g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * (i / steps))
        b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * (i / steps))

        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        app.after(i * delay, lambda c=hex_color: widget.configure(fg_color=c))


    app.after((steps + 1) * delay,
              lambda: widget.configure(fg_color=theme_color))

    
def returnButtonClick():
    resultPage.pack_forget()
    searchPage.pack(fill="both", expand="True")
    searchPage.pack(pady=70)


def get_current_color(widget="CTkFrame"):
    global fgColors
    fgColors = ctk.ThemeManager.theme[widget]["fg_color"]

    if ctk.get_appearance_mode() == "Dark":
        return fgColors[1]
    else:
        return fgColors[0]


def checkSystem():

    global degrees
    if system == "metric":
        degrees = "°C"
        changeFromMetric.set(False)

    elif system == "imperial":
        degrees = "°F"
        changeFromMetric.set(True)

        






if os.path.exists("config/config.json"):
    with open("config/config.json", "r") as f:
        config = json.load(f)
        system = config.get("system", "metric")
    checkSystem()

searchPage = ctk.CTkFrame(app, fg_color="transparent")
resultPage = ctk.CTkFrame(app, fg_color="transparent")

if os.path.exists("config/API.config.json"):
    with open("config/API.config.json", "r") as f:
        config = json.load(f)
        APIKey = config.get("api_key")

def openAPIPopup():
    global popup

    popup = ctk.CTkToplevel(app)
    popup.title("API Key")

    popup.update_idletasks()

    x = app.winfo_x() + (app.winfo_width() // 2) - 200
    y = app.winfo_y() + (app.winfo_height() // 2) - 100

    popup.geometry(f"400x200+{x}+{y}")

    popup.transient(app)
    popup.lift()
    popup.focus_force()
    popup.grab_set()
    popup.protocol("WM_DELETE_WINDOW", lambda: None)


    APIlabel = ctk.CTkLabel(popup, text="Enter your API key:")
    APIlabel.pack(pady=20)

    APIEntry = ctk.CTkEntry(popup, placeholder_text="API key...")
    APIEntry.pack(pady=10)

    APIErrorFrame = ctk.CTkFrame(popup, width=450, height=20)
    APIErrorLabel = ctk.CTkLabel(APIErrorFrame, text="", font=("Arial", 14))

    def getAPIkey():
        global APIKey
        APIKey = APIEntry.get()
        url = f"https://api.openweathermap.org/data/2.5/weather?q=bonn&appid={APIKey}&units=metric&lang=en"

        response = requests.get(url, timeout=5)
        APIcode = response.status_code

        def storeAPIKey():
            global APIKey

            APIKey = APIEntry.get()

            try:
                with open("config/API.config.json", "r") as f:
                    config = json.load(f)
            except:
                config = {}

            config["api_key"] = APIKey

            with open("config/API.config.json", "w") as f:
                json.dump(config, f, indent=4)

        if APIcode == 401:
            def show_error():
                print("401")
                APIErrorFrame.pack()
                APIErrorLabel.configure(text="Couldn't access the API key!")
                APIErrorLabel.pack(padx=10)
                glow_effect(APIErrorFrame, steps=50, start_rgb=(255, 68, 68), delay=10)
            app.after(0, show_error)

        if APIcode == 429:
             def show_error():
                 APIErrorFrame.pack()
                 APIErrorLabel.configure(text="Too many requests, try again later!")
                 APIErrorLabel.pack(padx=10)
                 glow_effect(APIErrorFrame, steps=50, start_rgb=(255, 68, 68), delay=10)
             app.after(0, show_error)

        if APIcode == 500:
            def show_error():
                APIErrorFrame.pack()
                APIErrorLabel.configure(text="Couldn't reach the Server, try again later!")
                APIErrorLabel.pack(padx=10)
                glow_effect(APIErrorFrame, steps=50, start_rgb=(255, 68, 68), delay=10)
            app.after(0, show_error)

        if APIcode == 200:
            storeAPIKey()
            popup.destroy()


    safeAPI = ctk.CTkButton(popup, text="Safe API key", command=getAPIkey)
    safeAPI.pack(pady=10)




if not APIKey:
    app.after(500, openAPIPopup)



searchPage.pack(fill="both", expand=True)
searchPage.pack(pady=200)

searchFrame = ctk.CTkFrame(searchPage, width=500)
searchFrame.pack(pady=30, anchor="center")

searchLabel = ctk.CTkLabel(searchFrame, text="Which city do you want to know the weather?", font=("Arial", 30))
searchLabel.pack(pady=5, padx=15)

cityEntry = ctk.CTkEntry(searchPage, placeholder_text="Enter City", font=("Arial", 22, "bold"), width=800, height=70)
cityEntry.pack(pady=10, anchor="center")

cityEntry.bind("<Return>", lambda event: doSearch())

resultTitle = ctk.CTkLabel(resultPage, text="Weather: ", font=("Arial", 60, "bold"))
resultTitle.pack(pady=20)

###################################################
####             WEATHER FRAMES                ####
###################################################

cardsFrame = ctk.CTkFrame(resultPage, fg_color="transparent")
cardsFrame.pack(fill="both", expand=True, padx=20, pady=20)

weatherTempFrame = ctk.CTkFrame(cardsFrame, width=500, height=350)
weatherTempFrame.pack(side="left", expand=True, fill="both", padx=10)
weatherTempFrame.pack_propagate(False)

weatherTempTitle = ctk.CTkLabel(weatherTempFrame, text="Temperature", font=("Arial", 45, "bold"))
weatherTempTitle.pack(expand=True, fill="both", pady=(20,10))

weatherTempLabel = ctk.CTkLabel(weatherTempFrame, font=("Arial", 25))
weatherTempLabel.pack(expand=True, anchor="n")

weatherGeneralFrame = ctk.CTkFrame(cardsFrame, width=500, height=350)
weatherGeneralFrame.pack(side="left", expand=True, fill="both", padx=10)
weatherGeneralFrame.pack_propagate(False)

weatherWindFrame = ctk.CTkFrame(cardsFrame, width=500, height=350)
weatherWindFrame.pack(side="left", expand=True, fill="both", padx=10)
weatherWindFrame.pack_propagate(False)


##################################################
####               Return Button              ####
##################################################

returnButton = ctk.CTkButton(resultPage, text="Return", command=returnButtonClick)
returnButton.pack(pady=10)


ErrorFrame = ctk.CTkFrame(searchPage)
ErrorLabel = ctk.CTkLabel(ErrorFrame, text="")

def doSearch():
    threading.Thread(target=searchWeather, daemon=True).start()

def searchWeather():

    city = cityEntry.get()

    if not city:
        return

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={APIKey}&units={system}&lang=en"


    try:
        response = requests.get(url, timeout=5)
        APIcode = response.status_code

        data = response.json()

        city = data["name"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        maxTemp = data["main"]["temp_max"]
        minTemp = data["main"]["temp_min"]

        def show_result():
            ErrorLabel.configure(text="")
            ErrorFrame.pack_forget()

            weatherTempLabel.configure(
                text=f"It is {temp}{degrees} in {city}. \n\n"
                     f"It feels like {feels_like}{degrees} and the \n\n"
                     f"max Temperature is {maxTemp}{degrees}, while\n\n"
                     f"the minimum Temperature is {minTemp}{degrees}"
            )
            searchPage.pack_forget()
            resultPage.pack(fill="both", expand=True)

        app.after(0, show_result)

    except (KeyError, requests.RequestException):

        if APIcode == 404:
            def show_error():
                ErrorFrame.pack()
                ErrorLabel.configure(text="Couldn't find the city, Check the spelling and try again!")
                ErrorLabel.pack(padx=10)
                glow_effect(ErrorFrame, steps=50, start_rgb=(255, 68, 68), delay=10)
            app.after(0, show_error)

        if APIcode == 401:
            def show_error():
                ErrorFrame.pack()
                ErrorLabel.configure(text="Couldn't access the API key!")
                ErrorLabel.pack(padx=10)
                glow_effect(ErrorFrame, steps=50, start_rgb=(255, 68, 68), delay=10)
            app.after(0, show_error)

        if APIcode == 429:
            def show_error():
                ErrorFrame.pack()
                ErrorLabel.configure(text="Too many requests, try again later!")
                ErrorLabel.pack(padx=10)
                glow_effect(ErrorFrame, steps=50, start_rgb=(255, 68, 68), delay=10)
            app.after(0, show_error)

        if APIcode == 500:
            def show_error():
                ErrorFrame.pack()
                ErrorLabel.configure(text="Couldn't reach the Server, try again later!")
                ErrorLabel.pack(padx=10)
                glow_effect(ErrorFrame, steps=50, start_rgb=(255, 68, 68), delay=10)
            app.after(0, show_error)

def showSearch():
    cityEntry.delete(0, "end")
    searchPage.pack_forget()

    resultPage.pack(fill="both", expand=True)


cityEntry.bind("<Return>", lambda event: doSearch())


app.mainloop()