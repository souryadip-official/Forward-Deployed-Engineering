const form = document.querySelector("#chatForm");
const input = document.querySelector("#messageInput");
const conversation = document.querySelector("#conversation");
const chatScroll = document.querySelector("#chatScroll");
const sendButton = document.querySelector("#sendButton");
const welcome = document.querySelector(".welcome");
const settingsDialog = document.querySelector("#settingsDialog");
let apiKey = sessionStorage.getItem("geminiApiKey") || "";

const toolMeta = {
  invoke_calculate: { label: "Calculator", icon: "÷" },
  invoke_weather: { label: "Weather", icon: "◉" },
  invoke_exchange_rate: { label: "Exchange rate", icon: "↔" }
};

function escapeHtml(value) {
  const element = document.createElement("div");
  element.textContent = value;
  return element.innerHTML;
}

function formatValue(value) {
  if (value === null || value === undefined) return "No result";
  if (typeof value === "object") return JSON.stringify(value, null, 2);
  return String(value);
}

function scrollToBottom() {
  chatScroll.scrollTop = chatScroll.scrollHeight;
}

function addUserMessage(message) {
  if (welcome) welcome.remove();
  conversation.insertAdjacentHTML("beforeend", `
    <article class="message-row user">
      <div class="message-bubble">${escapeHtml(message)}</div>
    </article>
  `);
  scrollToBottom();
}

function toolCard(tool) {
  const name = tool.name || "Unknown tool";
  const meta = toolMeta[name] || { label: name, icon: "◆" };
  return `
    <details class="tool-run" open>
      <summary>
        <span class="tool-symbol">${meta.icon}</span>
        <span class="tool-name">${escapeHtml(meta.label)}</span>
        <span class="tool-pill">Completed</span>
        <span class="tool-chevron">›</span>
      </summary>
      <div class="tool-content">
        <div class="data-label">Input</div>
        <pre class="data-box">${escapeHtml(formatValue(tool.arguments || {}))}</pre>
        <div class="data-label">Result</div>
        <pre class="data-box result-box">${escapeHtml(formatValue(tool.result))}</pre>
      </div>
    </details>
  `;
}

function addAssistantMessage(content, tools = []) {
  const toolMarkup = tools.map(toolCard).join("");
  conversation.insertAdjacentHTML("beforeend", `
    <article class="message-row assistant">
      <div class="assistant-avatar">✦</div>
      <div class="assistant-column">
        <div class="message-bubble">${escapeHtml(content).replace(/\n/g, "<br>")}</div>
        ${toolMarkup}
      </div>
    </article>
  `);
  scrollToBottom();
}

function addTyping() {
  const id = `typing-${Date.now()}`;
  conversation.insertAdjacentHTML("beforeend", `
    <article class="message-row assistant" id="${id}">
      <div class="assistant-avatar">✦</div>
      <div class="message-bubble typing"><span></span><span></span><span></span></div>
    </article>
  `);
  scrollToBottom();
  return id;
}

async function sendMessage(message) {
  if (!message.trim()) return;
  addUserMessage(message.trim());
  input.value = "";
  input.style.height = "auto";
  sendButton.disabled = true;
  const typingId = addTyping();

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: message.trim(), api_key: apiKey })
    });
    const data = await response.json();
    document.getElementById(typingId)?.remove();
    if (!response.ok) throw new Error(data.error || "The agent could not complete that request.");
    addAssistantMessage(data.content, data.tool_results || []);
  } catch (error) {
    document.getElementById(typingId)?.remove();
    addAssistantMessage(error.message);
  } finally {
    sendButton.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", event => {
  event.preventDefault();
  sendMessage(input.value);
});

input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 120)}px`;
});

input.addEventListener("keydown", event => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

document.querySelectorAll("[data-prompt]").forEach(button => {
  button.addEventListener("click", () => sendMessage(button.dataset.prompt));
});

document.querySelector("#newChat").addEventListener("click", () => window.location.reload());

document.querySelector("#settingsButton").addEventListener("click", () => {
  document.querySelector("#apiKey").value = apiKey;
  settingsDialog.showModal();
});

document.querySelector("#settingsForm").addEventListener("submit", event => {
  const submitter = event.submitter;
  if (submitter?.value === "cancel") return;
  event.preventDefault();
  apiKey = document.querySelector("#apiKey").value.trim();
  sessionStorage.setItem("geminiApiKey", apiKey);
  document.querySelector("#keyStatus").textContent = apiKey ? "Connected" : "Not set";
  settingsDialog.close();
});

document.querySelector("#keyStatus").textContent = apiKey ? "Connected" : "Not set";
