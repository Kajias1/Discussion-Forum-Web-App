document.addEventListener("DOMContentLoaded", () => {
    const passwordInput = document.getElementById("password");
    const feedback = document.getElementById("password-feedback");
    const submitBtn = document.getElementById("submit-btn");
    const weakPasswords = [
        "12345678", "password", "qwerty", "123456", "123456789", "abc123",
        "11111111", "123123", "password1", "1234"
    ];

    passwordInput.addEventListener("input", () => {
        const password = passwordInput.value;
        
        feedback.textContent = "";
        submitBtn.disabled = false;

        if (password.length < 8) {
            feedback.textContent = "Password must be at least 8 characters long.";
            submitBtn.disabled = true;
        } else if (weakPasswords.includes(password.toLowerCase())) {
            feedback.textContent = "Password is too simple. Try something stronger.";
            submitBtn.disabled = true;
        }
    });
});
