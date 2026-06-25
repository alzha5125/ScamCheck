from pathlib import Path
from datetime import datetime, timezone
import json
import os
import re
from uuid import uuid4
from urllib.parse import urlparse
import socket
import ipaddress
import urllib.request
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from google import genai

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
