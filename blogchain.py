from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from solve_recaptcha import solve_recaptcha
from pathlib import Path

directory_path = Path().absolute()
cookie = directory_path.joinpath('mahdmarjany')

opts = webdriver.ChromeOptions()
opts.add_argument('--lang=en-US')
opts.add_argument(
    f"--user-data-dir={cookie}")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-extensions")
opts.add_argument('--headless')
opts.add_argument('--disable-gpu')

driver = webdriver.Chrome(service=Service(
    ChromeDriverManager().install()), options=opts)

url = 'https://blogchain.eu.org/dashboard/captcha/recaptcha'
driver.get(url)

while True:
    solve_recaptcha(driver)
    btn_claim = WebDriverWait(driver=driver, timeout=10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[text()="SUBMIT"]')))
    btn_claim.click()
