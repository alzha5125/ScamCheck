const button = document.getElementById("analyzeButton");
const resultText = document.getElementById("resultText");
const messageInput = document.getElementById("messageInput");
const severityFill = document.getElementById("severityFill");

function setSeverity(level) {
  const safeLevel = ["low", "medium", "high", "critical"].includes(level)
    ? level
    : "low";

  severityFill.classList.remove(
    "severity-low",
    "severity-medium",
    "severity-high",
    "severity-critical"
  );
  severityFill.classList.add(`severity-${safeLevel}`);
}

function classifySeverity(text, riskScore) {
  const normalizedText = (text || "").toString().toLowerCase();
  const score = Number(riskScore);

  if (
    normalizedText.includes("nghiêm trọng") ||
    normalizedText.includes("nghiem trong") ||
    score >= 85
  ) {
    return "critical";
  }

  if (normalizedText.includes("cao") || score >= 65) {
    return "high";
  }

  if (
    normalizedText.includes("trung bình") ||
    normalizedText.includes("trung binh") ||
    score >= 35
  ) {
    return "medium";
  }

  return "low";
}

button.addEventListener("click", async () => {
  const message = messageInput.value.trim();

  if (!message) {
    alert("Vui lòng nhập nội dung tin nhắn");
    return;
  }

  resultText.innerHTML = "Đang phân tích...";
  severityFill.style.width = "0%";
  setSeverity("low");

  try {
    const response = await fetch(
      "https://scamcheck-2-07zf.onrender.com/analyze",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        },
        body: new URLSearchParams({ message }),
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const rawResponse = await response.text();
    let result = rawResponse;

    try {
      result = JSON.parse(rawResponse);
    } catch (_) {
      // Backend can return plain text; keep the original string.
    }

    const analysisText =
      typeof result === "string"
        ? result
        : result.analysis || result.text || rawResponse;
    const riskScore = typeof result === "object" ? result.riskScore : undefined;
    const severity =
      typeof result === "object" && result.severity
        ? result.severity
        : classifySeverity(analysisText, riskScore);
    const width =
      typeof riskScore === "number" && !Number.isNaN(riskScore)
        ? `${Math.max(0, Math.min(riskScore, 100))}%`
        : severity === "critical"
          ? "100%"
          : severity === "high"
            ? "75%"
            : severity === "medium"
              ? "50%"
              : "25%";

    resultText.innerHTML = analysisText;
    severityFill.style.width = width;
    setSeverity(severity);
  } catch (error) {
    console.error(error);

    resultText.innerHTML = "❌ Không thể kết nối tới máy chủ";
    severityFill.style.width = "0%";
    setSeverity("low");
  }
});
