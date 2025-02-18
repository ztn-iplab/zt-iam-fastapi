console.log("Dashboard JS loaded");

document.addEventListener('DOMContentLoaded', function() {
  const token = localStorage.getItem('access_token');
  if (!token) {
    window.location.href = '/auth/login_form';
    return;
  }

  // Fetch user and wallet data
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
      // Set welcome message using first_name only
      document.getElementById('welcome-title').textContent = `Welcome, ${data.first_name || 'User'}!`;

      // Update wallet info if it exists
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

  // Fetch recent transactions
  function fetchTransactions() {
    fetch('/api/transactions', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })
    .then(response => response.json())
    .then(data => {
      const historyList = document.getElementById('transaction-history');
      historyList.innerHTML = ''; // Clear the list
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

  // Initial load
  fetchUserData();
  fetchTransactions();

  // Logout
  const logoutLink = document.getElementById('logout-link');
  logoutLink.addEventListener('click', function(e) {
    e.preventDefault();
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_id');
    window.location.href = '/';
  });
});
