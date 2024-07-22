import datetime
import os
import pandas as pd

def load_appointments():
    if not os.path.exists('appointments.csv'):
        return pd.DataFrame(columns=['date', 'time', 'user_name', 'email', 'phone_number'])
    return pd.read_csv('appointments.csv')

def save_appointments(appointments):
    appointments.to_csv('appointments.csv', index=False)

def check_current_date(input_date_str):
    print(input_date_str)

    # Parse the input date string into a datetime object
    input_date = datetime.datetime.strptime(input_date_str, "%Y-%m-%d %H:%M:%S")
    
    # Get the current date and time
    now = datetime.datetime.now()
    
    # Compare the input date with the current date
    if input_date < now:
        return "Day already passed, impossible to book"
    else:
        return "Booking is possible"
    
def check_availability(date, time):
    appointments = load_appointments()
    for index, row in appointments.iterrows():
        if row['date'] == date and row['time'] == time:
            return "Requested time is not available"
    return "True"

def book_appointment(date, time, user_name, email, phone_number):
    if "Requested time is not available" in check_availability(date, time):
        return "The requested slot is already booked."
    new_appointment = {'date': date, 'time': time, 'user_name': user_name, 'email': email, 'phone_number': phone_number}
    appointments = load_appointments()
    appointments = pd.concat([appointments, pd.DataFrame([new_appointment])], ignore_index=True)
    save_appointments(appointments)
    return f"Your appointment is booked for {date} at {time}."

def query_appointment_by_email(email):
    appointments = load_appointments()
    user_appointments = appointments[appointments['email'] == email]
    if user_appointments.empty:
        return f"No appointments found for email: {email}"
    return user_appointments.to_string()