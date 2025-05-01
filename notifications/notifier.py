import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_CONFIG

def send_email_notification(car):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_CONFIG["email"]
    msg["To"] = EMAIL_CONFIG["email"]
    msg["Subject"] = "New Car Matching Your Criteria"

    body = f"New car found:\n\nBrand: {car['brand']}\nModel: {car['model']}\nPrice: {car['price']}\nLink: {car['link']}"
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
        server.starttls()
        server.login(EMAIL_CONFIG["email"], EMAIL_CONFIG["password"])
        server.send_message(msg)

def show_popup_notification(car):
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("New Car Alert", f"New {car['brand']} {car['model']} found!\nPrice: {car['price']}\nLink: {car['link']}")
