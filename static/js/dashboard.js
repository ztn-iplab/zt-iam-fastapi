console.log("Dashboard JS loaded");

document.addEventListener('DOMContentLoaded', function() {
  // Retrieve the JWT token from localStorage
  const token = localStorage.getItem('access_token');
  if (!token) {
    window.location.href = '/auth/login_form';
    return;
  }

  // -------------------------------
  // Fetch User Data (including wallet info)
  // -------------------------------
  function fetchUserData() {
    fetch('/api/user', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to load user data');
      }
      return response.json();
    })
    .then(data => {
      // Update the welcome message using only the first name
      document.getElementById('welcome-title').textContent = `Welcome, ${data.first_name || 'User'}!`;

      // Combine first name and last name for full name display in profile (if an element exists)
      const fullName = data.first_name + (data.last_name ? " " + data.last_name : "");
      const fullNameElem = document.getElementById('full-name');
      if (fullNameElem) {
        fullNameElem.textContent = fullName || 'N/A';
      }

      // Update wallet info
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
  }

  // -------------------------------
  // Fetch Transactions History
  // -------------------------------
  function fetchTransactions() {
    fetch('/api/transactions', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to load transactions');
      }
      return response.json();
    })
    .then(data => {
      const historyList = document.getElementById('transaction-history');
      historyList.innerHTML = ''; // Clear any existing list items
      data.forEach(tx => {
        const li = document.createElement('li');
        li.textContent = `${tx.transaction_type.toUpperCase()} of ${tx.amount} on ${tx.timestamp}`;
        historyList.appendChild(li);
      });
    })
    .catch(error => {
      console.error("Error fetching transactions:", error);
    });
  }

  // Initial load of user data and transactions
  fetchUserData();
  fetchTransactions();

  // -------------------------------
  // Logout Functionality
  // -------------------------------
  document.getElementById('logout-link').addEventListener('click', function(e) {
    e.preventDefault();
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_id');
    window.location.href = '/';
  });
});
