import json
import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
import re
from email.mime.text import MIMEText
import os

game_name = "The Elder Scrolls IV: Oblivion Remastered" 
game_id = 2623190
target_price = 40
sender_email = os.environ["EMAIL_USER"]
sender_pass = os.environ["EMAIL_PASS"]
receiver_email = os.environ["EMAIL_USER"]


def send_email_notification(sender_email: str, receiver_email: str, game_name: str, target_price: float, actual_price: float, discount=False):
    subject_discount = f"Steam discount!!!!!, {game_name}, actual price: {actual_price}"
    body_discount = f"There is a discount for {game_name}, actual price: {actual_price}"

    subject_no_discount = f"No discount for {game_name}, actual price: {actual_price}, expected: {target_price} "
    body_no_discount = f"No discount for {game_name}, actual price: {actual_price}, expected: {target_price}"

    msg = MIMEText(body_discount if discount else body_no_discount)
    msg["Subject"] = subject_discount if discount else subject_no_discount
    msg["From"] = sender_email
    msg["To"] = receiver_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_pass)
        server.send_message(msg)

import re

def parse_price(price_text: str) -> float:
    if "₡" in price_text:        
        price_clean = re.sub(r"[^\d]", "", price_text) 
        return float(price_clean)
    elif "$" in price_text:        
        price_clean = re.sub(r"[^\d.]", "", price_text) 
        return float(price_clean)
    else:        
        price_clean = re.sub(r"[^\d.]", "", price_text)
        try:
            return float(price_clean)
        except ValueError:
            return -1


def get_game_price(game):
    game_id = game["id"]
    game_name = game["name"]
    game_target_price = game["target_price"]
    game_agecheck_url = f"https://store.steampowered.com/agecheck/app/{game_id}/?cc=us"
    game_url = f"https://store.steampowered.com/app/{game_id}/?cc=us"
    

    session = requests.Session()
    session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115.0.0.0 Safari/537.36" 
    })

    session.post(game_agecheck_url, data={
        "ageDay": "1",
        "ageMonth": "January",
        "ageYear": "1990"
    })

    session.cookies.set("Steam_Language", "english", domain=".steampowered.com")
    session.cookies.set("birthtime", "568022401", domain=".steampowered.com")
    session.cookies.set("lastagecheckage", "1-January-1990", domain=".steampowered.com")
    session.cookies.set("wants_currency", "1", domain=".steampowered.com")

    response = session.get(game_url)

    if response.status_code != 200:
        print(f"Status code: {response.status_code} ")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    game_price = soup.find("div", class_="discount_final_price") or soup.find("div", class_="game_purchase_price price")
    print(f"[DEBUG] {game_name} - raw price tag: '{game_price}'")

    if game_price:
        price_text = game_price.get_text(strip=True)
        price_value = parse_price(price_text)

    
    if price_value <= target_price:                 
        send_email_notification(sender_email=sender_email, receiver_email=receiver_email, game_name=game_name, target_price=game_target_price, actual_price=price_value, discount=True)
    else:
        send_email_notification(sender_email=sender_email, receiver_email=receiver_email, game_name=game_name, target_price=game_target_price, actual_price=price_value, discount=False)

   
with open("games.json", "r") as file:
    games = json.load(file)

for game in games:
    get_game_price(game)
        

