import time
import sys
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

INPUT_FILE = "contacts.csv"
DEFAULT_MESSAGE = """Assalam-o-Alaikum! I'm Mohid, a Data Science student at IMSciences currently working as an AI Engineer at Code Club in Peshawar[cite: 1].

I specialize in building production Generative AI systems—from autonomous voice agents to URL-to-video ad generators and enterprise RAG pipelines[cite: 1].

I'm reaching out to see if your team is currently open to hiring an AI/ML Engineer or Python Automation Developer[cite: 1].

Here is my GitHub & Resume for a quick look:
- GitHub: github.com/Mohammad-Mohid18[cite: 1]
- LinkedIn: linkedin.com/in/mohammad-mohid-162585361[cite: 1]

Happy to share a quick demo of what I'm building or hop on a call if you're open to connecting[cite: 1].

Thanks!"""
DELAY_SECONDS = 5
LOG_FILE = "send_log.txt"

def load_contacts(path: str) -> pd.DataFrame:
    """Load contacts from CSV or Excel into a DataFrame."""
    if path.lower().endswith(".csv"):
        df = pd.read_csv(path, dtype=str)
    else:
        df = pd.read_excel(path, dtype=str)

    if "phone" not in df.columns:
        raise ValueError("Input file must have a 'phone' column.")

    df["phone"] = df["phone"].astype(str).str.strip()

    # Safely handle missing 'message' column or empty values
    if "message" not in df.columns:
        df["message"] = DEFAULT_MESSAGE
    else:
        df["message"] = df["message"].fillna(DEFAULT_MESSAGE)

    # Basic phone validation
    bad = df[~df["phone"].str.startswith("+")]
    if not bad.empty:
        print("WARNING: Skipping rows missing '+' country code:")
        print(bad)
        df = df[df["phone"].str.startswith("+")]

    return df.reset_index(drop=True)

def log(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def send_bulk_selenium(df: pd.DataFrame):
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=./whatsapp_session")
    
    # Prevents driver from waiting on background network streams endlessly
    options.page_load_strategy = 'eager'
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Limit how long Selenium waits for a page load before raising a TimeoutException
    driver.set_page_load_timeout(30)
    
    driver.get("https://web.whatsapp.com")

    print("\n>>> Scan the QR code if prompted. Press Enter in this console once logged in. <<<")
    input("Press ENTER after WhatsApp Web is fully loaded...")

    total = len(df)
    log(f"Starting bulk send to {total} contacts.")

    for i, row in df.iterrows():
        phone = row["phone"].replace("+", "").replace(" ", "")
        message = row["message"]
        url = f"https://web.whatsapp.com/send?phone={phone}"

        sent = False
        max_retries = 2

        for attempt in range(1, max_retries + 1):
            try:
                log(f"({i+1}/{total}) Attempt {attempt}: Navigating to +{phone}...")
                
                try:
                    driver.get(url)
                except Exception as e:
                    # Page load timed out (buffering hang) - stop loading and retry
                    log(f"Navigation timed out for +{phone}. Stopping page load and retrying...")
                    driver.execute_script("window.stop();")

                wait = WebDriverWait(driver, 20)
                msg_box = wait.until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
                )

                msg_box.click()
                time.sleep(1)

                for line in message.split("\n"):
                    msg_box.send_keys(line)
                    msg_box.send_keys(Keys.SHIFT + Keys.ENTER)

                time.sleep(1)
                msg_box.send_keys(Keys.ENTER)

                time.sleep(2)
                log(f"({i+1}/{total}) Sent to +{phone} successfully.")
                sent = True
                break

            except Exception as e:
                log(f"({i+1}/{total}) Attempt {attempt} failed for +{phone}: {e}")
                
                # Refresh main WhatsApp page to unfreeze tab state
                try:
                    driver.get("https://web.whatsapp.com")
                    time.sleep(5)
                except Exception:
                    pass

        if not sent:
            log(f"({i+1}/{total}) PERMANENT FAILURE for +{phone}")

        if i < total - 1:
            time.sleep(DELAY_SECONDS)

    driver.quit()
    log("Bulk send complete.")

if __name__ == "__main__":
    try:
        contacts = load_contacts(INPUT_FILE)
        if contacts.empty:
            print("No valid contacts found. Exiting.")
            sys.exit(1)
            
        send_bulk_selenium(contacts)
    except Exception as e:
        print(f"ERROR: {e}")