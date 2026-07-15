# 🤖 Aria AI Chatbot

Aria AI Chatbot is a full-stack AI-powered conversational application that provides an interactive chat experience with secure user authentication, persistent conversation history, and AI-generated responses using Google's Gemini API.

---

## ✨ Features

- 🔐 User Authentication (Login & Signup)
- 🤖 AI-powered conversations using Google Gemini
- 💬 Multiple conversation support
- 📝 Automatic conversation title generation
- 📜 Persistent chat history
- 🗑️ Delete conversations
- 🔒 JWT-based authentication
- 💾 MongoDB database integration
- 📱 Clean and responsive user interface

---

## 🛠️ Tech Stack

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- FastAPI
- Python

### Database
- MongoDB Atlas

### AI Model
- Google Gemini

### Authentication
- JWT
- Passlib (Password Hashing)

### Deployment
- Render (Backend)
- Vercel (Frontend)

---

## 📁 Project Structure

```
aria-chatbot/
│
├── backend/
│   ├── models/
│   ├── routes/
│   ├── utils/
│   ├── ai_client.py
│   ├── database.py
│   ├── main.py
│   ├── schemas.py
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── style.css
│   ├── script.js
│   ├── login.js
│   └── signup.js
│
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/aria-chatbot.git
```

---

### 2. Navigate to backend

```bash
cd backend
```

---

### 3. Create a virtual environment

```bash
python -m venv venv
```

---

### 4. Activate the virtual environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / macOS

```bash
source venv/bin/activate
```

---

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 6. Create a `.env` file

```env
MONGO_URL=YOUR_MONGODB_CONNECTION_STRING

GEMINI_API_KEY=YOUR_GEMINI_API_KEY

JWT_SECRET_KEY=YOUR_SECRET_KEY
```

---

### 7. Run the backend

```bash
uvicorn main:app --reload
```

---

### 8. Open the frontend

Open `frontend/login.html` using Live Server.

---

## 🔒 Environment Variables

| Variable | Description |
|----------|-------------|
| MONGO_URL | MongoDB Atlas connection string |
| GEMINI_API_KEY | Google Gemini API Key |
| JWT_SECRET_KEY | Secret key used for JWT authentication |

---

## 📸 Screenshots

Coming Soon

---

## 🌐 Live Demo

Coming Soon

---

## 👩‍💻 Author

**Riya Srivastava**

## ⭐ Future Improvements

- Password strength validation
- Email validation
- Password reset
- Dark mode
- Typing indicator
- Streaming AI responses
- Rate limiting

## 📚 Key Learning Outcomes

1. Built a complete full-stack AI application from scratch.
2. Implemented JWT-based authentication and authorization.
3. Integrated Google Gemini API with conversational context.
4. Designed RESTful APIs using FastAPI.
5. Stored and managed chat history in MongoDB Atlas.
6. Managed environment variables securely using `.env`.
7. Applied Git and GitHub best practices for version control.
