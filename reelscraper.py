from playwright.sync_api import sync_playwright
from datetime import datetime
import requests
import json

USERNAME = "xhamasters_"
WEBHOOK_URL = "https://alphabuilder.app.n8n.cloud/webhook/ig-reel"
MAX_REELS = 10

def get_today_reels():
    today = datetime.now().date()
    reels = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"https://www.instagram.com/{USERNAME}/", timeout=60000)
        page.wait_for_selector("article")

        links = page.eval_on_selector_all(
            "article a",
            "els => els.map(e => e.href).filter(href => href.includes('/reel/'))"
        )

        seen = set()
        for link in links:
            if link not in seen:
                seen.add(link)
                reels.append(link)
            if len(reels) >= MAX_REELS:
                break

        browser.close()
    return reels

def send_to_webhook(reels):
    for url in reels:
        payload = {"url": url}
        try:
            response = requests.post(WEBHOOK_URL, json=payload)
            print(f"✅ Sent {url} | Status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error sending {url}: {e}")

if __name__ == "__main__":
    reels = get_today_reels()
    if reels:
        send_to_webhook(reels)
    else:
        print("ℹ️ No new reels found.")
