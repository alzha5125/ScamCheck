const messageInput = document.getElementById("messageInput");
const analyzeButton = document.getElementById("analyzeButton");
const resultText = document.getElementById("resultText");
const sampleMessages = {
  bank: "[VietBank] Tài khoản của quý khách đang bị khóa do giao dịch bất thường. Vui lòng bấm vào link http://vietbank-xacminh.top và nhập OTP để mở lại tài khoản trong 10 phút.",

  police:
    "Tôi là cán bộ công an. Anh/chị đang liên quan đến đường dây rửa tiền. Chuyển ngay 20 triệu vào tài khoản này để phục vụ điều tra, nếu không sẽ bị bắt giam.",

  job: "Chào bạn, công ty đang tuyển nhân viên làm việc online tại nhà với mức lương 20 triệu/tháng. Để nhận việc, bạn cần chuyển trước 500.000đ phí hồ sơ trong hôm nay.",
};

document.querySelectorAll(".sample-btn").forEach((button) => {
  button.addEventListener("click", () => {
    const type = button.dataset.type;
    messageInput.value = sampleMessages[type];
    messageInput.focus();
  });
});
const HOSTED_API_URL = "https://scamcheck-2-07zf.onrender.com/analyze";

function getAnalyzeUrl() {
  const { hostname, port } = window.location;
  const isFlaskServer =
    (hostname === "127.0.0.1" || hostname === "localhost") && port === "5000";

  return isFlaskServer ? "/analyze" : HOSTED_API_URL;
}

function buildAnalyzeRequest(message) {
  const isHostedApi = getAnalyzeUrl() === HOSTED_API_URL;

  if (isHostedApi) {
    return {
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    };
  }

  return {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    },
    body: new URLSearchParams({ message }),
  };
}

async function analyzeMessage() {
  const message = messageInput.value.trim();

  if (!message) {
    resultText.textContent = "Vui lòng nhập nội dung cần kiểm tra.";
    return;
  }

  analyzeButton.disabled = true;
  analyzeButton.textContent = "Đang phân tích...";
  resultText.textContent = "Đang gửi dữ liệu đến backend...";

  try {
    const requestData = buildAnalyzeRequest(message);
    const response = await fetch(getAnalyzeUrl(), {
      method: "POST",
      headers: requestData.headers,
      body: requestData.body,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || `HTTP ${response.status}`);
    }

    const text = await response.text();
    resultText.textContent = text || "Không nhận được phản hồi từ server.";
  } catch (error) {
    resultText.textContent = `Lỗi: ${error.message}`;
    console.error("Analyze request failed:", error);
  } finally {
    analyzeButton.disabled = false;
    analyzeButton.textContent = "Phân tích";
  }
}

analyzeButton.addEventListener("click", analyzeMessage);

messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
    analyzeMessage();
  }
});
