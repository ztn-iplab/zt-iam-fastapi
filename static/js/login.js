console.log("Login JS loaded");

const loginForm = document.getElementById('login-form');

if (loginForm) {
  loginForm.addEventListener('submit', function (e) {
    e.preventDefault();  // Prevent form from submitting in the default way

    const mobile = document.getElementById('mobile-number').value;  // Get mobile number/email from form
    const password = document.getElementById('password').value;  // Get password from form

    // Send login request to backend
    fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ identifier: mobile, password: password }),  // Send credentials as JSON
      credentials: 'include'  // Include cookies (if any)
    })
    .then(async res => {
      const data = await res.json();  // Parse JSON response

      // TOTP setup is required (TOTP not configured)
      if (data.require_totp_setup && data.user_id) {
        // Redirect to TOTP setup page
        window.location.href = `/setup-totp?user_id=${data.user_id}`;
        return;  // Stop further execution
      }

      // Handle login errors (invalid credentials, etc.)
      if (!res.ok) {
        throw new Error(data.error || "Login failed");
      }

      // If TOTP is configured, redirect to TOTP verification page
      if (data.require_totp && data.user_id) {
        window.location.href = `/api/auth/verify-totp?user_id=${data.user_id}`;
      } else {
        // Fully authenticated, redirect to the appropriate dashboard
        window.location.href = data.dashboard_url;
      }
    })
    .catch(err => {
      console.error("Login error:", err);
      const errorDiv = document.getElementById('login-error');
      if (errorDiv) {
        errorDiv.textContent = "Login error: " + (err.message || "Unexpected error");
      }
    });
  });
}
