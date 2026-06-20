from pathlib import Path
from datetime import datetime, timezone
import json
import os
import re
import socket
import ssl
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from uuid import uuid4

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from google import genai

APP_DIR = Path(__file__).resolve().parent
CONFIG_PATH = APP_DIR / ".gitignore" / "config.json"
DATA_DIR = APP_DIR / "data"
RESULTS_PATH = DATA_DIR / "results.json"

from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = APP_DIR / "FrontEnd"

app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIR),
    static_url_path=""
)
CORS(app)

VALID_LEVELS = ["Thấp", "Trung bình", "Cao", "Nghiêm trọng"]


def load_config():
    if not CONFIG_PATH.exists():
        return {}

    with open(CONFIG_PATH, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def load_api_key():
    config = load_config()

    return (
        os.environ.get("GEMINI_API_KEY")
        or config.get("GEMINI_API_KEY")
    )


def load_results():
    if not RESULTS_PATH.exists():
        return {}

    with open(RESULTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data if isinstance(data, dict) else {}


def save_results(results):
    DATA_DIR.mkdir(exist_ok=True)

    sorted_items = sorted(
        results.items(),
        key=lambda item: item[1].get("created_at", ""),
        reverse=True,
    )[:1000]

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(dict(sorted_items), f, ensure_ascii=False, indent=2)


def create_saved_result(message, result):
    result_id = uuid4().hex[:12]
    results = load_results()

    results[result_id] = {
        "id": result_id,
        "message": message,
        "result": result,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    save_results(results)
    return result_id


def normalize_url(raw_url):
    raw_url = (raw_url or "").strip()

    if not raw_url:
        return ""

    if not re.match(r"^https?://", raw_url, re.IGNORECASE):
        raw_url = "https://" + raw_url

    parsed = urlparse(raw_url)

    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""

    return raw_url


def get_ssl_info(hostname):
    try:
        context = ssl.create_default_context()

        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as secure_sock:
                cert = secure_sock.getpeercert()

        return {
            "valid": True,
            "issuer": dict(x[0] for x in cert.get("issuer", [])),
            "not_after": cert.get("notAfter"),
        }
    except Exception as exc:
        return {
            "valid": False,
            "error": str(exc),
        }


def get_domain_age_info(domain):
    try:
        import requests

        response = requests.get(
            f"https://rdap.org/domain/{domain}",
            timeout=8,
            headers={"User-Agent": "ScamCheckBot/1.0"},
        )

        if not response.ok:
            return {"available": False, "error": f"RDAP status {response.status_code}"}

        data = response.json()
        registration_date = None

        for event in data.get("events", []):
            if event.get("eventAction") in {"registration", "registered"}:
                registration_date = event.get("eventDate")
                break

        age_days = None
        if registration_date:
            registered = datetime.fromisoformat(registration_date.replace("Z", "+00:00"))
            age_days = (datetime.now(timezone.utc) - registered).days

        return {
            "available": True,
            "registration_date": registration_date,
            "age_days": age_days,
            "registrar": (data.get("registrar") or {}).get("name"),
        }
    except Exception as exc:
        return {"available": False, "error": str(exc)}


def scan_website_signals(url, html, title, final_url, redirects, ssl_info, domain_info):
    parsed = urlparse(final_url or url)
    domain = parsed.netloc.lower()
    text = re.sub(r"\s+", " ", html).lower()
    signals = []
    score = 0

    suspicious_keywords = [
        "urgent",
        "verify account",
        "claim reward",
        "limited time",
        "otp",
        "password",
        "bank account",
        "winner",
        "congratulations",
        "transfer money",
        "khẩn cấp",
        "xác minh",
        "trúng thưởng",
        "mã otp",
        "mật khẩu",
        "chuyển tiền",
    ]
    keyword_hits = [word for word in suspicious_keywords if word in text]

    if keyword_hits:
        score += min(3, len(keyword_hits))
        signals.append(f"Suspicious keywords found: {', '.join(keyword_hits[:8])}.")

    if redirects:
        score += min(3, len(redirects))
        signals.append(f"Page redirects {len(redirects)} time(s) before loading.")

    if not ssl_info.get("valid"):
        score += 2
        signals.append("SSL certificate could not be verified.")

    age_days = domain_info.get("age_days")
    if age_days is not None and age_days < 90:
        score += 3
        signals.append(f"Domain appears new: about {age_days} day(s) old.")
    elif age_days is None:
        score += 1
        signals.append("Domain age could not be confirmed.")

    known_brands = [
        "vietcombank",
        "bidv",
        "techcombank",
        "mbbank",
        "facebook",
        "zalo",
        "shopee",
        "lazada",
        "paypal",
        "apple",
        "google",
        "microsoft",
    ]
    brand_hits = [brand for brand in known_brands if brand in text or brand in domain]
    suspicious_domain_parts = ["-", "verify", "security", "support", "login", "account"]

    if brand_hits and any(part in domain for part in suspicious_domain_parts):
        score += 3
        signals.append(
            f"Possible brand impersonation involving: {', '.join(sorted(set(brand_hits)))}."
        )

    contact_matches = re.findall(
        r"[\w.+-]+@[\w-]+\.[\w.-]+|\+?\d[\d\s().-]{7,}\d",
        html,
    )

    if not contact_matches:
        score += 1
        signals.append("No clear contact email or phone number found.")

    form_count = len(re.findall(r"<form\b", html, flags=re.IGNORECASE))
    password_fields = len(re.findall(r'type=["\']password["\']', html, flags=re.IGNORECASE))

    if form_count:
        score += 1
        signals.append(f"Page contains {form_count} form(s).")

    if password_fields:
        score += 3
        signals.append("Page contains password input fields.")

    level = "Thấp"
    if score >= 8:
        level = "Nghiêm Trọng"
    elif score >= 5:
        level = "Cao"
    elif score >= 2:
        level = "Trung bình"

    return {
        "level": level,
        "score": score,
        "signals": signals or ["No major heuristic scam signal found."],
        "keyword_hits": keyword_hits,
        "contact_count": len(contact_matches),
        "form_count": form_count,
        "password_fields": password_fields,
        "title": title,
        "domain": domain,
    }


def explain_website_with_ai(url, title, html, findings):
    if not api_key:
        return None

    prompt = f"""
Analyze this website for scam indicators. Explain in Vietnamese, concise and practical.

URL: {url}
Title: {title}
Heuristic findings:
{json.dumps(findings, ensure_ascii=False)}

Content:
{html[:10000]}

Return valid JSON only:
{{
  "description": "short conclusion",
  "signs": ["signal 1", "signal 2", "signal 3"],
  "actions": ["action 1", "action 2", "action 3"],
  "counselor": "friendly warning in Vietnamese"
}}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        raw_text = response.text or ""
        cleaned = raw_text.strip()
        cleaned = re.sub(r"^```json", "", cleaned, flags=re.MULTILINE).strip()
        cleaned = re.sub(r"^```", "", cleaned, flags=re.MULTILINE).strip()
        cleaned = re.sub(r"```$", "", cleaned, flags=re.MULTILINE).strip()

        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            cleaned = match.group(0)

        data = json.loads(cleaned)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


api_key = load_api_key()

if not api_key:
    print("CẢNH BÁO: Chưa đọc được GEMINI_API_KEY")
else:
    print("Đã đọc được GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/r/<result_id>")
def shared_result_page(result_id):
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/api/results/<result_id>")
def get_saved_result(result_id):
    saved = load_results().get(result_id)

    if not saved:
        return jsonify({"error": "Result not found"}), 404

    return jsonify(saved)


@app.route("/send-alert", methods=["POST"])
def send_alert():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    result_id = (data.get("result_id") or "").strip()

    if not message:
        return jsonify({"error": "message is required"}), 400

    config = load_config()
    zalo_token = os.environ.get("ZALO_ACCESS_TOKEN") or config.get("ZALO_ACCESS_TOKEN")
    facebook_token = (
        os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN")
        or config.get("FACEBOOK_PAGE_ACCESS_TOKEN")
    )

    # Provider API calls belong here. Keep tokens in environment variables or
    # .gitignore/config.json, never in frontend JavaScript.
    print(
        json.dumps(
            {
                "event": "send_alert_requested",
                "message": message,
                "result_id": result_id,
                "has_zalo_token": bool(zalo_token),
                "has_facebook_token": bool(facebook_token),
            },
            ensure_ascii=False,
        )
    )

    return jsonify({"ok": True})


@app.route("/analyze-website", methods=["POST"])
def analyze_website():
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        return jsonify({
            "error": "Website scanner dependencies are missing. Run: pip install -r requirements.txt"
        }), 500

    data = request.get_json(silent=True) or {}
    raw_url = data.get("url") or data.get("message") or ""
    url = normalize_url(raw_url)

    if not url:
        return jsonify({"error": "A valid http/https URL is required."}), 400

    try:
        session = requests.Session()
        session.trust_env = False
        response = session.get(
            url,
            timeout=10,
            allow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 ScamCheckBot/1.0"},
        )
    except requests.RequestException as exc:
        hostname = urlparse(url).hostname or url
        return jsonify({
            "error": (
                f"Could not fetch {hostname}. Check that the domain exists and is reachable. "
                "For Scamwatch, try https://www.scamwatch.gov.au"
            ),
            "details": str(exc),
        }), 400

    content_type = response.headers.get("Content-Type", "")
    html = response.text or ""

    if "text/html" not in content_type and "<html" not in html.lower():
        return jsonify({"error": "The URL did not return an HTML page."}), 400

    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else "No title"
    visible_text = soup.get_text(" ", strip=True)
    final_url = response.url
    redirects = [item.url for item in response.history]
    hostname = urlparse(final_url).hostname or urlparse(url).hostname or ""
    ssl_info = get_ssl_info(hostname) if hostname else {"valid": False, "error": "No hostname"}
    domain_info = get_domain_age_info(hostname) if hostname else {"available": False}

    findings = scan_website_signals(
        url=url,
        html=html,
        title=title,
        final_url=final_url,
        redirects=redirects,
        ssl_info=ssl_info,
        domain_info=domain_info,
    )
    ai_explanation = explain_website_with_ai(
        final_url,
        title,
        visible_text[:10000],
        {
            **findings,
            "ssl": ssl_info,
            "domain_age": domain_info,
            "redirects": redirects,
        },
    )

    default_description = (
        f"ScamCheck inspected {hostname}. Risk score: {findings['score']}."
    )
    result = {
        "level": findings["level"],
        "description": (ai_explanation or {}).get("description", default_description),
        "signs": (ai_explanation or {}).get("signs", findings["signals"]),
        "suspicious_quote": title,
        "actions": (ai_explanation or {}).get("actions", [
            "Do not enter passwords, OTPs, or banking details on this site until verified.",
            "Check the official domain by typing it yourself in the browser.",
            "Ask the real organization through an official phone number or app.",
        ]),
        "counselor": (ai_explanation or {}).get(
            "counselor",
            "Con hãy kiểm tra thật kỹ trước khi nhập thông tin cá nhân. Nếu website tạo cảm giác gấp gáp hoặc yêu cầu mật khẩu, OTP, tài khoản ngân hàng thì nên dừng lại và xác minh qua kênh chính thức.",
        ),
        "website": {
            "url": url,
            "final_url": final_url,
            "title": title,
            "domain": hostname,
            "redirects": redirects,
            "ssl": ssl_info,
            "domain_age": domain_info,
            "keyword_hits": findings["keyword_hits"],
            "contact_count": findings["contact_count"],
            "form_count": findings["form_count"],
            "password_fields": findings["password_fields"],
        },
    }

    result_id = create_saved_result(final_url, result)
    result["result_id"] = result_id
    result["result_url"] = request.host_url.rstrip("/") + f"/r/{result_id}"

    return jsonify(result)


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({
            "error": "Bạn chưa nhập tin nhắn cần kiểm tra. Hãy dán một tin nhắn rồi thử lại nhé."
        }), 400

    if len(message) > 5000:
        return jsonify({
            "error": "Tin nhắn quá dài. Bạn hãy rút gọn dưới 5000 ký tự rồi phân tích lại nhé."
        }), 400

    if not api_key:
        return jsonify({
            "error": "Ứng dụng chưa có API key. Hãy kiểm tra file .gitignore/config.json rồi chạy lại app nhé."
        }), 500

    prompt = f"""
Bạn là chuyên gia phát hiện tin nhắn lừa đảo, giải thích dễ hiểu cho người lớn tuổi 45+.

Hãy phân tích tin nhắn sau:
\"\"\"{message}\"\"\"

Chỉ trả về JSON hợp lệ, không markdown, không giải thích thêm.

JSON bắt buộc có đúng các khóa sau:
{{
  "level": "Thấp",
  "description": "Kết luận ngắn gọn, dễ hiểu",
  "signs": ["dấu hiệu 1", "dấu hiệu 2", "dấu hiệu 3"],
  "suspicious_quote": "đoạn đáng ngờ nhất trong tin nhắn, nếu không có thì ghi: Không có đoạn nào đáng ngờ.",
  "actions": ["hành động 1", "hành động 2", "hành động 3"],
  "counselor": "lời khuyên nhẹ nhàng của Cô tâm lý, giọng gần gũi, xưng con và gọi người dùng là bác. Kết quả trả về từ hai đến ba câu, giải thích chiêu thức tâm lý mà kẻ lừa đảo đã dùng trong tin nhắn."
}}

Quy ước mức độ:
- Thấp: chưa có dấu hiệu nguy hiểm rõ ràng.
- Trung bình: có vài dấu hiệu đáng ngờ.
- Cao: nhiều dấu hiệu lừa đảo, nguy cơ mất tiền/thông tin cao.
- Nghiêm trọng: yêu cầu OTP, mật khẩu, chuyển tiền, thông tin ngân hàng/CCCD hoặc giả mạo cơ quan chức năng.

Giá trị của "level" chỉ được là một trong bốn giá trị:
"Thấp", "Trung bình", "Cao", "Nghiêm trọng".
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        raw_text = response.text or ""

        if not raw_text.strip():
            return jsonify({
                "error": "AI từ chối hoặc không thể phân tích nội dung này. Bạn hãy thử viết lại tin nhắn ngắn gọn hơn nhé."
            }), 403

        cleaned = raw_text.strip()
        cleaned = re.sub(r"^```json", "", cleaned, flags=re.MULTILINE).strip()
        cleaned = re.sub(r"^```", "", cleaned, flags=re.MULTILINE).strip()
        cleaned = re.sub(r"```$", "", cleaned, flags=re.MULTILINE).strip()

        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            cleaned = match.group(0)

        try:
            result = json.loads(cleaned)
        except json.JSONDecodeError:
            result = {}

        if not isinstance(result, dict):
            result = {}

        level = result.get("level", "Trung bình")
        if level not in VALID_LEVELS:
            level = "Trung bình"

        signs = result.get("signs")
        if not isinstance(signs, list) or len(signs) == 0:
            signs = ["Có nội dung cần được kiểm tra thêm trước khi làm theo."]

        actions = result.get("actions")
        if not isinstance(actions, list) or len(actions) == 0:
            actions = [
                "Không cung cấp OTP, mật khẩu hoặc thông tin cá nhân.",
                "Không chuyển tiền khi chưa xác minh rõ nguồn gửi.",
                "Liên hệ kênh chính thức của ngân hàng hoặc cơ quan liên quan để kiểm tra."
            ]

        safe_result = {
            "level": level,
            "description": result.get(
                "description",
                "AI đã hoàn tất phân tích tin nhắn này."
            ),
            "signs": signs,
            "suspicious_quote": result.get(
                "suspicious_quote",
                message[:180] if level != "Thấp" else "Không có đoạn nào đáng ngờ."
            ),
            "actions": actions,
            "counselor": result.get(
                "counselor",
                "Hãy bình tĩnh, không vội làm theo tin nhắn. Nếu thấy nghi ngờ, hãy hỏi người thân hoặc liên hệ kênh chính thức để kiểm tra lại."
            )
        }

        result_id = create_saved_result(message, safe_result)
        safe_result["result_id"] = result_id
        safe_result["result_url"] = request.host_url.rstrip("/") + f"/r/{result_id}"

        return jsonify(safe_result)

    except Exception as e:
        error_text = str(e).lower()

        if (
            "safety" in error_text
            or "blocked" in error_text
            or "refuse" in error_text
            or "finish_reason" in error_text
        ):
            return jsonify({
                "error": "AI từ chối phân tích nội dung này. Bạn hãy thử viết lại tin nhắn ngắn gọn hơn nhé."
            }), 403

        return jsonify({
            "error": f"Hệ thống đang gặp sự cố khi gọi AI: {str(e)}"
        }), 500


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
