import cv2
import dotenv
import json
import numpy as np
import os
import requests
import threading
import time

dotenv.load_dotenv()

RIOT_GAMES_API_KEY = os.getenv("RIOT_GAMES_API_KEY")
RIOT_GAMES_API_PLATFORM_ROUTING = os.getenv("RIOT_GAMES_API_PLATFORM_ROUTING")
RIOT_GAMES_API_REGIONAL_ROUTING = os.getenv("RIOT_GAMES_API_REGIONAL_ROUTING")
RIOT_ID_GAME_NAME = os.getenv("RIOT_ID_GAME_NAME")
RIOT_ID_TAG_LINE = os.getenv("RIOT_ID_TAG_LINE")
GAME_MAP_SCREENSHOT_URL = os.getenv("GAME_MAP_SCREENSHOT_URL")
GAME_MAP_SCALE = float(os.getenv("GAME_MAP_SCALE"))
CHECK_GAME_STATUS_INTERVAL = int(os.getenv("CHECK_GAME_STATUS_INTERVAL"))
FRAME_DELAY = float(os.getenv("FRAME_DELAY"))
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD"))
LAST_SEEN_CHAMPION_MAX_TIME = int(os.getenv("LAST_SEEN_CHAMPION_MAX_TIME"))

CHAMPION_BOX_COLOR = (0, 255, 0)
CHAMPION_BOX_THICKNESS = 2
FONT = cv2.FONT_HERSHEY_SIMPLEX

class RiotGamesApiUnauthorizedException(Exception):
    pass

puuid = None
in_game = False
enemies = []

champions = []
with open("champions.json", "r", encoding="utf-8") as file:
    champions = json.load(file)

def set_interval(callback, interval):
    def schedule():
        callback()
        threading.Timer(interval, schedule).start()

    schedule()

def get_champion(champion_id):
    for champion in champions:
        if champion.get("id") == champion_id:
            return champion

    return None

def setup_tracker(participants):
    global enemies

    enemies = []

    team_id = None
    for participant in participants:
        if participant.get("puuid") == puuid:
            team_id = participant.get("teamId")
            break

    for participant in participants:
        if participant.get("teamId") == team_id:
            continue

        champion = get_champion(participant.get("championId"))

        templates = []
        for image in champion.get("images"):
            template_bgra = cv2.imread(f"images/champions/{image}", cv2.IMREAD_UNCHANGED)

            if template_bgra is not None:
                mask = template_bgra[:, :, 3] 
                template_gray = cv2.cvtColor(template_bgra[:, :, :3], cv2.COLOR_BGR2GRAY)
                height, width = template_gray.shape

                templates.append({
                    "mask": mask,
                    "bgra": template_bgra,
                    "gray": template_gray,
                    "height": height,
                    "width": width
                })

        enemies.append({
            "champion_id": champion.get("id"),
            "champion_name": champion.get("name"),
            "last_seen_position": None,
            "last_seen_template": None,
            "last_seen_time": 0,
            "templates": templates
        })

def show_map():
    global enemies

    while True:
        if not in_game:
            black_screen = np.zeros((558, 560, 3), dtype = np.uint8)
            black_screen_resized = cv2.resize(black_screen, (0, 0), fx = GAME_MAP_SCALE, fy = GAME_MAP_SCALE, interpolation = cv2.INTER_LINEAR)

            cv2.imshow("LoL map champion tracker", black_screen_resized)
            cv2.waitKey(1)

            time.sleep(FRAME_DELAY)
            continue

        try:
            response = requests.get(GAME_MAP_SCREENSHOT_URL, timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            time.sleep(5)
            continue

        map_screenshot_array = np.frombuffer(response.content, dtype=np.uint8)
        map_screenshot_bgr = cv2.imdecode(map_screenshot_array, cv2.IMREAD_COLOR)
        map_screenshot_gray = cv2.cvtColor(map_screenshot_bgr, cv2.COLOR_BGR2GRAY)

        for enemy in enemies:
            detected = False

            for template in enemy.get("templates"):
                result = cv2.matchTemplate(map_screenshot_gray, template.get("gray"), cv2.TM_CCOEFF_NORMED, mask=template.get("mask"))
                locations = np.where(result >= CONFIDENCE_THRESHOLD)

                if locations[0].size > 0:
                    detected = True

                    point = (locations[1][0], locations[0][0])
                    top_left = point
                    bottom_right = (point[0] + template.get("width"), point[1] + template.get("height"))

                    cv2.rectangle(map_screenshot_bgr, top_left, bottom_right, CHAMPION_BOX_COLOR, CHAMPION_BOX_THICKNESS)

                    enemy["last_seen_position"] = top_left
                    enemy["last_seen_template"] = template
                    enemy["last_seen_time"] = int(time.time() * 1000)
                    break 

            if not detected and enemy.get("last_seen_position") is not None:
                time_since_last_seen = int((time.time() * 1000 - enemy["last_seen_time"]) / 1000)

                if time_since_last_seen > LAST_SEEN_CHAMPION_MAX_TIME:
                    continue

                template = enemy.get("last_seen_template")
                template_bgra = template["bgra"]
                height = template["height"]
                width = template["width"]

                x, y = enemy["last_seen_position"]

                if y + height <= map_screenshot_bgr.shape[0] and x + width <= map_screenshot_bgr.shape[1]:
                    roi = map_screenshot_bgr[y:y + height, x:x + width]
                    template_rgb = template_bgra[:, :, :3]
                    alpha = (template_bgra[:, :, 3] / 255.0) * 0.5
                    alpha = alpha[..., np.newaxis]

                    map_screenshot_bgr[y:y + height, x:x + width] = cv2.addWeighted(alpha * template_rgb, 1, (1 - alpha) * roi, 1, 0).astype(np.uint8)

                    label = f"{time_since_last_seen}s"
                    (text_width, text_height), _ = cv2.getTextSize(label, FONT, 0.5, 1)
                    text_x = x + (width - text_width) // 2
                    text_y = y - 5

                    if text_y > text_height:
                        cv2.putText(map_screenshot_bgr, label, (text_x, text_y), FONT, 0.5, (0, 165, 255), 1, cv2.LINE_AA)

        map_screenshot_bgr_resized = cv2.resize(map_screenshot_bgr, (0, 0), fx = GAME_MAP_SCALE, fy = GAME_MAP_SCALE, interpolation = cv2.INTER_LINEAR)

        cv2.imshow("LoL map champion tracker", map_screenshot_bgr_resized)
        cv2.waitKey(1)

        time.sleep(FRAME_DELAY)

def get_player_puuid():
    response = requests.get(f"https://{RIOT_GAMES_API_REGIONAL_ROUTING}/riot/account/v1/accounts/by-riot-id/{RIOT_ID_GAME_NAME}/{RIOT_ID_TAG_LINE}", headers = { "X-Riot-Token": RIOT_GAMES_API_KEY })

    if response.status_code == 401:
        raise RiotGamesApiUnauthorizedException()

    response.raise_for_status()

    account = response.json()
    return account.get("puuid")

def check_game_status():
    global in_game, enemies

    response = requests.get(f"https://{RIOT_GAMES_API_PLATFORM_ROUTING}/lol/spectator/v5/active-games/by-summoner/{puuid}", headers = { "X-Riot-Token": RIOT_GAMES_API_KEY })

    if response.status_code == 401:
        raise RiotGamesApiUnauthorizedException()

    if response.status_code == 404:
        in_game = False
        enemies = []
        return

    response.raise_for_status()

    if in_game:
        return

    game = response.json()
    participants = game.get("participants")
    threading.Thread(target=setup_tracker, args=(participants,), daemon=True).start()

    in_game = True

def main():
    global puuid

    puuid = get_player_puuid()

    set_interval(check_game_status, CHECK_GAME_STATUS_INTERVAL)

    show_map()

if __name__ == "__main__":
    main()
