import hashlib
import time
import requests

TELEGRAM_BOT_TOKEN = "8932115756:AAHhNCr56PjAPUCC6UyS_Qj-jNOttM2cSKs"
TELEGRAM_CHAT_ID = "560877981"

DEYE_EMAIL = "romchik.develop@gmail.com"
DEYE_PASSWORD = "uI3%cvdi25"  # Вкажіть свій пароль

CHECK_INTERVAL = 60
last_state = None


def send_telegram_msg(text):
    url = (
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    )
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }
    try:
        requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print(f"Помилка Telegram: {e}")


def get_password_hash(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def check_deye_status():
    try:
        auth_url = "https://globalapi.solarmanpv.com/account/v1.0/token"
        auth_data = {
            "appId": "2021111018",
            "email": DEYE_EMAIL,
            "password": get_password_hash(DEYE_PASSWORD),
        }
        res = requests.post(auth_url, json=auth_data, timeout=15)
        data = res.json()

        if not data.get("success"):
            print(f"Помилка авторизації Deye: {data.get('msg')}")
            return None

        token = data.get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        info_url = "https://globalapi.solarmanpv.com/station/v1.0/list"
        station_res = requests.post(
            info_url, headers=headers, json={}, timeout=15
        )
        station_data = station_res.json()

        stations = station_data.get("stationList", [])
        if not stations:
            return None

        # Якщо usePower > 0 — мережа є
        return stations[0].get("usePower", 0) > 0
    except Exception as e:
        print(f"Помилка Deye API: {e}")
        return None


def main():
    global last_state
    send_telegram_msg("🤖 Бот моніторингу Deye успішно запущений на Render!")

    while True:
        current_state = check_deye_status()

        if current_state is not None:
            if current_state != last_state and last_state is not None:
                if current_state:
                    send_telegram_msg(
                        "🟢 <b>Світло з'явилося!</b>\nІнвертор перейшов на роботу від мережі."
                    )
                else:
                    send_telegram_msg(
                        "🔴 <b>Світло зникло!</b>\nДім працює від акумуляторної батареї."
                    )

            last_state = current_state

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
