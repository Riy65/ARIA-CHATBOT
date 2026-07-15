const loginForm = document.getElementById("loginForm");
const loginBtn = document.getElementById("loginBtn");
const API_URL= "https://aria-chatbot-backend-jxbf.onrender.com"

loginForm.addEventListener("submit", async function (e) {

    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    if (!email || !password) {
        alert("Please fill all fields.");
        return;
    }

    loginBtn.disabled = true;
    loginBtn.textContent = "Logging in...";

    try {

        const response = await fetch(
            `${API_URL}/auth/login`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Invalid email or password"
            );
        }

        localStorage.setItem(
            "token",
            data.access_token
        );

        localStorage.setItem(
            "email",
            email
        );

        localStorage.setItem(
            "isLoggedIn",
            "true"
        );

        window.location.href = "index.html";

    }

    catch (error) {

        alert(error.message);

    }

    finally {

        loginBtn.disabled = false;
        loginBtn.textContent = "Login";

    }

});