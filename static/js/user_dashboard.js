console.log("User Dashboard JS loaded");

// ============================
// Inactivity Timeout Logic
// ============================
const INACTIVITY_LIMIT = 15 * 60 * 1000; // 15 minutes in milliseconds
let lastActivityTime = Date.now();
["mousemove", "keydown", "click", "scroll"].forEach(evt => {
  document.addEventListener(evt, () => {
    lastActivityTime = Date.now();
    console.log("Activity detected: " + evt);
  });
});
setInterval(() => {
  if (Date.now() - lastActivityTime > INACTIVITY_LIMIT) {
    alert("You've been inactive. Logging out.");
    window.location.href = '/api/auth/logout';
  }
}, 60000);

// ============================
// Utility Functions
// ============================
function getDeviceInfo() {
  return navigator.userAgent;
}

function getLocation() {
  return new Promise((resolve) => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        pos => {
          const lat = pos.coords.latitude.toFixed(4);
          const lon = pos.coords.longitude.toFixed(4);
          resolve(`${lat}, ${lon}`);
        },
        err => {
          console.error("Geolocation error:", err);
          resolve("");
        },
        { timeout: 5000 }
      );
    } else {
      resolve("");
    }
  });
}

// ============================
// Toggle Recipient Input for Transfer
// ============================
document.addEventListener('DOMContentLoaded', function() {
  const transactionTypeSelect = document.getElementById('transaction-type');
  const recipientMobileInput = document.getElementById('recipient-mobile');
  if (transactionTypeSelect && recipientMobileInput) {
    transactionTypeSelect.addEventListener('change', function() {
      console.log("Transaction type changed to: " + this.value);
      if (this.value === 'transfer') {
        recipientMobileInput.style.display = 'block';
      } else {
        recipientMobileInput.style.display = 'none';
      }
    });
  } else {
    console.error("Transaction type select or recipient mobile input not found");
  }
});

// ============================
// Section Toggling for Sidebar
// ============================
document.addEventListener('DOMContentLoaded', function() {
  const overviewSection = document.getElementById('content-overview');
  const transactionsSection = document.getElementById('content-transactions');
  const profileSection = document.getElementById('content-profile');

  // Ensure these elements exist
  if (!overviewSection || !transactionsSection || !profileSection) {
    console.error("One or more content sections not found");
    return;
  }

  document.getElementById('show-overview-link').addEventListener('click', function(e) {
    e.preventDefault();
    console.log("Overview link clicked");
    overviewSection.style.display = 'block';
    transactionsSection.style.display = 'none';
    profileSection.style.display = 'none';
  });

  document.getElementById('show-transactions-link').addEventListener('click', function(e) {
    e.preventDefault();
    console.log("Transactions link clicked");
    overviewSection.style.display = 'none';
    transactionsSection.style.display = 'block';
    profileSection.style.display = 'none';
    fetchTransactions();
  });

  document.getElementById('show-profile-link').addEventListener('click', function(e) {
    e.preventDefault();
    console.log("Profile link clicked");
    overviewSection.style.display = 'none';
    transactionsSection.style.display = 'none';
    profileSection.style.display = 'block';
    // Optionally: call a fetchProfileData() function if needed.
  });

  // Initially, show the overview section
  overviewSection.style.display = 'block';
  transactionsSection.style.display = 'none';
  profileSection.style.display = 'none';

  // ============================
  // Fetch Wallet Information
  // ============================
  function fetchWalletInfo() {
    fetch('/api/wallets', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include' // Ensures the JWT cookie is sent
    })
    .then(res => {
      if (!res.ok) {
        throw new Error("Failed to fetch wallet info");
      }
      return res.json();
    })
    .then(data => {
      console.log("Wallet info received:", data);
      document.getElementById('wallet-balance').textContent = data.balance;
      document.getElementById('wallet-currency').textContent = data.currency;
    })
    .catch(err => console.error("Error fetching wallet info:", err));
  }
  

  // ============================
  // Fetch Transaction History
  // ============================
  function fetchTransactions() {
    fetch('/api/transactions', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include'
    })
    .then(res => {
      if (!res.ok) throw new Error("Failed to fetch transactions");
      return res.json();
    })
    .then(data => {
      console.log("Transactions received:", data);
      const historyList = document.getElementById('transaction-history');
      historyList.innerHTML = "";
      data.forEach(tx => {
        const li = document.createElement('li');
        li.textContent = `${tx.transaction_type.toUpperCase()} of ${tx.amount} on ${tx.timestamp}`;
        historyList.appendChild(li);
      });
    })
    .catch(err => console.error("Error fetching transactions:", err));
  }

  // ============================
  // Transaction Form Submission
  // ============================
  const transactionForm = document.getElementById('transaction-form');
  if (transactionForm) {
    transactionForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      const amount = transactionForm.querySelector('[name="amount"]').value;
      const transactionType = transactionForm.querySelector('[name="transaction_type"]').value;
      const recipientMobileInput = transactionForm.querySelector('[name="recipient_mobile"]');
      let recipient_mobile = recipientMobileInput ? recipientMobileInput.value : null;

      const device_info = getDeviceInfo();
      const location = await getLocation();

      const payload = {
        amount: amount,
        transaction_type: transactionType,
        device_info: device_info,
        location: location
      };
      if (transactionType === 'transfer') {
        if (!recipient_mobile) {
          alert("Please provide a recipient mobile number for transfers.");
          return;
        }
        payload.recipient_mobile = recipient_mobile;
      }

      fetch('/api/transactions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload)
      })
      .then(async response => {
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || "Transaction failed");
        }
        return response.json();
      })
      .then(data => {
        alert("Transaction successful! Updated balance: " + data.updated_balance);
        transactionForm.reset();
        fetchTransactions();
        fetchWalletInfo();
      })
      .catch(err => {
        alert("Transaction error: " + err.message);
        console.error("Transaction error:", err);
      });
    });
  }

  // Initial data load
  fetchWalletInfo();
  fetchTransactions();
});
