// script.js

const chatMessages = document.getElementById('chat-messages');
const msgInput = document.getElementById('msg-input');
const sendBtn = document.getElementById('send-btn');
const newChatBtn = document.getElementById('new-chat-btn');
const chatTopbar = document.getElementById('chat-topbar');
const logoutBtn = document.getElementById('logout-btn');
const historyList = document.getElementById('history-list');
const API_URL= "https://aria-chatbot-1shq.onrender.com"
let currentConversationId = null;

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

                `<div class="ai-label">Aria</div>${escapeHtml(result.reply)}`;
                if (result.title) {
            await loadConversations();
        }

            chatMessages.scrollTop =

                chatMessages.scrollHeight;

        })

        .catch((err) => {

            typingEl.querySelector(".bubble").innerHTML =

                `<div class="ai-label">Aria</div>${escapeHtml(err.message)}`;

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

            `<div class="bubble user">${escapeHtml(text)}</div>`;

    }

    else {

        row.innerHTML =

            `<div class="bubble ai"><div class="ai-label">Aria</div>${escapeHtml(text)}</div>`;

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

    window.location.href = "login.html";

});

async function initializeChat() {

    try {

        await loadConversations();

    }

    catch (err) {

        console.error(err);

    }

}

initializeChat();