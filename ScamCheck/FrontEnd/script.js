const samples = {
  bank: "[VietBank] Tài khoản của quý khách đang bị khóa do giao dịch bất thường. Vui lòng bấm vào link http://vietbank-xacminh.top và nhập OTP để mở lại tài khoản trong 10 phút.",
  police:
    "Tôi là cán bộ công an. Anh/chị đang liên quan đến đường dây rửa tiền. Chuyển ngay 20 triệu vào tài khoản này để phục vụ điều tra, nếu không sẽ bị bắt giam.",
  prize:
    "Chúc mừng bạn đã trúng thưởng xe SH và 100 triệu đồng. Hãy gửi phí hồ sơ 500.000đ và CCCD để nhận thưởng ngay hôm nay.",
};

const scamLibrary = [
  {
    title: "Giả mạo ngân hàng",
    summary: "Dọa khóa tài khoản, báo giao dịch lạ, dụ bấm link hoặc đọc OTP.",
    examples: [
      "Tài khoản của quý khách sắp bị khóa. Vui lòng truy cập link dưới đây để xác thực thông tin.",
      "Tài khoản của bạn vừa nhận 20 triệu đồng. Nếu không phải bạn thực hiện, hãy gọi ngay số này.",
    ],
    signs: [
      "Tạo cảm giác khẩn cấp.",
      "Yêu cầu bấm vào đường link.",
      "Đòi mật khẩu, mã OTP.",
      "Số điện thoại hoặc website lạ.",
    ],
    defenses: [
      "Không cung cấp OTP cho bất kỳ ai.",
      "Tự gọi tổng đài chính thức của ngân hàng.",
      "Kiểm tra kỹ tên miền website.",
    ],
    note: "Ví dụ: đúng là vietcombank.com.vn, giả có thể là vietcombank-security.com.",
  },
  {
    title: "Giả mạo công an, viện kiểm sát",
    summary: "Tự xưng cơ quan chức năng, đe dọa bắt giữ và ép chuyển tiền.",
    examples: [
      "Bạn liên quan đến đường dây rửa tiền. Chúng tôi yêu cầu chuyển toàn bộ tiền sang tài khoản điều tra.",
    ],
    signs: [
      "Gọi điện tự xưng công an.",
      "Đe dọa bắt giữ.",
      "Yêu cầu giữ bí mật.",
      "Bắt chuyển tiền để chứng minh vô tội.",
    ],
    facts: [
      "Cơ quan chức năng không yêu cầu chuyển tiền qua điện thoại.",
      "Không điều tra qua Zalo.",
      "Không yêu cầu cung cấp OTP.",
    ],
    defenses: [
      "Cúp máy ngay.",
      "Gọi trực tiếp cơ quan công an địa phương để xác minh.",
    ],
  },
  {
    title: "Tuyển dụng online lương cao",
    summary: "Việc nhẹ lương cao, yêu cầu nộp phí hoặc làm nhiệm vụ nạp tiền.",
    examples: ["Làm việc tại nhà, 500.000 - 2.000.000đ/ngày."],
    signs: [
      "Không cần kinh nghiệm.",
      "Lương quá cao.",
      "Bắt nộp phí trước.",
      "Yêu cầu làm nhiệm vụ để nhận thưởng.",
    ],
    tactics: [
      "Nạp 100.000đ, hoàn lại 120.000đ.",
      "Nạp 500.000đ, hoàn lại 600.000đ.",
      "Sau đó yêu cầu nạp 5 triệu, 10 triệu và không cho rút tiền.",
    ],
    defenses: [
      "Không chuyển tiền để được nhận việc.",
      "Tìm hiểu công ty trước khi ứng tuyển.",
    ],
  },
  {
    title: "Lừa đảo đầu tư tài chính",
    summary: "Cam kết lợi nhuận cao, không rủi ro, rút tiền khó hoặc phải mời người mới.",
    examples: ["Đầu tư AI mới, lợi nhuận 5% mỗi ngày."],
    signs: [
      "Cam kết lợi nhuận.",
      "Nói rằng không có rủi ro.",
      "Rút tiền khó khăn.",
      "Tập trung vào việc giới thiệu người mới.",
    ],
    facts: ["Tiền của người đến sau trả cho người đến trước. Đây là mô hình Ponzi."],
    defenses: [
      "Nếu lợi nhuận nghe quá tốt để là sự thật thì thường là lừa đảo.",
      "Kiểm tra xem tổ chức có được cấp phép hay không.",
    ],
  },
  {
    title: "Mạo danh người thân",
    summary: "Dùng tài khoản bị chiếm hoặc tài khoản mới để nhắn vay tiền gấp.",
    examples: ["Mẹ ơi con đang cần chuyển gấp 8 triệu."],
    signs: [
      "Tài khoản mới lập.",
      "Tin nhắn bất thường.",
      "Thúc giục chuyển tiền ngay.",
    ],
    defenses: [
      "Gọi video hoặc gọi điện xác nhận.",
      "Không dựa hoàn toàn vào tin nhắn.",
    ],
  },
  {
    title: "Trúng thưởng giả",
    summary: "Báo trúng thưởng dù bạn không tham gia, rồi yêu cầu đóng phí nhận thưởng.",
    examples: ["Chúc mừng bạn đã trúng xe máy SH trị giá 90 triệu đồng."],
    signs: [
      "Chưa từng tham gia chương trình.",
      "Yêu cầu đóng phí nhận thưởng.",
      "Yêu cầu cung cấp thông tin cá nhân.",
    ],
    facts: ["Người trúng thưởng thật không phải trả phí để nhận thưởng."],
  },
  {
    title: "Link giả mạo (Phishing)",
    summary: "Tên miền gần giống website thật để đánh cắp tài khoản, email hoặc ngân hàng.",
    examples: ["Xem hóa đơn điện tại đây: dienluc-vn.com thay vì evn.com.vn."],
    signs: [
      "Tên miền gần giống.",
      "Chứa nhiều dấu gạch ngang.",
      "Rút gọn link bất thường.",
    ],
    targets: [
      "Đánh cắp tài khoản ngân hàng.",
      "Đánh cắp Facebook.",
      "Đánh cắp email.",
    ],
    defenses: [
      "Không đăng nhập từ link nhận qua SMS hoặc Messenger.",
      "Tự gõ địa chỉ website chính thức.",
    ],
  },
  {
    title: "Lừa đảo giao hàng",
    summary: "Giả shipper hoặc đơn hàng để dụ quét QR, bấm link thanh toán lạ.",
    examples: ["Anh/chị có đơn hàng chưa thanh toán 25.000đ."],
    signs: [
      "Bạn không đặt hàng.",
      "Yêu cầu quét QR.",
      "Gửi link thanh toán lạ.",
    ],
    defenses: [
      "Kiểm tra trên ứng dụng mua sắm.",
      "Không quét QR từ nguồn không tin cậy.",
    ],
  },
  {
    title: "Chiếm đoạt Facebook, Zalo",
    summary: "Giả cảnh báo vi phạm để dụ đăng nhập vào trang giả.",
    examples: [
      "Tài khoản của bạn vi phạm tiêu chuẩn cộng đồng. Nhấn vào đây để xác minh.",
    ],
    signs: [
      "Tin nhắn từ fanpage lạ.",
      "Link đăng nhập giả.",
      "Yêu cầu nhập mật khẩu.",
    ],
    defenses: [
      "Bật xác thực hai lớp (2FA).",
      "Không đăng nhập qua liên kết gửi riêng.",
    ],
  },
  {
    title: "Romance Scam (Lừa đảo tình cảm)",
    summary: "Làm quen lâu ngày, tạo niềm tin rồi dựng chuyện cần tiền.",
    examples: [
      "Đang bị tai nạn, cần tiền viện phí.",
      "Gửi quà nhưng cần đóng thuế.",
    ],
    signs: [
      "Yêu nhanh bất thường.",
      "Tránh gặp mặt.",
      "Cuối cùng luôn nhắc đến tiền.",
    ],
    defenses: [
      "Không gửi tiền cho người chưa gặp ngoài đời.",
      "Cảnh giác với các câu chuyện quá hoàn hảo.",
    ],
  },
  {
    title: "Scam AI",
    summary: "Dùng AI giả giọng người thân hoặc video deepfake để tạo áp lực chuyển tiền.",
    examples: [
      "Mẹ ơi con bị tai nạn, chuyển tiền giúp con.",
      "Cuộc gọi video deepfake giả người quen.",
    ],
    signs: [
      "Cuộc gọi ngắn.",
      "Âm thanh hơi méo.",
      "Thúc giục chuyển tiền ngay.",
    ],
    defenses: [
      "Gọi lại bằng số quen thuộc.",
      "Đặt mật khẩu gia đình để xác thực.",
    ],
  },
  {
    title: "Dấu hiệu đỏ và quy tắc 30 giây",
    summary: "Những tín hiệu xuất hiện trong hầu hết các vụ lừa đảo.",
    signs: [
      "Yêu cầu chuyển tiền ngay.",
      "Bảo giữ bí mật.",
      "Đòi OTP.",
      "Hứa lợi nhuận cao.",
      "Đe dọa khóa tài khoản.",
      "Tạo áp lực thời gian.",
      "Yêu cầu cài ứng dụng lạ.",
      "Yêu cầu truy cập từ xa vào điện thoại hoặc máy tính.",
      "Yêu cầu cung cấp CCCD, ảnh khuôn mặt, thông tin ngân hàng.",
    ],
    defenses: [
      "Dừng lại 30 giây.",
      "Không bấm link ngay.",
      "Không cung cấp OTP.",
      "Xác minh bằng kênh chính thức.",
      "Hỏi ý kiến người thân nếu thấy áp lực hoặc hoang mang.",
    ],
    note: "Chỉ cần tuân thủ 5 bước này, bạn có thể tránh được phần lớn các hình thức lừa đảo phổ biến hiện nay.",
  },
];

let historyData = JSON.parse(localStorage.getItem("scamcheck_history")) || [];

function saveHistory() {
  localStorage.setItem("scamcheck_history", JSON.stringify(historyData));
}

const screens = {
  home: document.getElementById("homeScreen"),
  loading: document.getElementById("loadingScreen"),
  result: document.getElementById("resultScreen"),
  history: document.getElementById("historyScreen"),
  library: document.getElementById("libraryScreen"),
};

const messageInput = document.getElementById("messageInput");
const analyzeBtn = document.getElementById("analyzeBtn");
const websiteUrlInput = document.getElementById("websiteUrlInput");
const analyzeWebsiteBtn = document.getElementById("analyzeWebsiteBtn");
const openHistoryBtn = document.getElementById("openHistoryBtn");
const closeHistoryBtn = document.getElementById("closeHistoryBtn");
const openLibraryBtn = document.getElementById("openLibraryBtn");
const closeLibraryBtn = document.getElementById("closeLibraryBtn");
const backHomeBtn = document.getElementById("backHomeBtn");
const resultShareUrl = document.getElementById("resultShareUrl");
const copyShareUrlBtn = document.getElementById("copyShareUrlBtn");

function showScreen(name) {
  Object.values(screens).forEach((screen) => screen.classList.remove("active"));
  screens[name].classList.add("active");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function showFriendlyError(message) {
  alert(message);
  showScreen("home");
}

function classifyMessage(text) {
  const lower = text.toLowerCase();
  let score = 0;

  if (
    lower.includes("otp") ||
    lower.includes("mật khẩu") ||
    lower.includes("ngân hàng")
  )
    score += 3;

  if (
    lower.includes("chuyển") ||
    lower.includes("tiền") ||
    lower.includes("phí")
  )
    score += 2;

  if (
    lower.includes("công an") ||
    lower.includes("điều tra") ||
    lower.includes("bắt")
  )
    score += 3;

  if (
    lower.includes("link") ||
    lower.includes("http") ||
    lower.includes("bấm vào")
  )
    score += 2;

  if (
    lower.includes("gấp") ||
    lower.includes("ngay") ||
    lower.includes("10 phút") ||
    lower.includes("khóa")
  )
    score += 2;

  if (lower.includes("trúng thưởng") || lower.includes("cccd")) score += 2;

  if (score >= 7) return "Nghiêm trọng";
  if (score >= 5) return "Cao";
  if (score >= 2) return "Trung bình";
  return "Thấp";
}

function levelClass(level) {
  return (
    {
      Thấp: "low",
      "Trung bình": "medium",
      Cao: "high",
      "Nghiêm trọng": "severe",
    }[level] || "medium"
  );
}

function riskDisplay(level) {
  if (level === "Thấp") {
    return {
      label: "An toàn",
      percent: "18%",
    };
  }

  if (level === "Trung bình") {
    return {
      label: "Nghi ngờ",
      percent: "55%",
    };
  }

  return {
    label: "Nguy hiểm",
    percent: level === "Cao" ? "82%" : "100%",
  };
}

function renderResult(text, aiResult = null, shouldSaveHistory = true) {
  const level = aiResult?.level || classifyMessage(text);
  const type = levelClass(level);
  const displayRisk = riskDisplay(level);
  const shouldShowWarningDetails = level !== "Thấp";

  const riskCard = document.getElementById("riskCard");
  const riskTitle = document.getElementById("riskTitle");
  const riskDescription = document.getElementById("riskDescription");
  const riskBadge = document.getElementById("riskBadge");
  const riskMeterFill = document.getElementById("riskMeterFill");

  riskCard.className = `main-card risk-card risk-${type}`;
  riskTitle.textContent = displayRisk.label;
  riskBadge.textContent = displayRisk.label;

  if (riskMeterFill) {
    riskMeterFill.style.width = displayRisk.percent;
  }

  const descriptions = {
    Thấp: "Tin nhắn chưa có dấu hiệu nguy hiểm rõ ràng, nhưng vẫn nên kiểm tra nguồn gửi.",
    "Trung bình":
      "Tin nhắn có một số điểm đáng ngờ, cần xác minh trước khi làm theo.",
    Cao: "Tin nhắn có nhiều dấu hiệu lừa đảo và có thể gây mất tiền hoặc lộ thông tin.",
    "Nghiêm trọng":
      "Tin nhắn có dấu hiệu lừa đảo rất rõ, tuyệt đối không làm theo yêu cầu.",
  };

  riskDescription.textContent = aiResult?.description || descriptions[level];

  if (resultShareUrl) {
    resultShareUrl.value = aiResult?.result_url || "";
  }

  const signCard = document.getElementById("signCard");
  const suspiciousCard = document.getElementById("suspiciousCard");
  const counselorCard = document.querySelector(".counselor-card");

  if (signCard) {
    signCard.style.display = shouldShowWarningDetails ? "block" : "none";
  }

  if (suspiciousCard) {
    suspiciousCard.style.display = shouldShowWarningDetails ? "block" : "none";
  }

  if (counselorCard) {
    counselorCard.style.display = shouldShowWarningDetails ? "flex" : "none";
  }

  if (shouldShowWarningDetails) {
    const signs = aiResult?.signs || [
      "Có yếu tố thúc giục hoặc gây áp lực thời gian.",
      "Có thể yêu cầu thông tin nhạy cảm như OTP, CCCD, tài khoản ngân hàng.",
      "Nội dung có dấu hiệu giả danh tổ chức hoặc cơ quan chức năng.",
    ];

    document.getElementById("signList").innerHTML = signs
      .map((item) => `<li>${item}</li>`)
      .join("");

    const quote =
      aiResult?.suspicious_quote ||
      text.slice(0, 180) + (text.length > 180 ? "..." : "");

    document.getElementById("suspiciousQuote").textContent = quote;

    document.getElementById("counselorText").textContent =
      aiResult?.counselor ||
      "Con hãy bình tĩnh, đừng bấm vào liên kết và cũng đừng chuyển tiền. Hãy hỏi người thân hoặc gọi tổng đài chính thức để kiểm tra lại nhé.";
  }

  const actions = shouldShowWarningDetails
    ? aiResult?.actions || [
        "Không bấm vào đường link lạ.",
        "Không chuyển tiền hoặc cung cấp OTP.",
        "Gọi số chính thức của ngân hàng/cơ quan để xác minh.",
      ]
    : [
        "Kiểm tra xem người gửi là ai, bạn có quen biết họ không.",
        "Chưa cần làm gì đặc biệt, nhưng nếu là số lạ, hãy cẩn trọng với các tin nhắn tiếp theo.",
        "Tuyệt đối không nhập vào đường link hay cung cấp thông tin cá nhân nếu có yêu cầu trong tương lai.",
      ];

  document.getElementById("actionList").innerHTML = actions
    .map(
      (item, index) =>
        `<div class="action-item"><strong>${index + 1}.</strong> ${item}</div>`,
    )
    .join("");

  if (shouldSaveHistory) {
    historyData.unshift({
      time: new Date().toLocaleString("vi-VN", {
        hour: "2-digit",
        minute: "2-digit",
        day: "2-digit",
        month: "2-digit",
      }),
      level,
      short: text.slice(0, 58) + (text.length > 58 ? "..." : ""),
      sample: text,
      aiResult,
    });

    historyData = historyData.slice(0, 10);
    saveHistory();
  }
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderLibrarySection(title, items, className = "") {
  if (!items || items.length === 0) return "";

  return `
    <div class="library-section ${className}">
      <h3>${escapeHtml(title)}</h3>
      <ul>
        ${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
      </ul>
    </div>
  `;
}

function renderScamLibrary() {
  const libraryList = document.getElementById("libraryList");

  libraryList.innerHTML = scamLibrary
    .map(
      (item, index) => `
        <article class="library-item">
          <button class="library-toggle" type="button" aria-expanded="false" data-index="${index}">
            <span class="library-toggle-title">
              <strong>${index + 1}. ${escapeHtml(item.title)}</strong>
              <span>${escapeHtml(item.summary)}</span>
            </span>
            <span class="library-chevron" aria-hidden="true">⌄</span>
          </button>
          <div class="library-detail">
            ${renderLibrarySection("Ví dụ", item.examples, "library-example")}
            ${renderLibrarySection("Dấu hiệu nhận biết", item.signs)}
            ${renderLibrarySection("Chiêu thức thường gặp", item.tactics)}
            ${renderLibrarySection("Mục tiêu của kẻ gian", item.targets)}
            ${renderLibrarySection("Sự thật / Quy tắc vàng", item.facts, "library-rule")}
            ${renderLibrarySection("Cách phòng tránh", item.defenses)}
            ${
              item.note
                ? `<div class="library-section library-rule"><h3>Ghi nhớ</h3><p>${escapeHtml(item.note)}</p></div>`
                : ""
            }
          </div>
        </article>
      `,
    )
    .join("");

  document.querySelectorAll(".library-toggle").forEach((button) => {
    button.addEventListener("click", () => {
      const item = button.closest(".library-item");
      const isOpen = item.classList.toggle("open");

      button.setAttribute("aria-expanded", String(isOpen));
    });
  });
}

function renderHistory() {
  const historyList = document.getElementById("historyList");

  if (historyData.length === 0) {
    historyList.innerHTML = `
      <div class="empty-history">
        Chưa có lịch sử phân tích. Hãy nhập một tin nhắn và bấm Phân tích nhé.
      </div>
    `;
    return;
  }

  historyList.innerHTML = historyData
    .map((item, index) => {
      const type = levelClass(item.level);
      return `
      <article class="history-item">
        <strong>${item.time}</strong>
        <span class="level-pill level-${type}">${item.level}</span>
        <span>${item.short}</span>
        <button class="view-btn" data-index="${index}">Xem lại</button>
      </article>
    `;
    })
    .join("");

  document.querySelectorAll(".view-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const item = historyData[Number(btn.dataset.index)];
      renderResult(item.sample, item.aiResult || null, false);
      showScreen("result");
    });
  });
}

document.querySelectorAll(".sample-buttons button").forEach((button) => {
  button.addEventListener("click", () => {
    messageInput.value = samples[button.dataset.sample];
    messageInput.focus();
  });
});

async function analyzeWithAI(text) {
  try {
    const response = await fetch("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });

    let data;

    try {
      data = await response.json();
    } catch {
      throw new Error(
        "AI trả về dữ liệu không đúng cấu trúc. Bạn hãy thử lại nhé.",
      );
    }

    if (!response.ok) {
      throw new Error(
        data.error || "Không thể gọi AI lúc này. Bạn hãy thử lại sau nhé.",
      );
    }

    const requiredFields = [
      "level",
      "description",
      "signs",
      "suspicious_quote",
      "actions",
      "counselor",
    ];

    const validLevels = ["Thấp", "Trung bình", "Cao", "Nghiêm trọng"];

    const isValid =
      data &&
      typeof data === "object" &&
      requiredFields.every((field) => field in data) &&
      validLevels.includes(data.level) &&
      Array.isArray(data.signs) &&
      Array.isArray(data.actions);

    if (!isValid) {
      throw new Error(
        "AI trả về dữ liệu chưa đúng cấu trúc. Ứng dụng vẫn hoạt động, bạn hãy thử lại nhé.",
      );
    }

    return data;
  } catch (error) {
    if (!navigator.onLine) {
      throw new Error(
        "Bạn đang mất kết nối mạng. Hãy kiểm tra Wi-Fi/Internet rồi thử lại nhé.",
      );
    }

    throw error;
  }
}

async function analyzeWebsite(url) {
  try {
    const response = await fetch("/analyze-website", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });

    const rawBody = await response.text();
    let data;

    try {
      data = rawBody ? JSON.parse(rawBody) : {};
    } catch {
      throw new Error(
        rawBody.slice(0, 220) ||
          "Backend returned an empty website scan response.",
      );
    }

    if (!response.ok) {
      throw new Error(data.error || "Could not scan this website.");
    }

    return data;
  } catch (error) {
    if (!navigator.onLine) {
      throw new Error("Bạn đang mất kết nối mạng. Hãy kiểm tra Internet rồi thử lại.");
    }

    throw error;
  }
}

async function sendAlert(message, resultId = "") {
  try {
    await fetch("/send-alert", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        result_id: resultId,
      }),
    });
  } catch (error) {
    console.warn("Could not send alert", error);
  }
}

async function loadSharedResultFromUrl() {
  const match = window.location.pathname.match(/^\/r\/([^/]+)$/);

  if (!match) return;

  showScreen("loading");

  try {
    const response = await fetch(`/api/results/${encodeURIComponent(match[1])}`);
    const saved = await response.json();

    if (!response.ok) {
      throw new Error(saved.error || "Không tìm thấy kết quả đã lưu.");
    }

    const savedResult = saved.result || {};
    savedResult.result_id = saved.id;
    savedResult.result_url = window.location.href;

    renderResult(saved.message || "", savedResult, false);
    showScreen("result");
  } catch (error) {
    alert(error.message || "Không thể tải kết quả đã lưu.");
    showScreen("home");
  }
}

analyzeBtn.addEventListener("click", async () => {
  const text = messageInput.value.trim();

  if (!text) {
    showFriendlyError(
      "Bạn chưa nhập tin nhắn. Hãy dán một tin nhắn cần kiểm tra nhé.",
    );
    return;
  }

  if (text.length > 5000) {
    showFriendlyError(
      "Tin nhắn quá dài. Bạn hãy rút gọn dưới 5000 ký tự rồi thử lại nhé.",
    );
    return;
  }

  showScreen("loading");

  try {
    const aiResult = await analyzeWithAI(text);
    renderResult(text, aiResult, true);
    sendAlert("Someone submitted a scam check", aiResult.result_id || "");
    showScreen("result");
  } catch (error) {
    console.warn(error);
    alert(
      error.message ||
        "Ứng dụng gặp lỗi nhưng vẫn hoạt động. Bạn hãy thử lại nhé.",
    );
    renderResult(text, null, true);
    showScreen("result");
  }
});

if (analyzeWebsiteBtn && websiteUrlInput) {
  analyzeWebsiteBtn.addEventListener("click", async () => {
    const url = websiteUrlInput.value.trim();

    if (!url) {
      showFriendlyError("Bạn chưa nhập URL website cần kiểm tra.");
      return;
    }

    showScreen("loading");

    try {
      const websiteResult = await analyzeWebsite(url);
      const source = websiteResult.website?.final_url || url;

      renderResult(source, websiteResult, true);
      sendAlert("Someone submitted a website scam check", websiteResult.result_id || "");
      showScreen("result");
    } catch (error) {
      alert(error.message || "Không thể kiểm tra website này. Bạn hãy thử lại.");
      showScreen("home");
    }
  });
}

openHistoryBtn.addEventListener("click", () => {
  renderHistory();
  showScreen("history");
});

openLibraryBtn.addEventListener("click", () => {
  renderScamLibrary();
  showScreen("library");
});

closeHistoryBtn.addEventListener("click", () => showScreen("home"));
closeLibraryBtn.addEventListener("click", () => showScreen("home"));
backHomeBtn.addEventListener("click", () => showScreen("home"));
let latestMessage = "";
let latestResult = null;

const originalRenderResult = renderResult;

renderResult = function (text, aiResult = null, shouldSaveHistory = true) {
  latestMessage = text;
  warningCardCreated = false;

  latestResult = aiResult || {
    level: classifyMessage(text),
    description: "Kết quả phân tích mẫu.",
    signs: ["Có nội dung cần kiểm tra kỹ."],
    suspicious_quote: text.slice(0, 120),
    actions: [
      "Không bấm link lạ.",
      "Không cung cấp OTP hoặc mật khẩu.",
      "Xác minh qua kênh chính thức.",
    ],
  };

  originalRenderResult(text, aiResult, shouldSaveHistory);
};

function canvasRoundRect(ctx, x, y, width, height, radius) {
  ctx.beginPath();

  if (ctx.roundRect) {
    ctx.roundRect(x, y, width, height, radius);
  } else {
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
  }

  ctx.closePath();
  ctx.fill();
}

function wrapText(ctx, text, x, y, maxWidth, lineHeight, maxLines = 4) {
  const words = String(text || "").split(" ");
  let line = "";
  let lines = 0;

  for (let i = 0; i < words.length; i++) {
    const testLine = line + words[i] + " ";
    const width = ctx.measureText(testLine).width;

    if (width > maxWidth && i > 0) {
      ctx.fillText(line.trim(), x, y);
      line = words[i] + " ";
      y += lineHeight;
      lines++;

      if (lines >= maxLines - 1) {
        ctx.fillText(
          (line + words.slice(i + 1).join(" ")).trim().slice(0, 90) + "...",
          x,
          y,
        );
        return y + lineHeight;
      }
    } else {
      line = testLine;
    }
  }

  ctx.fillText(line.trim(), x, y);
  return y + lineHeight;
}
let warningCardCreated = false;

async function createWarningCard() {
  if (!latestResult) {
    alert("Bạn hãy phân tích một tin nhắn trước khi tạo thẻ cảnh báo nhé.");
    return;
  }

  const canvas = document.getElementById("warningCanvas");
  const ctx = canvas.getContext("2d");

  const level = latestResult.level || "Trung bình";
  const productUrl = "https://sc-bdwz.onrender.com";

  const levelColors = {
    Thấp: "#16a34a",
    "Trung bình": "#d49b00",
    Cao: "#f97316",
    "Nghiêm trọng": "#dc2626",
  };

  const color = levelColors[level] || "#d49b00";

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = "#f8fbff";
  ctx.fillRect(0, 0, 1080, 1350);

  ctx.fillStyle = "#0f172a";
  ctx.fillRect(0, 0, 1080, 190);

  ctx.fillStyle = "#ffffff";
  ctx.font = "bold 58px Arial";
  ctx.fillText("🛡️ ScamCheck AI", 70, 90);

  ctx.font = "28px Arial";
  ctx.fillText("Thẻ cảnh báo lừa đảo để chia sẻ cho người thân", 70, 140);

  ctx.fillStyle = "#ffffff";
  canvasRoundRect(ctx, 60, 240, 960, 220, 28);

  ctx.fillStyle = color;
  ctx.font = "bold 38px Arial";
  ctx.fillText("MỨC RỦI RO", 100, 300);

  ctx.font = "bold 66px Arial";
  ctx.fillText(level.toUpperCase(), 100, 380);

  ctx.fillStyle = "#334155";
  ctx.font = "30px Arial";
  wrapText(
    ctx,
    latestResult.description || "Cần kiểm tra kỹ trước khi làm theo.",
    100,
    430,
    850,
    36,
    2,
  );

  ctx.fillStyle = "#ffffff";
  canvasRoundRect(ctx, 60, 500, 960, 300, 28);

  ctx.fillStyle = "#0f172a";
  ctx.font = "bold 36px Arial";
  ctx.fillText("DẤU HIỆU CHÍNH", 100, 560);

  ctx.font = "28px Arial";
  let y = 620;

  const signs = latestResult.signs || ["Có nội dung cần kiểm tra kỹ."];

  signs.slice(0, 4).forEach((sign) => {
    ctx.fillStyle = color;
    ctx.fillText("•", 105, y);

    ctx.fillStyle = "#1f2937";
    y = wrapText(ctx, sign, 135, y, 800, 38, 2);
    y += 8;
  });

  ctx.fillStyle = "#ffffff";
  canvasRoundRect(ctx, 60, 840, 960, 210, 28);

  ctx.fillStyle = "#0f172a";
  ctx.font = "bold 34px Arial";
  ctx.fillText("ĐOẠN TRÍCH ĐÁNG NGỜ", 100, 900);

  ctx.fillStyle = "#374151";
  ctx.font = "28px Arial";
  wrapText(
    ctx,
    `"${latestResult.suspicious_quote || latestMessage.slice(0, 120)}"`,
    100,
    955,
    850,
    38,
    3,
  );

  ctx.fillStyle = "#ffffff";
  canvasRoundRect(ctx, 60, 1100, 960, 190, 28);

  const qrImage = new Image();
  qrImage.crossOrigin = "anonymous";

  qrImage.src =
    "https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=" +
    encodeURIComponent(productUrl);

  await new Promise((resolve, reject) => {
    qrImage.onload = resolve;
    qrImage.onerror = reject;
  });

  ctx.drawImage(qrImage, 95, 1125, 150, 150);

  ctx.fillStyle = "#0f172a";
  ctx.font = "bold 30px Arial";
  ctx.fillText("Quét mã để truy cập ScamCheck AI", 270, 1160);

  ctx.fillStyle = "#2563eb";
  ctx.font = "26px Arial";
  wrapText(ctx, productUrl, 270, 1205, 700, 34, 2);

  ctx.fillStyle = "#6b7280";
  ctx.font = "24px Arial";
  ctx.fillText("Chia sẻ để giúp người thân tránh lừa đảo.", 270, 1265);

  warningCardCreated = true;
  alert("Đã tạo thẻ cảnh báo. Bạn có thể tải ảnh về máy.");
}

async function downloadWarningCard() {
  const canvas = document.getElementById("warningCanvas");

  if (!latestResult) {
    alert("Bạn hãy phân tích tin nhắn trước nhé.");
    return;
  }

  if (!warningCardCreated) {
    await createWarningCard();
  }

  canvas.toBlob((blob) => {
    if (!blob) {
      alert("Không thể tạo ảnh. Bạn hãy thử lại nhé.");
      return;
    }

    const imageUrl = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = imageUrl;
    link.download = "the-canh-bao-scamcheck.png";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(imageUrl);
  }, "image/png");
}

const createWarningCardBtn = document.getElementById("createWarningCardBtn");
const downloadWarningCardBtn = document.getElementById(
  "downloadWarningCardBtn",
);

if (createWarningCardBtn) {
  createWarningCardBtn.addEventListener("click", createWarningCard);
}

if (downloadWarningCardBtn) {
  downloadWarningCardBtn.addEventListener("click", downloadWarningCard);
}

if (copyShareUrlBtn && resultShareUrl) {
  copyShareUrlBtn.addEventListener("click", async () => {
    if (!resultShareUrl.value) {
      alert("Chưa có link kết quả để sao chép.");
      return;
    }

    try {
      await navigator.clipboard.writeText(resultShareUrl.value);
      copyShareUrlBtn.textContent = "Đã sao chép";

      setTimeout(() => {
        copyShareUrlBtn.textContent = "Sao chép";
      }, 1600);
    } catch {
      resultShareUrl.select();
      document.execCommand("copy");
    }
  });
}

loadSharedResultFromUrl();
