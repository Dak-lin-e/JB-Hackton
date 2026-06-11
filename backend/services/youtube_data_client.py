import os
from pathlib import Path

import requests
from dotenv import load_dotenv

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
SERVICE_DIR = Path(__file__).resolve().parent
load_dotenv(SERVICE_DIR.parent / ".env")
load_dotenv(SERVICE_DIR.parent.parent / ".env")


class YouTubeDataApiError(RuntimeError):
    pass


def _api_key() -> str:
    key = os.getenv("YOUTUBE_API_KEY")
    if not key:
        raise YouTubeDataApiError("YOUTUBE_API_KEY가 설정되어 있지 않습니다.")
    return key


def _get(path: str, params: dict) -> dict:
    response = requests.get(
        f"{YOUTUBE_API_BASE}/{path}",
        params={**params, "key": _api_key()},
        timeout=12,
    )
    if not response.ok:
        raise YouTubeDataApiError(f"YouTube Data API 요청 실패: {response.status_code} {response.text}")
    return response.json()


def parse_iso8601_duration_to_seconds(duration: str | None) -> int | None:
    if not duration:
        return None
    # YouTube duration examples: PT59S, PT1M, PT1M2S, PT2H3M4S
    value = duration.replace("PT", "")
    hours = minutes = seconds = 0
    number = ""
    for char in value:
        if char.isdigit():
            number += char
            continue
        if char == "H":
            hours = int(number or 0)
        elif char == "M":
            minutes = int(number or 0)
        elif char == "S":
            seconds = int(number or 0)
        number = ""
    return hours * 3600 + minutes * 60 + seconds
