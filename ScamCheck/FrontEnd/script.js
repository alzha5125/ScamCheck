const samples = {
  bank: "[VietBank] Tài khoản của quý khách đang bị khóa do giao dịch bất thường. Vui lòng bấm vào link http://vietbank-xacminh.top và nhập OTP để mở lại tài khoản trong 10 phút.",
  police:
    "Tôi là cán bộ công an. Anh/chị đang liên quan đến đường dây rửa tiền. Chuyển ngay 20 triệu vào tài khoản này để phục vụ điều tra, nếu không sẽ bị bắt giam.",
  prize:
    "Chúc mừng bạn đã trúng thưởng xe SH và 100 triệu đồng. Hãy gửi phí hồ sơ 500.000đ và CCCD để nhận thưởng ngay hôm nay.",
};

const scamLibrary = [
  {
    category: "Giả ngân hàng",
    title: "Khóa tài khoản ngân hàng",
    summary:
      "Kẻ gian giả mạo ngân hàng, thông báo tài khoản bị khóa để dụ người dùng bấm link hoặc nhập OTP.",
    examples: [
      "Tài khoản của quý khách đang bị khóa do giao dịch bất thường. Vui lòng truy cập link để xác minh.",
      "Nếu không xác thực trong 10 phút, tài khoản ngân hàng của bạn sẽ bị tạm khóa.",
    ],
    signs: [
      "Dọa khóa tài khoản.",
      "Tạo áp lực thời gian.",
      "Yêu cầu bấm vào đường link.",
      "Đòi OTP hoặc thông tin ngân hàng.",
    ],
    defenses: [
      "Không bấm vào link trong tin nhắn.",
      "Không cung cấp OTP cho bất kỳ ai.",
      "Tự gọi tổng đài chính thức của ngân hàng để kiểm tra.",
    ],
  },
  {
    category: "Giả ngân hàng",
    title: "Giao dịch bất thường",
    summary:
      "Tin nhắn giả cảnh báo có giao dịch lạ để khiến người dùng hoảng sợ và làm theo hướng dẫn.",
    examples: [
      "Tài khoản của bạn vừa phát sinh giao dịch 20.000.000đ. Nếu không phải bạn, hãy xác minh ngay.",
      "Hệ thống phát hiện giao dịch đáng ngờ. Vui lòng đăng nhập để kiểm tra.",
    ],
    signs: [
      "Thông báo giao dịch bất thường.",
      "Yêu cầu xác minh gấp.",
      "Có thể kèm link lạ.",
      "Khiến người nhận lo sợ mất tiền.",
    ],
    defenses: [
      "Mở app ngân hàng chính thức để kiểm tra.",
      "Không đăng nhập qua link được gửi trong SMS.",
      "Liên hệ ngân hàng bằng số tổng đài chính thức.",
    ],
  },
  {
    category: "Giả ngân hàng",
    title: "Nâng cấp hoặc xác minh tài khoản",
    summary:
      "Kẻ gian yêu cầu cập nhật hồ sơ, nâng cấp tài khoản hoặc xác minh thông tin để lấy dữ liệu cá nhân.",
    examples: [
      "Quý khách cần cập nhật CCCD để tiếp tục sử dụng dịch vụ ngân hàng số.",
      "Tài khoản của bạn cần được xác minh để nâng cấp bảo mật.",
    ],
    signs: [
      "Yêu cầu cập nhật thông tin cá nhân.",
      "Đòi CCCD, số tài khoản hoặc OTP.",
      "Dùng lý do bảo mật để tạo sự tin tưởng.",
    ],
    defenses: [
      "Chỉ cập nhật thông tin trên app hoặc website chính thức.",
      "Không gửi ảnh CCCD qua tin nhắn.",
      "Kiểm tra tên miền trước khi đăng nhập.",
    ],
  },

  {
    category: "Giả cơ quan công an",
    title: "Liên quan đường dây rửa tiền",
    summary:
      "Kẻ gian giả danh công an, nói người dùng liên quan vụ án để đe dọa và ép chuyển tiền.",
    examples: [
      "Anh/chị đang liên quan đến đường dây rửa tiền. Cần chuyển tiền để phục vụ điều tra.",
      "Tài khoản của anh/chị có dấu hiệu phạm pháp. Hãy hợp tác ngay để tránh bị bắt.",
    ],
    signs: [
      "Tự xưng công an hoặc viện kiểm sát.",
      "Đe dọa bắt giữ.",
      "Yêu cầu giữ bí mật.",
      "Ép chuyển tiền để chứng minh vô tội.",
    ],
    defenses: [
      "Cúp máy và không làm theo yêu cầu.",
      "Không chuyển tiền cho bất kỳ tài khoản cá nhân nào.",
      "Liên hệ công an địa phương để xác minh.",
    ],
  },
  {
    category: "Giả cơ quan công an",
    title: "Lệnh bắt giữ giả",
    summary:
      "Đối tượng gửi hoặc đọc lệnh bắt giữ giả nhằm tạo áp lực tâm lý khiến nạn nhân mất bình tĩnh.",
    examples: [
      "Chúng tôi đã có lệnh bắt giữ anh/chị. Nếu không hợp tác ngay sẽ bị xử lý.",
      "Anh/chị phải chuyển tiền bảo lãnh trong hôm nay để được xem xét.",
    ],
    signs: [
      "Dọa có lệnh bắt giữ.",
      "Yêu cầu xử lý qua điện thoại.",
      "Đòi chuyển tiền bảo lãnh.",
      "Không cho người dùng hỏi người thân.",
    ],
    defenses: [
      "Không trao đổi tiếp qua cuộc gọi lạ.",
      "Không gửi giấy tờ cá nhân.",
      "Đến trực tiếp cơ quan công an gần nhất nếu cần xác minh.",
    ],
  },
  {
    category: "Giả cơ quan công an",
    title: "Giả cán bộ hướng dẫn cài ứng dụng",
    summary:
      "Kẻ gian giả danh cán bộ, yêu cầu cài ứng dụng lạ hoặc cấp quyền điều khiển điện thoại.",
    examples: [
      "Anh/chị cần cài ứng dụng định danh để phục vụ điều tra.",
      "Cài app này để chúng tôi kiểm tra tài khoản và xác minh thông tin.",
    ],
    signs: [
      "Yêu cầu cài ứng dụng ngoài kho chính thức.",
      "Đòi quyền truy cập điện thoại.",
      "Yêu cầu chia sẻ màn hình.",
      "Có thể đánh cắp OTP hoặc tài khoản ngân hàng.",
    ],
    defenses: [
      "Không cài ứng dụng từ link lạ.",
      "Không chia sẻ màn hình khi mở app ngân hàng.",
      "Gỡ ứng dụng lạ nếu đã cài và đổi mật khẩu ngay.",
    ],
  },

  {
    category: "Trúng thưởng",
    title: "Trúng xe máy hoặc tiền mặt",
    summary:
      "Tin nhắn báo trúng thưởng giá trị lớn dù người dùng không tham gia chương trình nào.",
    examples: [
      "Chúc mừng bạn đã trúng xe SH và 100 triệu đồng.",
      "Bạn là khách hàng may mắn nhận giải thưởng đặc biệt hôm nay.",
    ],
    signs: [
      "Báo trúng thưởng bất ngờ.",
      "Giải thưởng có giá trị lớn.",
      "Không nêu rõ chương trình thật.",
      "Yêu cầu phản hồi nhanh.",
    ],
    defenses: [
      "Không tin khi chưa từng tham gia chương trình.",
      "Kiểm tra fanpage hoặc website chính thức.",
      "Không gửi thông tin cá nhân để nhận thưởng.",
    ],
  },
  {
    category: "Trúng thưởng",
    title: "Đóng phí nhận thưởng",
    summary:
      "Kẻ gian yêu cầu người dùng chuyển một khoản phí nhỏ trước khi nhận phần thưởng lớn.",
    examples: [
      "Vui lòng chuyển 500.000đ phí hồ sơ để nhận giải thưởng 100 triệu.",
      "Bạn cần đóng phí vận chuyển quà tặng trước khi nhận giải.",
    ],
    signs: [
      "Yêu cầu chuyển phí trước.",
      "Hứa nhận phần thưởng lớn sau đó.",
      "Có thể yêu cầu CCCD hoặc số tài khoản.",
    ],
    defenses: [
      "Không chuyển tiền để nhận thưởng.",
      "Không gửi CCCD hoặc thông tin ngân hàng.",
      "Báo cáo tin nhắn cho nhà mạng hoặc nền tảng liên quan.",
    ],
  },
  {
    category: "Trúng thưởng",
    title: "Vòng quay may mắn giả",
    summary:
      "Đường link mời quay thưởng, nhận quà miễn phí hoặc chia sẻ cho bạn bè để lấy phần thưởng.",
    examples: [
      "Bạn có một lượt quay trúng iPhone miễn phí. Bấm vào link để nhận quà.",
      "Chia sẻ link này cho 5 người để mở khóa phần thưởng.",
    ],
    signs: [
      "Link quay thưởng không rõ nguồn gốc.",
      "Yêu cầu chia sẻ cho nhiều người.",
      "Hứa quà tặng quá hấp dẫn.",
      "Có thể yêu cầu đăng nhập hoặc nhập thông tin cá nhân.",
    ],
    defenses: [
      "Không tham gia vòng quay từ link lạ.",
      "Không chia sẻ link chưa kiểm chứng.",
      "Không nhập tài khoản mạng xã hội vào trang lạ.",
    ],
  },

  {
    category: "Giả đơn vị giao hàng",
    title: "Shipper yêu cầu chuyển khoản trước",
    summary:
      "Kẻ gian giả làm shipper, yêu cầu người nhận chuyển khoản phí hàng hoặc phí giao trước.",
    examples: [
      "Em là shipper, đơn của anh/chị cần thanh toán trước 35.000đ để giao.",
      "Đơn hàng đang chờ giao, vui lòng chuyển khoản phí vận chuyển trước.",
    ],
    signs: [
      "Tự xưng shipper nhưng không có thông tin đơn rõ ràng.",
      "Yêu cầu chuyển khoản trước.",
      "Tạo cảm giác đơn hàng sắp bị hủy.",
    ],
    defenses: [
      "Kiểm tra đơn hàng trong app mua sắm.",
      "Không chuyển khoản nếu không xác minh được đơn.",
      "Gọi tổng đài đơn vị vận chuyển nếu nghi ngờ.",
    ],
  },
  {
    category: "Giả đơn vị giao hàng",
    title: "Cập nhật địa chỉ giao hàng",
    summary:
      "Tin nhắn báo giao hàng thất bại và gửi link yêu cầu cập nhật địa chỉ.",
    examples: [
      "Đơn hàng giao thất bại. Bấm vào link để cập nhật địa chỉ nhận hàng.",
      "Vui lòng xác nhận lại địa chỉ giao hàng tại đường dẫn bên dưới.",
    ],
    signs: [
      "Thông báo giao thất bại bất ngờ.",
      "Gửi link cập nhật thông tin.",
      "Yêu cầu nhập số điện thoại, địa chỉ hoặc thông tin thanh toán.",
    ],
    defenses: [
      "Không nhập thông tin qua link lạ.",
      "Mở app mua sắm hoặc app vận chuyển để kiểm tra.",
      "Chỉ cập nhật địa chỉ qua kênh chính thức.",
    ],
  },
  {
    category: "Giả đơn vị giao hàng",
    title: "Phí hải quan hoặc phí lưu kho giả",
    summary:
      "Đối tượng giả danh đơn vị vận chuyển, báo đơn hàng bị giữ và yêu cầu đóng phí.",
    examples: [
      "Đơn hàng của bạn đang bị giữ tại kho. Vui lòng thanh toán phí lưu kho để nhận hàng.",
      "Kiện hàng quốc tế cần đóng phí hải quan trước khi giao.",
    ],
    signs: [
      "Yêu cầu đóng phí bất thường.",
      "Không cung cấp mã vận đơn hợp lệ.",
      "Gửi tài khoản cá nhân để nhận tiền.",
      "Thúc giục thanh toán nhanh.",
    ],
    defenses: [
      "Kiểm tra mã vận đơn trên website chính thức.",
      "Không chuyển tiền vào tài khoản cá nhân.",
      "Liên hệ tổng đài đơn vị vận chuyển để xác minh.",
    ],
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
const openHistoryBtn = document.getElementById("openHistoryBtn");
const closeHistoryBtn = document.getElementById("closeHistoryBtn");
const openLibraryBtn = document.getElementById("openLibraryBtn");
const closeLibraryBtn = document.getElementById("closeLibraryBtn");
const backHomeBtn = document.getElementById("backHomeBtn");
const resultShareUrl = document.getElementById("resultShareUrl");
const copyShareUrlBtn = document.getElementById("copyShareUrlBtn");
const websiteUrlInput = document.getElementById("websiteUrlInput");

const analyzeWebsiteBtn = document.getElementById("analyzeWebsiteBtn");
if (analyzeWebsiteBtn) {
  analyzeWebsiteBtn.addEventListener("click", async () => {
    const url = websiteUrlInput.value.trim();

    if (!url) {
      alert("Nhập website cần kiểm tra.");
      return;
    }

    showScreen("loading");

    try {
      const response = await fetch("/analyze-website", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url }),
      });

      const result = await response.json();

      renderResult(`Website: ${url}`, result, true);

      showScreen("result");
    } catch (error) {
      alert("Không thể kiểm tra website.");
      showScreen("home");
    }
  });
}
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

  if (score >= 5) return "Nguy hiểm";
  if (score >= 2) return "Nghi ngờ";
  return "An toàn";
}

function levelClass(level) {
  return (
    {
      "An toàn": "low",
      "Nghi ngờ": "medium",
      "Nguy hiểm": "severe",
    }[level] || "medium"
  );
}

function riskDisplay(level) {
  if (level === "An toàn") {
    return { label: "An toàn", percent: "18%" };
  }

  if (level === "Nghi ngờ") {
    return { label: "Nghi ngờ", percent: "55%" };
  }

  return { label: "Nguy hiểm", percent: "100%" };
}

function renderResult(text, aiResult = null, shouldSaveHistory = true) {
  const level = aiResult?.level || classifyMessage(text);
  const type = levelClass(level);
  const displayRisk = riskDisplay(level);
  const shouldShowWarningDetails = level !== "An toàn";
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
    "An toàn":
      "Tin nhắn chưa có dấu hiệu nguy hiểm rõ ràng nhưng vẫn nên kiểm tra nguồn gửi.",

    "Nghi ngờ":
      "Tin nhắn có một số dấu hiệu đáng ngờ, nên xác minh trước khi làm theo.",

    "Nguy hiểm":
      "Tin nhắn có dấu hiệu lừa đảo rõ ràng. Không nên bấm link, chuyển tiền hoặc cung cấp thông tin.",
  };
  riskDescription.textContent = aiResult?.description || descriptions[level];

  if (resultShareUrl) {
    resultShareUrl.value = aiResult?.result_url || "";
  }

  const signCard = document.getElementById("signCard");
  const suspiciousCard = document.getElementById("suspiciousCard");
  const counselorCard = document.querySelector(".counselor-card");
  const choiceCard = document.getElementById("ChoiceCard");
  if (signCard) {
    signCard.style.display = shouldShowWarningDetails ? "block" : "none";
  }

  if (suspiciousCard) {
    suspiciousCard.style.display = shouldShowWarningDetails ? "block" : "none";
  }

  if (counselorCard) {
    counselorCard.style.display = shouldShowWarningDetails ? "flex" : "none";
  }
  if (choiceCard) {
    choiceCard.style.display = shouldShowWarningDetails ? "block" : "none";
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

  <div class="library-header">

    <strong>${index + 1}. ${escapeHtml(item.title)}</strong>

    <span class="library-category">
      ${escapeHtml(item.category)}
    </span>

  </div>

  <span>${escapeHtml(item.summary)}</span>

</span>
            <span class="library-chevron" aria-hidden="true">▼</span>
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

    const validLevels = ["An toàn", "Nghi ngờ", "Nguy hiểm"];
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
    const response = await fetch(
      `/api/results/${encodeURIComponent(match[1])}`,
    );
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
    "An toàn": "#16a34a",
    "Nghi ngờ": "#d49b00",
    "Nguy hiểm": "#dc2626",
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
document.querySelectorAll(".choice-button").forEach((button) => {
  button.addEventListener("click", async () => {
    document.querySelectorAll(".choice-button").forEach((btn) => {
      btn.classList.remove("selected");
    });

    button.classList.add("selected");

    const choice = button.dataset.choice;
    const resultBox = document.getElementById("Result");

    if (choice === "None") {
      resultBox.innerHTML =
        "<strong>Tốt.</strong> Bạn chưa làm gì nên nguy cơ hiện tại thấp. Hãy xóa tin nhắn và không phản hồi.";
      return;
    }

    resultBox.textContent = "Người ứng cứu đang tạo các bước xử lý...";

    try {
      const response = await fetch("/rescue", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          choice,
          message: latestMessage,
          result: latestResult,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Không thể gọi Người ứng cứu.");
      }

      resultBox.innerHTML = `
  <ol class="rescue-steps">
    ${(data.steps || [])
      .map((step) => {
        const cleanStep = String(step).replace(/^\d+\.\s*/, "");
        return `<li>${escapeHtml(cleanStep)}</li>`;
      })
      .join("")}
  </ol>
`;
    } catch (error) {
      resultBox.textContent =
        "Không thể gọi Người ứng cứu lúc này. Hãy liên hệ ngay ngân hàng hoặc cơ quan chức năng chính thức.";
    }
  });
});
