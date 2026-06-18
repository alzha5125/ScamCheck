from pathlib import Path
import json
import os

import certifi
import httpx
from flask import Flask, request, send_from_directory
from google import genai
from google.genai import errors
from google.genai import types

APP_DIR = Path(__file__).resolve().parent
CONFIG_PATH = APP_DIR / ".gitignore" / "config.json"
FRONTEND_DIR = APP_DIR / "FrontEnd"
MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
FALLBACK_MODEL_NAME = os.environ.get("GEMINI_FALLBACK_MODEL", "gemini-2.0-flash")

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


def load_config():
    if not CONFIG_PATH.exists():
        return {}

    with CONFIG_PATH.open("r", encoding="utf-8-sig") as config_file:
        return json.load(config_file)


def load_api_key():
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_APP_KEY")
    if api_key:
        return api_key

    config = load_config()
    return config.get("GEMINI_API_KEY") or config.get("GEMINI_APP_KEY")


def load_ssl_verify():
    raw_value = os.environ.get("GEMINI_SSL_VERIFY")
    if raw_value is None:
        raw_value = load_config().get("GEMINI_SSL_VERIFY", True)

    if raw_value is False:
        return False

    if str(raw_value).strip().lower() in {"0", "false", "no", "off"}:
        return False

    return certifi.where()


def create_client(api_key):
    http_client = httpx.Client(verify=load_ssl_verify())
    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(httpx_client=http_client),
    )


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.post("/analyze")
def analyze():
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        message = str(payload.get("message", "")).strip()
    else:
        message = request.form.get("message", "").strip()

    if not message:
        return "Vui lòng nhập nội dung cần kiểm tra.", 400

    api_key = load_api_key()
    if not api_key:
        return (
            "Backend chưa được cấu hình GEMINI_API_KEY hoặc GEMINI_APP_KEY.",
            500,
        )

    prompt = (
        "Bạn là một chuyên gia phân tích tin nhắn lừa đảo. "
        "Hãy đánh giá tin nhắn sau, nêu mức độ rủi ro, dấu hiệu đáng ngờ, "
        "và lời khuyên ngắn gọn cho người nhận. "
        "Trả lời bằng tiếng Việt, văn bản thuần, không dùng Markdown.\n\n"
        f"Tin nhắn:\n{message}"
    )

    try:
        client = create_client(api_key)
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )
        except errors.ServerError as error:
            if error.code != 503 or not FALLBACK_MODEL_NAME:
                raise

            app.logger.warning(
                "Gemini model %s unavailable, retrying with %s",
                MODEL_NAME,
                FALLBACK_MODEL_NAME,
            )
            response = client.models.generate_content(
                model=FALLBACK_MODEL_NAME,
                contents=prompt,
            )
    except httpx.ConnectError as error:
        if "CERTIFICATE_VERIFY_FAILED" in str(error):
            app.logger.exception("Gemini SSL verification failed")
            return (
                "Lỗi SSL khi kết nối Gemini. Hãy cài chứng chỉ CA hợp lệ cho Python "
                "hoặc đặt GEMINI_SSL_VERIFY=false trong môi trường local nếu chỉ dùng để phát triển.",
                500,
            )
        app.logger.exception("Gemini connection error")
        return f"Lỗi kết nối Gemini: {error}", 500
    except errors.APIError as error:
        app.logger.exception("Gemini API error")
        return f"Lỗi Gemini API: {error}", 500
    except Exception as error:
        app.logger.exception("AI error")
        return f"Lỗi backend: {error}", 500

    return response.text or "AI không trả lời."


@app.route("/analyze", methods=["OPTIONS"])
def analyze_options():
    return "", 204


if __name__ == "__main__":
    app.run(debug=True)
