console.log("Transactions JS loaded");

document.addEventListener('DOMContentLoaded', function(){
  // Retrieve the token from localStorage
  const token = localStorage.getItem('access_token');
  if (!token) {
    window.location.href = '/auth/login_form';
    return;
  }

  // Function to fetch and update wallet info
  function fetchWallet(){
    fetch('/api/wallets', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })
    .then(res => {
      console.log("Wallet fetch response status:", res.status);
      return res.json();
    })
    .then(data => {
      console.log("Wallet data:", data);
      const walletBalanceEl = document.getElementById('wallet-balance');
      const walletCurrencyEl = document.getElementById('wallet-currency');
      if (walletBalanceEl) {
        walletBalanceEl.textContent = data.balance;
      }
      if (walletCurrencyEl) {
        walletCurrencyEl.textContent = data.currency;
      }
    })
    .catch(err => {
      console.error("Error fetching wallet info:", err);
    });
  }

  // Function to fetch and update transaction history
  function fetchTransactions(){
    fetch('/api/transactions', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })
    .then(res => {
      console.log("Transactions fetch response status:", res.status);
      return res.json();
    })
    .then(data => {
      console.log("Transaction history:", data);
      const historyList = document.getElementById('transaction-history');
      historyList.innerHTML = ''; // Clear current list
      data.forEach(tx => {
        const li = document.createElement('li');
        li.textContent = `${tx.transaction_type.toUpperCase()} of ${tx.amount} on ${tx.timestamp}`;
        historyList.appendChild(li);
      });
    })
    .catch(err => {
      console.error("Error fetching transactions:", err);
    });
  }

  // Initially load wallet info and transaction history
  fetchWallet();
  fetchTransactions();

  // Handle transaction form submission
  const transactionForm = document.getElementById('transaction-form');
  if (transactionForm) {
    transactionForm.addEventListener('submit', function(e){
      e.preventDefault(); // Prevent default form submission

      const amount = parseFloat(e.target.amount.value);
      const transaction_type = e.target.transaction_type.value;
      
      console.log("Submitting transaction:", { amount, transaction_type });
      
      fetch('/api/transactions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ amount, transaction_type })
      })
      .then(response => {
        console.log("POST transaction response status:", response.status);
        if (!response.ok) {
          throw new Error('Transaction failed');
        }
        return response.json();
      })
      .then(data => {
        console.log("Transaction successful:", data);
        alert('Transaction successful!');
        // Update wallet info and transaction history after a successful transaction
        fetchWallet();
        fetchTransactions();
        transactionForm.reset();
      })
      .catch(error => {
        console.error("Error during transaction:", error);
        alert("Transaction failed. " + error.message);
      });
    });
  }

  // Back button functionality
  const backButton = document.getElementById('back-to-dashboard');
  if (backButton) {
    backButton.addEventListener('click', function() {
      window.location.href = '/dashboard';
    });
  }

  // Logout functionality
  const logoutButton = document.getElementById('logout-button');
  if (logoutButton) {
    logoutButton.addEventListener('click', function(){
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_id');
      window.location.href = '/';
    });
  }
});
