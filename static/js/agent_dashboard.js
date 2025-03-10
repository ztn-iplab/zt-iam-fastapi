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
    const amount = parseFloat(document.querySelector('[name="amount"]').value);
    const transactionType = document.querySelector('[name="transaction_type"]').value;
    const recipientMobileInput = document.querySelector('[name="recipient_mobile"]');
    const recipientMobile = recipientMobileInput && recipientMobileInput.value.trim() ? recipientMobileInput.value.trim() : null;

    const device_info = navigator.userAgent;
    const location = await getLocation();

    fetch("/agent/transaction", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ amount, transaction_type: transactionType, recipient_mobile: recipientMobile, device_info, location })
    })
    .then(async response => {
      const responseData = await response.json();
      if (!response.ok) {
        throw new Error(responseData.error || "Transaction failed");
      }
      return responseData;
    })
    .then(data => {
      alert(`✅ Success: ${data.message}`);
      fetchWalletInfo();
      fetchTransactionHistory();
    })
    .catch(error => {
      alert(`❌ Error: ${error.message}`);
      console.error("Transaction error:", error);
    });
  }

  // ✅ Render Transaction Chart
  function renderTransactionChart(transactions) {
    const ctx = document.getElementById("transactionChart").getContext("2d");

    if (transactionChart) transactionChart.destroy(); // Clear previous chart

    const labels = transactions.map(tx => tx.timestamp.slice(0, 10));
    const data = transactions.map(tx => tx.amount);

    transactionChart = new Chart(ctx, {
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

  // ✅ Show Mobile Input for Transfer Transactions
  document.getElementById("transaction-type").addEventListener("change", function () {
    const recipientMobileField = document.getElementById("recipient-mobile");
    if (this.value === "transfer") {
        recipientMobileField.style.display = "block"; // ✅ Show when Transfer is selected
        recipientMobileField.setAttribute("required", "true"); // ✅ Ensure it's required
    } else {
        recipientMobileField.style.display = "none"; // ✅ Hide for other transaction types
        recipientMobileField.removeAttribute("required"); // ✅ Remove required for non-transfer transactions
    }
  });

  // ✅ SIM Registration
  function registerSIM(event) {
    event.preventDefault();
    
    const mobileInput = document.querySelector('input[name="mobile_number"]');
    
    if (!mobileInput) {
        console.error("❌ Error: SIM mobile number input field not found!");
        alert("❌ SIM mobile number input field is missing.");
        return;
    }

    const mobileNumber = mobileInput.value.trim();
    
    if (!mobileNumber) {
        alert("❌ Mobile number is required!");
        return;
    }

    fetch("/agent/register_sim", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ mobile_number: mobileNumber })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(`❌ Error: ${data.error}`);
        } else {
            alert(`✅ ${data.message}`);
            document.querySelector("#sim-registration-form").reset();
            fetchSimRegistrationHistory(); // ✅ Refresh SIM history
        }
    })
    .catch(error => {
        console.error("❌ Error registering SIM:", error);
        alert("❌ An unexpected error occurred while registering the SIM.");
    });
}

// ✅ Function to fetch and display the SIMs registered by the agent.
function fetchSimRegistrationHistory() {
  fetch("/agent/sim-registrations", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      credentials: "include"
  })
  .then(response => {
      console.log("Raw Response:", response); // ✅ Debugging
      return response.text(); // Read response as text first
  })
  .then(text => {
      console.log("Response Text:", text); // ✅ Debugging
      return JSON.parse(text); // Convert text to JSON
  })
  .then(data => {
      console.log("SIM Registration History:", data);
      const simTable = document.getElementById("sim-registration-history").querySelector("tbody");

      if (!simTable) {
          console.error("❌ Error: SIM registration history table not found!");
          return;
      }

      simTable.innerHTML = ""; // ✅ Clear table before adding new rows

      if (data.sims.length === 0) {
          simTable.innerHTML = `<tr><td colspan='3'>No SIMs registered yet.</td></tr>`;
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
  .catch(error => console.error("❌ Error fetching SIM registrations:", error));
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
