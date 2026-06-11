def fetch_transcript_text(video_id: str, languages: list[str] | None = None) -> tuple[str | None, str]:
    languages = languages or ["ko", "en"]
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except Exception:
        return None, "youtube-transcript-api가 설치되어 있지 않습니다."

    try:
        api = YouTubeTranscriptApi()
        fetched = api.fetch(video_id, languages=languages)
        snippets = [
            getattr(item, "text", None) if not isinstance(item, dict) else item.get("text")
            for item in fetched
        ]
        transcript = " ".join(text for text in snippets if text)
        return transcript or None, "success" if transcript else "empty"
    except Exception:
        try:
            fetched = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
            transcript = " ".join(item.get("text", "") for item in fetched)
            return transcript or None, "success" if transcript else "empty"
        except Exception as exc:
            return None, f"failed: {exc}"
