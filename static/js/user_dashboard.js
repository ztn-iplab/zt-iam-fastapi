console.log("User Dashboard JS loaded");

let transactionChart; // Global chart variable

// ============================
// Inactivity Timeout Logic
// ============================
const INACTIVITY_LIMIT = 15 * 60 * 1000; // 15 minutes
let lastActivityTime = Date.now();

function resetActivityTimer() { 
  lastActivityTime = Date.now(); 
}

["mousemove", "keydown", "click", "scroll"].forEach(evt =>
  document.addEventListener(evt, resetActivityTimer)
);

setInterval(() => {
  if (Date.now() - lastActivityTime > INACTIVITY_LIMIT) {
    alert("You've been inactive. Logging out.");
    // Redirect to the logout endpoint which clears the cookie
    fetch("/api/auth/logout", { method: "POST" })
      .then(() => {
        window.location.href = '/api/auth/login_form';
      });
  }
}, 60000);

// ============================
// Utility Functions
// ============================
function getDeviceInfo() {
  return navigator.userAgent;
}

// ============================
// Get Location
// ============================
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
      if (this.value === 'transfer') {
        recipientMobileInput.style.display = 'block';
      } else {
        recipientMobileInput.style.display = 'none';
      }
    });
  }
});

// ============================
// Section Toggling for Sidebar
// ============================
document.addEventListener('DOMContentLoaded', function() {
  const overviewSection = document.getElementById('content-overview');
  const transactionsSection = document.getElementById('content-transactions');
  const profileSection = document.getElementById('content-profile');

  document.getElementById('show-overview-link').addEventListener('click', function(e) {
    e.preventDefault();
    overviewSection.style.display = 'block';
    transactionsSection.style.display = 'none';
    profileSection.style.display = 'none';
  });

  document.getElementById('show-transactions-link').addEventListener('click', function(e) {
    e.preventDefault();
    overviewSection.style.display = 'none';
    transactionsSection.style.display = 'block';
    profileSection.style.display = 'none';
    fetchTransactions();
  });

  document.getElementById('show-profile-link').addEventListener('click', function(e) {
    e.preventDefault();
    overviewSection.style.display = 'none';
    transactionsSection.style.display = 'none';
    profileSection.style.display = 'block';
    // Optionally: fetchProfileData();
  });

  // Initially show the overview section
  overviewSection.style.display = 'block';
  transactionsSection.style.display = 'none';
  profileSection.style.display = 'none';
});

// ============================
// Fetch Wallet Information
// ============================
function fetchWalletInfo() {
  fetch('/api/wallets', {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include'
  })
  .then(res => {
    if (!res.ok) throw new Error("Failed to fetch wallet info");
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
// Fetch Transactions and Render Chart
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
  .then(response => {
    console.log("Transactions received:", response);
    
    const transactions = response.transactions;
    if (!Array.isArray(transactions)) {
      throw new Error("Invalid transaction data format");
    }

    const historyTable = document.getElementById('transaction-history').querySelector('tbody');
    historyTable.innerHTML = "";

    transactions.forEach(tx => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${new Date(tx.timestamp).toLocaleDateString()}</td>
        <td>${tx.transaction_type.toUpperCase()}</td>
        <td>${tx.amount}</td>
        <td>${tx.label || 'N/A'}</td>
      `;
      historyTable.appendChild(row);
    });

    // ✅ Aggregate transaction data for chart rendering
    const aggregationSelect = document.getElementById('aggregation-type');
    const aggregationType = aggregationSelect ? aggregationSelect.value : 'daily';
    const aggregated = {};
    transactions.forEach(tx => {
      let label;
      if (aggregationType === 'daily') {
        label = tx.timestamp.slice(0, 10);
      } else {
        label = tx.timestamp.slice(0, 7);
      }
      const amount = parseFloat(tx.amount) * (tx.transaction_type === 'withdrawal' ? -1 : 1);
      aggregated[label] = (aggregated[label] || 0) + amount;
    });
    const labels = Object.keys(aggregated).sort();
    const data = labels.map(label => aggregated[label]);
    renderTransactionChart(labels, data);
  })
  .catch(err => console.error("Error fetching transactions:", err));
}


// ============================
// Render Transaction Chart
// ============================
function renderTransactionChart(labels, data) {
  const ctx = document.getElementById('transactionChart').getContext('2d');
  if (transactionChart) {
    transactionChart.destroy();
  }
  transactionChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Net Transaction Amount',
        data: data,
        backgroundColor: 'rgba(41, 98, 255, 0.2)',
        borderColor: '#2962ff',
        borderWidth: 2,
        fill: true
      }]
    },
    options: {
      scales: {
        x: {
          title: { display: true, text: 'Date', color: '#ffffff' },
          ticks: { color: '#ffffff' },
          grid: { color: 'rgba(255, 255, 255, 0.1)' }
        },
        y: {
          title: { display: true, text: 'Net Amount', color: '#ffffff' },
          ticks: { color: '#ffffff' },
          grid: { color: 'rgba(255, 255, 255, 0.1)' }
        }
      },
      plugins: {
        legend: {
          labels: {
            font: { family: 'Inter' },
            color: '#ffffff'
          }
        }
      }
    }
  });
}

// ============================
// Transaction Form Submission
// ============================
document.addEventListener('DOMContentLoaded', function () {
  const transactionForm = document.getElementById('transaction-form');
  const transactionTypeSelect = transactionForm.querySelector('[name="transaction_type"]');
  const recipientGroup = document.getElementById("recipient-mobile-group");
  const agentGroup = document.getElementById("agent-mobile-group");

  // 🔄 Show/hide inputs dynamically
  transactionTypeSelect.addEventListener("change", function () {
    const selectedType = transactionTypeSelect.value;
    if (selectedType === "transfer") {
      recipientGroup.style.display = "block";
      agentGroup.style.display = "none";
    } else if (selectedType === "withdrawal") {
      agentGroup.style.display = "block";
      recipientGroup.style.display = "none";
    } else {
      recipientGroup.style.display = "none";
      agentGroup.style.display = "none";
    }
  });

  // ✅ Form submission logic
  if (transactionForm) {
    transactionForm.addEventListener('submit', async function (e) {
      e.preventDefault();

      const amount = transactionForm.querySelector('[name="amount"]').value;
      const transactionType = transactionForm.querySelector('[name="transaction_type"]').value;
      const recipientMobileInput = transactionForm.querySelector('[name="recipient_mobile"]');
      const agentMobileInput = transactionForm.querySelector('[name="agent_mobile"]');
      let recipient_mobile = recipientMobileInput ? recipientMobileInput.value : null;
      let agent_mobile = agentMobileInput ? agentMobileInput.value : null;

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

      if (transactionType === 'withdrawal') {
        if (!agent_mobile) {
          alert("Please provide the agent's mobile number for withdrawals.");
          return;
        }
        payload.agent_mobile = agent_mobile;
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
          console.error("Transaction error data:", errorData);
          throw new Error(errorData.error || "Transaction failed");
        }
        return response.json();
      })
      .then(data => {
        alert("Transaction successful! Updated balance: " + data.updated_balance);
        transactionForm.reset();
        recipientGroup.style.display = "none";
        agentGroup.style.display = "none";
        fetchTransactions();
        fetchWalletInfo();
      })
      .catch(err => {
        alert("Transaction error: " + err.message);
        console.error("Transaction error:", err);
      });
    });
  }
});

// ============================
// Initial Data Load
// ============================
document.addEventListener('DOMContentLoaded', function() {
  fetchWalletInfo();
  fetchTransactions();
});

// / ============================
// Apply Table Styling for Professional Look
// ============================
document.addEventListener('DOMContentLoaded', function() {
  const table = document.getElementById('transaction-history');
  if (table) {
    table.classList.add('styled-table');
  }
});

// ---------------------------
// Bind Logout Event
// ---------------------------
document.addEventListener('DOMContentLoaded', function(){
  const logoutLink = document.getElementById('logout-link');
  if (logoutLink) {
    logoutLink.addEventListener('click', function(e){
      e.preventDefault();
      fetch("/api/auth/logout", { method: "POST" })
        .then(() => {
          window.location.href = "/api/auth/login_form";
        });
    });
  }
});

