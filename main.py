import os
import re
import requests
from datetime import datetime

APK_COOKIE = os.getenv("APK_COOKIE")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")


def send_discord(msg, color=0x00ff99):
    if not DISCORD_WEBHOOK:
        return

    requests.post(DISCORD_WEBHOOK, json={
        "username": "APK簽到",
        "embeds": [
            {
                "title": "APK.TW 簽到通知",
                "description": msg,
                "color": color,
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
    })


def main():
    headers = {
        "Cookie": APK_COOKIE,
        "User-Agent": "Mozilla/5.0"
    }

    try:
        # 1. 進入頁面確認登入
        home = requests.get(
            "https://apk.tw/home.php?mod=spacecp",
            headers=headers
        ).text

        if "退出" not in home:
            send_discord("❌ APK.TW Cookie 已失效", 0xff5555)
            return

        # 2. 抓 formhash
        match = re.search(r'name="formhash" value="([^"]+)"', home)
        if not match:
            send_discord("❌ 無法取得 formhash", 0xffcc00)
            return

        formhash = match.group(1)

        # 3. 執行簽到
        sign_url = f"https://apk.tw/plugin.php?id=dsu_amupper:pper&ajax=1&formhash={formhash}"
        requests.get(sign_url, headers=headers)

        # 4. 檢查結果
        check = requests.get(
            "https://apk.tw/plugin.php?id=dsu_amupper:pper",
            headers=headers
        ).text

        still_button = "id=\"my_amupper\"" in check
        already = "已經簽到" in check or "今日已簽" in check

        if (not still_button) or already:
            send_discord("✅ APK.TW 簽到成功", 0x00ff99)

        elif "退出" in check:
            send_discord("✅ APK.TW 簽到成功（狀態確認）", 0x00ff99)

        else:
            send_discord("❌ APK.TW 簽到異常", 0xff5555)

    except Exception as e:
        send_discord(f"⚠️ 系統錯誤：{str(e)}", 0xffcc00)


if __name__ == "__main__":
    main()
