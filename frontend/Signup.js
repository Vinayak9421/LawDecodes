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
    signupForm.addEventListener("submit", (e) => {
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
            securityQuestion: securityQuestionSelect.value,
            securityAnswer: securityAnswerInput.value.trim()
        };

        // Here you would typically send data to your backend
        console.log("User signup data:", userData);
        
        alert("Account created successfully! You can now login.");
        
        // Redirect to login page
        window.location.href = "./NFC4_HugsForBugs/Ltest.html";
    });
});
