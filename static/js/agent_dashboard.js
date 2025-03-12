console.log("Agent Dashboard JS Loaded");

document.addEventListener("DOMContentLoaded", function () {
  // Section Elements
  const overviewSection = document.getElementById("content-overview");
  const transactionsSection = document.getElementById("content-transactions");
  const simRegistrationSection = document.getElementById("content-sim-registration");
  const profileSection = document.getElementById("content-profile");
  let transactionChart;

  // ✅ Function to Show Sections
  function showSection(section, callback = null) {
    document.querySelectorAll(".content-section").forEach(s => s.style.display = "none");
    section.style.display = "block";
    if (callback) callback();
  }

  // ✅ Fetch Agent Dashboard Data
  function fetchAgentDashboardData() {
    fetch("/agent/dashboard/data", { method: "GET", credentials: "include" })
    .then(response => response.json())
    .then(data => {
      console.log("Agent Dashboard Data:", data);
      document.getElementById("total-transactions").textContent = data.total_transactions || 0;
      document.getElementById("total-sims").textContent = data.total_sims || 0;
    })
    .catch(error => console.error("Error fetching agent dashboard data:", error));
  }

  // ✅ Fetch Wallet Info
  function fetchWalletInfo() {
    fetch("/agent/wallet", { method: "GET", credentials: "include" })
    .then(response => response.json())
    .then(data => {
      console.log("Wallet Info:", data);
      document.getElementById("wallet-balance").textContent = data.balance;
      document.getElementById("wallet-currency").textContent = data.currency;
    })
    .catch(error => console.error("Error fetching wallet info:", error));
  }

  // ✅ Fetch Transaction History and Render Chart
  function fetchTransactionHistory() {
    fetch("/agent/transactions", { method: "GET", credentials: "include" })
    .then(response => response.json())
    .then(data => {
      console.log("Transaction History:", data);
      const historyTable = document.getElementById("transaction-history").querySelector("tbody");
      historyTable.innerHTML = "";
      data.transactions.forEach(tx => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${new Date(tx.timestamp).toLocaleDateString()}</td>
          <td>${tx.transaction_type.toUpperCase()}</td>
          <td>${tx.amount}</td>
          <td>${tx.transaction_type === 'transfer' ? tx.recipient_mobile : 'Self'}</td>
        `;
        historyTable.appendChild(row);
      });

      // ✅ Render transaction chart
      renderTransactionChart(data.transactions);
    })
    .catch(error => console.error("Error fetching transactions:", error));
}

  // ✅ Function to Get User Location
  function getLocation() {
    return new Promise((resolve) => {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            resolve(`${position.coords.latitude.toFixed(4)}, ${position.coords.longitude.toFixed(4)}`);
          },
          (error) => {
            console.error("Geolocation error:", error);
            resolve("Location not available");
          },
          { timeout: 5000 }
        );
      } else {
        resolve("Geolocation not supported");
      }
    });
  }

  // ✅ Submit Transaction (Show Backend Validation Messages)
async function submitTransaction(event) {
  event.preventDefault();

  const amountInput = document.querySelector('[name="amount"]');
  const transactionTypeInput = document.querySelector('[name="transaction_type"]');
  const recipientMobileInput = document.querySelector('[name="recipient_mobile"]');

  const amount = parseFloat(amountInput.value);
  const transactionType = transactionTypeInput.value;
  const recipientMobile = recipientMobileInput && recipientMobileInput.value.trim() ? recipientMobileInput.value.trim() : null;

  if (isNaN(amount) || amount <= 0) {
    alert("❌ Error: Please enter a valid amount greater than zero.");
    return;
  }

  if (!transactionType) {
    alert("❌ Error: Please select a transaction type.");
    return;
  }

  // ✅ Ensure deposits require a recipient (Agents cannot deposit to themselves)
  if (transactionType === "deposit" && !recipientMobile) {
    alert("❌ Error: Deposits must have a recipient mobile number.");
    return;
  }

  // ✅ Ensure transfers have a recipient
  if (transactionType === "transfer" && !recipientMobile) {
    alert("❌ Error: Transfers require a recipient mobile number.");
    return;
  }

  const device_info = navigator.userAgent;
  const location = await getLocation();

  try {
    const response = await fetch("/agent/transaction", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        amount,
        transaction_type: transactionType,
        recipient_mobile: recipientMobile,
        device_info,
        location
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Transaction failed");
    }

    alert(`✅ Success: ${data.message}`);
    fetchWalletInfo(); // ✅ Refresh wallet balance
    fetchTransactionHistory(); // ✅ Refresh transaction history
  } catch (error) {
    alert(`❌ Error: ${error.message}`);
    console.error("Transaction error:", error);
  }
}

// ✅ Attach Event Listener for Transactions
document.addEventListener("DOMContentLoaded", function () {
  const transactionForm = document.getElementById("transaction-form");
  if (transactionForm) {
    transactionForm.addEventListener("submit", submitTransaction);
  }
});

// ✅ Render Transaction Chart
function renderTransactionChart(transactions) {
  const ctx = document.getElementById("transactionChart").getContext("2d");

  if (window.transactionChart) {
    window.transactionChart.destroy(); // ✅ Destroy previous chart before rendering new one
  }

  const labels = transactions.map(tx => tx.timestamp.slice(0, 10));
  const data = transactions.map(tx => tx.amount);

  window.transactionChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [{
        label: "Transaction Amount",
        data: data,
        borderColor: "#2962ff",
        borderWidth: 2,
        fill: true
      }]
    },
    options: {
      responsive: true,
      scales: {
        x: { title: { display: true, text: "Date" } },
        y: { title: { display: true, text: "Amount" } }
      }
    }
  });
}

// ✅ Show Mobile Input for Transfer & Deposit Transactions
document.getElementById("transaction-type").addEventListener("change", function () {
  const recipientMobileField = document.getElementById("recipient-mobile");
  
  if (this.value === "transfer" || this.value === "deposit") {
    recipientMobileField.style.display = "block"; // ✅ Show input field
    recipientMobileField.setAttribute("required", "true"); // ✅ Make it required
  } else {
    recipientMobileField.style.display = "none"; // ✅ Hide input field
    recipientMobileField.removeAttribute("required"); // ✅ Remove required for other transactions
  }
});

// ✅ SIM Registration (Agent Registers SIMs)
function registerSIM(event) {
  event.preventDefault();

  const userIdInput = document.getElementById("register-user-id");
  const userId = userIdInput ? userIdInput.value.trim() : null; // Get user ID if provided

  const payload = userId ? { user_id: userId } : {}; // Include user_id only if available

  fetch("/agent/register_sim", {
      method: "POST",
      headers: { 
          "Content-Type": "application/json"
      },
      credentials: "include",  // ✅ Uses HTTP-only cookies for authentication
      body: JSON.stringify(payload) // ✅ Send user_id if available
  })
  .then(response => response.json())
  .then(data => {
      if (data.error) {
          alert(`❌ Error: ${data.error}`);
      } else {
          alert(`✅ SIM Registered Successfully!\nICCID: ${data.iccid}\nMobile Number: ${data.mobile_number}`);
          fetchSimRegistrationHistory(); // ✅ Refresh SIM list after registration
      }
  })
  .catch(error => {
      console.error("❌ Error registering SIM:", error);
      alert("❌ An unexpected error occurred while registering the SIM.");
  });
}

// ✅ Attach Event Listener for SIM Registration
document.addEventListener("DOMContentLoaded", function () {
  const simRegistrationForm = document.getElementById("sim-registration-form");
  if (simRegistrationForm) {
      simRegistrationForm.addEventListener("submit", registerSIM);
  }
});


// ✅ Function to fetch and display the SIMs registered by the agent.
function fetchSimRegistrationHistory() {
  fetch("/agent/sim-registrations", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      credentials: "include"
  })
  .then(response => {
      if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json(); // ✅ Convert response to JSON
  })
  .then(data => {
      console.log("SIM Registration History:", data);
      const simTable = document.getElementById("sim-registration-history").querySelector("tbody");

      if (!simTable) {
          console.error("❌ Error: SIM registration history table not found!");
          return;
      }

      simTable.innerHTML = ""; // ✅ Clear table before adding new rows

      if (!data.sims || data.sims.length === 0) {
          simTable.innerHTML = `<tr><td colspan='3' class="text-center">No SIMs registered yet.</td></tr>`;
          return;
      }

      data.sims.forEach(sim => {
          const row = document.createElement("tr");
          row.innerHTML = `
            <td>${sim.mobile_number}</td>
            <td>${new Date(sim.timestamp).toLocaleDateString()}</td>
            <td>${sim.status}</td>
          `;
          simTable.appendChild(row);
      });
  })
  .catch(error => {
      console.error("❌ Error fetching SIM registrations:", error);
      alert("❌ Failed to load SIM registration history.");
  });
}


 // ✅ Fetch Profile Information
 function fetchProfileInfo() {
  fetch("/agent/profile", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      credentials: "include"
  })
  .then(response => response.json())
  .then(data => {
      console.log("Profile Info:", data);

      if (data.error) {
          alert(`❌ Error: ${data.error}`);
          return;
      }

      document.getElementById("full-name").textContent = data.full_name || "N/A";
      document.getElementById("mobile-number").textContent = data.mobile_number || "N/A";
      document.getElementById("user-country").textContent = data.country || "N/A";
  })
  .catch(error => console.error("Error fetching profile info:", error));
}

// ✅ Ensure Sections Work
document.getElementById("transaction-form").addEventListener("submit", submitTransaction);
document.getElementById("show-overview").addEventListener("click", () => showSection(overviewSection, fetchAgentDashboardData));
document.getElementById("show-transactions").addEventListener("click", () => showSection(transactionsSection, fetchTransactionHistory));
document.getElementById("show-sim-registration").addEventListener("click", () => showSection(simRegistrationSection));
document.getElementById("show-profile").addEventListener("click", () => showSection(profileSection, fetchProfileInfo));
document.getElementById("sim-registration-form").addEventListener("submit", registerSIM);

// ✅ Logout Button
document.getElementById("logout-link").addEventListener("click", function (e) {
  e.preventDefault();
  fetch("/api/auth/logout", { method: "POST" }).then(() => window.location.href = "/api/auth/login_form");
});

// ✅ Show Overview on First Load
showSection(overviewSection);
fetchAgentDashboardData();
fetchWalletInfo();
fetchTransactionHistory();
fetchProfileInfo();
fetchSimRegistrationHistory();
});

