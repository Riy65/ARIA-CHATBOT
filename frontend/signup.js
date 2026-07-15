const signupForm = document.getElementById("signupForm");
const signupBtn = document.getElementById("signupBtn");
const API_URL= "https://aria-chatbot-backend-jxbf.onrender.com"

signupForm.addEventListener("submit", async function (e) {

    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    if (!email || !password) {
        alert("Please fill all fields.");
        return;
    }

    signupBtn.disabled = true;
    signupBtn.textContent = "Creating Account...";

    try {

        const response = await fetch(
            `${API_URL}/auth/signup`,
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
                data.detail || data.message || "Signup failed"
            );
        }

        alert("Account created successfully!");

        window.location.href = "login.html";

    }

    catch (error) {

        alert(error.message);

    }

    finally {

        signupBtn.disabled = false;
        signupBtn.textContent = "Sign Up";

    }

});