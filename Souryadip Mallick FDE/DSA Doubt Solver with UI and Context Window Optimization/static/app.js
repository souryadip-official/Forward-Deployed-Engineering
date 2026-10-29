const API_URL = "/chat";
const KEY_NAME = "algomentor_google_key";

const elements = {
  form: document.querySelector("#chatForm"),
  question: document.querySelector("#question"),
  send: document.querySelector("#sendButton"),
  messages: document.querySelector("#messages"),
  welcome: document.querySelector("#welcome"),
  suggestions: document.querySelector("#suggestions"),
  chatArea: document.querySelector("#chatArea"),
  modal: document.querySelector("#keyModal"),
  apiKey: document.querySelector("#apiKey"),
  toast: document.querySelector("#toast"),
  contextBar: document.querySelector("#contextBar"),
  turnCount: document.querySelector("#turnCount"),
  keyStatus: document.querySelector("#keyStatus"),
  sidebar: document.querySelector("#sidebar")
};

let turns = 0;
let busy = false;

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value;
  return div.innerHTML;
}

function renderMarkdown(markdown) {
  let text = escapeHtml(markdown);
  const codeBlocks = [];
  text = text.replace(/```(?:\w+)?\n([\s\S]*?)```/g, (_, code) => {
    codeBlocks.push(`<pre><code>${code.trim()}</code></pre>`);
    return `\n[[CODEBLOCK_${codeBlocks.length - 1}]]\n`;
  });
  text = text
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/###\s(.+)/g, "<h3>$1</h3>")
    .replace(/##\s(.+)/g, "<h2>$1</h2>")
    .replace(/^\s*[-*]\s(.+)/gm, "<li>$1</li>")
    .replace(/(<li>.*<\/li>)/gs, "<ul>$1</ul>")
    .replace(/\n\n+/g, "</p><p>")
    .replace(/\n/g, "<br>");
  text = `<p>${text}</p>`;
  codeBlocks.forEach((block, index) => {
    text = text.replace(`<p><br>[[CODEBLOCK_${index}]]<br></p>`, block);
    text = text.replace(`[[CODEBLOCK_${index}]]`, block);
  });
  text = text.replace(/<p><\/p>/g, "");
  return text;
}

function savedKey() {
  return localStorage.getItem(KEY_NAME) || "";
}

function setKeyState() {
  elements.keyStatus.classList.toggle("connected", Boolean(savedKey()));
}

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.classList.add("show");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => elements.toast.classList.remove("show"), 2400);
}

function openKeyModal() {
  elements.apiKey.value = savedKey();
  elements.modal.classList.add("open");
  setTimeout(() => elements.apiKey.focus(), 100);
}

function closeKeyModal() {
  elements.modal.classList.remove("open");
}

function updateContext() {
  elements.turnCount.textContent = turns;
  elements.contextBar.style.width = `${Math.min(100, turns * 5)}%`;
}

function startConversation() {
  elements.welcome.style.display = "none";
  elements.suggestions.style.display = "none";
  elements.messages.classList.add("active");
}

function scrollToBottom() {
  requestAnimationFrame(() => {
    elements.chatArea.scrollTop = elements.chatArea.scrollHeight;
  });
}

function addMessage(role, content) {
  startConversation();
  const message = document.createElement("article");
  message.className = `message ${role}`;
  message.innerHTML = role === "user"
    ? `<div class="avatar">YOU</div><div class="message-body">${escapeHtml(content).replace(/\n/g, "<br>")}</div>`
    : `<div class="avatar">AM</div><div class="message-body">${renderMarkdown(content)}</div>`;
  elements.messages.appendChild(message);
  scrollToBottom();
  return message;
}

function addTyping() {
  const message = document.createElement("article");
  message.className = "message assistant";
  message.innerHTML = '<div class="avatar">AM</div><div class="message-body"><div class="typing"><i></i><i></i><i></i></div></div>';
  elements.messages.appendChild(message);
  scrollToBottom();
  return message;
}

async function sendQuestion(question) {
  if (busy) return;
  const apiKey = savedKey();
  if (!apiKey) {
    openKeyModal();
    showToast("Add your Gemini API key to start");
    return;
  }

  busy = true;
  elements.send.disabled = true;
  elements.question.value = "";
  resizeTextarea();
  addMessage("user", question);
  turns += 1;
  updateContext();
  const typing = addTyping();

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: question, api_key: apiKey })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "The tutor could not answer that.");
    typing.remove();
    addMessage("assistant", data.content);
  } catch (error) {
    typing.remove();
    addMessage("assistant", `I couldn't complete that request. ${error.message}`);
  } finally {
    busy = false;
    elements.send.disabled = false;
    elements.question.focus();
  }
}

function resizeTextarea() {
  elements.question.style.height = "auto";
  elements.question.style.height = `${Math.min(150, elements.question.scrollHeight)}px`;
}

elements.form.addEventListener("submit", event => {
  event.preventDefault();
  const question = elements.question.value.trim();
  if (question) sendQuestion(question);
});

elements.question.addEventListener("input", resizeTextarea);
elements.question.addEventListener("keydown", event => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    elements.form.requestSubmit();
  }
});

document.querySelectorAll("[data-prompt]").forEach(button => {
  button.addEventListener("click", () => sendQuestion(button.dataset.prompt));
});

document.querySelector("#keyButton").addEventListener("click", openKeyModal);
document.querySelector("#modalClose").addEventListener("click", closeKeyModal);
elements.modal.addEventListener("click", event => {
  if (event.target === elements.modal) closeKeyModal();
});
document.querySelector("#toggleKey").addEventListener("click", event => {
  const visible = elements.apiKey.type === "text";
  elements.apiKey.type = visible ? "password" : "text";
  event.currentTarget.textContent = visible ? "Show" : "Hide";
});
document.querySelector("#saveKey").addEventListener("click", () => {
  const key = elements.apiKey.value.trim();
  if (!key) {
    showToast("Enter an API key");
    return;
  }
  localStorage.setItem(KEY_NAME, key);
  setKeyState();
  closeKeyModal();
  showToast("API key saved");
});

document.querySelector("#newChat").addEventListener("click", () => {
  clearConversation();
  elements.sidebar.classList.remove("open");
});
document.querySelector("#clearButton").addEventListener("click", clearConversation);
document.querySelector("#menuButton").addEventListener("click", () => elements.sidebar.classList.toggle("open"));

async function clearConversation() {
  elements.messages.innerHTML = "";
  elements.messages.classList.remove("active");
  elements.welcome.style.display = "";
  elements.suggestions.style.display = "";
  turns = 0;
  updateContext();
  try {
    await fetch("/reset", { method: "POST" });
  } catch (error) {
    showToast("Backend reset failed");
  }
  showToast("Conversation cleared");
}

setKeyState();
updateContext();
