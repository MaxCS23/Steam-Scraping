# 🎮 Steam Price Watcher

A Python script that automatically checks the price of games on the Steam store and sends an email notification if the price drops below a user-defined target.

Perfect for users who want to track deals without manually checking the store. It can be run daily via GitHub Actions or a local scheduler like `cron`.

---

## 🧠 What does this project do?

- Connects to the Steam store page of each game.
- Bypasses age verification (for age-restricted games).
- Extracts the current price.
- Compares it against your desired target price.
- Sends an email notification if a discount is found (or just to report the current price).

---

## 📦 Requirements

- Python 3.8 or higher
- Gmail account (or another SMTP-compatible email service)
- A `.env` file with your credentials

---

## 🛠 Features
- Console logging (logging.INFO, logging.ERROR)
- Handles price parsing for USD and CRC (Costa Rican Colón)
- Automatic age-check handling for restricted games
- Easily configurable game list and price thresholds
- Ready for GitHub Actions or scheduled local runs

---

## 📬 Example Email
When a game is on sale:
```yaml
Subject: Steam discount!!!!!, Oblivion Remastered, actual price: 39.99
Body: Discount detected for Oblivion Remastered, actual price: 39.99
```

---

## 👤 Author
Max Cortes Serrano
QA Engineer
[LinkedIn Profile](https://www.linkedin.com/in/max-cortés-6a132b21b)
Email: maxcortes23@gmail.com
