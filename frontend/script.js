// script.js

const chatMessages = document.getElementById('chat-messages');
const msgInput = document.getElementById('msg-input');
const sendBtn = document.getElementById('send-btn');
const newChatBtn = document.getElementById('new-chat-btn');
const chatTopbar = document.getElementById('chat-topbar');
const logoutBtn = document.getElementById('logout-btn');
const historyList = document.getElementById('history-list');
const fileInput = document.getElementById('file-input');
const composerHint = document.getElementById('composer-hint');

const API_URL = window.ARIA_API_URL || "";
let currentConversationId = null;
const token = localStorage.getItem("token");

if (!token) {
    window.location.replace("login.html");
}

async function verifyToken() {

    try {

        const response = await fetch(
            `${API_URL}/auth/me`,
            {
                headers: {
                    "Authorization": "Bearer " + token
                }
            }
        );

        if (!response.ok) {

            localStorage.removeItem("token");
            localStorage.removeItem("email");

            window.location.replace("login.html");
        }

    }

    catch (error) {

        console.error(error);

        localStorage.removeItem("token");
        localStorage.removeItem("email");

        window.location.replace("login.html");
    }

}



(function loadUser() {

    const email = localStorage.getItem("email");

    if (!email) {

        window.location.href = "login.html";
        return;

    }

    document.getElementById("user-name").textContent =
        email.split("@")[0];

    document.getElementById("user-email").textContent =
        email;

    document.getElementById("user-avatar").textContent =
        email.charAt(0).toUpperCase();

})();

async function createNewConversation() {

    const token = localStorage.getItem("token");

    const response = await fetch(
        `${API_URL}/chat/new`,
        {

            method: "POST",

            headers: {
                "Authorization": "Bearer " + token
            }

        }
    );

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Unable to create conversation");
    }

    currentConversationId = data.conversation_id;

    return data;
}
async function loadConversations() {

    const token = localStorage.getItem("token");

    const response = await fetch(

        `${API_URL}/chat/conversations`,

        {

            headers: {

                "Authorization":
                    "Bearer " + token

            }

        }

    );

    const conversations =
        await response.json();

    if (!response.ok) {

        throw new Error(
            conversations.detail
        );

    }

    if (conversations.length === 0) {

        await createNewConversation();

        return loadConversations();

    }

    renderConversations(conversations);

    await loadMessages(
        conversations[0].conversation_id
    );

}

function renderConversations(conversations) {

    historyList.innerHTML = "";

    conversations.forEach((conversation, index) => {

        const item = document.createElement("div");

        item.className = "history-item";

        if (index === 0) {

            item.classList.add("active");

            currentConversationId = conversation.conversation_id;

            chatTopbar.textContent = conversation.title;

        }

        item.dataset.id = conversation.conversation_id;

        item.innerHTML = `

            <span class="conversation-title">
                ${conversation.title}
            </span>

            <button
                class="delete-btn"
                data-id="${conversation.conversation_id}">
                ×
            </button>

        `;

        historyList.appendChild(item);

    });

}
async function loadMessages(conversationId) {

    const token = localStorage.getItem("token");

    const response = await fetch(

        `${API_URL}/chat/messages/${conversationId}`,

        {
            headers: {
                "Authorization": "Bearer " + token
            }
        }

    );

    const messages = await response.json();

    if (!response.ok) {

        throw new Error(

            messages.detail || "Unable to load messages."

        );

    }

    renderMessages(messages);

}
function renderMessages(messages) {

    chatMessages.innerHTML = "";

    messages.forEach((message) => {

        appendMessage(
            message.role,
            message.content
        );

    });

}

async function deleteConversation(conversationId){

    const token = localStorage.getItem("token");

    const response = await fetch(

        `${API_URL}/chat/conversation/${conversationId}`,

        {

            method:"DELETE",

            headers:{

                "Authorization":"Bearer " + token

            }

        }

    );

    if(!response.ok){

        throw new Error("Unable to delete conversation.");

    }

}
msgInput.addEventListener('input', function () {

    this.style.height = 'auto';

    this.style.height =
        Math.min(this.scrollHeight, 120) + 'px';

});

msgInput.addEventListener('keydown', function (e) {

    if (e.key === 'Enter' && !e.shiftKey) {

        e.preventDefault();

        sendMessage();

    }

});

sendBtn.addEventListener('click', sendMessage);

fileInput.addEventListener("change", async function () {
    const [file] = this.files;
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) {
        composerHint.textContent = "That file is larger than 10 MB. Please choose a smaller file.";
        this.value = "";
        return;
    }
    composerHint.textContent = `Uploading ${file.name}…`;
    try {
        const formData = new FormData();
        formData.append("file", file);
        const response = await fetch(`${API_URL}/profile/uploads`, {
            method: "POST",
            headers: { "Authorization": "Bearer " + token },
            body: formData,
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Unable to upload this file.");
        if (data.extraction_status !== "completed") {
            throw new Error("The document was uploaded, but Gemini could not extract its portfolio details. Check your Gemini API key and model, then try again.");
        }
        const extractedSections = Object.keys(data.extracted_facts || {}).length;
        composerHint.textContent = `${data.original_filename} analyzed. Gemini will use it as portfolio context in this chat.`;
        appendMessage("assistant", `I’ve analyzed “${data.original_filename}” and found ${extractedSections} portfolio detail${extractedSections === 1 ? "" : "s"}. Ask me to create or improve your portfolio, and I’ll use this document as context.`);
    } catch (error) {
        composerHint.textContent = error.message;
    } finally {
        this.value = "";
    }
});

function sendMessage() {

    const text = msgInput.value.trim();

    if (!text) return;

    appendMessage("user", text);

    msgInput.value = "";

    msgInput.style.height = "auto";

    const typingEl = appendTypingIndicator();

    sendToBackend(text)

        .then(async(result) => {

            typingEl.querySelector(".bubble").innerHTML =

                assistantBubbleContent(result.reply);
                if (result.title) {
            await loadConversations();
        }

            chatMessages.scrollTop =

                chatMessages.scrollHeight;

        })

        .catch((err) => {

            typingEl.querySelector(".bubble").innerHTML =

                assistantBubbleContent(err.message);

        });

}

async function sendToBackend(message) {

    const token = localStorage.getItem("token");

    if (!token) {

        window.location.href = "login.html";

        return;

    }

    const response = await fetch(

        `${API_URL}/chat/send`,

        {

            method: "POST",

            headers: {

                "Content-Type": "application/json",

                "Authorization": "Bearer " + token

            },

            body: JSON.stringify({
                conversation_id: currentConversationId,

                message: message

            })

        }

    );

    const data = await response.json();

    if (!response.ok) {

        throw new Error(

            data.detail || "Unable to send message."

        );

    }

    return data;

}


function appendMessage(role, text) {

    const row = document.createElement("div");

    row.className = `msg-row ${role}`;

    if (role === "user") {

        row.innerHTML =

            `<div class="bubble user"><div class="message-content">${escapeHtml(text).replace(/\r?\n/g, "<br>")}</div></div>`;

    }

    else {

        row.innerHTML =

            `<div class="bubble ai">${assistantBubbleContent(text)}</div>`;

    }

    chatMessages.appendChild(row);

    chatMessages.scrollTop =

        chatMessages.scrollHeight;

    return row;

}

function appendTypingIndicator() {

    const row = document.createElement("div");

    row.className = "msg-row ai";

    row.innerHTML =

        `<div class="bubble ai">
            <div class="ai-label">Aria</div>
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>`;

    chatMessages.appendChild(row);

    chatMessages.scrollTop =

        chatMessages.scrollHeight;

    return row;

}

function escapeHtml(str) {

    const div = document.createElement("div");

    div.textContent = str;

    return div.innerHTML;

}

function formatInlineMarkdown(text) {

    return text
        .replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
        .replace(/__([^_]+)__/g, '<strong>$1</strong>')
        .replace(/\*([^*]+)\*/g, '<em>$1</em>')
        .replace(/_([^_]+)_/g, '<em>$1</em>');

}

function renderMarkdown(text) {

    const lines = escapeHtml(String(text || "")).replace(/\r\n?/g, "\n").split("\n");
    const output = [];
    let paragraph = [];
    let listType = null;
    let codeLines = null;

    function closeParagraph() {
        if (paragraph.length) {
            output.push(`<p>${formatInlineMarkdown(paragraph.join("<br>"))}</p>`);
            paragraph = [];
        }
    }

    function closeList() {
        if (listType) {
            output.push(`</${listType}>`);
            listType = null;
        }
    }

    lines.forEach((line) => {
        if (line.trim().startsWith("```")) {
            closeParagraph();
            closeList();
            if (codeLines === null) {
                codeLines = [];
            } else {
                output.push(`<pre><code>${codeLines.join("\n")}</code></pre>`);
                codeLines = null;
            }
            return;
        }
        if (codeLines !== null) {
            codeLines.push(line);
            return;
        }
        const heading = line.match(/^(#{1,3})\s+(.+)$/);
        const orderedItem = line.match(/^\d+[.)]\s+(.+)$/);
        const unorderedItem = line.match(/^[-*]\s+(.+)$/);
        const quote = line.match(/^>\s?(.+)$/);

        if (!line.trim()) {
            closeParagraph();
            closeList();
        } else if (heading) {
            closeParagraph();
            closeList();
            const level = heading[1].length;
            output.push(`<h${level}>${formatInlineMarkdown(heading[2])}</h${level}>`);
        } else if (quote) {
            closeParagraph();
            closeList();
            output.push(`<blockquote>${formatInlineMarkdown(quote[1])}</blockquote>`);
        } else if (orderedItem || unorderedItem) {
            closeParagraph();
            const nextListType = orderedItem ? "ol" : "ul";
            if (listType !== nextListType) {
                closeList();
                listType = nextListType;
                output.push(`<${listType}>`);
            }
            output.push(`<li>${formatInlineMarkdown((orderedItem || unorderedItem)[1])}</li>`);
        } else {
            closeList();
            paragraph.push(line);
        }
    });

    closeParagraph();
    closeList();
    if (codeLines !== null) output.push(`<pre><code>${codeLines.join("\n")}</code></pre>`);
    return output.join("");

}

function assistantBubbleContent(text) {

    return `<div class="ai-label">Aria</div><div class="message-content">${renderMarkdown(text)}</div>`;

}

newChatBtn.addEventListener("click", async function () {

    chatMessages.innerHTML = "";

    chatTopbar.textContent = "New Chat";

    try {

        await createNewConversation();
        await loadConversations();

    }

    catch (err) {

        console.error(err)

    }

});

historyList.addEventListener("click", async function (e) {
    const deleteBtn = e.target.closest(".delete-btn");

if(deleteBtn){

    e.stopPropagation();

    const conversationId = deleteBtn.dataset.id;

    if(confirm("Delete this conversation?")){

        try{

            await deleteConversation(conversationId);

            await loadConversations();

        }

        catch(err){

            alert(err.message);

        }

    }

    return;

}

    const item = e.target.closest(".history-item");

    if (!item) return;

    document
        .querySelectorAll(".history-item")
        .forEach((i) => i.classList.remove("active"));

    item.classList.add("active");

    currentConversationId = item.dataset.id;

    chatTopbar.textContent = item.textContent;

    try {

        await loadMessages(currentConversationId);

    }

    catch (err) {

        console.error(err);

        alert("Unable to load conversation.");

    }

});

logoutBtn.addEventListener("click", function () {

    localStorage.removeItem("token");

    localStorage.removeItem("email");

    window.location.replace("login.html");

});

async function initializeChat() {

    try {
        await verifyToken();

        await loadConversations();

    }

    catch (err) {

        console.error(err);

    }

}

initializeChat();
