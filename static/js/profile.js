console.log("Profile JS loaded");

document.addEventListener('DOMContentLoaded', function() {
  const token = localStorage.getItem('access_token');
  if (!token) {
    window.location.href = '/auth/login_form';
    return;
  }

  // Fetch profile data from the API
  fetch('/api/user/profile', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Failed to load profile data');
    }
    return response.json();
  })
  .then(data => {
    // Assuming your API returns data with keys: first_name, last_name, mobile_number, country, trust_score
    const fullName = data.first_name + (data.last_name ? " " + data.last_name : "");
    document.getElementById('full-name').textContent = fullName || 'N/A';
    document.getElementById('mobile-number').textContent = data.mobile_number || 'N/A';
    document.getElementById('user-country').textContent = data.country || 'N/A';
    document.getElementById('user-trust-score').textContent = data.trust_score || 'N/A';
  })
  .catch(error => {
    console.error("Error fetching profile data:", error);
    alert("Failed to load profile data. Please log in again.");
    window.location.href = '/auth/login_form';
  });

  // Logout functionality
  const logoutButton = document.getElementById('logout-button');
  if (logoutButton) {
    logoutButton.addEventListener('click', function(e) {
      e.preventDefault();
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_id');
      window.location.href = '/';
    });
  }
});
