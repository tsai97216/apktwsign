import os
import re
import requests
from datetime import datetime
APK_COOKIE = os.getenv("APK_COOKIE")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
def send_discord_msg(content):
    if DISCORD_WEBHOOK:
        try:
            requests.post(DISCORD_WEBHOOK, json={
                "username": "簽到",
                "embeds": [
                    {
                        "title": "APK.TW 簽到通知",
                        "description": content,
                        "color": 0x00ff99 if content.startswith("✅") else 0xff5555,
                        "footer": {
                            "text": "Auto Check-in Bot"
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    }
                ]
            })
        except Exception as e:
            print(f"Discord 發送失敗: {e}")
def main():
    headers = {
        "Cookie": APK_COOKIE,
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        # 1. 取得首頁並確認登入
        home = requests.get(
            "https://apk.tw/home.php?mod=spacecp",
            headers=headers,
            timeout=30
        )
        html = home.text
        if "退出" not in html:
            discord_msg = "❌ **APK.TW 簽到失敗：Cookie 已失效**"
            send_discord_msg(discord_msg)
            return
        # 2. 取得 formhash
        match = re.search(r'name="formhash" value="([^"]+)"', html)
        if not match:
            discord_msg = "❌ **APK.TW 簽到失敗：無法取得 formhash**"
            send_discord_msg(discord_msg)
            return
        formhash = match.group(1)
        # 3. 執行簽到
        sign_url = (
            f"https://apk.tw/plugin.php?"
            f"id=dsu_amupper:pper&ajax=1&formhash={formhash}"
        )
        requests.get(
            sign_url,
            headers=headers,
            timeout=30
        )
        # 4. 檢查簽到狀態
        check = requests.get(
            "https://apk.tw/plugin.php?id=dsu_amupper:pper",
            headers=headers,
            timeout=30
        ).text
        already_signed = (
            "已經簽到" in check or
            "今日已簽" in check
        )
        still_has_button = 'id="my_amupper"' in check
        if already_signed:
            discord_msg = "✅ **APK.TW 今日已簽到**"
        elif not still_has_button:
            discord_msg = "✅ **APK.TW 簽到成功**"
        elif "退出" not in check:
            discord_msg = "❌ **APK.TW 簽到失敗：Cookie 已失效**"
        else:
            discord_msg = "❌ **APK.TW 簽到失敗：發生未知錯誤**"
        # 5. 發送通知
        send_discord_msg(discord_msg)
    except Exception as e:
        discord_msg = f"❌ **APK.TW 簽到失敗：{str(e)}**"
        send_discord_msg(discord_msg)
if __name__ == "__main__":
    main()
