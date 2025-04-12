console.log("🔐 TOTP Verification JS loaded");

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("totp-form");
  const input = document.getElementById("totp-code");
  const errorDiv = document.getElementById("totp-error");
  const verifyBtn = document.getElementById("verify-btn");
  const spinner = document.getElementById("totp-spinner");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearError();

    const code = input.value.trim();
    if (!/^\d{6}$/.test(code)) {
      return showError("Please enter a valid 6-digit TOTP code.");
    }

    setLoading(true);

    try {
      const res = await fetch("/api/auth/verify-totp-login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ totp: code }), // ⛔ No user_id in body — use JWT!
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "TOTP verification failed.");
      }
      
      if (data.require_webauthn && data.user_id) {
        if (data.has_webauthn_credentials) {
          console.log("🧬 WebAuthn required — redirecting to biometric verification...");
          window.location.href = "/api/auth/verify-biometric";
        } else {
          console.log("🧬 No WebAuthn credential found — redirecting to enroll...");
          window.location.href = "/api/auth/enroll-biometric";
        }
      } else {
        console.log("✅ Fully authenticated — redirecting to dashboard...");
        window.location.href = data.dashboard_url || "/";
      }     
         
    } catch (err) {
      console.error("❌ TOTP error:", err);
      showError(err.message || "Verification failed.");
    } finally {
      setLoading(false);
    }
  });

  function showError(msg) {
    if (errorDiv) {
      errorDiv.textContent = msg;
      errorDiv.style.display = "block";
    }
  }

  function clearError() {
    if (errorDiv) {
      errorDiv.textContent = "";
      errorDiv.style.display = "none";
    }
  }

  function setLoading(isLoading) {
    if (verifyBtn) {
      verifyBtn.disabled = isLoading;
      verifyBtn.innerHTML = isLoading ? "Verifying..." : "Verify";
    }
    if (spinner) {
      spinner.style.display = isLoading ? "block" : "none";
    }
  }
});
