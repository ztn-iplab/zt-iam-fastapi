console.log("Transactions JS loaded");

// Wait until the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function(){
  // Retrieve the token from localStorage
  const token = localStorage.getItem('access_token');
  if (!token) {
    // If no token is found, redirect to the login page
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
    .then(res => res.json())
    .then(data => {
      console.log("Wallet data:", data);
      document.getElementById('wallet-balance').textContent = data.balance;
      document.getElementById('wallet-currency').textContent = data.currency;
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
    .then(res => res.json())
    .then(data => {
      console.log("Transaction history:", data);
      const historyList = document.getElementById('transaction-history');
      historyList.innerHTML = ''; // Clear current list
      data.forEach(tx => {
        const li = document.createElement('li');
        // Format the transaction information (e.g., "DEPOSIT of 100.00 on 2025-02-17T14:30:00")
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
  transactionForm.addEventListener('submit', function(e){
    e.preventDefault(); // Prevent default form submission

    const amount = parseFloat(e.target.amount.value);
    const transaction_type = e.target.transaction_type.value;
    
    // Log the transaction details for debugging
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
      // Reset the form
      transactionForm.reset();
    })
    .catch(error => {
      console.error("Error during transaction:", error);
      alert("Transaction failed. " + error.message);
    });
  });

  // Logout functionality
  document.getElementById('logout-button').addEventListener('click', function(){
    console.log("Logout button clicked");
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_id');
    window.location.href = '/';
  });
});
