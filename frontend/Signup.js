

document.addEventListener("DOMContentLoaded", () => {
    const moveForwardBtn = document.getElementById("moveForwardBtn");
    const signupForm = document.getElementById("signupForm");
    const signupFields = document.getElementById("signupFields");
    const securitySection = document.getElementById("securitySection");
    const backToSignupBtn = document.getElementById("backToSignupBtn");
    const signupBtn = document.getElementById("signupBtn");

    // Form inputs
    const usernameInput = document.getElementById("username");
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");
    const securityQuestionSelect = document.getElementById("securityQuestionSelect");
    const securityAnswerInput = document.getElementById("securityAnswer");

    // Move to security question section
    moveForwardBtn.addEventListener("click", (e) => {
        e.preventDefault();

        // Validate basic signup fields first
        if (!usernameInput.value.trim() || !emailInput.value.trim() || !passwordInput.value.trim()) {
            alert("Please fill in all fields before proceeding.");
            return;
        }

        // Hide signup fields and show security section
        signupFields.style.display = "none";
        securitySection.style.display = "block";
    });

    // Back to signup fields
    backToSignupBtn.addEventListener("click", (e) => {
        e.preventDefault();

        // Show signup fields and hide security section
        signupFields.style.display = "block";
        securitySection.style.display = "none";
    });

    // Handle final signup submission
    signupForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        // Validate security question fields
        if (!securityQuestionSelect.value || !securityAnswerInput.value.trim()) {
            alert("Please select a security question and provide an answer.");
            return;
        }

        // Collect all form data
        const userData = {
            username: usernameInput.value.trim(),
            email: emailInput.value.trim(),
            password: passwordInput.value.trim(),
            securityQuestion: parseInt(securityQuestionSelect.value), // ✅ FIX: send ID as integer
            securityAnswer: securityAnswerInput.value.trim()
        };

        try {
            // Send data to backend API
            const response = await fetch("http://127.0.0.1:8000/signup", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(userData)
            });

            const result = await response.json();

            if (response.ok) {
                alert("✅ Account created successfully! You can now login.");
                window.location.href = "./Login.html"; // Redirect to login page
            } else {
                alert("❌ Signup failed: " + (result.detail || result.message || "Unknown error"));
            }
        } catch (error) {
            console.error("Error during signup:", error);
            alert("⚠️ Error connecting to the server. Please try again later.");
        }
    });
});
