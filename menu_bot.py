import os
from playwright.sync_api import sync_playwright
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

MENU_URL = "https://apps.cloud-cast.com/menuboard/frt/vertical_ourhome?menuboardId=3678"
IMAGE_PATH = "menu.png"

def capture_menu():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1920})
        page.goto(MENU_URL, wait_until="networkidle", timeout=60000)
        page.screenshot(path=IMAGE_PATH, full_page=True)
        browser.close()

def send_to_slack():
    token = os.environ["SLACK_BOT_TOKEN"]
    channel = os.environ["SLACK_CHANNEL_ID"]

    client = WebClient(token=token)

    try:
        client.files_upload_v2(
            channel=channel,
            file=IMAGE_PATH,
            title="🍱 오늘의 식단",
            initial_comment="🍱 오늘의 식단입니다."
        )
        print("Slack upload success")

    except SlackApiError as e:
        print("Slack upload failed:", e.response["error"])
        raise

if __name__ == "__main__":
    capture_menu()
    send_to_slack()
