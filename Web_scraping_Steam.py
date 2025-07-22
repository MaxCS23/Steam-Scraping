import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
import re
from email.mime.text import MIMEText
import os

game_name = "The Elder Scrolls IV: Oblivion Remastered" 
game_id = 2623190
target_price = 20000
sender_email = os.environ["EMAIL_USER"]
sender_pass = os.environ["EMAIL_PASS"]
receiver_email = os.environ["EMAIL_USER"]
game_agecheck_url = f"https://store.steampowered.com/agecheck/app/{game_id}/"
game_url = f"https://store.steampowered.com/app/{game_id}/"

def send_email_notification(sender_email: str, receiver_email: str, discount=False):
    subject_discount = f"Steam discount!!!!!, {game_name}, actual price: {price_value}"
    body_discount = f"There is a discount for {game_name}, actual price: {price_value}"

    subject_no_discount = f"No discount for {game_name}, actual price: {price_value}, expected: {target_price} "
    body_no_discount = f"No discount for {game_name}, actual price: {price_value}, expected: {target_price}"

    msg = MIMEText(body_discount if discount else body_no_discount)
    msg["Subject"] = subject_discount if discount else subject_no_discount
    msg["From"] = sender_email
    msg["To"] = receiver_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_pass)
        server.send_message(msg)

session = requests.Session()

session.headers.update({
   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115.0.0.0 Safari/537.36" 
})

session.post(game_agecheck_url, data={
    "ageDay": "1",
    "ageMonth": "January",
    "ageYear": "1990"
})

session.cookies.set("birthtime", "568022401", domain=".steampowered.com")
session.cookies.set("lastagecheckage", "1-January-1990", domain=".steampowered.com")

response = session.get(game_url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    game_price = soup.find("div", class_="game_purchase_price price")
    if not game_price:
        game_price = soup.find("div", class_="discount_final_price")

    if game_price:
        game_price_str = game_price.get_text(strip=True)
        price_clean = re.sub(r"[^\d]", "", game_price_str)
        price_value = int(price_clean)
        print(f"{game_name} price is: {price_value}")

        if price_value <= target_price:            
            send_email_notification(sender_email=sender_email, receiver_email=receiver_email,discount=True)
        else:
            send_email_notification(sender_email=sender_email, receiver_email=receiver_email)
    else:        
        print("Game price not found.")
else:
    print(f"Execution error, response code: {response.status_code}")