import json
import time
from config import CONFIG
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_google_maps(key: str):
    driver = webdriver.Chrome()
    driver.maximize_window()
    wait = WebDriverWait(driver, 10000)

    try:
        driver.get("https://www.google.com/maps")

        search_input = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//form[@jsaction='submit:omnibox.searchboxFormSubmit']/input")
            )
        )
        search_input.send_keys(key)
        search_input.send_keys(Keys.ENTER)
        scan_leads = True

        while scan_leads:
            # 1. Clean up any infinite loaders first
            driver.execute_script("""
                let element = document.querySelector('div.lXJj5c.Hk4XGb');
                if (element && element.parentElement) {
                    element.parentElement.remove();
                }
            """)
            driver.execute_script("document.querySelectorAll('div.lXJj5c.Hk4XGb').forEach(el => el.remove());")

            try:
                # 2. Find the fresh "top" article
                article = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="article"]')))
            except:
                print("No more results found.")
                break

            article.click()

            name = wait.until(
                EC.visibility_of_element_located((By.XPATH,'//h1[contains(@class,"DUwDvf")]'))
            ).text

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

            yield business_data
            print(f"Name: {name}")
            # Wait for the Close button to be both present and clickable
            wait.until(
                EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Close"]'))
            )
            driver.execute_script('document.querySelector("button[aria-label=\'Close\'][data-disable-idom=\'true\']").click();')
            # Remove processed element
            driver.execute_script("arguments[0].parentElement.remove()", article)
            time.sleep(0.3)

    finally:
        driver.quit()


if __name__ == "__main__":
    keyword = CONFIG['keyword']
    with open("google_maps_results.jsonl", "w", encoding="utf-8") as f:
        for business in scrape_google_maps(keyword):
            f.write(json.dumps(business, ensure_ascii=False) + "\n")
            f.flush()

    print("Saved to google_maps_results.jsonl")