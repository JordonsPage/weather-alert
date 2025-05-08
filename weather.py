import smtplib
from email.message import EmailMessage
import requests
from datetime import datetime

def get_weather_ct():
    """Get current weather for Connecticut (using Hartford as reference)"""
    api_key = "d52d54440d0a700b969cc4311106d243" 
    city = "Hartford"
    state_code = "CT"
    country_code = "US"
    
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city},{state_code},{country_code}&appid={api_key}&units=imperial"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            
            
            weather_msg = f"{desc.capitalize()}, {int(temp)}°F in CT"
            
            return weather_msg
        else:
            print(f"API Error: {data}") 
            return "Weather unavailable"
    
    except Exception as e:
        print(f"Exception: {e}") 
        return "Weather unavailable"

def email_alert(to, subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg["subject"] = subject
    msg["to"] = to
    
    user = "jordon.quinn1@gmail.com"
    msg["from"] = user
    password = "dkbmcbkjgwjojgne"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)

    server.quit()

if __name__ == "__main__":
    
    weather_info = get_weather_ct()
    print(f"Weather info: {weather_info}")  
    

    email_alert("jordon.quinn3@gmail.com", f"Weather: {weather_info}", "Current weather update")