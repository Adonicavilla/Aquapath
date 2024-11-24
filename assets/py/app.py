from flask import Flask, request, render_template
import mysql.connector

app = Flask(__name__)

def add_contact(name, email, phone_number):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_sms"
        )
        cursor = conn.cursor()
        cursor.execute("INSERT INTO contacts (name, email, phone_number) VALUES (%s, %s, %s)", (name, email, phone_number))
        conn.commit()
        conn.close()
        return "Contact added successfully!"
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return "Failed to add contact."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    if name and email and phone:
        result = add_contact(name, email, phone)
        return result
    else:
        return "Please enter all details", 400

if __name__ == '__main__':
    app.run(debug=True)
