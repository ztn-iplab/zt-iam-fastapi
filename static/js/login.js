console.log("Login JS loaded");

document.getElementById('login-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const mobile = document.getElementById('mobile-number').value;
    const password = document.getElementById('password').value;
    console.log("Form submission intercepted");
    
    fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier: mobile, password: password }),
        credentials: 'include'  // Ensure cookies are included
    })
    .then(async res => {
        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.error || "Login failed");
        }

        if (data.otp_required && data.user_id) {
            // Redirect to OTP verification page with user_id as query param
            window.location.href = `/api/auth/verify-otp?user_id=${data.user_id}`;
        } else {
            // Logged in successfully without OTP
            window.location.href = data.dashboard_url;
        }
    })
    .catch(err => {
        console.error("Login error:", err);
        const errorDiv = document.getElementById('login-error');
        if (errorDiv) {
            errorDiv.textContent = "Login error: " + err.message;
        } else {
            alert("Login error: " + err.message);
        }
    });
});
