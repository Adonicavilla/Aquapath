from flask import Flask, request, render_template
import mysql.connector
import requests
import tkinter as tk
from tkinter import messagebox

app = Flask(__name__)

def fetch_phone_numbers():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="adonicavilla02.",
            database="db_aquapath"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT phone_number FROM contacts")
        rows = cursor.fetchall()
        phone_numbers = [row[0] for row in rows]
        conn.close()
        return ','.join(phone_numbers)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return ""

def fetch_latest_sensor_data():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="adonicavilla02.",
            database="db_aquapath"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT water_lvl, location FROM tbl_sensor_value ORDER BY timestamp DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        return row if row else (None, None)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return (None, None)

def send_sms():
    apiSecret = "d876bad8084ee5626e015904752ea9b3df328588"
    deviceId = "00000000-0000-0000-29ac-666853fbd26e"
    phones = fetch_phone_numbers()

    if not phones:
        messagebox.showerror("Error", "Failed to fetch phone numbers.")
        return

    water_level, location = fetch_latest_sensor_data()
    if water_level is None or location is None:
        messagebox.showerror("Error", "Failed to fetch sensor data.")
        return

    if water_level == 0:
        message = f"""
        ********** RECEIPT **********
        Location: {location}
        Water Level: {water_level} ft
        Status: Safe way to go
        *******************************
        Do not reply to this message.
        """
    elif water_level == 1:
        message = f"""
        ********** RECEIPT **********
        Location: {location}
        Water Level: {water_level} ft
        Status: Warning: There's water
        *******************************
        Do not reply to this message.
        """
    elif water_level >= 3:
        message = f"""
        ********** RECEIPT **********
        Location: {location}
        Water Level: {water_level} ft
        Status: Street is blocked
        *******************************
        Do not reply to this message.
        """
    else:
        message = f"""
        ********** RECEIPT **********
        Location: {location}
        Water Level: {water_level} ft
        Status: General Alert
        *******************************
        Do not reply to this message.
        """

    message_data = {
        "secret": apiSecret,
        "mode": "devices",
        "campaign": "bulk test",
        "numbers": phones,
        "device": deviceId,
        "sim": 1,
        "priority": 1,
        "message": message
    }

    try:
        r = requests.post(url="https://www.cloud.smschef.com/api/send/sms.bulk", params=message_data, timeout=30)
        r.raise_for_status()
        result = r.json()
        if result.get('status') == 200:
            messagebox.showinfo("Success", "Message sent successfully!")
        else:
            messagebox.showerror("Error", f"Failed to send message: {result.get('message')}")
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        messagebox.showerror("Error", "Failed to send message. Please try again.")

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
