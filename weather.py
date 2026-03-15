import requests
import json
import os
from datetime import datetime
from twilio.rest import Client

ACCOUNT_SID = "your_account_sid"
AUTH_TOKEN  = "your_auth_token"
FROM_NUMBER = "your_twilio_number"   
TO_NUMBER   = "your_real_number"     


API_KEY = "your_openweathermap_key"
CITY    = "Hartford"
STATE   = "CT"
COUNTRY = "US"


LOG_FILE = "alert_log.json"


def get_weather():
    """grab weatehr"""
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={CITY},{STATE},{COUNTRY}&appid={API_KEY}&units=imperial"
    )
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            temp        = data["main"]["temp"]
            description = data["weather"][0]["description"]
            main        = data["weather"][0]["main"].lower()  # "rain", "snow", etc.
            return {"temp": temp, "description": description, "main": main}
        else:
            print(f"API Error: {data}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None


def check_conditions(weather):
    """Return a list of triggered alert reasons."""
    reasons = []
    if weather["temp"] <= 32:
        reasons.append(f"Freezing temp: {int(weather['temp'])}°F")
    if weather["temp"] >= 90:
        reasons.append(f"Extreme heat: {int(weather['temp'])}°F")
    if weather["main"] in ("rain", "snow", "drizzle", "thunderstorm"):
        reasons.append(f"{weather['description'].capitalize()} detected")
    return reasons


def send_sms(message):
    """sends message to #"""
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    msg = client.messages.create(
        body=message,
        from_=FROM_NUMBER,
        to=TO_NUMBER
    )
    print(f"SMS sent: {msg.sid}")
    return msg.sid


def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return []


def save_log(log):
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def run():
    weather = get_weather()
    if not weather:
        print("Could not fetch weather.")
        return

    print(f"Weather: {weather['description']}, {int(weather['temp'])}°F")

    reasons = check_conditions(weather)
    if not reasons:
        print("No alert conditions met.")
        return

    """makes msg"""
    alert_text = " Weather Alert:\n" + "\n".join(f"- {r}" for r in reasons)
    print(alert_text)

    
    log = load_log()
    unacknowledged = [e for e in log if not e["acknowledged"]]

    if unacknowledged:
        
        followup = f"Follow-up (unacknowledged):\n{alert_text}"
        sid = send_sms(followup)
        
        for e in unacknowledged:
            e["acknowledged"] = True
        log.append({
            "timestamp": datetime.now().isoformat(),
            "message": followup,
            "sid": sid,
            "acknowledged": False,
            "type": "followup"
        })
    else:
        sid = send_sms(alert_text)
        log.append({
            "timestamp": datetime.now().isoformat(),
            "message": alert_text,
            "sid": sid,
            "acknowledged": False,
            "type": "initial"
        })

    save_log(log)


def acknowledge():
    """Call this manually to mark latest alert as acknowledged."""
    log = load_log()
    for e in log:
        if not e["acknowledged"]:
            e["acknowledged"] = True
    save_log(log)
    print("All alerts acknowledged.")


if __name__ == "__main__":
    run()
