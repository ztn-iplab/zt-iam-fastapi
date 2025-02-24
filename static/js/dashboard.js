console.log("Dashboard JS loaded");

// ============================
// Inactivity Timeout Logic
// ============================
const INACTIVITY_LIMIT = 15 * 60 * 1000; // 15 minutes in milliseconds
let lastActivityTime = Date.now();
function resetActivityTimer() { lastActivityTime = Date.now(); }
document.addEventListener('mousemove', resetActivityTimer);
document.addEventListener('keydown', resetActivityTimer);
document.addEventListener('click', resetActivityTimer);
document.addEventListener('scroll', resetActivityTimer);
setInterval(() => {
  if (Date.now() - lastActivityTime > INACTIVITY_LIMIT) {
    alert("You've been inactive. Logging out.");
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_id');
    window.location.href = '/api/auth/login_form';
  }
}, 60000); // check every minute

// ============================
// Check the Admin Access
// ============================

function checkAdminAccess() {
  const token = localStorage.getItem("access_token");
  if (!token) return;

  fetch("/api/user", {
      method: "GET",
      headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
      }
  })
  .then(res => res.json())
  .then(data => {
      if (data.role === "admin" || data.role === "agent") {
          document.getElementById("admin-panel").style.display = "block";
          fetchUsersForAdmin();
          fetchFlaggedTransactions();
      }
  })
  .catch(error => console.error("Error checking admin access:", error));
}

// Call the function when dashboard loads
document.addEventListener("DOMContentLoaded", function() {
  checkAdminAccess();
});


// Fetch Users & Display in Admin Panel
function fetchUsersForAdmin() {
    const token = localStorage.getItem("access_token");

    fetch("/api/admin/users", {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        }
    })
    .then(res => res.json())
    .then(users => {
        const userList = document.getElementById("admin-user-list");
        userList.innerHTML = ""; // Clear previous content

        users.forEach(user => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${user.id}</td>
                <td>${user.first_name} ${user.last_name || ""}</td>
                <td>${user.mobile_number}</td>
                <td>${user.email}</td>
                <td>
                    <select class="role-select" data-user-id="${user.id}">
                        <option value="user" ${user.role === "user" ? "selected" : ""}>User</option>
                        <option value="agent" ${user.role === "agent" ? "selected" : ""}>Agent</option>
                        <option value="admin" ${user.role === "admin" ? "selected" : ""}>Admin</option>
                    </select>
                </td>
                <td>
                    <button class="suspend-user" data-user-id="${user.id}">Suspend</button>
                    <button class="verify-user" data-user-id="${user.id}">Verify</button>
                </td>
            `;
            userList.appendChild(row);
        });

        // Attach event listeners to role selectors
        document.querySelectorAll(".role-select").forEach(select => {
            select.addEventListener("change", function () {
                updateUserRole(this.dataset.userId, this.value);
            });
        });

        // Attach event listeners to suspend buttons
        document.querySelectorAll(".suspend-user").forEach(button => {
            button.addEventListener("click", function () {
                suspendUser(this.dataset.userId);
            });
        });

        // Attach event listeners to verify buttons
        document.querySelectorAll(".verify-user").forEach(button => {
            button.addEventListener("click", function () {
                verifyUser(this.dataset.userId);
            });
        });
    })
    .catch(error => console.error("Error fetching users:", error));
}

// Function to Update User Role
function updateUserRole(userId, newRole) {
    const token = localStorage.getItem("access_token");

    fetch("/api/admin/assign_role", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ user_id: userId, role_id: newRole })
    })
    .then(response => response.json())
    .then(data => {
        alert("Role updated successfully!");
        fetchUsersForAdmin(); // Refresh user list
    })
    .catch(error => console.error("Error updating role:", error));
}

// Function to Suspend User
function suspendUser(userId) {
    const token = localStorage.getItem("access_token");

    fetch(`/api/admin/suspend_user/${userId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        }
    })
    .then(response => response.json())
    .then(data => {
        alert("User suspended successfully!");
        fetchUsersForAdmin();
    })
    .catch(error => console.error("Error suspending user:", error));
}

// Function to Verify User
function verifyUser(userId) {
    const token = localStorage.getItem("access_token");

    fetch(`/api/admin/verify_user/${userId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        }
    })
    .then(response => response.json())
    .then(data => {
        alert("User verified successfully!");
        fetchUsersForAdmin();
    })
    .catch(error => console.error("Error verifying user:", error));
}

// Load Admin Dashboard Functions
document.addEventListener("DOMContentLoaded", function() {
    checkAdminAccess();
});

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
      if (transactionTypeSelect.value === 'transfer') {
        recipientMobileInput.style.display = 'block';
      } else {
        recipientMobileInput.style.display = 'none';
      }
    });
  }
});

// ============================
// Main Dashboard Functionality
// ============================
document.addEventListener('DOMContentLoaded', function() {
  const token = localStorage.getItem('access_token');
  if (!token) {
    window.location.href = '/api/auth/login_form';
    return;
  }

  // DOM Elements for section toggling
  const overviewSection = document.getElementById('content-overview');
  const transactionsSection = document.getElementById('content-transactions');
  const profileSection = document.getElementById('content-profile');
  const showOverviewLink = document.getElementById('show-overview-link');
  const showTransactionsLink = document.getElementById('show-transactions-link');
  const showProfileLink = document.getElementById('show-profile-link');
  const aggregationSelect = document.getElementById('aggregation-type');
  let transactionChart; // Chart.js instance

  // Section toggling event listeners
  if (showOverviewLink) {
    showOverviewLink.addEventListener('click', function(e) {
      e.preventDefault();
      overviewSection.style.display = 'block';
      transactionsSection.style.display = 'none';
      profileSection.style.display = 'none';
      fetchUserData();
      fetchTransactionsForChart();
    });
  }
  if (showTransactionsLink) {
    showTransactionsLink.addEventListener('click', function(e) {
      e.preventDefault();
      overviewSection.style.display = 'none';
      transactionsSection.style.display = 'block';
      profileSection.style.display = 'none';
      fetchTransactions();
    });
  }
  if (showProfileLink) {
    showProfileLink.addEventListener('click', function(e) {
      e.preventDefault();
      overviewSection.style.display = 'none';
      transactionsSection.style.display = 'none';
      profileSection.style.display = 'block';
      fetchProfileData();
    });
  }

  // ============================
  // Fetch User Data (Overview)
  // ============================
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
      alert("Your session has expired due to inactivity. Please log in again.");
      window.location.href = '/api/auth/login_form';
    });
  }

  // ============================
  // Fetch Profile Data (Profile Section)
  // ============================
  function fetchProfileData() {
    fetch('/api/user/profile', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })
    .then(res => {
      if (!res.ok) throw new Error('Failed to load profile data');
      return res.json();
    })
    .then(data => {
      const fullName = data.first_name + (data.last_name ? " " + data.last_name : "");
      document.getElementById('full-name').textContent = fullName || 'N/A';
      document.getElementById('mobile-number').textContent = data.mobile_number || 'N/A';
      document.getElementById('user-country').textContent = data.country || 'N/A';
      document.getElementById('user-trust-score').textContent = data.trust_score || 'N/A';
    })
    .catch(error => {
      console.error("Error fetching profile data:", error);
      alert("Your session has expired due to inactivity,Please log in again.");
      window.location.href = '/api/auth/login_form';
    });
  }

  // ============================
  // Aggregate Transactions for Chart
  // ============================
  function aggregateTransactions(data, aggregationType) {
    const aggregated = {};
    if (aggregationType === 'daily') {
      data.forEach(tx => {
        const dateStr = tx.timestamp.slice(0, 10); // YYYY-MM-DD
        const amount = parseFloat(tx.amount) * (tx.transaction_type === 'withdrawal' ? -1 : 1);
        aggregated[dateStr] = (aggregated[dateStr] || 0) + amount;
      });
    } else if (aggregationType === 'monthly') {
      data.forEach(tx => {
        const dateStr = tx.timestamp.slice(0, 7); // YYYY-MM
        const amount = parseFloat(tx.amount) * (tx.transaction_type === 'withdrawal' ? -1 : 1);
        aggregated[dateStr] = (aggregated[dateStr] || 0) + amount;
      });
    }
    const labels = Object.keys(aggregated).sort();
    const amounts = labels.map(date => aggregated[date]);
    return { labels, amounts };
  }

  // ============================
  // Fetch Transactions for Chart
  // ============================
  function fetchTransactionsForChart() {
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
      const aggregationType = aggregationSelect.value; // "daily" or "monthly"
      const aggregatedData = aggregateTransactions(data, aggregationType);
      renderTransactionChart(aggregatedData.labels, aggregatedData.amounts);
    })
    .catch(error => {
      console.error("Error fetching transactions for chart:", error);
    });
  }

  // ============================
  // Render Chart using Chart.js
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
  // Fetch Transaction History (Transactions Section)
  // ============================
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

  // Transaction Form Submission with Transfer Support and Better Error Handling
const transactionForm = document.getElementById('transaction-form');
if (transactionForm) {
  transactionForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const amount = parseFloat(e.target.amount.value);
    const transaction_type = e.target.transaction_type.value;

    // For transfers, get the recipient mobile number
    let recipient_mobile = "";
    if (transaction_type === 'transfer') {
      recipient_mobile = e.target.recipient_mobile ? e.target.recipient_mobile.value : "";
      if (!recipient_mobile) {
        alert("Please provide a recipient mobile number for transfers.");
        return;
      }
    }

    const device_info = getDeviceInfo();
    const location = await getLocation();

    // Build payload; include recipient_mobile only if it's a transfer
    const payload = {
      amount,
      transaction_type,
      device_info,
      location
    };
    if (transaction_type === 'transfer') {
      payload.recipient_mobile = recipient_mobile;
    }

    fetch('/api/transactions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    })
    .then(async response => {
      // If the response is not OK, try to extract and throw the error message
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Transaction failed');
      }
      return response.json();
    })
    .then(data => {
      alert('Transaction successful!');
      fetchUserData();
      fetchTransactions();
      fetchTransactionsForChart();
      transactionForm.reset();
    })
    .catch(error => {
      console.error("Error during transaction:", error);
      alert("Transaction failed. " + error.message);
    });
  });
}

  // ============================
  // Logout Functionality
  // ============================
  const logoutLink = document.getElementById('logout-link');
  if (logoutLink) {
    logoutLink.addEventListener('click', function(e) {
      e.preventDefault();
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_id');
      window.location.href = '/';
    });
  }

  // Update chart when aggregation type changes
  const aggregationSelectEl = document.getElementById('aggregation-type');
  if (aggregationSelectEl) {
    aggregationSelectEl.addEventListener('change', function() {
      fetchTransactionsForChart();
    });
  }

  // Initial load: default to Overview section
  document.getElementById('content-overview').style.display = 'block';
  document.getElementById('content-transactions').style.display = 'none';
  document.getElementById('content-profile').style.display = 'none';
  fetchUserData();
  fetchTransactionsForChart();
});
