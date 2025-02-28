console.log("Agent Dashboard JS Loaded");

document.addEventListener("DOMContentLoaded", function () {
  // Section Elements
  const overviewSection = document.getElementById("content-overview");
  const transactionsSection = document.getElementById("content-transactions");
  const simRegistrationSection = document.getElementById("content-sim-registration");
  const profileSection = document.getElementById("content-profile");
  const settingsSection = document.getElementById("content-settings");

  // Sidebar Navigation
  document.getElementById("show-overview").addEventListener("click", function (e) {
    e.preventDefault();
    showSection(overviewSection);
    fetchAgentOverview();
  });

  document.getElementById("show-transactions").addEventListener("click", function (e) {
    e.preventDefault();
    showSection(transactionsSection);
    fetchTransactionHistory();
  });

  document.getElementById("show-sim-registration").addEventListener("click", function (e) {
    e.preventDefault();
    showSection(simRegistrationSection);
    fetchSimRegistrationHistory();
  });

  document.getElementById("show-profile").addEventListener("click", function (e) {
    e.preventDefault();
    showSection(profileSection);
  });

  document.getElementById("show-settings").addEventListener("click", function (e) {
    e.preventDefault();
    showSection(settingsSection);
  });

  // Initially show Overview
  showSection(overviewSection);
  fetchAgentOverview();

  // Toggle Recipient Mobile Field
  const transactionTypeSelect = document.getElementById("transaction-type");
  const recipientMobileInput = document.getElementById("recipient-mobile");
  transactionTypeSelect.addEventListener("change", function () {
    recipientMobileInput.style.display = this.value === "transfer" ? "block" : "none";
  });

  // Fetch Agent Overview
  function fetchAgentOverview() {
    fetch("/api/agent/overview", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      credentials: "include"
    })
      .then(response => response.json())
      .then(data => {
        document.getElementById("total-transactions").textContent = data.total_transactions || 0;
        document.getElementById("total-sims").textContent = data.total_sims || 0;
      })
      .catch(error => console.error("Error fetching overview:", error));
  }

  // Fetch Transaction History
  function fetchTransactionHistory() {
    fetch("/api/agent/transactions", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      credentials: "include"
    })
      .then(response => response.json())
      .then(data => {
        const historyList = document.getElementById("transaction-history");
        historyList.innerHTML = "";
        data.transactions.forEach(tx => {
          const li = document.createElement("li");
          li.textContent = `${tx.transaction_type.toUpperCase()} of ${tx.amount} on ${tx.timestamp}`;
          historyList.appendChild(li);
        });
      })
      .catch(error => console.error("Error fetching transactions:", error));
  }

  // Fetch SIM Registration History
  function fetchSimRegistrationHistory() {
    fetch("/api/agent/sim-registrations", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      credentials: "include"
    })
      .then(response => response.json())
      .then(data => {
        const simList = document.getElementById("sim-registration-history");
        simList.innerHTML = "";
        data.sims.forEach(sim => {
          const li = document.createElement("li");
          li.textContent = `SIM registered: ${sim.mobile_number} on ${sim.timestamp}`;
          simList.appendChild(li);
        });
      })
      .catch(error => console.error("Error fetching SIM registrations:", error));
  }

  // Utility function to switch sections
  function showSection(section) {
    document.querySelectorAll(".content-section").forEach(s => s.style.display = "none");
    section.style.display = "block";
  }

  // Bind Logout event
  const logoutLink = document.getElementById("logout-link");
  if (logoutLink) {
    logoutLink.addEventListener("click", function(e){
      e.preventDefault();
      fetch("/api/auth/logout", { method: "POST" })
          .then(() => {
              window.location.href = "/api/auth/login_form";
          });
    });
  }
});
