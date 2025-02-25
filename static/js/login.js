console.log("Login JS loaded");

document.getElementById('login-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const mobile = document.getElementById('mobile-number').value;
    const password = document.getElementById('password').value;
    console.log("Form submission intercepted");
    
    fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mobile_number: mobile, password: password }),
        credentials: 'include'
    })
    .then(async res => {
        if (!res.ok) {
            const data = await res.json();
            throw new Error(data.error || "Login failed");
        }
        return res.json();
    })
    .then(data => {
        console.log("Login successful, received data:", data);
        // Redirect to the dashboard URL returned in the JSON
        window.location.href = data.dashboard_url;
    })
    .catch(err => {
        console.error("Login error:", err);
        // Display error message on the login page in the element with id "login-error"
        const errorDiv = document.getElementById('login-error');
        if (errorDiv) {
            errorDiv.textContent = "Login error: " + err.message;
        } else {
            alert("Login error: " + err.message);
        }
    });
});
