import re

import requests
from bs4 import BeautifulSoup


def scrape_cars():
    base_url = "https://philkotse.com"
    cnt = 0
    for i in range(1, 100):
        url = f"https://philkotse.com/used-cars-for-sale/p{i}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        col_4_divs = soup.find_all("div", class_="col-4")
        # print(col_4_divs)
        print(f"for page {i} {len(col_4_divs)}")
        for div in col_4_divs:
            try:
                # Attempt to get the 'a' tag and href attribute
                link_tag = div.find("a", href=True)
                relative_url = link_tag["href"]
                full_url = base_url + relative_url

                # Fetch the linked page's HTML content
                linked_response = requests.get(full_url)
                linked_soup = BeautifulSoup(linked_response.text, "html.parser")

                car_details = {}

                # Extract car details from parameter-info section
                parameter_info = linked_soup.find("div", class_="parameter-info")
                if parameter_info:
                    # Extract car name and model from specification list
                    spec_list = parameter_info.find("ul", class_="list")
                    if spec_list:
                        items = spec_list.find_all("li")
                        car_specs = []
                        for item in items:
                            # Remove icon content and get clean text
                            for icon in item.find_all("i"):
                                icon.decompose()
                            spec_text = item.get_text(strip=True)
                            if spec_text:  # Filter out empty strings
                                car_specs.append(spec_text)

                        # First 2 non-empty specs are make and model
                        if len(car_specs) >= 2:
                            car_details["car_name"] = car_specs[0]
                            car_details["model"] = car_specs[1]

                # Extract the price
                price_text = None
                # Try original price location
                total_pay_price = linked_soup.find("p", class_="total-pay-price")
                if total_pay_price:
                    price_span = total_pay_price.find("span", class_="price")
                    if price_span:
                        price_text = price_span.get_text(strip=True)

                # If not found, try alternative location
                if not price_text:
                    new_total_pay = linked_soup.find("div", class_="new-total-pay")
                    if new_total_pay:
                        price_div = new_total_pay.find("div", class_="price")
                        if price_div:
                            price_text = price_div.get_text(strip=True)

                # Process price text if found
                if price_text:
                    try:
                        cleaned_price = re.sub(r"[^\d.]", "", price_text)
                        car_details["price"] = float(cleaned_price)
                    except ValueError:
                        pass

                date_posted = linked_soup.find("p", class_="date-post")
                if date_posted:
                    car_details["date_posted"] = date_posted.get_text(
                        strip=True
                    ).replace("Posted on ", "")

                print(f"url no:{cnt + 1} {full_url}")
                print(f"Car Name: {car_details.get('car_name')}")
                print(f"Model: {car_details.get('model')}")
                print(f"Date Posted: {car_details.get('date_posted')}")
                print(f"Price: {car_details.get('price')}")
                print("-" * 40)

                cnt += 1  # Increment the counter after processing the car

            except Exception as e:
                # If there's an error accessing or processing the link, print the error and skip this iteration
                print(f"Error processing link: {e}")
                continue

    print(f"Processed {cnt} cars.")


if __name__ == "__main__":
    scrape_cars()
