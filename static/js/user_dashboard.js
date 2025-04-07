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

["mousemove", "keydown", "click", "scroll"].forEach((evt) =>
  document.addEventListener(evt, resetActivityTimer)
);

setInterval(() => {
  if (Date.now() - lastActivityTime > INACTIVITY_LIMIT) {
    alert("You've been inactive. Logging out.");
    // Redirect to the logout endpoint which clears the cookie
    fetch("/api/auth/logout", { method: "POST" }).then(() => {
      window.location.href = "/api/auth/login_form";
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
        (pos) => {
          const lat = pos.coords.latitude.toFixed(4);
          const lon = pos.coords.longitude.toFixed(4);
          resolve(`${lat}, ${lon}`);
        },
        (err) => {
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
document.addEventListener("DOMContentLoaded", function () {
  const transactionTypeSelect = document.getElementById("transaction-type");
  const recipientMobileInput = document.getElementById("recipient-mobile");
  if (transactionTypeSelect && recipientMobileInput) {
    transactionTypeSelect.addEventListener("change", function () {
      if (this.value === "transfer") {
        recipientMobileInput.style.display = "block";
      } else {
        recipientMobileInput.style.display = "none";
      }
    });
  }
});

// ============================
// Section Toggling for Sidebar
// ============================
document.addEventListener("DOMContentLoaded", function () {
  const overviewSection = document.getElementById("content-overview");
  const transactionsSection = document.getElementById("content-transactions");
  const profileSection = document.getElementById("content-profile");

  document
    .getElementById("show-overview-link")
    .addEventListener("click", function (e) {
      e.preventDefault();
      overviewSection.style.display = "block";
      transactionsSection.style.display = "none";
      profileSection.style.display = "none";
    });

  document
    .getElementById("show-transactions-link")
    .addEventListener("click", function (e) {
      e.preventDefault();
      overviewSection.style.display = "none";
      transactionsSection.style.display = "block";
      profileSection.style.display = "none";
      fetchTransactions();
    });

  document
    .getElementById("show-profile-link")
    .addEventListener("click", function (e) {
      e.preventDefault();
      overviewSection.style.display = "none";
      transactionsSection.style.display = "none";
      profileSection.style.display = "block";
      // Optionally: fetchProfileData();
    });

  // Initially show the overview section
  overviewSection.style.display = "block";
  transactionsSection.style.display = "none";
  profileSection.style.display = "none";
});

// ============================
// Fetch Wallet Information
// ============================
function fetchWalletInfo() {
  fetch("/api/wallets", {
    method: "GET",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
  })
    .then((res) => {
      if (!res.ok) throw new Error("Failed to fetch wallet info");
      return res.json();
    })
    .then((data) => {
      console.log("Wallet info received:", data);
      document.getElementById("wallet-balance").textContent = data.balance;
      document.getElementById("wallet-currency").textContent = data.currency;
    })
    .catch((err) => console.error("Error fetching wallet info:", err));
}

// ============================
// Fetch Transactions and Render Chart
// ============================
function fetchTransactions() {
  fetch("/api/transactions", {
    method: "GET",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
  })
    .then((res) => {
      if (!res.ok) throw new Error("Failed to fetch transactions");
      return res.json();
    })
    .then((response) => {
      console.log("Transactions received:", response);

      const transactions = response.transactions;
      if (!Array.isArray(transactions)) {
        throw new Error("Invalid transaction data format");
      }

      const historyTable = document
        .getElementById("transaction-history")
        .querySelector("tbody");
      historyTable.innerHTML = "";

      transactions.forEach((tx) => {
        const row = document.createElement("tr");
        row.innerHTML = `
        <td>${new Date(tx.timestamp).toLocaleDateString()}</td>
        <td>${tx.transaction_type.toUpperCase()}</td>
        <td>${tx.amount}</td>
        <td class="${tx.status_class || ""}">${tx.label || "N/A"}</td>
      `;
        historyTable.appendChild(row);
      });

      // ✅ Aggregate transaction data for chart rendering
      const aggregationSelect = document.getElementById("aggregation-type");
      const aggregationType = aggregationSelect
        ? aggregationSelect.value
        : "daily";
      const aggregated = {};
      transactions.forEach((tx) => {
        let label;
        if (aggregationType === "daily") {
          label = tx.timestamp.slice(0, 10);
        } else {
          label = tx.timestamp.slice(0, 7);
        }
        const amount =
          parseFloat(tx.amount) *
          (tx.transaction_type === "withdrawal" ? -1 : 1);
        aggregated[label] = (aggregated[label] || 0) + amount;
      });
      const labels = Object.keys(aggregated).sort();
      const data = labels.map((label) => aggregated[label]);
      renderTransactionChart(labels, data);
    })
    .catch((err) => console.error("Error fetching transactions:", err));
}

// ============================
// Render Transaction Chart
// ============================
function renderTransactionChart(labels, data) {
  const ctx = document.getElementById("transactionChart").getContext("2d");
  if (transactionChart) {
    transactionChart.destroy();
  }
  transactionChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Net Transaction Amount",
          data: data,
          backgroundColor: "rgba(41, 98, 255, 0.2)",
          borderColor: "#2962ff",
          borderWidth: 2,
          fill: true,
        },
      ],
    },
    options: {
      scales: {
        x: {
          title: { display: true, text: "Date", color: "#ffffff" },
          ticks: { color: "#ffffff" },
          grid: { color: "rgba(255, 255, 255, 0.1)" },
        },
        y: {
          title: { display: true, text: "Net Amount", color: "#ffffff" },
          ticks: { color: "#ffffff" },
          grid: { color: "rgba(255, 255, 255, 0.1)" },
        },
      },
      plugins: {
        legend: {
          labels: {
            font: { family: "Inter" },
            color: "#ffffff",
          },
        },
      },
    },
  });
}

// ============================
// Transaction Form Submission
// ============================
document.addEventListener("DOMContentLoaded", function () {
  const transactionForm = document.getElementById("transaction-form");
  const transactionTypeSelect = transactionForm.querySelector(
    '[name="transaction_type"]'
  );
  const recipientGroup = document.getElementById("recipient-mobile-group");
  const agentGroup = document.getElementById("agent-mobile-group");
  const totpGroup = document.getElementById("totp-group");

  // 🔄 Show/hide inputs dynamically
  transactionTypeSelect.addEventListener("change", function () {
    const selectedType = transactionTypeSelect.value;

    if (selectedType === "transfer") {
      recipientGroup.style.display = "block";
      agentGroup.style.display = "none";
      totpGroup.style.display = "block";
    } else if (selectedType === "withdrawal") {
      agentGroup.style.display = "block";
      recipientGroup.style.display = "none";
      totpGroup.style.display = "block";
    } else {
      recipientGroup.style.display = "none";
      agentGroup.style.display = "none";
      totpGroup.style.display = "none";
    }
  });

  // ✅ Transaction Form Submission with Confirmation Modal
  if (transactionForm) {
    transactionForm.addEventListener("submit", async function (e) {
      e.preventDefault();

      const amountInput = transactionForm.querySelector('[name="amount"]');
      const transactionTypeInput = transactionForm.querySelector(
        '[name="transaction_type"]'
      );
      const recipientMobileInput = transactionForm.querySelector(
        '[name="recipient_mobile"]'
      );
      const agentMobileInput = transactionForm.querySelector(
        '[name="agent_mobile"]'
      );
      const totpInput = document.getElementById("totp-input");

      const amount = parseFloat(amountInput.value);
      const transactionType = transactionTypeInput.value;
      const recipient_mobile = recipientMobileInput?.value.trim();
      const agent_mobile = agentMobileInput?.value.trim();
      const totp = totpInput?.value.trim();

      const device_info = getDeviceInfo();
      const location = await getLocation();

      // ✅ Validate amount
      if (isNaN(amount) || amount <= 0) {
        Toastify({
          text: "❌ Invalid amount. Please enter a value greater than 0 RWF.",
          style: { background: "#d32f2f" },
          duration: 4000,
        }).showToast();
        return;
      }

      // ✅ Validate transaction type
      if (!transactionType) {
        Toastify({
          text: "❌ Please select a transaction type.",
          style: { background: "#d32f2f" },
          duration: 4000,
        }).showToast();
        return;
      }

      // ✅ Validate TOTP
      if (!totp || totp.length < 6) {
        Toastify({
          text: "❌ Please enter a valid TOTP code.",
          style: { background: "#d32f2f" },
          duration: 4000,
        }).showToast();
        return;
      }

      const payload = {
        amount,
        transaction_type: transactionType,
        device_info,
        location,
        totp,
      };

      // ✅ Handle Transfer
      if (transactionType === "transfer") {
        if (!recipient_mobile) {
          Toastify({
            text: "❌ Please provide a recipient mobile number for transfers.",
            style: { background: "#d32f2f" },
            duration: 4000,
          }).showToast();
          return;
        }

        try {
          const res = await fetch(`/user-info/${recipient_mobile}`, {
            credentials: "include",
          });
          const userInfo = await res.json();

          if (!res.ok || !userInfo?.name) {
            Toastify({
              text: "❌ Recipient not found.",
              style: { background: "#d32f2f" },
              duration: 4000,
            }).showToast();
            return;
          }

          const confirmTransfer = confirm(
            `Are you sure you want to transfer ${amount} RWF to ${userInfo.name} (${recipient_mobile})?`
          );
          if (!confirmTransfer) return;

          payload.recipient_mobile = recipient_mobile;
        } catch (err) {
          Toastify({
            text: "❌ Failed to verify recipient info.",
            style: { background: "#d32f2f" },
            duration: 4000,
          }).showToast();
          return;
        }
      }

      // ✅ Handle Withdrawal
      if (transactionType === "withdrawal") {
        if (!agent_mobile) {
          Toastify({
            text: "❌ Please provide the agent's mobile number for withdrawals.",
            style: { background: "#d32f2f" },
            duration: 4000,
          }).showToast();
          return;
        }

        try {
          const res = await fetch(`/user-info/${agent_mobile}`, {
            credentials: "include",
          });
          const agentInfo = await res.json();

          if (!res.ok || !agentInfo?.name) {
            Toastify({
              text: "❌ Agent not found.",
              style: { background: "#d32f2f" },
              duration: 4000,
            }).showToast();
            return;
          }

          const confirmWithdraw = confirm(
            `Are you sure you want to request a ${amount} RWF withdrawal from ${agentInfo.name} (${agent_mobile})?`
          );
          if (!confirmWithdraw) return;

          payload.agent_mobile = agent_mobile;
        } catch (err) {
          Toastify({
            text: "❌ Failed to verify agent info.",
            style: { background: "#d32f2f" },
            duration: 4000,
          }).showToast();
          return;
        }
      }

      // ✅ Submit transaction
      fetch("/api/transactions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(payload),
      })
        .then(async (response) => {
          const result = await response.json();
          if (!response.ok)
            throw new Error(result.error || "Transaction failed");

          Toastify({
            text: result.message || "✅ Transaction successful.",
            style: { background: "#27ae60" },
            duration: 4000,
          }).showToast();

          transactionForm.reset();
          recipientGroup.style.display = "none";
          agentGroup.style.display = "none";
          totpGroup.style.display = "none";
          fetchTransactions();
          fetchWalletInfo();
        })
        .catch((err) => {
          Toastify({
            text: "❌ Transaction error: " + err.message,
            style: { background: "#d32f2f" },
            duration: 4000,
          }).showToast();
          console.error("Transaction error:", err);
        });
    });
  }
});

// ============================
// Initial Data Load
// ============================
document.addEventListener("DOMContentLoaded", function () {
  fetchWalletInfo();
  fetchTransactions();
});

// / ============================
// Apply Table Styling for Professional Look
// ============================
document.addEventListener("DOMContentLoaded", function () {
  const table = document.getElementById("transaction-history");
  if (table) {
    table.classList.add("styled-table");
  }
});

// ---------------------------
// Bind Logout Event
// ---------------------------
document.addEventListener("DOMContentLoaded", function () {
  const logoutLink = document.getElementById("logout-link");
  if (logoutLink) {
    logoutLink.addEventListener("click", function (e) {
      e.preventDefault();
      fetch("/api/auth/logout", { method: "POST" }).then(() => {
        window.location.href = "/api/auth/login_form";
      });
    });
  }
});
