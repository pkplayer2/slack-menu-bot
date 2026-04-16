import time
import os
import subprocess
import requests
from playwright.sync_api import sync_playwright

MENU_URL = "https://apps.cloud-cast.com/menuboard/frt/vertical_ourhome?menuboardId=3678"
IMAGE_PATH = "menu.png"

# 👇 본인 GitHub 정보로 수정
GITHUB_RAW_IMAGE_URL = "https://raw.githubusercontent.com/jihmoon-SG/slack-menu-bot/main/menu.png"

def wait_for_image(url, timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.head(url, timeout=5)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(3)
    return False

def capture_menu():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1920})
        page.goto(MENU_URL, wait_until="load", timeout=60000)
        page.wait_for_timeout(3000)
        page.screenshot(path=IMAGE_PATH, full_page=True)
        browser.close()

def git_commit_and_push():
    subprocess.run(["git", "config", "--global", "user.email", "menu-bot@github.com"])
    subprocess.run(["git", "config", "--global", "user.name", "menu-bot"])
    subprocess.run(["git", "add", IMAGE_PATH])
    subprocess.run(
        ["git", "commit", "-m", "update menu image"],
        check=False  # 변경 없으면 commit 실패하므로 무시
    )
    subprocess.run(["git", "push"])



def send_to_slack():
    webhook_url = os.environ["SLACK_WEBHOOK_URL"]

    if not wait_for_image(GITHUB_RAW_IMAGE_URL):
        print("Image not available yet, skipping Slack post")
        return  # ❗ 실패 처리 안 하고 조용히 종료 (자동화 안정성 ↑)

    payload = {
        "text": "🍱 오늘의 식단",
        "blocks": [
            {
                "type": "image",
                "image_url": GITHUB_RAW_IMAGE_URL,
                "alt_text": "오늘의 식단"
            }
        ]
    }

    response = requests.post(webhook_url, json=payload)
    print("Slack response:", response.status_code, response.text)
    response.raise_for_status()

if __name__ == "__main__":
    capture_menu()
    git_commit_and_push()
    send_to_slack()
