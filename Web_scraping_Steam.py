import json
import logging
import time
import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
import re
from email.mime.text import MIMEText
import os

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

sender_email = os.environ["EMAIL_USER"]
sender_pass = os.environ["EMAIL_PASS"]
receiver_email = os.environ["EMAIL_USER"]


def send_email_notification(sender_email: str, receiver_email: str, game_name: str, target_price: float, actual_price: float, discount=False):
    subject_discount = f"Steam discount!!!!!, {game_name}, actual price: {actual_price}"
    body_discount = f"Discount detected for {game_name}, actual price: {actual_price}"

    subject_no_discount = f"No discount for {game_name}, actual price: {actual_price}, expected: {target_price} "
    body_no_discount = f"No discount for {game_name}, actual price: {actual_price}, expected: {target_price}"

    msg = MIMEText(body_discount if discount else body_no_discount)
    msg["Subject"] = subject_discount if discount else subject_no_discount
    msg["From"] = sender_email
    msg["To"] = receiver_email

    logging.info(f"Sending email to {receiver_email}")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_pass)
        server.send_message(msg)

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
    try:
        game_id = game["id"]
        game_name = game.get('name', 'Unknown')
        game_target_price = game["target_price"]
        game_agecheck_url = f"https://store.steampowered.com/agecheck/app/{game_id}/?cc=us"
        game_url = f"https://store.steampowered.com/app/{game_id}/?cc=us"
        
        logging.info(f"Checking price for: {game_name}")

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
            logging.error(f"Error accessing the url: {game_url}, status code: {response.status_code}")            
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        game_price = soup.find("div", class_="discount_final_price") or soup.find("div", class_="game_purchase_price price")
        

        if not game_price:
            logging.warning(f"Price was not found for:  {game_name}")
            return 

        price_text = game_price.get_text(strip=True)
        price_value = parse_price(price_text)

        if price_value == -1:
            logging.warning(f"Invalid price for:  {game_name}: {price_value}")
            return 
        
        if price_value <= game_target_price:                 
            send_email_notification(sender_email=sender_email, receiver_email=receiver_email, game_name=game_name, target_price=game_target_price, actual_price=price_value, discount=True)
        else:
            send_email_notification(sender_email=sender_email, receiver_email=receiver_email, game_name=game_name, target_price=game_target_price, actual_price=price_value, discount=False)
    except Exception as e:
        logging.error(f"Failed to process {game_name}: {e}")


with open("games.json", "r") as file:
    games = json.load(file)

for game in games:
    get_game_price(game)
    time.sleep(2)
        

