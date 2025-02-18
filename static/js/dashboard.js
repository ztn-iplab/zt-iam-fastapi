console.log("Dashboard JS loaded");

// 1. Retrieve the access token
const token = localStorage.getItem('access_token');
if (!token) {
  // If no token, redirect to login
  window.location.href = '/auth/login_form';
}

// 2. Fetch the user data from /api/user
fetch('/api/user', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  }
})
.then(response => {
  console.log("Fetch /api/user status:", response.status);
  if (response.status === 401) {
    throw new Error('Unauthorized');
  }
  return response.json();
})
.then(data => {
  console.log("Received user data:", data);

  // 2a. Personalized welcome message
  document.getElementById('welcome-title').textContent = `Welcome, ${data.first_name || 'User'}!`;

  
  // Combine first_name and last_name for the full name in profile details
  
  const fullName = data.first_name + (data.last_name ? " " + data.last_name : "");

  // 2b. Populate the profile fields
  document.getElementById('full-name').textContent = fullName || 'N/A'
  document.getElementById('mobile-number').textContent = data.mobile_number || 'N/A';
  document.getElementById('country').textContent = data.country || 'N/A';
  document.getElementById('trust-score').textContent = data.trust_score || 'N/A';
  
  // 2c. Populate the wallet info
  if (data.wallet) {
    document.getElementById('wallet-balance').textContent = data.wallet.balance;
    document.getElementById('wallet-currency').textContent = data.wallet.currency;
  } else {
    document.getElementById('wallet-balance').textContent = 'No wallet found';
  }
})
.catch(error => {
  console.error("Error fetching user data:", error);
  alert("Failed to load user data. Please log in again.");
  window.location.href = '/auth/login_form';
});

// 3. Logout functionality
document.getElementById('logout-button').addEventListener('click', function() {
  console.log("Logout button clicked");
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_id');
  window.location.href = '/';
});
