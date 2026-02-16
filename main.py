import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import CONFIG

articles = []
def scrape_google_maps(key: str):
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 15)

    try:
        global articles
        driver.get("https://www.google.com/maps")

        search_input = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//form[@jsaction='submit:omnibox.searchboxFormSubmit']/input")
            )
        )
        search_input.send_keys(key)
        search_input.send_keys(Keys.ENTER)
        time.sleep(3)

        scraped = set()

        while True:
            time.sleep(2)
            articles = driver.find_elements(By.XPATH, '//div[@role="article"]')
            print(len(articles))
            if len(articles) <= 0:
                break
            for article in articles:
                try:
                    article.click()
                except:
                    break

                time.sleep(2)

                # Extract data
                try:
                    name = driver.find_element(By.XPATH, '//h1[contains(@class,"DUwDvf")]').text
                except:
                    name = "N/A"

                # Deduplicate
                if name in scraped:
                    driver.execute_script("arguments[0].remove()", article)
                    continue

                scraped.add(name)

                try:
                    rating = driver.find_element(
                        By.XPATH,
                        '//div[contains(@class,"fontBodyMedium")]//span[@aria-hidden="true"]'
                    ).text
                except:
                    rating = "N/A"

                try:
                    address = driver.find_element(
                        By.XPATH,
                        '//button[@data-item-id="address"]'
                    ).text
                except:
                    address = "N/A"

                try:
                    phone = driver.find_element(
                        By.XPATH,
                        '//button[starts-with(@data-item-id,"phone:")]'
                    ).text
                except:
                    phone = "N/A"

                try:
                    website = driver.find_element(
                        By.XPATH,
                        '//a[@data-item-id="authority"]'
                    ).get_attribute("href")
                except:
                    website = "N/A"

                business_data = {
                    "business_name": name,
                    "rating": rating,
                    "address": address,
                    "phone": phone,
                    "website": website,
                }

                print(f"Scraped #{len(scraped)}: {name}")
                time.sleep(5)
                driver.execute_script('document.querySelector("button[aria-label=\'Close\'][data-disable-idom=\'true\']").click();')
                # Remove processed element
                driver.execute_script("arguments[0].remove()", article)
                yield business_data

    finally:
        driver.quit()


if __name__ == "__main__":
    keyword = CONFIG['keyword']
    with open("google_maps_results.jsonl", "w", encoding="utf-8") as f:
        for business in scrape_google_maps(keyword):
            f.write(json.dumps(business, ensure_ascii=False) + "\n")
            f.flush()

    print("Saved to google_maps_results.jsonl")