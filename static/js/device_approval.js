document.addEventListener("DOMContentLoaded", () => {
  const statusEl = document.getElementById("approval-status");
  const countdownEl = document.getElementById("approval-countdown");
  const totpCountdownEl = document.getElementById("totp-countdown");
  const hintEl = document.getElementById("approval-hint");
  const errorEl = document.getElementById("approval-error");
  let loginId = window.__LOGIN_ID__ || "";
  const resendBtn = document.getElementById("approval-resend");
  const cancelBtn = document.getElementById("approval-cancel");

  let polling = true;
  let totpTimer = null;

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
        if (typeof data.expires_in === "number" && countdownEl) {
          countdownEl.textContent = `Request expires in ${Math.max(0, data.expires_in)} seconds.`;
        }
        return;
      }
      if (data.status === "ok") {
        polling = false;
        if (totpTimer) {
          clearInterval(totpTimer);
        }
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
      statusEl.textContent =
        data.status === "expired" ? "This approval request expired." : "Approval denied.";
      if (countdownEl) {
        countdownEl.textContent = "Request expired.";
      }
      if (totpCountdownEl) {
        totpCountdownEl.textContent = "Current TOTP window ended.";
      }
      if (hintEl) {
        hintEl.textContent = "Start again to generate a fresh TOTP and approval request.";
      }
      errorEl.textContent = data.reason || "Approval denied.";
      errorEl.style.display = "block";
    } catch (err) {
      polling = false;
      if (totpTimer) {
        clearInterval(totpTimer);
      }
      statusEl.textContent = "Approval failed.";
      errorEl.textContent = err.message || "Approval failed.";
      errorEl.style.display = "block";
    }
  }

  pollStatus();
  setInterval(pollStatus, 3000);

  if (resendBtn) {
    resendBtn.addEventListener("click", async () => {
      try {
        const res = await fetch("/api/auth/login/resend", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ login_id: loginId }),
        });
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.detail || data.reason || "Unable to resend request.");
        }
        loginId = data.login_id ? String(data.login_id) : loginId;
        polling = true;
        statusEl.textContent = "Approval request resent. Waiting...";
        if (hintEl) {
          hintEl.textContent = "Approvals must arrive before the current TOTP code expires.";
        }
        errorEl.style.display = "none";
      } catch (err) {
        errorEl.textContent = err.message || "Unable to resend request.";
        errorEl.style.display = "block";
      }
    });
  }

  if (cancelBtn) {
    cancelBtn.addEventListener("click", async () => {
      try {
        await fetch("/api/auth/login/deny", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ login_id: loginId }),
        });
      } finally {
        window.location.href = "/api/auth/login_form";
      }
    });
  }

  function startTotpCountdown() {
    if (!totpCountdownEl) {
      return;
    }
    if (totpTimer) {
      clearInterval(totpTimer);
    }
    totpTimer = setInterval(() => {
      const nowSeconds = Math.floor(Date.now() / 1000);
      const remaining = 30 - (nowSeconds % 30);
      totpCountdownEl.textContent = `Current TOTP window ends in ${remaining} seconds.`;
    }, 1000);
  }

  startTotpCountdown();
});
