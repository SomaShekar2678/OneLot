import re
from datetime import datetime

import psycopg2
import requests
from bs4 import BeautifulSoup


def get_db_connection():
    return psycopg2.connect(
        dbname="car_db",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432",
    )


def scrape_cars():
    base_url = "https://philkotse.com"
    conn = get_db_connection()  # establish a connection to a database
    cur = conn.cursor()  # create a cursor object to execute SQL commands
    cnt = 0

    try:
        i = 1
        while True:
            url = f"https://philkotse.com/used-cars-for-sale/p{i}"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")

            col_4_divs = soup.find_all("div", class_="col-4")
            if len(col_4_divs) < 4:
                break
            print(f"Page {i} - Found {len(col_4_divs)} cars")

            for div in col_4_divs:
                try:
                    link_tag = div.find("a", href=True)
                    if not link_tag:
                        continue

                    relative_url = link_tag["href"]
                    full_url = base_url + relative_url
                    linked_response = requests.get(full_url)
                    linked_soup = BeautifulSoup(linked_response.text, "html.parser")

                    car_details = {}

                    # Extract car details
                    parameter_info = linked_soup.find("div", class_="parameter-info")
                    if parameter_info:
                        spec_list = parameter_info.find("ul", class_="list")
                        if spec_list:
                            items = spec_list.find_all("li")
                            car_specs = []
                            for item in items:
                                for icon in item.find_all("i"):
                                    icon.decompose()
                                spec_text = item.get_text(strip=True)
                                if spec_text:
                                    car_specs.append(spec_text)
                            if len(car_specs) >= 2:
                                car_details["car_name"] = car_specs[0]
                                car_details["model"] = car_specs[1]

                    # Price extraction
                    price_text = None
                    total_pay_price = linked_soup.find("p", class_="total-pay-price")
                    if total_pay_price:
                        price_span = total_pay_price.find("span", class_="price")
                        if price_span:
                            price_text = price_span.get_text(strip=True)

                    if not price_text:
                        new_total_pay = linked_soup.find("div", class_="new-total-pay")
                        if new_total_pay:
                            price_div = new_total_pay.find("div", class_="price")
                            if price_div:
                                price_text = price_div.get_text(strip=True)

                    if price_text:
                        try:
                            car_details["price"] = float(
                                re.sub(r"[^\d.]", "", price_text)
                            )
                        except ValueError:
                            pass

                    # Date extraction
                    date_posted = linked_soup.find("p", class_="date-post")
                    if date_posted:
                        date_str = date_posted.get_text(strip=True).replace(
                            "Posted on ", ""
                        )
                        try:
                            car_details["date_posted"] = datetime.strptime(
                                date_str, "%d/%m/%Y"
                            ).date()
                        except ValueError:
                            pass
                    # In the car_details collection
                    car_details["url"] = full_url
                    # Database insertion
                    if all(
                        key in car_details
                        for key in ["car_name", "model", "price", "date_posted"]
                    ):
                        try:
                            cur.execute(
                                """
                                INSERT INTO cars (name, model, date_posted, price, url)
                                VALUES (%s, %s, %s, %s, %s)
                                ON CONFLICT (url) DO NOTHING
                            """,
                                (
                                    car_details["car_name"],
                                    car_details["model"],
                                    car_details["date_posted"],
                                    car_details["price"],
                                    car_details["url"],  # Add this
                                ),
                            )
                            conn.commit()
                            cnt += 1
                            print(f"Inserted {cnt} cars")
                        except Exception as e:
                            print(f"Database error: {e}")
                            conn.rollback()

                except Exception as e:
                    print(f"Error processing car: {e}")
                    continue
            i += 1
    finally:
        cur.close()
        conn.close()
        print(f"Total cars processed: {cnt}")


if __name__ == "__main__":
    scrape_cars()
