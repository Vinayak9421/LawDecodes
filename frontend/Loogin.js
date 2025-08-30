document.addEventListener("DOMContentLoaded", () => {
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

    // User data with security questions
    const dummyUsers = [
        { 
            username: "admin", 
            password: "admin123", 
            securityQuestion: "What is your favorite color?",
            securityAnswer: "blue" 
        },
        { 
            username: "testuser", 
            password: "test123", 
            securityQuestion: "What is your mother's maiden name?",
            securityAnswer: "smith" 
        },
        { 
            username: "john", 
            password: "john123", 
            securityQuestion: "What was the name of your first pet?",
            securityAnswer: "buddy" 
        }
    ];

    let currentUser = null;

    // NEW LOGIN LOGIC
    loginForm.addEventListener("submit", (event) => {
        event.preventDefault();

        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();

        // Find user by username
        const user = dummyUsers.find(u => u.username === username);

        if (!user) {
            // Username doesn't exist
            alert("Username not found. Please check your username.");
            return;
        }

        if (user.password === password) {
            // Correct username and password - LOGIN SUCCESS
            alert("Login successful!");
            window.location.href = "./MainHomePage.html";
        } else {
            // Username exists but password is wrong - FORCE SECURITY QUESTION
            alert("Incorrect password. Please answer your security question to proceed.");
            showSecurityQuestion(user);
        }
    });

    // Show security question (called from login or forgot password)
    function showSecurityQuestion(user) {
        currentUser = user;
        securityQuestionText.textContent = user.securityQuestion;
        
        // Switch to security section
        loginSection.style.display = "none";
        securitySection.style.display = "block";
    }

    // Forgot password link (optional path)
    forgotPasswordLink.addEventListener("click", (event) => {
        event.preventDefault();
        
        const username = usernameInput.value.trim();
        
        if (!username) {
            alert("Please enter your username first.");
            return;
        }

        const user = dummyUsers.find(u => u.username === username);
        
        if (user) {
            showSecurityQuestion(user);
        } else {
            alert("Username not found. Please check your username.");
        }
    });

    // Verify security answer
    verifyBtn.addEventListener("click", (event) => {
        const answer = securityAnswerInput.value.trim();

        if (!answer) {
            alert("Please enter your answer.");
            return;
        }

        if (currentUser && currentUser.securityAnswer.toLowerCase() === answer.toLowerCase()) {
            // Security question answered correctly - ALLOW ACCESS
            alert("Security verification successful! Redirecting to homepage.");
            window.location.href = "./MainHomePage.html";
        } else {
            alert("Incorrect security answer. Please try again.");
        }
    });

    // Back to login
    backToLoginBtn.addEventListener("click", () => {
        backToLogin();
    });

    // Reset to login view
    function backToLogin() {
        securitySection.style.display = "none";
        loginSection.style.display = "block";
        securityAnswerInput.value = "";
        currentUser = null;
    }
});
