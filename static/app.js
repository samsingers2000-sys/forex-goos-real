const $ = (id) => document.getElementById(id);

function setSignalColor(signal) {
  const el = $("signal");
  el.className = "";
  if (signal === "BUY") el.classList.add("positive");
  else if (signal === "SELL") el.classList.add("negative");
  else el.classList.add("neutral");
}

async function loadPositions() {
  try {
    const res = await fetch("/api/positions");
    const data = await res.json();
    const tbody = $("positionsTableBody");

    if (!data.positions || data.positions.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5">لا توجد صفقات حالياً.</td></tr>';
      return;
    }

    tbody.innerHTML = data.positions.map((p) => `
      <tr>
        <td>${p.symbol}</td>
        <td>${p.side}</td>
        <td>${Number(p.entry).toFixed(5)}</td>
        <td>${Number(p.stop).toFixed(5)}</td>
        <td>${Number(p.target).toFixed(5)}</td>
      </tr>
    `).join("");
  } catch (err) {
    console.error(err);
  }
}

async function analyze() {
  const symbol = $("symbol").value;
  const timeframe = $("timeframe").value;

  const btn = $("analyzeBtn");
  btn.disabled = true;
  btn.textContent = "جاري التحليل...";

  try {
    const res = await fetch(`/api/analyze?symbol=${symbol}&timeframe=${timeframe}`);
    if (!res.ok) throw new Error("API error");

    const data = await res.json();

    $("price").textContent = data.price ?? "—";
    $("change").textContent = `${Number(data.change || 0) >= 0 ? "+" : ""}${data.change ?? 0}%`;
    $("signal").textContent = data.signal ?? "WAIT";
    $("confidence").textContent = `الثقة: ${data.confidence ?? 0}%`;
    $("trend").textContent = data.trend ?? "—";
    $("rsi").textContent = data.rsi ?? "—";
    $("entry").textContent = data.plan?.entry ?? "—";
    $("sl").textContent = data.plan?.sl ?? "—";
    $("tp1").textContent = data.plan?.tp1 ?? "—";
    $("tp2").textContent = data.plan?.tp2 ?? "—";
    $("summary").textContent = data.summary ?? "لا يوجد ملخص";

    setSignalColor((data.signal || "WAIT").toUpperCase());

    $("indicators").innerHTML = (data.indicators || []).map((item) => `<li>${item}</li>`).join("");

    $("systemStatus").textContent = "متصل";
    $("systemStatus").style.color = "#39d98a";
  } catch (err) {
    $("summary").textContent = "تعذر الوصول إلى خادم التحليل. تأكد من تشغيل Flask.";
    $("systemStatus").textContent = "خطأ";
    $("systemStatus").style.color = "#ff5d73";
  } finally {
    btn.disabled = false;
    btn.textContent = "تحليل السوق";
  }

  await loadPositions();
}

async function sendChatMessage() {
  const message = $("chatInput").value.trim();
  if (!message) return;

  const chatMessages = $("chatMessages");
  const userBox = document.createElement("div");
  userBox.className = "chat-message user";
  userBox.textContent = message;
  chatMessages.appendChild(userBox);

  $("chatInput").value = "";

  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      symbol: $("symbol").value,
    }),
  });

  const data = await res.json();
  const botBox = document.createElement("div");
  botBox.className = "chat-message bot";
  botBox.textContent = data.reply;
  chatMessages.appendChild(botBox);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

$("analyzeBtn").addEventListener("click", analyze);
$("sendChatBtn").addEventListener("click", sendChatMessage);
$("chatInput").addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendChatMessage();
});

window.addEventListener("load", () => {
  analyze();
  loadPositions();
});
