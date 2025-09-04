document.addEventListener("DOMContentLoaded", () => {
    document.addEventListener("DOMContentLoaded", () => {
    console.log("🟢 JavaScript file loaded successfully!");
    
    const loginForm = document.getElementById("loginForm");
    console.log("🔍 Login form found:", loginForm);
    
    const loginSection = document.getElementById("loginSection");
    const securitySection = document.getElementById("securitySection");
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    
    console.log("🔍 Elements found:", {
        loginSection: !!loginSection,
        securitySection: !!securitySection,
        usernameInput: !!usernameInput,
        passwordInput: !!passwordInput
    });

    // Your existing code continues here...
    loginForm.addEventListener("submit", async (event) => {
        console.log("🚀 FORM SUBMITTED! This should appear when you click Login");
        event.preventDefault();
        
        // Rest of your existing login code...
    });
});

    const loginForm = document.getElementById("loginForm");
    const loginSection = document.getElementById("loginSection");
    const securitySection = document.getElementById("securitySection");
    const forgotPasswordLink = document.getElementById("forgotPasswordLink");
    const verifyBtn = document.getElementById("verifyBtn");
    const backToLoginBtn = document.getElementById("backToLoginBtn");
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const securityAnswerInput = document.getElementById("securityAnswer");
    const securityQuestionText = document.querySelector("#securitySection p");

    let currentUser = null;
    const API_BASE = "http://127.0.0.1:8000";

    // ------------------------
    // LOGIN LOGIC (FIXED)
    // ------------------------
    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();

        if (!username || !password) {
            alert("Please enter both username and password.");
            return;
        }

        try {
            const response = await fetch(`${API_BASE}/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok) {
                // SUCCESS: Correct credentials
                alert("Login successful!");
                window.location.href = "./MainHomePage.html";
            } else if (response.status === 401) {
                // WRONG PASSWORD: Show security question
                alert("Incorrect password. Please answer your security question.");
                await fetchSecurityQuestion(username);
            } else {
                // OTHER ERRORS
                alert("Login failed: " + (data.detail || "Please try again"));
            }
        } catch (error) {
            console.error("Error during login:", error);
            alert("Connection error. Please check if the server is running.");
        }
    });

    // ------------------------
    // FETCH SECURITY QUESTION (FIXED)
    // ------------------------
    // async function fetchSecurityQuestion(username) {
    //     try {
    //         const response = await fetch(`${API_BASE}/get-security-question/${username}`);
            
    //         if (response.ok) {
    //             const data = await response.json();
    //             currentUser = username;
    //             securityQuestionText.textContent = data.securityQuestion;

    //             // Switch view
    //             loginSection.style.display = "none";
    //             securitySection.style.display = "block";
    //         } else {
    //             const errorData = await response.json();
    //             alert("Error: " + (errorData.detail || "Username not found"));
    //         }
    //     } catch (error) {
    //         console.error("Error fetching security question:", error);
    //         alert("Failed to load security question. Please try again.");
    //     }
    // }

    // ------------------------
    // FORGOT PASSWORD FLOW
    // ------------------------
    forgotPasswordLink.addEventListener("click", async (event) => {
        event.preventDefault();
        const username = usernameInput.value.trim();
        
        if (!username) {
            alert("Please enter your username first.");
            return;
        }

        await fetchSecurityQuestion(username);
    });

    // ------------------------
    // VERIFY SECURITY ANSWER (FIXED)
    // ------------------------
    verifyBtn.addEventListener("click", async () => {
        const answer = securityAnswerInput.value.trim();
        
        if (!answer) {
            alert("Please enter your answer.");
            return;
        }

        if (!currentUser) {
            alert("Please try logging in again.");
            return;
        }

        try {
            const response = await fetch(`${API_BASE}/verify-security`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    username: currentUser,
                    securityAnswer: answer
                })
            });

            const data = await response.json();

            if (response.ok) {
                alert("Security verification successful! Redirecting...");
                window.location.href = "./MainHomePage.html";
            } else {
                alert("Incorrect security answer. Please try again.");
                console.log("Security verification failed:", data.detail);
            }
        } catch (error) {
            console.error("Error verifying security answer:", error);
            alert("Verification failed. Please try again.");
        }
    });

    // ------------------------
    // BACK TO LOGIN
    // ------------------------
    backToLoginBtn.addEventListener("click", () => {
        backToLogin();
    });

    function backToLogin() {
        securitySection.style.display = "none";
        loginSection.style.display = "block";
        securityAnswerInput.value = "";
        currentUser = null;
    }
});

