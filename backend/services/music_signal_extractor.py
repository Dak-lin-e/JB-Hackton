import re

MUSIC_KEYWORDS = [
    "music",
    "song",
    "sound",
    "audio",
    "bgm",
    "ost",
    "remix",
    "sped up",
    "slowed",
    "lofi",
    "beat",
    "노래",
    "음원",
    "사운드",
    "브금",
    "비지엠",
    "리믹스",
    "챌린지곡",
    "댄스",
]


def _sentences(text: str) -> list[str]:
    return [
        sentence.strip()
        for sentence in re.split(r"[\n\r.!?。]+", text)
        if sentence.strip()
    ]


def extract_music_signal(video: dict, transcript_text: str | None = None) -> dict:
    title = video.get("title", "") or ""
    description = video.get("description", "") or ""
    transcript = transcript_text or ""
    combined = f"{title}\n{description}\n{transcript}"
    lowered = combined.lower()
    matched_keywords = [keyword for keyword in MUSIC_KEYWORDS if keyword.lower() in lowered]
    evidence = [
        sentence
        for sentence in _sentences(combined)
        if any(keyword.lower() in sentence.lower() for keyword in MUSIC_KEYWORDS)
    ][:5]

    if any(keyword in lowered for keyword in ["dance", "댄스", "챌린지", "challenge"]):
        mood = "댄스 챌린지에 어울리는 빠른 템포와 반복 훅"
        safe_direction = "원곡 대신 저작권 클리어된 120-140 BPM 밝은 댄스 팝/일렉트로 루프"
    elif any(keyword in lowered for keyword in ["lofi", "감성", "슬퍼", "sad", "slow"]):
        mood = "감성적이고 부드러운 중간 템포"
        safe_direction = "원곡 대신 저작권 클리어된 80-100 BPM 감성 팝/로파이 BGM"
    elif matched_keywords:
        mood = "짧은 숏폼 반복에 맞는 리듬감 있는 사운드"
        safe_direction = "원곡 대신 저작권 클리어된 밝은 숏폼용 BGM과 짧은 효과음"
    else:
        mood = "메타데이터만으로 특정 음원은 확인되지 않음"
        safe_direction = "특정 곡을 모방하지 않는 밝고 경쾌한 100-130 BPM 범용 숏폼 BGM"

    return {
        "matchedMusicKeywords": matched_keywords,
        "musicEvidence": evidence,
        "inferredMusicMood": mood,
        "safeMusicDirection": safe_direction,
        "copyrightNote": "YouTube 원본 음원명/멜로디를 직접 복제하지 말고 분위기와 템포만 참고하세요.",
    }
