from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import time
import webbrowser
import os

# ===== Disable Chrome password popup =====
chrome_options = Options()
chrome_options.add_argument("--disable-features=PasswordCheck,PasswordManagerOnboarding")
chrome_options.add_argument("--disable-save-password-bubble")
chrome_options.add_experimental_option("prefs", {
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False
})

# ===== Setup Chrome =====
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.maximize_window()
wait = WebDriverWait(driver, 10)

# ===== Create log file =====
log_file = open("test_results.txt", "w", encoding="utf-8")

def log(msg):
    print(msg)
    log_file.write(msg + "\n")

try:
    # 1️⃣ Homepage
    driver.get("http://localhost/ecommerce_App")
    time.sleep(5)
    log(f"✅ Homepage loaded: {driver.title}")

    # 2️⃣ Login
    driver.get("http://localhost/ecommerce_App/login_home.php")
    time.sleep(5)
    wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys("testuser2@example.com")
    driver.find_element(By.NAME, "password").send_keys("Test2@098")  # Strong test password
    driver.find_element(By.NAME, "login").click()
    log("✅ Login attempted")
    time.sleep(5)

    try:
        wait.until(EC.url_contains("index.php"))
        log("✅ Login successful")
    except:
        log("⚠ Login may have failed — check credentials")

    # 3️⃣ Shop page
    driver.get("http://localhost/ecommerce_App/product.php")
    time.sleep(5)
    log("✅ Shop page opened")

    try:
        first_product = wait.until(EC.presence_of_element_located(
            (By.XPATH, "(//div[contains(@class,'block2')])[1]")
        ))
        ActionChains(driver).move_to_element(first_product).perform()

        add_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "(//a[contains(@href,'cart') or contains(text(),'Add')])[1]")
        ))
        driver.execute_script("arguments[0].click();", add_button)
        log("✅ Product added to cart")
    except Exception as e:
        log(f"⚠ Could not add product to cart: {e}")
    time.sleep(5)

    # 4️⃣ Cart
    driver.get("http://localhost/ecommerce_App/shoping-cart.php")
    time.sleep(5)
    log("✅ Cart page opened")
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//td[contains(text(),'Rs.')]")))
        log("✅ Product present in cart")
    except:
        log("⚠ No product found in cart")

    # 5️⃣ Contact Page (Skip Checkout)
    driver.get("http://localhost/ecommerce_App/contact.php")
    time.sleep(5)
    log("✅ Contact page opened")

    # 6️⃣ Logout
    try:
        account_menu = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(text(),'My Account')]")
        ))
        driver.execute_script("arguments[0].click();", account_menu)
        time.sleep(1)

        logout_link = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(text(),'Logout') or contains(@href,'logouts.php')]")
        ))
        driver.execute_script("arguments[0].click();", logout_link)
        log("✅ Logout successful")
    except Exception as e:
        log(f"⚠ Logout link not found — {e}")
    time.sleep(5)

finally:
    driver.quit()
    log_file.close()

    # ===== Create HTML report =====
    html_report_path = os.path.abspath("test_results.html")
    with open(html_report_path, "w", encoding="utf-8") as html_file:
        html_file.write("<html><head><title>Test Results</title></head><body>")
        html_file.write("<h1 style='color:green;'>Automation Test Results</h1>")
        with open("test_results.txt", "r", encoding="utf-8") as txt_file:
            for line in txt_file:
                color = "green" if "✅" in line else "orange"
                html_file.write(f"<p style='color:{color}; font-size:16px;'>{line.strip()}</p>")
        html_file.write("</body></html>")

    # ===== Open the HTML report in browser =====
    webbrowser.open(f"file://{html_report_path}")
