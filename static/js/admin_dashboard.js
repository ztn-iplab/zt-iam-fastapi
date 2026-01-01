console.log("Admin Dashboard JS loaded");

// ---------------------------
// Inactivity Timeout Logic
// ---------------------------
// const INACTIVITY_LIMIT = 60 * 60 * 1000; // 15 minutes in milliseconds
// let lastActivityTime = Date.now();
// ["mousemove", "keydown", "click", "scroll"].forEach((evt) =>
//   document.addEventListener(evt, () => {
//     lastActivityTime = Date.now();
//   })
// );
// setInterval(() => {
//   if (Date.now() - lastActivityTime > INACTIVITY_LIMIT) {
//     alert("You've been inactive. Logging out.");
//     fetch("/api/auth/logout", { method: "POST" }).then(() => {
//       window.location.href = "/api/auth/login_form";
//     });
//   }
// }, 60000);

// ---------------------------
// Admin Section Toggle
// ---------------------------
document.addEventListener("DOMContentLoaded", function () {
  const sectionMap = {
    "show-user-management": "user-management",
    "show-flagged-transactions": "flagged-transactions-section",
    "show-real-time-logs": "real-time-logs",
    "show-user-auth-logs": "user-auth-logs",
    "show-fund-agent": "fund-agent-section",
    "show-all-transactions": "all-transactions-section",
    "show-tenant-management": "tenant-management-section", // ✅ Added
  };

  Object.entries(sectionMap).forEach(([menuId, sectionId]) => {
    document.getElementById(menuId)?.addEventListener("click", () => {
      document
        .querySelectorAll(".admin-section")
        .forEach((s) => (s.style.display = "none"));
      document.getElementById(sectionId).style.display = "block";

      if (sectionId === "fund-agent-section") {
        fetchHqBalance();
        fetchFloatHistory();
        bindFundAgentForm();
      }

      if (sectionId === "flagged-transactions-section") {
        loadFlaggedTransactions();
      }

      if (sectionId === "real-time-logs") {
        loadRealTimeLogs();
      }

      if (sectionId === "user-auth-logs") {
        loadUserAuthLogs();
      }

      if (sectionId === "tenant-management-section") {
        bindRegisterTenantForm();
        loadTenants(); 
      }
    });
  });

  document
    .querySelectorAll(".admin-section")
    .forEach((s) => (s.style.display = "none"));
  document.getElementById("admin-welcome").style.display = "block";

  // ---------------------------
  // Admin Metrics Section
  // ---------------------------
  // Final Enhanced Admin Dashboard JavaScript with Full Feature Reintegration

  (async () => {
    const loginChart = document.getElementById("login-method-chart");
    const authFailuresChart = document.getElementById("auth-failures-chart");
    const transactionTypeChart = document.getElementById(
      "transaction-type-chart"
    );
    const flaggedChart = document.getElementById("flagged-transactions-chart");
    const heatmapContainer = document.getElementById("heatmap-container");
    const anomalyPanel = document.getElementById("anomaly-panel");

    let loginChartInstance,
      authFailuresInstance,
      transactionTypeInstance,
      flaggedInstance;
    let lastFetchedMetrics = {};

    const dateControls = document.createElement("div");
    dateControls.className = "d-flex gap-2 align-items-center mt-2 mb-3";
    dateControls.innerHTML = `
    <input type="text" id="daterange" class="form-control form-control-sm" style="max-width: 250px;" placeholder="Select date range">
    <button id="filter-date" class="btn btn-sm btn-outline-primary">🔍 Apply Filter</button>
  `;
    document.querySelector("#dashboard-metrics")?.prepend(dateControls);

    setTimeout(() => {
      if (window.flatpickr && document.getElementById("daterange")) {
        flatpickr("#daterange", {
          mode: "range",
          dateFormat: "Y-m-d",
          onClose: function (selectedDates, dateStr) {
            const range = dateStr.split(" to ");
            const from = range[0]?.trim() || null;
            const to = range[1]?.trim() || null;
            loadMetrics(from, to);
          },
        });
      }
    }, 100);

    const kpiContainer = document.createElement("div");
    kpiContainer.className = "row mb-4";
    document.querySelector("#dashboard-metrics")?.prepend(kpiContainer);

    function updateKPIs(data) {
      const animated = (id, value) => {
        const el = document.getElementById(id);
        if (!el) return;
        let count = 0;
        const step = Math.ceil(value / 30);
        const interval = setInterval(() => {
          count += step;
          if (count >= value) {
            el.textContent = value;
            clearInterval(interval);
          } else {
            el.textContent = count;
          }
        }, 20);
      };

      kpiContainer.innerHTML = `
    <div class="row row-cols-2 row-cols-md-4 g-3">
      <div class="col">
        <div class="card text-white bg-primary text-center shadow">
          <div class="card-body">
            <h5 class="card-title"><i class="bi bi-fingerprint me-2"></i>Total Logins</h5>
            <p class="card-text fs-4" id="kpi-total-logins">0</p>
          </div>
        </div>
      </div>
      <div class="col">
        <div class="card text-white bg-danger text-center shadow">
          <div class="card-body">
            <h5 class="card-title"><i class="bi bi-x-circle-fill me-2"></i>Failed Logins (7d)</h5>
            <p class="card-text fs-4" id="kpi-failed-logins">0</p>
          </div>
        </div>
      </div>
      <div class="col">
        <div class="card text-white bg-warning text-center shadow">
          <div class="card-body">
            <h5 class="card-title"><i class="bi bi-flag-fill me-2"></i>Flagged Txns</h5>
            <p class="card-text fs-4" id="kpi-flagged">0</p>
          </div>
        </div>
      </div>
      <div class="col">
        <div class="card text-white bg-success text-center shadow">
          <div class="card-body">
            <h5 class="card-title"><i class="bi bi-check-circle-fill me-2"></i>Clean Txns</h5>
            <p class="card-text fs-4" id="kpi-clean">0</p>
          </div>
        </div>
      </div>

      <div class="col">
        <div class="card text-white bg-dark text-center shadow">
          <div class="card-body">
            <h5 class="card-title"><i class="bi bi-person-check-fill me-2"></i>Active Users</h5>
            <p class="card-text fs-4" id="kpi-users-active">0</p>
          </div>
        </div>
      </div>
      <div class="col">
        <div class="card text-white bg-secondary text-center shadow">
          <div class="card-body">
            <h5 class="card-title"><i class="bi bi-person-dash-fill me-2"></i>Inactive Users</h5>
            <p class="card-text fs-4" id="kpi-users-inactive">0</p>
          </div>
        </div>
      </div>
      <div class="col">
        <div class="card text-white bg-danger text-center shadow">
          <div class="card-body">
            <h5 class="card-title"><i class="bi bi-lock-fill me-2"></i>Suspended Users</h5>
            <p class="card-text fs-4" id="kpi-users-suspended">0</p>
          </div>
        </div>
      </div>
      <div class="col">
        <div class="card text-white bg-warning text-center shadow">
          <div class="card-body">
            <h5 class="card-title"><i class="bi bi-question-circle-fill me-2"></i>Unverified Users</h5>
            <p class="card-text fs-4" id="kpi-users-unverified">0</p>
          </div>
        </div>
      </div>

      <div class="col">
        <div class="card text-white bg-info text-center shadow">
          <div class="card-body">
            <h5 class="card-title"><i class="bi bi-sim-fill me-2"></i>Active SIMs</h5>
            <p class="card-text fs-4" id="kpi-sims-active">0</p>
          </div>
        </div>
      </div>
      <div class="col">
        <div class="card text-white bg-warning text-center shadow">
          <div class="card-body">
            <h5 class="card-title"><i class="bi bi-arrow-repeat me-2"></i>Swapped SIMs</h5>
            <p class="card-text fs-4" id="kpi-sims-swapped">0</p>
          </div>
        </div>
      </div>
      <div class="col">
        <div class="card text-white bg-danger text-center shadow">
          <div class="card-body">
            <h5 class="card-title"><i class="bi bi-sim-slash-fill me-2"></i>Suspended SIMs</h5>
            <p class="card-text fs-4" id="kpi-sims-suspended">0</p>
          </div>
        </div>
      </div>
    </div>
  `;

      animated(
        "kpi-total-logins",
        data.login_methods.password +
          data.login_methods.totp +
          data.login_methods.webauthn
      );
      document.getElementById(
        "kpi-total-logins"
      ).parentElement.parentElement.onclick = () => {
        showOnlySection("user-auth-logs");
        function loadUserAuthLogsByUser(userId) {
          fetch(`/admin/user-auth-logs?user_id=${userId}`)
            .then((res) => res.json())
            .then((data) => {
              const tbody = document.getElementById("user-auth-logs-container");
              tbody.innerHTML = "";
              if (!data.length) {
                tbody.innerHTML = `<tr><td colspan="8" class="text-center text-muted">No logs yet</td></tr>`;
                return;
              }
              data.forEach((log) => {
                const row = `
          <tr>
            <td>${log.user}</td>
            <td>${log.method}</td>
            <td class="${
              log.status === "success" ? "text-success" : "text-danger"
            }">${log.status}</td>
            <td>${log.timestamp}</td>
            <td>${log.ip}</td>
            <td>${log.device}</td>
            <td>${log.location}</td>
            <td>${log.fails}</td>
          </tr>
        `;
                tbody.innerHTML += row;
              });
            });
        }

        function filterFlaggedByUser(userId) {
          fetch(`/admin/flagged-transactions?user_id=${userId}`)
            .then((res) => res.json())
            .then((data) => {
              const tbody = document.getElementById("flagged-transactions");
              tbody.innerHTML = "";
              if (!data.length) {
                tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted">No flagged transactions</td></tr>`;
                return;
              }
              data.forEach((txn) => {
                const row = `
          <tr>
            <td>User #${txn.user_id}</td>
            <td>${txn.amount}</td>
            <td>${txn.transaction_type}</td>
            <td>${txn.risk_score}</td>
            <td>${txn.status}</td>
            <td><button class="btn btn-sm btn-outline-info">View</button></td>
          </tr>
        `;
                tbody.innerHTML += row;
              });
            });
        }

        loadUserAuthLogs();
      };
      animated(
        "kpi-failed-logins",
        data.auth_failures.counts.reduce((a, b) => a + b, 0)
      );
      document.getElementById(
        "kpi-failed-logins"
      ).parentElement.parentElement.onclick = () => {
        showOnlySection("user-auth-logs");
        loadUserAuthLogs("failed");
      };
      animated("kpi-flagged", data.flagged.flagged);
      document.getElementById(
        "kpi-flagged"
      ).parentElement.parentElement.onclick = () => {
        showOnlySection("flagged-transactions-section");
        loadFlaggedTransactions();
      };
      animated("kpi-clean", data.flagged.clean);
      animated("kpi-users-active", data.user_states.active);
      document.getElementById(
        "kpi-users-active"
      ).parentElement.parentElement.onclick = () => {
        showOnlySection("user-management");
        filterUsers("active");
      };
      animated("kpi-users-inactive", data.user_states.inactive);
      animated("kpi-users-suspended", data.user_states.suspended);
      animated("kpi-users-unverified", data.user_states.unverified);
      animated("kpi-sims-active", data.sim_stats.new);
      animated("kpi-sims-swapped", data.sim_stats.swapped);
      animated("kpi-sims-suspended", data.sim_stats.suspended);
    }
    function renderCharts(data) {
      [
        loginChartInstance,
        authFailuresInstance,
        transactionTypeInstance,
        flaggedInstance,
      ].forEach((chart) => chart?.destroy());

      loginChartInstance = new Chart(loginChart, {
        type: "doughnut",
        data: {
          labels: ["Password", "TOTP", "WebAuthn"],
          datasets: [
            {
              label: "Login Methods",
              data: [
                data.login_methods.password,
                data.login_methods.totp,
                data.login_methods.webauthn,
              ],
              backgroundColor: ["#0d6efd", "#e83e8c", "#f0ad4e"],
            },
          ],
        },
        options: { responsive: true, maintainAspectRatio: false },
      });

      authFailuresInstance = new Chart(authFailuresChart, {
        type: "line",
        data: {
          labels: data.auth_failures.dates,
          datasets: [
            {
              label: "Auth Failures",
              data: data.auth_failures.counts,
              borderColor: "#dc3545",
              tension: 0.2,
            },
          ],
        },
        options: { responsive: true, maintainAspectRatio: false },
      });

      transactionTypeInstance = new Chart(transactionTypeChart, {
        type: "bar",
        data: {
          labels: ["User", "Agent", "Admin"],
          datasets: [
            {
              label: "Transactions by Actor",
              data: data.transaction_sources,
              backgroundColor: ["#007bff", "#28a745", "#ffc107"],
            },
          ],
        },
        options: { responsive: true, maintainAspectRatio: false },
      });

      flaggedInstance = new Chart(flaggedChart, {
        type: "pie",
        data: {
          labels: ["Clean", "Flagged"],
          datasets: [
            {
              data: [data.flagged.clean, data.flagged.flagged],
              backgroundColor: ["#6c757d", "#dc3545"],
            },
          ],
        },
        options: { responsive: true, maintainAspectRatio: false },
      });

      if (data.auth_failures.counts.every((c) => c === 0)) {
        Toastify({
          text: "No failed logins found in selected date range.",
          duration: 3000,
          backgroundColor: "#6c757d",
        }).showToast();
      }
      if (
        data.login_methods.password +
          data.login_methods.totp +
          data.login_methods.webauthn ===
        0
      ) {
        Toastify({
          text: "No successful logins found in selected date range.",
          duration: 3000,
          backgroundColor: "#6c757d",
        }).showToast();
      }
      if (data.transaction_sources.every((v) => v === 0)) {
        Toastify({
          text: "No transactions found in selected date range.",
          duration: 3000,
          backgroundColor: "#6c757d",
        }).showToast();
      }
      if (data.flagged.clean + data.flagged.flagged === 0) {
        Toastify({
          text: "No transactions flagged or clean in selected range.",
          duration: 3000,
          backgroundColor: "#6c757d",
        }).showToast();
      }
    }

    function renderHeatmap(data) {
      if (!heatmapContainer) return;
      const locationCounts = {};
      for (const log of data.logs || []) {
        let loc = log.location || "Unknown";
        if (loc.startsWith("{")) loc = "Map Point";
        locationCounts[loc] = (locationCounts[loc] || 0) + 1;
      }
      const entries = Object.entries(locationCounts).sort(
        (a, b) => b[1] - a[1]
      );
      heatmapContainer.innerHTML = `
      <ul class="list-group list-group-flush">
        ${entries
          .map(
            ([loc, count]) => `
          <li class="list-group-item d-flex justify-content-between align-items-center bg-dark text-white">
            ${loc}<span class="badge bg-danger rounded-pill">${count}</span>
          </li>`
          )
          .join("")}
      </ul>`;
    }

    function renderAnomalies(data) {
      if (!anomalyPanel) return;

      const failed = data.anomalies.multiple_failed_logins
        .map((u) => {
          const timestamp = u.last_failed_at
            ? new Date(u.last_failed_at).toLocaleString()
            : "recent";
          return `
      <a href="#" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" onclick="showOnlySection('user-auth-logs'); loadUserAuthLogsByUser(${u.user_id});">
        <div>
          <strong>User #${u.user_id}</strong><br><small class="text-muted">Last failed: ${timestamp}</small>
        </div>
        <span class="badge bg-danger">${u.count} failed</span>
      </a>
    `;
        })
        .join("");

      const flagged = data.anomalies.frequent_flagged_users
        .map((u) => {
          const timestamp = u.last_flagged_at
            ? new Date(u.last_flagged_at).toLocaleString()
            : "recent";
          return `
      <a href="#" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" onclick="showOnlySection('flagged-transactions-section'); filterFlaggedByUser(${u.user_id});">
        <div>
          <strong>User #${u.user_id}</strong><br><small class="text-muted">Last flagged: ${timestamp}</small>
        </div>
        <span class="badge bg-warning text-dark">${u.count} flagged</span>
      </a>
    `;
        })
        .join("");

      anomalyPanel.innerHTML = `
      <div class="card bg-dark text-white mb-3">
        <div class="card-header bg-danger"><i class="bi bi-shield-lock-fill me-2"></i> Multiple Failed Logins</div>
        <div class="card-body p-2"><ul class="list-group list-group-flush">${
          failed || '<li class="list-group-item">No anomalies</li>'
        }</ul></div>
      </div>
      <div class="card bg-dark text-white mb-3">
        <div class="card-header bg-warning text-dark"><i class="bi bi-exclamation-triangle-fill me-2"></i> Flagged Transactions</div>
        <div class="card-body p-2"><ul class="list-group list-group-flush">${
          flagged || '<li class="list-group-item">No anomalies</li>'
        }</ul></div>
      </div>`;
    }

    function showOnlySection(id) {
      document
        .querySelectorAll(".admin-section")
        .forEach((sec) => (sec.style.display = "none"));
      document.getElementById(id).style.display = "block";
    }

    async function loadMetrics(from = null, to = null) {
      try {
        document.body.classList.add("loading-overlay");

        const params = new URLSearchParams();
        if (from) params.append("from", from);
        if (to) params.append("to", to);

        const res = await fetch(`/api/admin/metrics?${params.toString()}`, {
          method: "GET",
          credentials: "include",
        });
        const data = await res.json();

        lastFetchedMetrics = data;
        updateKPIs(data);
        renderCharts(data);
        renderHeatmap(data);
        renderAnomalies(data);
      } catch (err) {
        console.error("Failed to load admin metrics:", err);
        Toastify({
          text: "❌ Failed to load metrics",
          duration: 4000,
          backgroundColor: "#dc3545",
        }).showToast();
      } finally {
        document.body.classList.remove("loading-overlay");
      }
    }

    const today = new Date();
    const lastWeek = new Date(today);
    lastWeek.setDate(today.getDate() - 7);
    await loadMetrics(
      lastWeek.toISOString().slice(0, 10),
      today.toISOString().slice(0, 10)
    );
  })();
});

function fetchHqBalance() {
  fetch("/admin/hq-balance", { credentials: "include" })
    .then((res) => res.json())
    .then((data) => {
      console.log("New balance:", data.balance); // ✅ Check this in browser devtools
      document.getElementById("hq-balance").innerText =
        data.balance?.toLocaleString() || "0";
    });
}

function fetchFloatHistory() {
  fetch("/admin/float-history", { credentials: "include" })
    .then((res) => res.json())
    .then((data) => {
      const tbody = document.getElementById("float-transfer-history");
      tbody.innerHTML = "";
      if (data.transfers?.length) {
        data.transfers.forEach((tx) => {
          const row = `<tr>
            <td>${new Date(tx.timestamp).toLocaleString()}</td>
            <td>${tx.agent_name}</td>
            <td>${tx.agent_mobile}</td>
            <td>${parseFloat(tx.amount).toLocaleString()} RWF</td>
          </tr>`;
          tbody.innerHTML += row;
        });
      } else {
        tbody.innerHTML =
          '<tr><td colspan="4" class="text-center">No transfers yet.</td></tr>';
      }
    });
}

function bindFundAgentForm() {
  const fundForm = document.getElementById("fund-agent-form");
  if (fundForm && !fundForm.dataset.bound) {
    fundForm.dataset.bound = "true";

    fundForm.addEventListener("submit", async function (e) {
      e.preventDefault();

      const mobile = document.getElementById("agent-mobile").value.trim();
      const amount = parseFloat(document.getElementById("float-amount").value);
      const device_info = getDeviceInfo();
      const location = await getLocation();

      if (!mobile || isNaN(amount) || amount <= 0) {
        document.getElementById("fund-result").innerHTML =
          '<p class="text-danger">❌ Invalid input.</p>';
        return;
      }

      fetch("/admin/fund-agent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          agent_mobile: mobile,
          amount,
          device_info,
          location,
        }),
      })
        .then(async (res) => {
          if (!res.ok) {
            const text = await res.text();
            throw new Error(`Server error: ${text}`);
          }
          return res.json();
        })
        .then((data) => {
          document.getElementById("fund-result").innerHTML = data.message
            ? `<p class='text-success'>${data.message}</p>`
            : `<p class='text-danger'>${data.detail || data.error || "Funding failed."}</p>`;

          fetchHqBalance();       
          fetchFloatHistory();
          fundForm.reset();       
        })
        .catch((err) => {
          console.error(err);
          document.getElementById(
            "fund-result"
          ).innerHTML = `<p class="text-danger">❌ ${err.message}</p>`;
        });
    });
  }
}

// // -------------------------------
// // Funcction for Tenant Management
// // -------------------------------

function bindRegisterTenantForm() {
  const tenantForm = document.getElementById("register-tenant-form");

  if (tenantForm && !tenantForm.dataset.bound) {
    tenantForm.dataset.bound = "true";

    tenantForm.addEventListener("submit", async function (e) {
      e.preventDefault();

      const name = document.getElementById("tenant-name").value.trim();
      const contactEmail = document
        .getElementById("tenant-contact")
        .value.trim();
      const apiKey = document.getElementById("tenant-api-key").value.trim();
      const device_info = getDeviceInfo();
      const location = await getLocation();

      const createAdmin = document.getElementById("toggle-admin-user")?.checked;
      let admin_user = null;

      if (createAdmin) {
        const mobile = document.getElementById("admin-mobile").value.trim();
        const firstname = document
          .getElementById("admin-firstname")
          .value.trim();
        const email = document.getElementById("admin-email").value.trim();
        const password = document.getElementById("admin-password").value;

        if (!mobile || !firstname || !email || !password) {
          Toastify({
            text: "❌ All admin fields are required when toggled ON.",
            duration: 5000,
            gravity: "top",
            position: "right",
            backgroundColor: "#dc3545",
          }).showToast();
          return;
        }

        admin_user = {
          mobile_number: mobile,
          first_name: firstname,
          email,
          password,
        };
      }

      if (!name || !contactEmail) {
        Toastify({
          text: "❌ Name and contact email are required.",
          duration: 4000,
          gravity: "top",
          position: "right",
          backgroundColor: "#dc3545",
        }).showToast();
        return;
      }

      const isValidEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(contactEmail);
      if (!isValidEmail) {
        Toastify({
          text: "❌ Please enter a valid email address.",
          duration: 4000,
          gravity: "top",
          position: "right",
          backgroundColor: "#dc3545",
        }).showToast();
        return;
      }

      fetch("/admin/register-tenant", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          name,
          api_key: apiKey || null,
          contact_email: contactEmail,
          device_info,
          location,
          admin_user, // optional
        }),
      })
        .then(async (res) => {
          const data = await res.json();
          if (!res.ok) throw new Error(data.detail || data.error || "Request failed");

          const toastText = data.email_sent
            ? `✅ Tenant registered — API Key sent to ${contactEmail}`
            : `⚠️ Tenant registered, but email delivery failed.`;

          const toastColor = data.email_sent ? "#198754" : "#ffc107";

          Toastify({
            text: toastText,
            duration: 5000,
            gravity: "top",
            position: "right",
            backgroundColor: toastColor,
          }).showToast();

          document.getElementById("register-tenant-result").innerHTML = `
            <div class="alert alert-light border text-start">
              <strong>Tenant ID:</strong> ${data.tenant_id}<br>
              <strong>API Key:</strong> <code>${data.api_key}</code>
            </div>
          `;

          //  Reset form and UI AFTER everything is rendered
          e.target.reset();

          const toggleSwitch = document.getElementById("toggle-admin-user");
          const adminFields = document.getElementById("admin-user-fields");

          if (toggleSwitch) toggleSwitch.checked = false;
          if (adminFields) adminFields.classList.add("d-none");

          if (typeof loadTenants === "function") {
            loadTenants();
          }
        })
        .catch((err) => {
          Toastify({
            text: `❌ ${err.message}`,
            duration: 5000,
            gravity: "top",
            position: "right",
            backgroundColor: "#dc3545",
          }).showToast();
        });
    });
  }
}

let fullTenantList = [];

async function loadTenants() {
  const tableBody = document.getElementById("tenant-table-body");

  try {
    const res = await fetch("/admin/tenants", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
    });

    const data = await res.json();

    if (!Array.isArray(data)) {
      tableBody.innerHTML = `
        <tr><td colspan="7" class="text-center text-danger">
          Failed to load tenants (unexpected response)
        </td></tr>`;
      return;
    }

    if (data.length === 0) {
      tableBody.innerHTML =
        "<tr><td colspan='7' class='text-center'>No tenants available.</td></tr>";
      return;
    }

    fullTenantList = data; //  Cache for filters
    tableBody.innerHTML = ""; // Clear table before rendering
    fullTenantList.forEach(renderTenantRow);
  } catch (error) {
    console.error("❌ Error loading tenants:", error);
    tableBody.innerHTML =
      "<tr><td colspan='7' class='text-center text-danger'>Error loading tenants</td></tr>";
  }
}

// Render each row (used in loadTenants + filtering)
function renderTenantRow(tenant) {
  const tableBody = document.getElementById("tenant-table-body");
  const row = document.createElement("tr");

  const statusBadge = tenant.is_active
    ? `<span class="badge bg-success">Active</span>`
    : `<span class="badge bg-danger">Suspended</span>`;

  const rotateKeyButton = tenant.is_active
    ? `<button class="btn btn-sm rotate-btn" onclick="rotateApiKey(${tenant.id}, '${tenant.name}', '${tenant.contact_email}')">
         <i class="fas fa-sync-alt"></i> Rotate Key
       </button>`
    : "";

  const resetTrustButton = !tenant.is_active
    ? `<button class="btn btn-sm reset-trust-btn" onclick="resetTrustScore(${tenant.id}, '${tenant.name}')">
         <i class="fas fa-undo-alt"></i> Reset Trust
       </button>`
    : "";

  const abuseScore = (tenant.api_score !== undefined && tenant.api_score !== null)
    ? tenant.api_score.toFixed(2)
    : "0.00";

  const abuseBadge = tenant.api_score >= 0.7
    ? `<span class="badge bg-danger">${abuseScore}</span>`
    : `<span class="badge bg-secondary">${abuseScore}</span>`;

  const viewButton = `
    <button class="btn btn-sm view-btn" onclick="viewTenantDetails(${tenant.id})">
      <i class="fas fa-eye"></i> View
    </button>`;

  row.innerHTML = `
    <td>${tenant.name}</td>
    <td>${tenant.contact_email}</td>
    <td>${tenant.plan.charAt(0).toUpperCase() + tenant.plan.slice(1)}</td>
    <td>${statusBadge}</td>
    <td>${tenant.created_at}</td>
    <td>${tenant.last_api_access || "Never"}</td>
    <td>${abuseBadge}</td>
    <td class="action-buttons">
      <div class="dropdown dropup">
        <button class="btn btn-sm dropdown-toggle" onclick="toggleDropdown(this)">
          Actions ▼
        </button>
        <div class="dropdown-menu">
          <button class="btn btn-sm toggle-status-btn" onclick="toggleTenantStatus(${tenant.id})">
            <i class="fas fa-toggle-on"></i> ${tenant.is_active ? "Suspend" : "Enable"}
          </button>
          <button class="btn btn-sm edit-btn" onclick="editTenant(${tenant.id}, '${tenant.contact_email}', '${tenant.plan}')">
            <i class="fas fa-edit"></i> Edit
          </button>
          ${rotateKeyButton}
          ${resetTrustButton}
          ${viewButton}
          <button class="btn btn-sm delete-btn" onclick="deleteTenant(${tenant.id})">
            <i class="fas fa-trash-alt"></i> Delete
          </button>
        </div>
      </div>
    </td>
  `;

  tableBody.appendChild(row);
}

function filterTenants(filterType) {
  const tableBody = document.getElementById("tenant-table-body");
  tableBody.innerHTML = ""; // Clear before rendering

  let filtered = [];

  const now = new Date();
  const sevenDaysAgo = new Date(now.setDate(now.getDate() - 7));

  switch (filterType) {
    case "active":
      filtered = fullTenantList.filter((t) => t.is_active);
      break;
    case "suspended":
      filtered = fullTenantList.filter((t) => !t.is_active);
      break;
    case "recent":
      filtered = fullTenantList.filter((t) => {
        if (!t.last_api_access) return false;
        const accessTime = new Date(t.last_api_access);
        return accessTime >= sevenDaysAgo;
      });
      break;
    case "all":
    default:
      filtered = fullTenantList;
      break;
  }

  if (filtered.length === 0) {
    tableBody.innerHTML = `
      <tr><td colspan="7" class="text-center text-muted">
        No tenants found for this filter.
      </td></tr>`;
  } else {
    filtered.forEach(renderTenantRow);
  }
}


async function toggleTenantStatus(id) {
  const res = await fetch(`/admin/toggle-tenant/${id}`, {
    method: "POST",
    credentials: "include"
  });
  const result = await res.json();

  Toastify({
    text: result.message || "Status updated",
    duration: 4000,
    gravity: "top",
    position: "right",
    backgroundColor: "#198754",
  }).showToast();

  loadTenants(); // Refresh
}

async function deleteTenant(id) {
  if (!confirm("Are you sure you want to delete this tenant?")) return;

  const res = await fetch(`/admin/delete-tenant/${id}`, {
    method: "DELETE",
    credentials: "include"
  });

  const result = await res.json();

  Toastify({
    text: result.message || "Tenant deleted",
    duration: 4000,
    gravity: "top",
    position: "right",
    backgroundColor: "#dc3545",
  }).showToast();

  loadTenants(); // Refresh
}

function editTenant(id, email, plan) {
  document.getElementById("edit-tenant-id").value = id;
  document.getElementById("edit-tenant-email").value = email;
  document.getElementById("edit-tenant-plan").value = plan.toLowerCase(); // normalize casing
  const modal = new bootstrap.Modal(document.getElementById("editTenantModal"));
  modal.show();
}

document.getElementById("edit-tenant-form").addEventListener("submit", function (e) {
  e.preventDefault();

  const tenantId = document.getElementById("edit-tenant-id").value;
  const contactEmail = document.getElementById("edit-tenant-email").value.trim();
  const plan = document.getElementById("edit-tenant-plan").value.trim().toLowerCase();

  if (!["basic", "premium", "enterprise"].includes(plan)) {
    Toastify({
      text: "❌ Invalid plan selected. Choose basic, premium, or enterprise.",
      duration: 4000,
      backgroundColor: "#dc3545",
    }).showToast();
    return;
  }

  fetch(`/admin/update-tenant/${tenantId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify({ contact_email: contactEmail, plan }),
  })
    .then((res) => res.json())
    .then((data) => {
      Toastify({
        text: `✅ ${data.message}`,
        duration: 4000,
        gravity: "top",
        position: "right",
        backgroundColor: "#198754",
      }).showToast();

      bootstrap.Modal.getInstance(document.getElementById("editTenantModal")).hide();
      loadTenants(); // Refresh updated view
    })
    .catch((err) => {
      console.error("❌ Edit failed:", err);
      Toastify({
        text: `❌ Failed to update tenant.`,
        duration: 4000,
        gravity: "top",
        position: "right",
        backgroundColor: "#dc3545",
      }).showToast();
    });
});

function rotateApiKey(tenantId, tenantName, contactEmail) {
  if (!confirm(`🔁 Are you sure you want to rotate the API Key for ${tenantName}?`)) {
    return;
  }

  fetch(`/admin/rotate-api-key/${tenantId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
  })
    .then(async (res) => {
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.error || "Rotation failed");

      Toastify({
        text: `✅ API Key rotated for ${tenantName}.`,
        duration: 4000,
        gravity: "top",
        position: "right",
        backgroundColor: "#198754",
      }).showToast();

      loadTenants(); // reloads the table
    })
    .catch((err) => {
      console.error("❌ Rotation failed:", err);
      Toastify({
        text: `❌ ${err.message}`,
        duration: 4000,
        gravity: "top",
        position: "right",
        backgroundColor: "#dc3545",
      }).showToast();
    });
}

function resetTrustScore(tenantId, tenantName) {
  if (!confirm(`Are you sure you want to reset trust score for ${tenantName}?`)) return;

  fetch(`/admin/reset-trust-score/${tenantId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
  })
    .then((res) => res.json())
    .then((data) => {
      alert(data.message || "Trust score reset.");
      loadTenants(); // refresh
    })
    .catch((err) => {
      console.error("❌ Failed to reset trust score:", err);
      alert("Failed to reset trust score.");
    });
}

//  Device Info Function
function getDeviceInfo() {
  return {
    platform: navigator.platform,
    userAgent: navigator.userAgent,
    screen: {
      width: window.screen.width,
      height: window.screen.height,
    },
  };
}

function viewTenantDetails(id) {
  fetch(`/admin/tenant-details/${id}`)
    .then(res => res.json())
    .then(data => {
      const modalBody = document.getElementById("tenant-details-body");
      modalBody.innerHTML = `
        <p><strong>Name:</strong> ${data.name}</p>
        <p><strong>Email:</strong> ${data.contact_email}</p>
        <p><strong>Plan:</strong> ${data.plan}</p>
        <p><strong>Status:</strong> ${data.is_active ? "Active" : "Suspended"}</p>
        <p><strong>API Key Expires:</strong> ${data.api_key_expires_at}</p>
        <p><strong>Created At:</strong> ${data.created_at}</p>
        <p><strong>Last Access:</strong> ${data.last_api_access}</p>
        <p><strong>Request Count:</strong> ${data.api_request_count}</p>
        <p><strong>Error Count:</strong> ${data.api_error_count}</p>
        <p><strong>Trust Score:</strong> ${data.api_score}</p>
      `;
      const modal = new bootstrap.Modal(document.getElementById("tenantDetailsModal"));
      modal.show();
    })
    .catch(err => {
      console.error("Failed to load tenant details", err);
      alert("Error fetching details");
    });
}


//  Location Info Function
async function getLocation() {
  return new Promise((resolve) => {
    if (!navigator.geolocation) {
      return resolve("Location not supported");
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        });
      },
      () => resolve("Location denied")
    );
  });
}

// ---------------------------
// Funcction to load all transactions
// ---------------------------
//
function loadAllTransactions() {
  fetch("/admin/all-transactions", {
    method: "GET",
    credentials: "include",
  })
    .then((res) => res.json())
    .then((data) => {
      const tbody = document.getElementById("all-transactions-body");
      tbody.innerHTML = "";

      if (!data.transactions.length) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center">No transactions found.</td></tr>`;
        return;
      }

      data.transactions.forEach((tx) => {
        const canReverse =
          tx.transaction_type === "transfer" && tx.status === "completed";

        const reverseBtn = canReverse
          ? `<button class="btn btn-sm btn-danger" onclick="reverseTransfer(${tx.id})">
               <i class="fas fa-undo"></i> Reverse
             </button>`
          : "";

        const row = `
          <tr>
            <td>${tx.id}</td>
            <td>${tx.user_name}</td>
            <td>${tx.transaction_type}</td>
            <td>${tx.amount}</td>
            <td>${tx.status}</td>
            <td>${tx.timestamp}</td>
            <td>${reverseBtn}</td>
          </tr>
        `;
        tbody.innerHTML += row;
      });
    })
    .catch((err) => {
      console.error("❌ Failed to load transactions:", err);
      alert("Could not load all transactions.");
    });
}
// Binding All transactions function
document
  .getElementById("show-all-transactions")
  .addEventListener("click", () => {
    document
      .querySelectorAll(".admin-section")
      .forEach((s) => (s.style.display = "none"));
    document.getElementById("all-transactions-section").style.display = "block";
    loadAllTransactions();
  });

// ---------------------------
// Function to reverse transfers
// ---------------------------
function reverseTransfer(transactionId) {
  if (!confirm("⚠️ Are you sure you want to reverse this transfer?")) return;

  fetch(`/admin/reverse-transfer/${transactionId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.message) {
        alert(data.message);
        loadAllTransactions();
        loadRealTimeLogs?.();
      } else {
        alert(data.detail || data.error || "Failed to reverse transfer.");
      }
    })
    .catch((err) => {
      console.error("❌ Error reversing transfer:", err);
      alert("❌ Something went wrong while reversing the transfer.");
    });
}

//  Expose globally
window.reverseTransfer = reverseTransfer;

//  Function to fetch and display users in Admin Dashboard
function fetchUsersForAdmin() {
  const userList = document.querySelector("#admin-user-list tbody");
  userList.innerHTML =
    "<tr><td colspan='6' class='text-center'>Loading users...</td></tr>";

  fetch("/admin/users", {
    method: "GET",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
  })
    .then((res) => res.json())
    .then((data) => {

      //  Validate that the response is an array
      if (!Array.isArray(data)) {
        userList.innerHTML = `
          <tr><td colspan="6" class="text-center text-danger">
            Failed to load users (unexpected response)
          </td></tr>`;
        console.error("❌ Expected array but got:", data);
        return;
      }

      const users = data;
      userList.innerHTML = "";

      if (users.length === 0) {
        userList.innerHTML =
          "<tr><td colspan='6' class='text-center'>No users available.</td></tr>";
        return;
      }

      users.forEach((user) => {
        const row = document.createElement("tr");

        const rowClass = user.is_locked ? "locked-user-row" : "";
        const lockedUntil = user.locked_until
          ? new Date(user.locked_until).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })
          : null;

        const lockBadge = user.is_locked
          ? `<div>
               <span class="badge bg-danger">🔒 Locked</span><br>
               <small class="text-danger">Until ${lockedUntil}</small>
             </div>`
          : "";

        const unlockButton = user.is_locked
          ? `<button class="btn btn-sm unlock-btn" onclick="unlockUser('${user.id}')">
               <i class="fas fa-unlock-alt"></i> Unlock
             </button>`
          : "";

        row.className = rowClass;

        row.innerHTML = `
          <td>${user.id}</td>
          <td>${user.name || "N/A"} ${lockBadge}</td>
          <td>${user.mobile_number || "N/A"}</td>
          <td>${user.email || "N/A"}</td>
          <td>${user.role || "N/A"}</td>
          <td class="action-buttons">
              <div class="dropdown dropup">
                  <button class="btn btn-sm dropdown-toggle" onclick="toggleDropdown(this)" style="background-color: var(--brand-blue); color: white;">
                      Actions ▼
                  </button>
                  <div class="dropdown-menu">
                      <button class="btn btn-sm view-btn" onclick="viewUser('${
                        user.id
                      }')">
                          <i class="fas fa-eye"></i> View
                      </button>
                      <button class="btn btn-sm activate-btn" onclick="assignUserRole('${
                        user.id
                      }', 'Admin')">
                          <i class="fas fa-user-tag"></i> Assign Role
                      </button>
                      <button class="btn btn-sm verify-btn" onclick="verifyUser('${
                        user.id
                      }')" ${user.identity_verified ? "disabled" : ""}>
                          <i class="fas fa-check-circle"></i> ${
                            user.identity_verified ? "Verified" : "Verify"
                          }
                      </button>
                      <button class="btn btn-sm suspend-btn" onclick="suspendUser('${
                        user.id
                      }')">
                          <i class="fas fa-user-slash"></i> Suspend
                      </button>
                      <button class="btn btn-sm delete-btn" onclick="deleteUser('${
                        user.id
                      }')">
                          <i class="fas fa-trash-alt"></i> Delete
                      </button>
                      <button class="btn btn-sm edit-btn" onclick="editUser('${
                        user.id
                      }')">
                          <i class="fas fa-edit"></i> Edit
                      </button>
                      ${unlockButton}
                  </div>
              </div>
          </td>
        `;
        userList.appendChild(row);
      });
    })
    .catch((error) => {
      console.error("❌ Error fetching users:", error);
      userList.innerHTML =
        "<tr><td colspan='6' class='text-center text-danger'>Error loading users</td></tr>";
    });
}

//  Function to toggle dropdown and adjust position
window.toggleDropdown = function (triggerButton) {
  console.log("✅ Dropdown Clicked!");

  const dropdown = triggerButton.nextElementSibling;

  if (!dropdown) {
    console.error("❌ Dropdown menu not found!");
    return;
  }

  //  Close all other dropdowns before opening the clicked one
  document.querySelectorAll(".dropdown-menu").forEach((menu) => {
    if (menu !== dropdown) {
      menu.style.display = "none";
    }
  });

  //  Toggle the visibility of the clicked dropdown
  dropdown.style.display =
    dropdown.style.display === "block" ? "none" : "block";

  //  Adjust positioning dynamically (drop up/down based on space)
  const rect = triggerButton.getBoundingClientRect();
  const dropdownHeight = dropdown.scrollHeight;
  const viewportHeight = window.innerHeight;
  const spaceBelow = viewportHeight - rect.bottom;
  const spaceAbove = rect.top;

  if (spaceBelow < dropdownHeight && spaceAbove > dropdownHeight) {
    dropdown.style.bottom = "100%";
    dropdown.style.top = "auto";
  } else {
    dropdown.style.top = "100%";
    dropdown.style.bottom = "auto";
  }
};

//  Close dropdowns when clicking outside
document.addEventListener("click", function (event) {
  if (!event.target.closest(".dropdown")) {
    document.querySelectorAll(".dropdown-menu").forEach((dropdown) => {
      dropdown.style.display = "none";
    });
  }
});

//  Ensure dropdowns start hidden on page load
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".dropdown-menu").forEach((menu) => {
    menu.style.display = "none";
  });
});

//  Make Modal Draggable
function makeModalDraggable() {
  const modal = document.getElementById("adminDetailsModal");
  const header = document.querySelector("#adminDetailsModal .modal-header");
  let offsetX,
    offsetY,
    isDragging = false;

  if (!header) return;

  header.addEventListener("mousedown", (e) => {
    isDragging = true;
    offsetX = e.clientX - modal.getBoundingClientRect().left;
    offsetY = e.clientY - modal.getBoundingClientRect().top;
    modal.style.position = "absolute"; 
  });

  document.addEventListener("mousemove", (e) => {
    if (!isDragging) return;
    modal.style.left = `${e.clientX - offsetX}px`;
    modal.style.top = `${e.clientY - offsetY}px`;
  });

  document.addEventListener("mouseup", () => {
    isDragging = false;
  });
}

//  Load users when the page is ready
document.addEventListener("DOMContentLoaded", fetchUsersForAdmin);

//  View User Info function
function viewUser(userId) {
  fetch(`/admin/view_user/${userId}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error || data.detail) {
        alert(`❌ Error: ${data.detail || data.error}`);
        return;
      }

      //  Remove existing content before adding new content
      const modalContent = document.querySelector(
        "#userDetailsModal .modal-content"
      );
      modalContent.innerHTML = "";

      //  Add formatted data WITHOUT extra space
      modalContent.innerHTML = `
          <div class="modal-header">
              <h2 style="color: #4CAF50; margin-bottom: 5px;">User Details</h2>
              <span id="closeUserDetails" class="close">&times;</span>
          </div>
          <div class="modal-body">
              <p><strong>ID:</strong> ${data.id}</p>
              <p><strong>Full Name:</strong> ${data.name}</p>
              <p><strong>Mobile Number:</strong> ${data.mobile_number}</p>
              <p><strong>Email:</strong> ${data.email}</p>
              <p><strong>Role:</strong> ${data.role}</p>
              <p><strong>Registration Date:</strong> ${data.registration_date}</p>
          </div>
      `;

      //  Show the modal
      const modal = document.getElementById("userDetailsModal");
      modal.style.display = "block";

      //  Attach the close event again (since we replaced modal content)
      document
        .getElementById("closeUserDetails")
        .addEventListener("click", function () {
          modal.style.display = "none";
        });

      //  Ensure modal resizes properly
      modal.style.height = "auto";
      modal.style.minHeight = "auto";

      //  Make the modal draggable
      makeModalDraggable();
    })
    .catch((error) => console.error("❌ Error fetching user details:", error));
}

// ---------------------------
// Admin User Actions
// ---------------------------

function assignUserRole(userId) {
  let newRole = prompt("Enter new role (admin, agent, user):");

  if (!newRole) {
    alert("❌ Role assignment cancelled.");
    return;
  }

  //  Convert role name to role ID
  const roleMapping = {
    admin: 1,
    agent: 2,
    user: 3,
  };

  const roleId = roleMapping[newRole.toLowerCase()];

  if (!roleId) {
    alert("❌ Invalid role. Please enter 'admin', 'agent', or 'user'.");
    return;
  }

  fetch("/admin/assign_role", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify({ user_id: userId, role_id: roleId }), // Send role ID, not string
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error || data.detail) {
        alert("❌ Error: " + (data.detail || data.error));
      } else {
        alert(`✅ Role updated to ${newRole} successfully!`);
        fetchUsersForAdmin(); // Refresh the list
      }
    })
    .catch((error) => console.error("❌ Error updating role:", error));
}

//  Ensure Assign Role button triggers the prompt-based role change
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".assign-role").forEach((button) => {
    button.addEventListener("click", function () {
      assignUserRole(this.dataset.userId);
    });
  });
});

// -------------------------
// Suspend the user
//--------------------------

function suspendUser(userId) {
  if (
    !confirm(
      "Are you sure you want to suspend this user? Their account will be disabled and marked for deletion."
    )
  ) {
    return;
  }

  fetch(`/admin/suspend_user/${userId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    credentials: "include", // Ensure cookies are included for authentication
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error || data.detail) {
        alert("Error: " + (data.detail || data.error));
      } else {
        alert(data.message); // Correctly display the returned message
        fetchUsersForAdmin(); // Refresh the user list
      }
    })
    .catch((error) => console.error("Error suspending user:", error));
}

// verify the user

function verifyUser(userId) {
  if (!confirm("Are you sure you want to verify this user?")) {
    return;
  }

  fetch(`/admin/verify_user/${userId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    credentials: "include", // Ensures authentication cookies are sent
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error || data.detail) {
        alert("Error: " + (data.detail || data.error));
      } else {
        alert("User has been verified and activated.");
        fetchUsersForAdmin(); // Refresh the user list
      }
    })
    .catch((error) => console.error("Error verifying user:", error));
}

// -------------------------
// permanently Delete the user
//--------------------------

function deleteUser(userId) {
  if (
    !confirm(
      "Are you sure you want to permanently delete this user? This action CANNOT be undone!"
    )
  ) {
    return;
  }

  fetch(`/admin/delete_user/${userId}`, {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    credentials: "include", // Include authentication cookies
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error || data.detail) {
        alert("Error: " + (data.detail || data.error));
        return;
      }
      alert("User permanently deleted.");
      fetchUsersForAdmin(); // Refresh the user list
    })
    .catch((error) => console.error("Error deleting user:", error));
}

// -------------------------
// Edit the user
//--------------------------

function editUser(userId) {
  fetch(`/admin/edit_user/${userId}`, {
    method: "GET",
    credentials: "include",
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error || data.detail) {
        alert("Error loading user: " + (data.detail || data.error));
        return;
      }
      openEditUserModal(data);
    })
    .catch((error) => console.error("Error loading user:", error));
}

function openEditUserModal(user) {
  const modal = document.getElementById("edit-user-modal");
  const backdrop = document.getElementById("edit-user-backdrop");
  if (!modal || !backdrop) return;

  document.getElementById("edit-user-id").value = user.id;
  document.getElementById("edit-first-name").value = user.first_name || "";
  document.getElementById("edit-last-name").value = user.last_name || "";
  document.getElementById("edit-email").value = user.email || "";
  document.getElementById("edit-mobile-number").value = user.mobile_number || "";

  backdrop.style.display = "block";
  modal.style.display = "block";
}

function closeEditUserModal() {
  const modal = document.getElementById("edit-user-modal");
  const backdrop = document.getElementById("edit-user-backdrop");
  if (!modal || !backdrop) return;
  modal.style.display = "none";
  backdrop.style.display = "none";
}

document.addEventListener("DOMContentLoaded", () => {
  const closeBtn = document.getElementById("close-edit-user-btn");
  const form = document.getElementById("edit-user-form");
  const backdrop = document.getElementById("edit-user-backdrop");

  closeBtn?.addEventListener("click", closeEditUserModal);
  backdrop?.addEventListener("click", closeEditUserModal);

  form?.addEventListener("submit", (e) => {
    e.preventDefault();

    const userId = document.getElementById("edit-user-id").value;
    const firstName = document.getElementById("edit-first-name").value.trim();
    const lastName = document.getElementById("edit-last-name").value.trim();
    const email = document.getElementById("edit-email").value.trim();
    const mobileNumber = document.getElementById("edit-mobile-number").value.trim();

    if (!firstName || !email || !mobileNumber) {
      alert("First name, email, and mobile number are required.");
      return;
    }

    const payload = {
      first_name: firstName,
      last_name: lastName,
      email: email,
      mobile_number: mobileNumber,
    };

    fetch(`/admin/edit_user/${userId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(payload),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error || data.detail) {
          alert("Error updating user: " + (data.detail || data.error));
          return;
        }
        alert(data.message || "User updated successfully!");
        closeEditUserModal();
        fetchUsersForAdmin();
      })
      .catch((error) => console.error("Error editing user:", error));
  });
});

// ------------------------------
// Unlock user account
// ------------------------------
function unlockUser(userId) {
  if (!confirm("Are you sure you want to unlock this user?")) return;

  fetch(`/admin/unlock-user/${userId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
  })
    .then((res) => res.json())
    .then((data) => {
      alert(data.message || "User unlocked.");
      // Optionally refresh user list
    })
    .catch((err) => {
      alert("Error unlocking user.");
      console.error(err);
    });
}

// ------------------------------
// Check for flagged Transactions
// ------------------------------
function loadFlaggedTransactions() {
  fetch("/admin/flagged-transactions")
    .then((res) => res.json())
    .then((data) => {
      const tbody = document.getElementById("flagged-transactions");
      tbody.innerHTML = "";
      if (!data.length) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted">No flagged transactions</td></tr>`;
        return;
      }
      data.forEach((tx) => {
        const row = `
          <tr>
            <td>${tx.user}</td>
            <td>${tx.amount}</td>
            <td>${tx.type}</td>
            <td>${tx.risk_score}</td>
            <td>${tx.status}</td>
            <td>
              <button class="btn btn-sm btn-outline-danger">Block</button>
              <button class="btn btn-sm btn-outline-success">Approve</button>
            </td>
          </tr>
        `;
        tbody.innerHTML += row;
      });
    });
}

// ------------------------------
// System Real time logs
// ------------------------------
function loadRealTimeLogs() {
  fetch("/admin/real-time-logs")
    .then((res) => res.json())
    .then((data) => {
      const container = document.getElementById("real-time-logs-container");
      container.innerHTML = "";
      if (!data.length) {
        container.innerHTML = `<p class="text-muted text-center">No alerts yet.</p>`;
        return;
      }
      data.forEach((log) => {
        const card = `
          <div class="alert alert-warning mb-2">
            <strong>${log.timestamp}</strong> - <b>${log.user}</b><br/>
            <code>${log.action}</code><br/>
            Location: ${log.location} | IP: ${log.ip} | Device: ${log.device}
          </div>
        `;
        container.innerHTML += card;
      });
    });
}

// ---------------------------
// User Authentication logs Function
// ---------------------------
function loadUserAuthLogs(filter = null) {
  fetch("/admin/user-auth-logs")
    .then((res) => res.json())
    .then((data) => {
      const tbody = document.getElementById("user-auth-logs-container");
      tbody.innerHTML = "";

      const logs =
        filter === "failed"
          ? data.filter((log) => log.status.toLowerCase() === "failed")
          : data;

      if (!logs.length) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-center text-muted">No logs yet</td></tr>`;
        return;
      }

      logs.forEach((log) => {
        const row = `
          <tr>
            <td>${log.user}</td>
            <td>${log.method}</td>
            <td class="${
              log.status === "success" ? "text-success" : "text-danger"
            }">${log.status}</td>
            <td>${log.timestamp}</td>
            <td>${log.ip}</td>
            <td>${log.device}</td>
            <td>${log.location}</td>
            <td>${log.fails}</td>
          </tr>
        `;
        tbody.innerHTML += row;
      });
    });
}

// ---------------------------
// Search Users Function
// ---------------------------
function searchUsers(searchTerm) {
  if (!searchTerm) {
    alert("Please enter a search term.");
    return;
  }

  const rows = document.querySelectorAll("#admin-user-list tr");
  let found = false;
  rows.forEach((row) => {
    const rowText = row.textContent.toLowerCase();
    if (rowText.indexOf(searchTerm.toLowerCase()) !== -1) {
      row.style.display = "";
      found = true;
    } else {
      row.style.display = "none";
    }
  });

  if (!found) {
    alert("No user found with the provided search term.");
  }
}

/// ---------------------------
// Bind All Events on DOMContentLoaded
// ---------------------------
document.addEventListener("DOMContentLoaded", function () {
  // Bind search events
  const searchBtn = document.getElementById("search-user-btn");
  const searchInput = document.getElementById("user-search");
  if (searchBtn && searchInput) {
    searchBtn.addEventListener("click", function () {
      const searchTerm = searchInput.value.trim();
      searchUsers(searchTerm);
    });
    searchInput.addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        const searchTerm = searchInput.value.trim();
        searchUsers(searchTerm);
      }
    });
  }

  // ---------------------------
  //  Open Add User Modal
  // ---------------------------
  const addUserBtn = document.getElementById("add-user-btn");
  if (addUserBtn) {
    addUserBtn.addEventListener("click", function () {

      const modalEl = document.getElementById("addUserModal");
      if (!modalEl) {
        console.error("❌ Modal element with id 'addUserModal' not found.");
        return;
      }

      //  Bootstrap 5 API to show the modal
      const addUserModal = new bootstrap.Modal(modalEl);
      addUserModal.show();

      //  Ensure fetchGeneratedSIM() only runs if function exists
      if (typeof fetchGeneratedSIM === "function") {
        fetchGeneratedSIM();
      } else {
        console.error("❌ fetchGeneratedSIM() function is not defined!");
      }
    });
  } else {
    console.error(
      "❌ Add User button (id 'add-user-btn') not found in the DOM."
    );
  }

  // ---------------------------
  //  Handle Manual SIM Refresh
  // ---------------------------
  const genBtn = document.getElementById("generate-mobile-btn");
  if (genBtn) {
    genBtn.addEventListener("click", function () {
      fetchGeneratedSIM();
    });
  }

  // ---------------------------
  //  Fetch Auto-Generated SIM Details & Update Input Fields
  // ---------------------------
  function fetchGeneratedSIM() {
    fetch("/admin/generate_sim", { method: "GET", credentials: "include" })
      .then((response) => response.json())
      .then((data) => {
        if (data.error || data.detail) {
          alert("❌ Error fetching SIM details: " + (data.detail || data.error));
        } else {
          //  Update the input fields with generated values
          document.getElementById("generated-mobile").value =
            data.mobile_number;
          document.getElementById("generated-iccid").value = data.iccid;

          //  Store values globally for form submission
          window.generatedSIM = {
            mobile_number: data.mobile_number,
            iccid: data.iccid,
          };
        }
      })
      .catch((error) => {
        console.error("❌ Error generating SIM:", error);
        alert("❌ Unexpected error occurred while generating SIM.");
      });
  }

  // ---------------------------
  // Admin: Add New User Form Submission (Modal)
  // ---------------------------
  const addUserForm = document.getElementById("add-user-form");
  if (addUserForm) {
    addUserForm.addEventListener("submit", async function (e) {
      e.preventDefault();

      //  Get values from the form fields (not from background storage)
      const firstName = document.getElementById("add-first-name").value.trim();
      const lastName = document.getElementById("add-last-name").value.trim();
      const email = document.getElementById("add-email").value.trim();
      const country = document.getElementById("add-country").value.trim();
      const password = document.getElementById("add-password").value.trim();
      const mobileNumber = document
        .getElementById("generated-mobile")
        .value.trim(); //  Use the visible input field
      const iccid = document.getElementById("generated-iccid").value.trim();

      if (
        !firstName ||
        !email ||
        !country ||
        !password ||
        !mobileNumber ||
        !iccid
      ) {
        alert("❌ Please fill in all required fields.");
        return;
      }

      //  Build user payload with displayed values
      const payload = {
        first_name: firstName,
        last_name: lastName,
        email: email,
        password: password,
        country: country,
        mobile_number: mobileNumber,
        iccid: iccid, //  
      };

      //  Step 3: Send registration request
      const registerResponse = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(payload),
      });

      const registerData = await registerResponse.json();

      if (registerData.error) {
        alert("❌ Error registering user: " + registerData.error);
      } else {
        alert(
          `✅ User registered successfully with Mobile: ${registerData.mobile_number}, ICCID: ${registerData.iccid}`
        );
        fetchUsersForAdmin(); //  Refresh user list

        //  Hide the modal after successful registration
        const addUserModal = bootstrap.Modal.getOrCreateInstance(
          document.getElementById("addUserModal")
        );
        addUserModal.hide();
        addUserForm.reset();
      }
    });
  }

  // ---------------------------
  // Logout Functionality
  // ---------------------------
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

function renderRiskPosture(data) {
  const scoreEl = document.getElementById("risk-score-value");
  const levelEl = document.getElementById("risk-level-value");
  const summaryEl = document.getElementById("risk-guidance-summary");
  const factorsEl = document.getElementById("risk-factors-list");
  if (!scoreEl || !levelEl || !summaryEl || !factorsEl) return;

  const score = typeof data.risk_score === "number" ? data.risk_score : 0;
  scoreEl.textContent = score.toFixed(2);
  levelEl.textContent = data.risk_level || "low";
  levelEl.className = `risk-level ${data.risk_level || "low"}`;

  const factors = Array.isArray(data.factors) ? data.factors : [];
  factorsEl.innerHTML = "";
  factors.slice(0, 3).forEach((factor) => {
    const li = document.createElement("li");
    li.textContent = `${factor.title}: ${factor.guidance}`;
    factorsEl.appendChild(li);
  });
  summaryEl.textContent =
    factors.length > 0
      ? "Review the guidance below to keep your account secure."
      : "No unusual activity detected.";
}

function loadRiskPosture() {
  fetch("/api/auth/risk-score", { credentials: "include" })
    .then((res) => res.json())
    .then(renderRiskPosture)
    .catch((err) => console.error("Failed to load risk posture", err));
}

document.addEventListener("DOMContentLoaded", loadRiskPosture);
