console.log("Login JS loaded");

document.addEventListener('DOMContentLoaded', function() {
  const loginForm = document.getElementById('login-form');
  if (!loginForm) {
    console.error("Login form not found!");
    return;
  }
  
  loginForm.addEventListener('submit', function(e) {
    e.preventDefault(); // Prevent default form submission
    console.log("Form submission intercepted");
    
    const mobile_number = loginForm.mobile_number.value;
    const password = loginForm.password.value;
    console.log("Mobile Number:", mobile_number, "Password:", password);
    
    fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ mobile_number, password })
    })
    .then(response => {
      console.log("Response status:", response.status);
      if (!response.ok) {
        throw new Error('Login failed');
      }
      return response.json();
    })
    .then(data => {
      console.log("Login successful, received data:", data);
      // Store the access token and user id in localStorage
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user_id', data.user_id);
      // Redirect to the dashboard
      window.location.href = '/dashboard';
    })
    .catch(error => {
      console.error("Error during login:", error);
      alert("Login failed. Please check your credentials.");
    });
  });
});
