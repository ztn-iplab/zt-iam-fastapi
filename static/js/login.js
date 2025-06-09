console.log("🔐 Login JS loaded");

document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("login-form");
  if (!loginForm) return;

  const mobileInput = document.getElementById("mobile-number");
  const passwordInput = document.getElementById("password");
  const errorDiv = document.getElementById("login-error");
  const submitBtn = loginForm.querySelector('button[type="submit"]');

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearError();
    setLoading(true);

    const mobile = mobileInput?.value.trim();
    const password = passwordInput?.value;

    if (!mobile || !password) {
      showError("Please enter both mobile number and password.");
      setLoading(false);
      return;
    }

    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ identifier: mobile, password: password }),
        credentials: "include", // Send cookie
      });

      let data;
      try {
        data = await res.json();
      } catch (jsonErr) {
        if (!res.ok) {
          // Server error, likely returned plain text instead of JSON
          const rawText = await res.text();  // ✅ Only happens if .json() failed
          console.error("❌ Server returned non-JSON response:", rawText);
          throw new Error(rawText || "Internal server error. Please try again later.");
        } else {
          // JSON parse failed but response was OK — weird case
          console.error("❌ JSON parse error on valid response:", jsonErr);
          throw new Error("Unexpected response format.");
        }
      }
      
      if (!res.ok) {
        throw new Error(
          data.error || "Login failed. Please check your credentials."
        );
      }

      console.log("✅ Login successful:", data);

      // Allow cookie storage time
      setTimeout(() => {
        if (data.require_totp_setup || data.require_totp_reset) {
          const reason = data.require_totp_reset ? "reset" : "setup";
          console.log(`➡️ Redirecting to TOTP ${reason}...`);
          window.location.href = `/setup-totp?reason=${reason}`;
        } else if (data.require_totp && data.user_id) {
          console.log("➡️ Redirecting to TOTP verification...");
          window.location.href = `/api/auth/verify-totp`;
        } else {
          console.log("✅ Fully authenticated — redirecting to dashboard...");
          window.location.href = data.dashboard_url || "/";
        }
      }, 500);
    } catch (err) {
      console.error("⚠️ Login error:", err.message || err);
      showError(err.message || "Login failed. Please try again.");
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
    if (!submitBtn) return;
    submitBtn.disabled = isLoading;
    submitBtn.innerHTML = isLoading ? "Logging in..." : "Login";
  }
});
