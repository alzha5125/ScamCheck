const button = document.getElementById("analyzeButton");
const resultText = document.getElementById("resultText");
const messageInput = document.getElementById("messageInput");

button.addEventListener("click", async () => {
  const message = messageInput.value.trim();

  if (!message) {
    alert("Vui lòng nhập nội dung tin nhắn");
    return;
  }

  resultText.innerHTML = "🔄 Đang phân tích...";

  try {
    const response = await fetch(
      "https://scamcheck-2-07zf.onrender.com/analyze",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: message,
        }),
      },
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const result = await response.text();

    resultText.innerHTML = result;
  } catch (error) {
    console.error(error);

    resultText.innerHTML = "❌ Không thể kết nối tới máy chủ";
  }
});
