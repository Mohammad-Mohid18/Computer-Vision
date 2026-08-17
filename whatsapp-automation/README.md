# WhatsApp Bulk Message Sender

A reliable Python automation script to send bulk personalized messages on WhatsApp Web using **Selenium**. Designed with self-healing navigation, retry mechanisms, and session persistence so you only have to scan the QR code once.

---

## 📌 Features

- **Single Tab Operation**: Navigates within a single tab session, eliminating browser tab clutter.
- **Session Persistence**: Saves login credentials in `./whatsapp_session` so you don't need to scan the QR code on every run.
- **Self-Healing & Anti-Hang**: Includes page load timeouts (`driver.set_page_load_timeout`), `eager` loading strategy, and automatic retries to prevent the script from getting stuck on WhatsApp Web's "buffering" screen.
- **Multiline Support**: Preserves multiline formatting in messages using `Shift + Enter`.
- **CSV / Excel Input**: Reads contacts directly from `.csv` or `.xlsx` files with input validation and fallback default messages.
- **Detailed Logging**: Records timestamps, success/failure statuses, and error messages to `send_log.txt`.

---

## 📁 Project Structure

```
├── send_whatsapp.py      # Main automation script
├── contacts.csv          # Contact details and custom messages (ignored by Git)
├── send_log.txt          # Automated execution logs (ignored by Git)
├── whatsapp_session/     # Chrome profile directory storing login session (ignored by Git)
├── requirements.txt      # Required Python dependencies
└── README.md             # Project documentation
```

---

## ⚙️ Requirements & Installation

### 1. Prerequisites
- Python 3.8+
- Google Chrome browser installed on your machine.

### 2. Install Dependencies
Clone this repository and install the required packages:

```bash
pip install -r requirements.txt
```

#### `requirements.txt`
```text
pandas
selenium
webdriver-manager
openpyxl
```

---

## 🚀 Usage

### 1. Prepare Contacts File (`contacts.csv`)
Create a `contacts.csv` file in the root directory. Ensure it includes a `phone` column with the country code (starting with `+`). You can optionally include a `message` column for custom per-recipient messages.

```csv
phone,message
+923001234567,"Hello John! Hope you are doing well."
+12345678901,"Hi Sarah! Your order is ready for pickup."
```

> **Note**: If the `message` column is omitted or left empty for a contact, the default message configured in `send_whatsapp.py` will be used.

### 2. Run the Script
Execute the script via terminal or command prompt:

```bash
python send_whatsapp.py
```

1. A Chrome browser window will launch and open WhatsApp Web.
2. Scan the **QR code** using your phone (first-time setup only).
3. Press `ENTER` in your terminal to start the bulk sending process.

---

## 🛠️ Configuration Options

You can adjust the following parameters inside `send_whatsapp.py`:

| Parameter | Default | Description |
| :--- | :--- | :--- |
| `INPUT_FILE` | `"contacts.csv"` | Path to input contact file (`.csv` or `.xlsx`) |
| `DEFAULT_MESSAGE` | `"Hello!..."` | Fallback message if `message` field is blank |
| `DELAY_SECONDS` | `5` | Pause duration between sends to avoid spam rate limits |
| `LOG_FILE` | `"send_log.txt"` | Output path for execution logs |

---

## 📝 `.gitignore` Setup

To protect your personal contacts, session tokens, and execution history from being committed to public repositories, ensure your `.gitignore` includes:

```gitignore
# WhatsApp session tokens & personal data
whatsapp_session/
contacts.csv
*.xlsx
*.csv
send_log.txt

# Python environment & cache
__pycache__/
*.py[cod]
.venv/
env/
```

---

## 🛡️ License

This project is intended for operational and informational automation purposes. Please ensure compliance with WhatsApp's Terms of Service when using bulk messaging functionality.
