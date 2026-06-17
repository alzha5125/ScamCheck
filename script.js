const messageInput = document.getElementById("messageInput");
const analyzeButton = document.getElementById("analyzeButton");
const resultText = document.getElementById("resultText");

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
    const response = await fetch("/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
      },
      body: new URLSearchParams({ message }),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const text = await response.text();
    resultText.textContent = text || "Không nhận được phản hồi từ server.";
  } catch (error) {
    resultText.textContent =
      "Không thể kết nối tới backend Python. Hãy kiểm tra Flask đang chạy và endpoint /analyze.";
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
