import smtplib
import requests
from bs4 import BeautifulSoup
from price_parser import Price
import pandas as pd
from datetime import datetime

PRODUCTS_CSV = "products.csv"
PRICES_CSV = "prices.csv"
SEND_MAIL = True

# Placeholder for mail credentials and recipient
mail_user = "your_email@example.com"
mail_pass = "your_password"
mail_to = "recipient_email@example.com"

def get_amazon_search_results(product_name):
    search_url = f"https://www.amazon.in/s?k={product_name.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(search_url, headers=headers)
    return response.text

def extract_product_info(html):
    soup = BeautifulSoup(html, "lxml")
    product = soup.select_one("div.s-main-slot div.s-result-item")
    if not product:
        return None, None, None
    product_name = product.h2.text.strip()
    product_url = "https://www.amazon.in" + product.h2.a["href"]
    price = product.select_one(".a-price-whole")
    if not price:
        return product_name, product_url, None
    price = Price.fromstring(price.text)
    return product_name, product_url, price.amount_float

def save_to_csv(data, file_name):
    df = pd.DataFrame([data])
    df.to_csv(file_name, index=False, mode='a', header=not pd.io.common.file_exists(file_name))

def update_product_prices():
    if not pd.io.common.file_exists(PRODUCTS_CSV):
        return []

    df = pd.read_csv(PRODUCTS_CSV)
    updated_products = []
    for product in df.to_dict(orient='records'):
        html = get_amazon_search_results(product["product_name"])
        product_name, product_url, price = extract_product_info(html)
        if not product_name or not product_url or price is None:
            continue
        product['price'] = price
        product['url'] = product_url
        product['alert'] = False  # Update this based on your alert logic
        updated_products.append(product)
    return updated_products

def send_mail(data):
    subject = "Price Drop Alert"
    body = f"Product: {data['product_name']}\nPrice: {data['price']}\nLink: {data['url']}"
    subject_and_message = f"Subject:{subject}\n\n{body}"
    with smtplib.SMTP("smtp.server.address", 587) as smtp:
        smtp.starttls()
        smtp.login(mail_user, mail_pass)
        smtp.sendmail(mail_user, mail_to, subject_and_message)

def check_prices(product_name=None):
    if product_name:
        html = get_amazon_search_results(product_name)
        product_name, product_url, price = extract_product_info(html)
        if not product_name or not product_url or price is None:
            print("No product found with the provided name.")
            return None
        product_data = {
            "product_name": product_name,
            "url": product_url,
            "price": price,
            "alert": False
        }
        save_to_csv(product_data, PRODUCTS_CSV)
        return product_data
    else:
        updated_products = update_product_prices()
        df_updated = pd.DataFrame(updated_products)
        if not df_updated.empty:
            df_updated.to_csv(PRICES_CSV, index=False, mode='a')
            if SEND_MAIL:
                for product in updated_products:
                    send_mail(product)
        return updated_products
