document.addEventListener("DOMContentLoaded", () => {
  const statusEl = document.getElementById("approval-status");
  const errorEl = document.getElementById("approval-error");
  const loginId = window.__LOGIN_ID__ || "";

  let polling = true;

  async function pollStatus() {
    if (!polling) return;
    try {
      const url = loginId
        ? `/api/auth/login-status?login_id=${encodeURIComponent(loginId)}`
        : "/api/auth/login-status";
      const res = await fetch(url, { credentials: "include" });
      const data = await res.json();
      if (data.status === "pending") {
        statusEl.textContent = "Waiting for approval...";
        return;
      }
      if (data.status === "ok") {
        polling = false;
        if (data.require_webauthn) {
          if (data.has_webauthn_credentials) {
            window.location.href = "/api/auth/verify-biometric";
          } else {
            window.location.href = "/api/auth/enroll-biometric";
          }
          return;
        }
        window.location.href = data.dashboard_url || "/";
        return;
      }

      polling = false;
      statusEl.textContent = "Approval denied.";
      errorEl.textContent = data.reason || "Approval denied.";
      errorEl.style.display = "block";
    } catch (err) {
      polling = false;
      statusEl.textContent = "Approval failed.";
      errorEl.textContent = err.message || "Approval failed.";
      errorEl.style.display = "block";
    }
  }

  pollStatus();
  setInterval(pollStatus, 3000);
});
