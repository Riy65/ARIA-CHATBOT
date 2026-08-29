# 🤖 Aria AI Chatbot

Aria AI Chatbot is a full-stack AI-powered conversational web application that allows users to securely interact with an AI assistant, manage multiple conversations, and store chat history.

---

## ✨ Features

- Secure User Authentication (Login & Signup)
- AI-powered portfolio conversations using OpenAI
- Multiple Chat Sessions
- Automatic Conversation Title Generation
- Persistent Chat History
- Delete Conversations
- JWT Authentication
- Responsive User Interface

---

## 🛠️ Tech Stack

| Technology | Why it was used | Benefits |
|------------|-----------------|----------|
| **FastAPI** | Backend API development | High performance, automatic API documentation, easy REST API development |
| **PostgreSQL** | Database | Strong relationships for users, chat sessions, and portfolio versions |
| **OpenAI API** | AI response generation | Portfolio-aware conversations and content analysis |
| **JWT** | User Authentication | Secure, stateless authentication without server-side sessions |
| **Passlib (bcrypt)** | Password Hashing | Prevents storing plain-text passwords and improves security |
| **HTML, CSS, JavaScript** | Frontend Development | Lightweight, responsive, and easy to customize |

---

## 📂 Project Structure

```text
aria-chatbot/
│
├── backend/
│   ├── routes/
│   ├── models/
│   ├── utils/
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── script.js
│   ├── style.css
│   └── ...
│
└── README.md
```

---

## 🚀 How to Run

1. Clone the repository.
2. Install backend dependencies:

```bash
pip install -r backend/requirements.txt
```

3. Create a `.env` file inside `backend/`:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/aria
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
JWT_SECRET_KEY=YOUR_SECRET_KEY
```

4. Start the backend:

```bash
cd backend
uvicorn main:app --reload
```

5. Open `frontend/login.html` using Live Server.

---

## 🔮 Future Improvements

1. Password strength validation
2. Email verification
3. Forgot password functionality
4. AI response streaming
5. Dark mode
6. Rate limiting

---

## 👩‍💻 Author

**Riya Srivastava**
## 📚 Key Learning Outcomes

1. Built a complete full-stack AI application from scratch.
2. Implemented JWT-based authentication and authorization.
3. Integrated Google Gemini API with conversational context.
4. Designed RESTful APIs using FastAPI.
5. Stored and managed chat history in MongoDB Atlas.
6. Managed environment variables securely using `.env`.
7. Applied Git and GitHub best practices for version control.
