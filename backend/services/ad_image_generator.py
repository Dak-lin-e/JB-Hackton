import base64
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

import requests
from dotenv import load_dotenv
from openai import OpenAI

SERVICE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SERVICE_DIR.parent
PROJECT_DIR = BACKEND_DIR.parent
load_dotenv(BACKEND_DIR / ".env")
load_dotenv(PROJECT_DIR / ".env")

GENERATED_IMAGE_DIR = BACKEND_DIR / "static" / "generated-images"


class AdImageGenerationError(RuntimeError):
    pass


def _use_mock_image() -> bool:
    return os.getenv("USE_MOCK_IMAGE_GENERATION", os.getenv("USE_MOCK_LLM", "true")).lower() == "true"


def _image_model() -> str:
    return os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")


def _image_size() -> str:
    return os.getenv("OPENAI_IMAGE_SIZE", "1024x1024")


def _image_quality() -> str:
    return os.getenv("OPENAI_IMAGE_QUALITY", "medium")


def _extract_b64(response) -> str:
    data = getattr(response, "data", None) or []
    if not data:
        raise AdImageGenerationError("이미지 생성 응답에 이미지 데이터가 없습니다.")
    b64_json = getattr(data[0], "b64_json", None)
    if not b64_json:
        raise AdImageGenerationError("이미지 생성 응답에 base64 데이터가 없습니다.")
    return b64_json


def _write_image_file(b64_json: str, output_format: str = "png") -> tuple[str, str]:
    GENERATED_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"ad-image-{uuid4()}.{output_format}"
    path = GENERATED_IMAGE_DIR / filename
    path.write_bytes(base64.b64decode(b64_json))
    return str(path), f"/static/generated-images/{filename}"


def _mock_image_file() -> tuple[str, str]:
    GENERATED_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"mock-ad-image-{uuid4()}.svg"
    path = GENERATED_IMAGE_DIR / filename
    path.write_text(
        """
<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">
  <rect width="1024" height="1024" fill="#f8fafc"/>
  <rect x="96" y="112" width="832" height="800" rx="32" fill="#ffffff" stroke="#dbeafe" stroke-width="6"/>
  <text x="128" y="240" font-size="54" font-weight="700" fill="#0f172a">Trend-to-FinAd</text>
  <text x="128" y="328" font-size="38" fill="#0891b2">AI 금융광고 이미지 시안</text>
  <rect x="128" y="420" width="768" height="120" rx="24" fill="#ecfeff"/>
  <text x="168" y="492" font-size="34" font-weight="700" fill="#155e75">혜택과 조건을 한 장으로</text>
  <rect x="128" y="588" width="360" height="180" rx="24" fill="#dcfce7"/>
  <rect x="536" y="588" width="360" height="180" rx="24" fill="#fef3c7"/>
  <text x="168" y="690" font-size="30" fill="#166534">조건 확인</text>
  <text x="576" y="690" font-size="30" fill="#92400e">유의사항 확인</text>
</svg>
""".strip(),
        encoding="utf-8",
    )
    return str(path), f"/static/generated-images/{filename}"


def _reference_media_urls(trend_result: dict | None) -> list[str]:
    urls = []
    for video in (trend_result or {}).get("videos", []):
        for key in ("thumbnailUrl", "mediaUrl", "sourceUrl", "videoUrl"):
            value = video.get(key)
            if value and value not in urls:
                urls.append(value)
    return urls[:6]


def _download_reference_images(urls: list[str], directory: Path) -> list[Path]:
    image_paths = []
    for url in urls:
        if len(image_paths) >= 3:
            break
        if not any(token in url.lower() for token in [".jpg", ".jpeg", ".png", ".webp", "cdninstagram", "fbcdn"]):
            continue
        try:
            response = requests.get(url, timeout=8)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            if "image" not in content_type:
                continue
            suffix = ".jpg"
            if "png" in content_type:
                suffix = ".png"
            elif "webp" in content_type:
                suffix = ".webp"
            path = directory / f"reference-{len(image_paths)}{suffix}"
            path.write_bytes(response.content)
            image_paths.append(path)
        except requests.RequestException:
            continue
    return image_paths


def build_ad_image_prompt(plan: dict, product: dict, trend_result: dict | None = None) -> str:
    image = plan.get("imageCreative", {})
    reference_urls = _reference_media_urls(trend_result)
    reference_note = "\n".join(f"- {url}" for url in reference_urls) if reference_urls else "- 없음"
    return f"""
Create a square Korean fintech advertisement image.

Product:
- Name: {product.get("productName")}
- Type: {product.get("productType")}
- Target: {product.get("targetCustomer")}
- Benefit: {product.get("keyBenefit")}
- Eligibility: {product.get("eligibility")}
- Caution: {product.get("caution")}

Creative direction:
- Feed copy: {image.get("instagramFeedCopy")}
- Visual direction: {image.get("visualDirection")}
- Layout guide: {image.get("layoutGuide")}
- Safe prompt: {image.get("safeImagePrompt")}

Reference media URLs from Instagram/short-form trend collection:
{reference_note}

Use the reference media only as high-level inspiration for color rhythm, social-feed energy, framing density, and visual tempo.
Do not copy any original person, logo, thumbnail composition, character, text, music cue, or recognizable scene.
Design a clean white/light-gray financial service dashboard style with cyan and emerald accents.
Use Korean placeholder headline-style text, but keep text minimal and legible.
Include visual areas for product name, key benefit, eligibility note, caution note, and CTA.
No celebrity likeness. No real bank logo. No copyrighted character. No guaranteed profit claim.
""".strip()


def generate_ad_image_asset(plan: dict, product: dict, trend_result: dict | None = None) -> dict:
    prompt = build_ad_image_prompt(plan, product, trend_result)

    if _use_mock_image():
        local_path, public_url = _mock_image_file()
        return {
            "url": public_url,
            "localPath": local_path,
            "prompt": prompt,
            "model": "mock",
            "status": "mock",
            "referenceMediaUrls": _reference_media_urls(trend_result),
        }

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    reference_urls = _reference_media_urls(trend_result)

    with TemporaryDirectory() as temp_dir:
        reference_images = _download_reference_images(reference_urls, Path(temp_dir))
        open_files = []
        try:
            if reference_images:
                open_files = [path.open("rb") for path in reference_images]
                response = client.images.edit(
                    model=_image_model(),
                    image=open_files,
                    prompt=prompt,
                    size=_image_size(),
                    quality=_image_quality(),
                    output_format="png",
                )
            else:
                response = client.images.generate(
                    model=_image_model(),
                    prompt=prompt,
                    size=_image_size(),
                    quality=_image_quality(),
                    output_format="png",
                )
        finally:
            for file in open_files:
                file.close()

    local_path, public_url = _write_image_file(_extract_b64(response))
    return {
        "url": public_url,
        "localPath": local_path,
        "prompt": prompt,
        "model": _image_model(),
        "status": "generated",
        "referenceMediaUrls": reference_urls,
    }
