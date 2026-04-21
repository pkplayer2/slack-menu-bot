import os
from datetime import datetime
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

MENU_URL = "https://apps.cloud-cast.com/menuboard/frt/vertical_ourhome?menuboardId=3678"
IMAGE_PATH = "menu.png"

CHANNEL_IDS = [
    "C09PX2A4V39", #DB팀
    "C09QCGKR0P4", #솔루션팀
    "C09FYR39J15", #웹개발
    #"C09LFFQDNP7",  # lam_db_alarm_test
    "C0ATH87EYBC"  # db_alarm_test
]

def today_message():
    weekday_map = {
        0: "월요일",
        1: "화요일",
        2: "수요일",
        3: "목요일",
        4: "금요일",
        5: "토요일",
        6: "일요일",
    }

    now = datetime.now(ZoneInfo("Asia/Seoul"))
    date_str = now.strftime("%Y-%m-%d")
    weekday_str = weekday_map[now.weekday()]

    return f":bento: 오늘의 메뉴 업로드 ({date_str} {weekday_str})"

def capture_menu():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1920})
        page.goto(MENU_URL, wait_until="networkidle", timeout=60000)
        page.screenshot(path=IMAGE_PATH, full_page=True)
        browser.close()

def send_to_slack():
    token = os.environ["SLACK_BOT_TOKEN"]
    client = WebClient(token=token)

    message = today_message()

    try:
        for channel in CHANNEL_IDS:
            client.files_upload_v2(
                channel=channel,
                file=IMAGE_PATH,
                title="오늘의 메뉴",
                initial_comment=message,
            )

        print("Slack multi-channel send success")

    except SlackApiError as e:
        print("Slack upload failed:", e.response["error"])
        raise

if __name__ == "__main__":
    capture_menu()
    send_to_slack()
