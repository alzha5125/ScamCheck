from pathlib import Path
from datetime import datetime, timezone
import json
import os
import re
from uuid import uuid4

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
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
