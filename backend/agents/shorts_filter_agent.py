SHORTS_KEYWORDS = [
    "shorts",
    "쇼츠",
    "릴스",
    "reels",
    "틱톡",
    "tiktok",
    "챌린지",
    "밈",
    "유행",
    "공감",
    "pov",
    "사람 특",
    "요즘 유행하는",
    "댄스"
    
]


def _judge(video: dict) -> tuple[bool, str]:
    duration = video.get("durationSeconds")
    if duration is not None and duration <= 60:
        return True, "영상 길이가 60초 이하입니다."
    text = f"{video.get('title', '')} {video.get('description', '')}".lower()
    for keyword in SHORTS_KEYWORDS:
        if keyword.lower() in text:
            return True, f"제목 또는 설명에 '{keyword}' 키워드가 포함되어 있습니다."
    return False, "Shorts 후보 판단 기준에 해당하지 않습니다."


def filter_shorts_candidates(videos: list[dict], include_non_shorts: bool = False) -> list[dict]:
    filtered = []
    for video in videos:
        is_candidate, reason = _judge(video)
        enriched = {
            **video,
            "isShortsCandidate": is_candidate,
            "shortsReason": reason,
        }
        if is_candidate or include_non_shorts:
            filtered.append(enriched)
    return filtered
