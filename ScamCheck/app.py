from pathlib import Path
from datetime import datetime, timezone
import json
import os
import random
import re
from uuid import uuid4
from urllib.parse import urlparse
import socket
import ipaddress
import urllib.request
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from google import genai
from google.genai import types

APP_DIR = Path(__file__).resolve().parent
CONFIG_PATH = APP_DIR / ".gitignore" / "config.json"
DATA_DIR = APP_DIR / "data"
RESULTS_PATH = DATA_DIR / "results.json"
HOTLINES_PATH = DATA_DIR / "hotlines.json"
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = APP_DIR / "FrontEnd"

app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIR),
    static_url_path=""
)
CORS(app)

VALID_LEVELS = ["An toàn", "Nghi ngờ", "Nguy hiểm"]
ALLOWED_IMAGE_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/gif",
}
MAX_IMAGE_BYTES = 8 * 1024 * 1024


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

def is_private_host(hostname):
    try:
        ip = socket.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_reserved
    except Exception:
        return True


def fetch_website_info(url):
    parsed = urlparse(url)

    if parsed.scheme not in ["http", "https"]:
        raise ValueError("Chỉ hỗ trợ link http hoặc https.")

    if not parsed.netloc:
        raise ValueError("Link không hợp lệ.")

    if is_private_host(parsed.hostname):
        raise ValueError("Không cho phép kiểm tra địa chỉ nội bộ.")

    request_obj = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 ScamCheckAI/1.0"
        }
    )

    with urllib.request.urlopen(request_obj, timeout=8) as response:
        final_url = response.geturl()
        status_code = response.status
        content_type = response.headers.get("Content-Type", "")
        html = response.read(50000).decode("utf-8", errors="ignore")

    return {
        "input_url": url,
        "final_url": final_url,
        "status_code": status_code,
        "content_type": content_type,
        "html_preview": html[:4000],
    }


def basic_url_risk(url):
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()

    signs = []

    if parsed.scheme != "https":
        signs.append("Website không dùng HTTPS.")

    if "-" in host:
        signs.append("Tên miền có dấu gạch ngang, dễ dùng để giả mạo.")

    if any(char.isdigit() for char in host):
        signs.append("Tên miền có chữ số, cần kiểm tra kỹ.")

    suspicious_words = [
        "verify", "login", "security", "bank", "otp", "gift",
        "bonus", "xacminh", "nhanthuong", "khoataikhoan"
    ]

    if any(word in host for word in suspicious_words):
        signs.append("Tên miền chứa từ khóa thường gặp trong link lừa đảo.")

    suspicious_tlds = [".top", ".xyz", ".click", ".shop", ".site", ".online"]

    if any(host.endswith(tld) for tld in suspicious_tlds):
        signs.append("Tên miền dùng đuôi dễ bị lợi dụng trong lừa đảo.")

    if len(signs) >= 3:
        level = "Nguy hiểm"
    elif len(signs) >= 1:
        level = "Nghi ngờ"
    else:
        level = "An toàn"

    return level, signs


@app.route("/analyze-website", methods=["POST"])
def analyze_website():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()

    if not url:
        return jsonify({
            "error": "Bạn chưa nhập đường dẫn website cần kiểm tra."
        }), 400

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        website_info = fetch_website_info(url)
    except Exception as error:
        level, signs = basic_url_risk(url)

        return jsonify({
            "level": level,
            "description": f"Không thể truy cập website để kiểm tra nội dung. Lý do: {str(error)}",
            "signs": signs or ["Không truy cập được website, cần kiểm tra lại nguồn gửi link."],
            "suspicious_quote": url,
            "actions": [
                "Không đăng nhập hoặc nhập OTP vào website này.",
                "Tự gõ địa chỉ website chính thức thay vì bấm link được gửi.",
                "Kiểm tra tên miền thật kỹ trước khi cung cấp thông tin."
            ],
            "counselor": "Bác nên dừng lại và không nhập thông tin vào đường dẫn này. Kẻ lừa đảo thường dùng link gần giống trang thật để tạo cảm giác tin cậy."
        })

    level, url_signs = basic_url_risk(website_info["final_url"])

    if not api_key:
        return jsonify({
            "level": level,
            "description": "Đã kiểm tra cơ bản đường dẫn website.",
            "signs": url_signs or ["Chưa phát hiện dấu hiệu nguy hiểm rõ ràng từ tên miền."],
            "suspicious_quote": website_info["final_url"],
            "actions": [
                "Không nhập OTP, mật khẩu hoặc thông tin ngân hàng nếu chưa chắc chắn.",
                "So sánh tên miền với website chính thức.",
                "Liên hệ kênh chính thức của tổ chức nếu nghi ngờ."
            ],
            "counselor": "Bác nên kiểm tra tên miền thật kỹ trước khi thao tác. Link giả thường tạo cảm giác giống trang thật nhưng khác vài ký tự."
        })

    prompt = f"""
Bạn là chuyên gia kiểm tra website lừa đảo.

Hãy phân tích website sau bằng tiếng Việt.
Chỉ trả về JSON hợp lệ, không markdown.

JSON bắt buộc có đúng các khóa:
{{
  "level": "An toàn",
  "description": "Kết luận ngắn gọn",
  "signs": ["dấu hiệu 1", "dấu hiệu 2", "dấu hiệu 3"],
  "suspicious_quote": "đoạn hoặc URL đáng ngờ nhất",
  "actions": ["hành động 1", "hành động 2", "hành động 3"],
  "counselor": "lời khuyên ngắn, dễ hiểu cho người lớn tuổi"
}}

Chỉ chọn level trong:
"An toàn"
"Nghi ngờ"
"Nguy hiểm".

Thông tin website:
URL người dùng nhập: {website_info["input_url"]}
URL sau chuyển hướng: {website_info["final_url"]}
HTTP status: {website_info["status_code"]}
Content-Type: {website_info["content_type"]}

Dấu hiệu kỹ thuật ban đầu:
{json.dumps(url_signs, ensure_ascii=False)}

Nội dung HTML rút gọn:
\"\"\"{website_info["html_preview"]}\"\"\"
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        raw_text = response.text or ""
        cleaned = raw_text.strip()
        cleaned = re.sub(r"^```json", "", cleaned, flags=re.MULTILINE).strip()
        cleaned = re.sub(r"^```", "", cleaned, flags=re.MULTILINE).strip()
        cleaned = re.sub(r"```$", "", cleaned, flags=re.MULTILINE).strip()

        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            cleaned = match.group(0)

        result = json.loads(cleaned)

        if result.get("level") not in VALID_LEVELS:
            result["level"] = level

        if not isinstance(result.get("signs"), list):
            result["signs"] = url_signs

        if not isinstance(result.get("actions"), list):
            result["actions"] = [
                "Không nhập thông tin cá nhân vào website này.",
                "Kiểm tra lại tên miền chính thức.",
                "Liên hệ tổ chức qua kênh chính thức."
            ]

        return jsonify(result)

    except Exception as error:
        return jsonify({
            "level": level,
            "description": "AI chưa phân tích được nội dung website, nhưng hệ thống đã kiểm tra cơ bản đường dẫn.",
            "signs": url_signs or ["Không phát hiện dấu hiệu rõ ràng từ tên miền, nhưng vẫn cần cẩn trọng."],
            "suspicious_quote": website_info["final_url"],
            "actions": [
                "Không nhập OTP, mật khẩu hoặc thông tin ngân hàng.",
                "Tự mở website chính thức thay vì dùng link được gửi.",
                "Hỏi người thân hoặc liên hệ tổng đài chính thức nếu nghi ngờ."
            ],
            "counselor": "Bác không nên vội tin đường dẫn lạ. Kẻ lừa đảo thường làm website giống thật để lấy thông tin đăng nhập."
        })
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


api_key = load_api_key()

client = None

if api_key:
    print("Đã đọc được GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
else:
    print("CẢNH BÁO: Chưa đọc được GEMINI_API_KEY")


TRAINING_FALLBACK_QUESTIONS = [
    {
        "text": "Đơn hàng của bạn không giao được. Thanh toán phí giao lại 12.000đ tại ship-fast-confirm.top trong 30 phút.",
        "is_scam": True,
        "explanation": "Tin này tạo áp lực thời gian, yêu cầu trả phí và dùng tên miền đáng ngờ thay vì website giao hàng chính thức.",
        "red_flags": ["Thời hạn gấp", "Yêu cầu trả phí", "Link đáng ngờ"],
    },
    {
        "text": "Lịch hẹn của bạn tại Phòng khám Nha khoa Thành Phố được xác nhận lúc 15:00 ngày mai. Trả lời HUY để hủy lịch.",
        "is_scam": False,
        "explanation": "Đây là tin nhắc lịch bình thường. Tin không yêu cầu chuyển tiền, mật khẩu, OTP hoặc bấm link đăng nhập.",
        "red_flags": [],
    },
    {
        "text": "Thông báo công an: tài khoản ngân hàng của bạn liên quan đến vụ rửa tiền. Chuyển toàn bộ tiền sang tài khoản an toàn để điều tra.",
        "is_scam": True,
        "explanation": "Công an thật không yêu cầu người dân chuyển tiền sang tài khoản an toàn qua tin nhắn.",
        "red_flags": ["Giả danh công an", "Đe dọa điều tra", "Yêu cầu chuyển tiền"],
    },
    {
        "text": "Hóa đơn điện tháng này đã có trên ứng dụng khách hàng chính thức. Mở ứng dụng để xem chi tiết.",
        "is_scam": False,
        "explanation": "Tin hướng dẫn người dùng tự mở ứng dụng chính thức và không gửi link thanh toán đáng ngờ.",
        "red_flags": [],
    },
    {
        "text": "Chúc mừng bạn trúng iPhone. Gửi ảnh CCCD và đóng phí hồ sơ 200.000đ để nhận thưởng trong hôm nay.",
        "is_scam": True,
        "explanation": "Tin báo trúng thưởng bất ngờ nhưng yêu cầu đóng phí hoặc gửi giấy tờ là dấu hiệu lừa đảo phổ biến.",
        "red_flags": ["Trúng thưởng bất ngờ", "Phí hồ sơ", "Yêu cầu ảnh CCCD"],
    },
]


def fallback_training_question():
    return random.choice(TRAINING_FALLBACK_QUESTIONS)


@app.route("/training-question", methods=["POST"])
def training_question():
    if not api_key or not client:
        return jsonify(fallback_training_question())

    prompt = """
Tạo một ví dụ luyện tập ngắn bằng tiếng Việt cho người dùng học cách nhận diện lừa đảo.

Chỉ trả về JSON hợp lệ đúng cấu trúc sau:
{
  "text": "tin nhắn để người học phán đoán",
  "is_scam": true,
  "explanation": "một hoặc hai câu giải thích vì sao",
  "red_flags": ["dấu hiệu ngắn", "dấu hiệu ngắn"]
}

Quy tắc:
- Chọn ngẫu nhiên ví dụ là lừa đảo hoặc không lừa đảo.
- Nội dung phải giống SMS, tin chat, email ngắn hoặc thông báo website ở Việt Nam.
- Giữ "text" dưới 70 từ.
- Không làm ví dụ nào cũng quá dễ đoán.
- Nếu không phải lừa đảo, không yêu cầu OTP, mật khẩu, chuyển tiền hoặc bấm link đáng ngờ.
- Toàn bộ text, explanation và red_flags phải viết bằng tiếng Việt.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        raw_text = response.text or ""
        cleaned = raw_text.strip()
        cleaned = re.sub(r"^```json", "", cleaned, flags=re.MULTILINE).strip()
        cleaned = re.sub(r"^```", "", cleaned, flags=re.MULTILINE).strip()
        cleaned = re.sub(r"```$", "", cleaned, flags=re.MULTILINE).strip()

        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            cleaned = match.group(0)

        question = json.loads(cleaned)

        if not isinstance(question, dict):
            return jsonify(fallback_training_question())

        text = str(question.get("text") or "").strip()
        is_scam = question.get("is_scam")
        explanation = str(question.get("explanation") or "").strip()
        red_flags = question.get("red_flags")

        if not text or not isinstance(is_scam, bool) or not explanation:
            return jsonify(fallback_training_question())

        if not isinstance(red_flags, list):
            red_flags = []

        return jsonify({
            "text": text,
            "is_scam": is_scam,
            "explanation": explanation,
            "red_flags": [str(item) for item in red_flags[:4]],
        })

    except Exception:
        return jsonify(fallback_training_question())


@app.route("/analyze-image", methods=["POST"])
def analyze_image():
    image_file = request.files.get("image")

    if not image_file:
        return jsonify({"error": "Bạn chưa chọn ảnh cần kiểm tra."}), 400

    mime_type = image_file.mimetype or image_file.content_type or ""

    if mime_type not in ALLOWED_IMAGE_MIME_TYPES:
        return jsonify({
            "error": "Chỉ hỗ trợ ảnh PNG, JPG, WEBP hoặc GIF."
        }), 400

    image_bytes = image_file.read(MAX_IMAGE_BYTES + 1)

    if len(image_bytes) > MAX_IMAGE_BYTES:
        return jsonify({
            "error": "Ảnh quá lớn. Hãy chọn ảnh dưới 8MB."
        }), 400

    filename = os.path.basename(image_file.filename or "uploaded-image")

    if not api_key or not client:
        safe_result = {
            "level": "Nghi ngờ",
            "description": "Chưa thể phân tích ảnh vì AI hình ảnh chưa được cấu hình. Bạn có thể nhập lại nội dung trong ảnh vào ô tin nhắn để kiểm tra.",
            "signs": [
                "Hệ thống đã nhận được ảnh nhưng chưa thể đọc nội dung trong ảnh.",
                "Nếu ảnh có link, mã OTP, yêu cầu chuyển tiền hoặc thông tin ngân hàng, hãy coi là cần kiểm tra kỹ.",
                "Không làm theo nội dung trong ảnh cho đến khi xác minh qua kênh chính thức."
            ],
            "suspicious_quote": filename,
            "actions": [
                "Nhập lại nội dung chính trong ảnh vào ô tin nhắn để ScamCheck phân tích bằng chữ.",
                "Không bấm link, quét QR hoặc chuyển tiền theo ảnh chụp khi chưa xác minh.",
                "Gọi kênh chính thức của ngân hàng hoặc cơ quan liên quan nếu ảnh yêu cầu thao tác khẩn cấp."
            ],
            "counselor": "Bác nên xem ảnh này như một nguồn chưa xác minh. Nếu ảnh tạo áp lực phải làm ngay, yêu cầu OTP hoặc chuyển tiền, bác hãy dừng lại và kiểm tra qua kênh chính thức trước."
        }
        result_id = create_saved_result(f"Image: {filename}", safe_result)
        safe_result["result_id"] = result_id
        safe_result["result_url"] = request.host_url.rstrip("/") + f"/r/{result_id}"
        return jsonify(safe_result)

    prompt = """
Bạn là chuyên gia phát hiện lừa đảo từ ảnh chụp tin nhắn, email, mạng xã hội hoặc website.

Hãy đọc nội dung nhìn thấy trong ảnh, trích xuất phần chữ quan trọng, rồi phân tích rủi ro bằng tiếng Việt.
Chỉ trả về JSON hợp lệ, không markdown, không giải thích thêm.

JSON bắt buộc có đúng các khóa sau:
{
  "level": "An toàn",
  "description": "Kết luận ngắn gọn, dễ hiểu",
  "signs": ["dấu hiệu 1", "dấu hiệu 2", "dấu hiệu 3"],
  "suspicious_quote": "đoạn chữ hoặc chi tiết đáng ngờ nhất trong ảnh, nếu không có thì ghi: Không có đoạn nào đáng ngờ.",
  "actions": ["hành động 1", "hành động 2", "hành động 3"],
  "counselor": "lời khuyên ngắn, dễ hiểu cho người lớn tuổi",
  "extracted_text": "phần chữ quan trọng đọc được từ ảnh"
}

Chỉ chọn level trong:
"An toàn"
"Nghi ngờ"
"Nguy hiểm".

Nếu ảnh mờ hoặc không đọc được, chọn "Nghi ngờ" và hướng dẫn người dùng nhập lại nội dung bằng chữ.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                prompt,
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            ],
        )

        raw_text = response.text or ""
        cleaned = raw_text.strip()
        cleaned = re.sub(r"^```json", "", cleaned, flags=re.MULTILINE).strip()
        cleaned = re.sub(r"^```", "", cleaned, flags=re.MULTILINE).strip()
        cleaned = re.sub(r"```$", "", cleaned, flags=re.MULTILINE).strip()

        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            cleaned = match.group(0)

        result = json.loads(cleaned)

        level = result.get("level", "Nghi ngờ")
        if level not in VALID_LEVELS:
            level = "Nghi ngờ"

        signs = result.get("signs")
        if not isinstance(signs, list) or len(signs) == 0:
            signs = ["Ảnh có nội dung cần kiểm tra kỹ trước khi làm theo."]

        actions = result.get("actions")
        if not isinstance(actions, list) or len(actions) == 0:
            actions = [
                "Không bấm link, quét QR hoặc chuyển tiền nếu chưa xác minh.",
                "Kiểm tra lại nguồn gửi ảnh.",
                "Liên hệ kênh chính thức nếu ảnh nhắc đến ngân hàng, công an hoặc tài khoản."
            ]

        safe_result = {
            "level": level,
            "description": result.get(
                "description",
                "AI đã hoàn tất phân tích ảnh này."
            ),
            "signs": signs,
            "suspicious_quote": result.get(
                "suspicious_quote",
                result.get("extracted_text", filename)[:180]
            ),
            "actions": actions,
            "counselor": result.get(
                "counselor",
                "Bác nên dừng lại và xác minh nội dung trong ảnh qua kênh chính thức trước khi làm theo."
            ),
            "extracted_text": result.get("extracted_text", "")
        }

        saved_message = f"Image: {filename}"
        if safe_result["extracted_text"]:
            saved_message += f"\nExtracted text: {safe_result['extracted_text']}"

        result_id = create_saved_result(saved_message, safe_result)
        safe_result["result_id"] = result_id
        safe_result["result_url"] = request.host_url.rstrip("/") + f"/r/{result_id}"

        return jsonify(safe_result)

    except Exception:
        safe_result = {
            "level": "Nghi ngờ",
            "description": "Chưa thể đọc ảnh này. Ảnh có thể quá mờ, sai định dạng hoặc AI đang gặp lỗi.",
            "signs": [
                "Không xác định được nội dung trong ảnh.",
                "Vẫn cần cảnh giác nếu ảnh yêu cầu chuyển tiền, OTP, mật khẩu hoặc bấm link.",
                "Ảnh chụp có thể bị chỉnh sửa hoặc lấy từ nguồn không đáng tin cậy."
            ],
            "suspicious_quote": filename,
            "actions": [
                "Nhập lại nội dung trong ảnh vào ô tin nhắn để kiểm tra bằng chữ.",
                "Không làm theo yêu cầu trong ảnh nếu chưa xác minh.",
                "Gửi ảnh cho người thân đáng tin cậy hoặc liên hệ kênh chính thức để kiểm tra."
            ],
            "counselor": "Bác chưa nên làm theo nội dung trong ảnh. Hãy nhập lại phần chữ quan trọng hoặc kiểm tra qua kênh chính thức trước."
        }
        result_id = create_saved_result(f"Image: {filename}", safe_result)
        safe_result["result_id"] = result_id
        safe_result["result_url"] = request.host_url.rstrip("/") + f"/r/{result_id}"
        return jsonify(safe_result)


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
def load_hotlines():
    if not HOTLINES_PATH.exists():
        return {"contacts": []}

    with open(HOTLINES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data if isinstance(data, dict) else {"contacts": []}


def fallback_rescue_steps(choice, contacts):
    banks = [c for c in contacts if c.get("type") == "bank"]
    police = next((c for c in contacts if c.get("type") == "police"), {"name": "Công an khẩn cấp", "phone": "113"})
    cyber = next((c for c in contacts if c.get("phone") == "156"), {"name": "Phản ánh lừa đảo", "phone": "156"})

    bank = banks[0] if banks else {"name": "ngân hàng của bạn", "phone": ""}

    if choice == "Link":
        return [
            f"1. Ngắt kết nối khỏi trang vừa mở. Câu nói mẫu: Tôi vừa bấm vào một đường dẫn nghi ngờ lừa đảo, xin hướng dẫn cách khóa tài khoản và kiểm tra giao dịch.",
            f"2. Gọi {bank['name']} theo số {bank['phone']}. Câu nói mẫu: Tôi cần kiểm tra tài khoản vì vừa truy cập đường dẫn lạ.",
            f"3. Gọi {cyber['phone']} để phản ánh đường dẫn lừa đảo. Câu nói mẫu: Tôi muốn phản ánh một đường dẫn nghi ngờ lừa đảo trực tuyến.",
        ]

    if choice == "Send":
        return [
            f"1. Gọi ngay ngân hàng đang dùng, ưu tiên {bank['name']} số {bank['phone']}. Câu nói mẫu: Tôi vừa chuyển tiền nhầm cho đối tượng nghi lừa đảo, xin hỗ trợ tra soát và khóa giao dịch.",
            f"2. Chuẩn bị mã giao dịch, số tài khoản nhận tiền, thời gian chuyển tiền. Câu nói mẫu: Tôi có mã giao dịch và thông tin người nhận, xin ghi nhận khẩn cấp.",
            f"3. Gọi {police['phone']}. Câu nói mẫu: Tôi muốn trình báo việc bị lừa chuyển tiền qua mạng.",
        ]

    if choice == "Otp":
        return [
            f"1. Gọi ngay ngân hàng đang dùng, ưu tiên {bank['name']} số {bank['phone']}. Câu nói mẫu: Tôi đã cung cấp mã OTP cho người lạ, xin khóa tài khoản và dịch vụ ngân hàng số ngay.",
            f"2. Yêu cầu khóa thẻ, khóa Internet Banking và kiểm tra giao dịch mới nhất. Câu nói mẫu: Xin kiểm tra toàn bộ giao dịch phát sinh trong hôm nay.",
            f"3. Gọi {police['phone']}. Câu nói mẫu: Tôi muốn trình báo việc bị chiếm đoạt thông tin xác thực ngân hàng.",
        ]

    return []


@app.route("/rescue", methods=["POST"])
def rescue():
    data = request.get_json(silent=True) or {}
    choice = (data.get("choice") or "").strip()
    message = (data.get("message") or "").strip()
    result = data.get("result") or {}

    hotlines = load_hotlines()
    contacts = hotlines.get("contacts", [])

    if choice == "None":
        return jsonify({
            "steps": [
                "Tốt. Bạn chưa làm gì nên nguy cơ hiện tại thấp. Hãy xóa tin nhắn và không phản hồi."
            ]
        })

    if choice not in ["Link", "Send", "Otp"]:
        return jsonify({"error": "Lựa chọn không hợp lệ."}), 400

    if not api_key:
        return jsonify({"steps": fallback_rescue_steps(choice, contacts)})

    system_prompt = f"""
Bạn là nhân vật Người ứng cứu.

Giọng văn: bình tĩnh, dứt khoát.
Không an ủi. Không phân tích. Không giải thích dài.
Chỉ liệt kê bước hành động cụ thể.

Quy tắc bắt buộc:
- Chỉ dùng số điện thoại có trong DANH_SACH_TONG_DAI.
- Không tự sinh thêm bất kỳ số điện thoại nào.
- Không dùng số điện thoại không có trong danh sách.
- Kết quả trả về là danh sách bước đánh số.
- Mỗi bước phải có một câu nói mẫu để người dùng đọc khi gọi điện.
- Không dùng câu cảm thán.
- Không dùng markdown.

DANH_SACH_TONG_DAI:
{json.dumps(contacts, ensure_ascii=False)}

Lựa chọn của người dùng: {choice}

Ngữ cảnh:
Tin nhắn/website: {message}
Kết quả phân tích: {json.dumps(result, ensure_ascii=False)}

Hãy tạo hướng dẫn ứng cứu phù hợp với lựa chọn của người dùng.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=system_prompt
        )

        text = (response.text or "").strip()

        if not text:
            return jsonify({"steps": fallback_rescue_steps(choice, contacts)})

        steps = [line.strip() for line in text.splitlines() if line.strip()]

        return jsonify({"steps": steps})

    except Exception:
        return jsonify({"steps": fallback_rescue_steps(choice, contacts)})
def fallback_analyze_result(message):
    lower = message.lower()
    signs = []
    score = 0

    if any(word in lower for word in ["otp", "mật khẩu", "ngân hàng", "tài khoản"]):
        score += 3
        signs.append("Tin nhắn nhắc đến tài khoản, ngân hàng, OTP hoặc mật khẩu.")

    if any(word in lower for word in ["chuyển tiền", "chuyển khoản", "phí", "500.000", "triệu"]):
        score += 2
        signs.append("Tin nhắn có yếu tố yêu cầu tiền hoặc phí.")

    if any(word in lower for word in ["công an", "điều tra", "bắt giam", "rửa tiền"]):
        score += 3
        signs.append("Tin nhắn có dấu hiệu giả danh cơ quan chức năng.")

    if any(word in lower for word in ["http", "link", "bấm vào", ".top", ".xyz"]):
        score += 2
        signs.append("Tin nhắn có đường dẫn hoặc yêu cầu bấm link.")

    if any(word in lower for word in ["gấp", "ngay", "10 phút", "khóa"]):
        score += 2
        signs.append("Tin nhắn tạo áp lực thời gian hoặc đe dọa.")

    if not signs:
        signs = ["Chưa phát hiện dấu hiệu nguy hiểm rõ ràng, nhưng vẫn nên xác minh nguồn gửi."]

    if score >= 5:
        level = "Nguy hiểm"
    elif score >= 2:
        level = "Nghi ngờ"
    else:
        level = "An toàn"

    return {
        "level": level,
        "description": "Đây là kết quả dự phòng vì AI chưa hoạt động hoặc API key bị lỗi.",
        "signs": signs,
        "suspicious_quote": message[:180] if level != "An toàn" else "Không có đoạn nào đáng ngờ.",
        "actions": [
            "Không cung cấp OTP, mật khẩu hoặc thông tin cá nhân.",
            "Không chuyển tiền khi chưa xác minh rõ nguồn gửi.",
            "Liên hệ kênh chính thức của ngân hàng hoặc cơ quan liên quan để kiểm tra."
        ],
        "counselor": "Bác nên dừng lại và kiểm tra qua kênh chính thức. Nếu tin nhắn tạo áp lực hoặc yêu cầu thông tin nhạy cảm, bác không nên làm theo."
    }
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
        safe_result = fallback_analyze_result(message)
        result_id = create_saved_result(message, safe_result)
        safe_result["result_id"] = result_id
        safe_result["result_url"] = request.host_url.rstrip("/") + f"/r/{result_id}"
        return jsonify(safe_result)

    prompt = f"""
Bạn là chuyên gia phát hiện tin nhắn lừa đảo, giải thích dễ hiểu cho người lớn tuổi 45+.

Hãy phân tích tin nhắn sau:
\"\"\"{message}\"\"\"

Chỉ trả về JSON hợp lệ, không markdown, không giải thích thêm.

JSON bắt buộc có đúng các khóa sau:
{{
  "level": "An toàn",
  "description": "Kết luận ngắn gọn, dễ hiểu",
  "signs": ["dấu hiệu 1", "dấu hiệu 2", "dấu hiệu 3"],
  "suspicious_quote": "đoạn đáng ngờ nhất trong tin nhắn, nếu không có thì ghi: Không có đoạn nào đáng ngờ.",
  "actions": ["hành động 1", "hành động 2", "hành động 3"],
  "counselor": "lời khuyên nhẹ nhàng của Cô tâm lý, giọng gần gũi, xưng con và gọi người dùng là bác. Kết quả trả về từ hai đến ba câu, giải thích chiêu thức tâm lý mà kẻ lừa đảo đã dùng trong tin nhắn."
}}

Quy ước mức độ:
- An toàn: chưa có dấu hiệu nguy hiểm rõ ràng.
- Nghi ngờ: có một số dấu hiệu đáng ngờ, cần xác minh trước khi làm theo.
- Nguy hiểm: có dấu hiệu lừa đảo rõ ràng, có thể gây mất tiền, lộ thông tin, yêu cầu OTP, mật khẩu, chuyển tiền, thông tin ngân hàng/CCCD hoặc giả mạo cơ quan chức năng.

Giá trị của "level" chỉ được là một trong ba giá trị:
"An toàn", "Nghi ngờ", "Nguy hiểm".
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        raw_text = response.text or ""

        if not raw_text.strip():
            safe_result = fallback_analyze_result(message)
            result_id = create_saved_result(message, safe_result)
            safe_result["result_id"] = result_id
            safe_result["result_url"] = request.host_url.rstrip("/") + f"/r/{result_id}"
            return jsonify(safe_result)

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
            safe_result = fallback_analyze_result(message)
            result_id = create_saved_result(message, safe_result)
            safe_result["result_id"] = result_id
            safe_result["result_url"] = request.host_url.rstrip("/") + f"/r/{result_id}"
            return jsonify(safe_result)

        if not isinstance(result, dict):
            safe_result = fallback_analyze_result(message)
            result_id = create_saved_result(message, safe_result)
            safe_result["result_id"] = result_id
            safe_result["result_url"] = request.host_url.rstrip("/") + f"/r/{result_id}"
            return jsonify(safe_result)

        level = result.get("level", "Nghi ngờ")
        if level not in VALID_LEVELS:
            level = "Nghi ngờ"

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
                message[:180] if level != "An toàn" else "Không có đoạn nào đáng ngờ."
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
        safe_result = fallback_analyze_result(message)
        result_id = create_saved_result(message, safe_result)
        safe_result["result_id"] = result_id
        safe_result["result_url"] = request.host_url.rstrip("/") + f"/r/{result_id}"
        return jsonify(safe_result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
