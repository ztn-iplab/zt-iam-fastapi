console.log("Dashboard JS loaded");

document.addEventListener('DOMContentLoaded', function() {
  const token = localStorage.getItem('access_token');
  if (!token) {
    window.location.href = '/auth/login_form';
    return;
  }

  // DOM Elements
  const overviewSection = document.getElementById('overview-section');
  const transactionsSection = document.getElementById('transactions-section');
  const showOverviewLink = document.getElementById('show-overview-link');
  const showTransactionsLink = document.getElementById('show-transactions-link');

  // 1) Show/hide sections
  if (showOverviewLink) {
    showOverviewLink.addEventListener('click', function(e) {
      e.preventDefault();
      overviewSection.style.display = 'flex';    // or block
      transactionsSection.style.display = 'none';
    });
  }

  if (showTransactionsLink) {
    showTransactionsLink.addEventListener('click', function(e) {
      e.preventDefault();
      overviewSection.style.display = 'none';
      transactionsSection.style.display = 'flex';
      fetchTransactions(); // load transactions whenever we switch to that section
    });
  }

  // 2) Fetch user data & wallet info
  function fetchUserData() {
    fetch('/api/user', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })
    .then(res => {
      if (!res.ok) throw new Error('Failed to load user data');
      return res.json();
    })
    .then(data => {
      document.getElementById('welcome-title').textContent = `Welcome, ${data.first_name || 'User'}!`;
      if (data.wallet) {
        document.getElementById('wallet-balance').textContent = data.wallet.balance;
        document.getElementById('wallet-currency').textContent = data.wallet.currency;
      }
    })
    .catch(error => {
      console.error("Error fetching user data:", error);
      alert("Failed to load user data. Please log in again.");
      window.location.href = '/auth/login_form';
    });
  }

  // 3) Fetch Transactions
  function fetchTransactions() {
    fetch('/api/transactions', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })
    .then(res => {
      if (!res.ok) throw new Error('Failed to load transactions');
      return res.json();
    })
    .then(data => {
      const historyList = document.getElementById('transaction-history');
      historyList.innerHTML = '';
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

  // 4) Transaction Form
  const transactionForm = document.getElementById('transaction-form');
  if (transactionForm) {
    transactionForm.addEventListener('submit', function(e) {
      e.preventDefault();
      const amount = parseFloat(e.target.amount.value);
      const transaction_type = e.target.transaction_type.value;

      fetch('/api/transactions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ amount, transaction_type })
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Transaction failed');
        }
        return response.json();
      })
      .then(data => {
        alert('Transaction successful!');
        // Refresh wallet info & transactions
        fetchUserData();
        fetchTransactions();
        transactionForm.reset();
      })
      .catch(error => {
        console.error("Error during transaction:", error);
        alert("Transaction failed. " + error.message);
      });
    });
  }

  // 5) Logout
  const logoutLink = document.getElementById('logout-link');
  if (logoutLink) {
    logoutLink.addEventListener('click', function(e) {
      e.preventDefault();
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_id');
      window.location.href = '/';
    });
  }

  // Initial load: show overview by default, fetch user data
  overviewSection.style.display = 'flex';
  transactionsSection.style.display = 'none';
  fetchUserData();
});
