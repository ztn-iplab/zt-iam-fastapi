document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("totp-setup-container");
  const manualKey = document.getElementById("manual-key");
  const copyBtn = document.getElementById("copy-manual-key");
  const continueBtn = document.getElementById("continue-btn");
  const messageContainer = document.getElementById("totp-reason-message");
  const recoverySection = document.getElementById("recovery-codes-section");
  const recoveryList = document.getElementById("recovery-codes-list");
  const copyRecoveryBtn = document.getElementById("copy-recovery-codes");
  const continueToVerifyBtn = document.getElementById("continue-to-verify");
  let enrollmentConfirmed = false;

  //  Handle reason message
  const urlParams = new URLSearchParams(window.location.search);
  const reason = urlParams.get("reason");

  if (reason === "reset") {
    messageContainer.textContent =
      "🔄 You've recently changed your email. For your security, please rescan the QR code.";
  } else if (reason === "setup") {
    messageContainer.textContent =
      "🔐 Two-Factor Authentication is required. Please scan the QR code to secure your login.";
  }

  //  Fetch QR code and secret using JWT from cookie
  fetch("/api/auth/setup-totp", {
    method: "GET",
    credentials: "include",
  })
    .then(async (res) => {
      const rawText = await res.text();
      let data;

      try {
        data = JSON.parse(rawText);
      } catch (err) {
        console.error("❌ Failed to parse JSON:", err);
        console.error("Raw response was:", rawText);
        throw new Error("Server returned an invalid response.");
      }

      if (!res.ok) {
        throw new Error(data.detail || data.error || "TOTP setup failed.");
      }

      if (data.qr_code) {
        const img = document.createElement("img");
        img.src = data.qr_code;
        img.alt = "TOTP QR Code";
        container.innerHTML = "";
        container.appendChild(img);
        manualKey.dataset.raw = data.manual_key || "";
        manualKey.innerText = data.manual_key || "-";
        continueBtn.style.display = "inline-block";
      } else {
        container.innerHTML = `<p>${
          data.message || "TOTP already configured."
        }</p>`;
        manualKey.dataset.raw = "";
        manualKey.innerText = "-";
        continueBtn.style.display = "inline-block";
      }
    })
    .catch((err) => {
      console.error("❌ TOTP Setup Error:", err);
      container.innerHTML = `<p style="color: red;">${
        err.message || "Something went wrong"
      }</p>`;
      manualKey.dataset.raw = "";
      manualKey.innerText = "-";
    });

  copyBtn?.addEventListener("click", async () => {
    const raw = manualKey?.dataset?.raw || "";
    if (!raw) return;
    try {
      await navigator.clipboard.writeText(raw);
      copyBtn.textContent = "Copied";
      setTimeout(() => {
        copyBtn.textContent = "Copy code";
      }, 1500);
    } catch (_) {
      copyBtn.textContent = "Copy failed";
      setTimeout(() => {
        copyBtn.textContent = "Copy code";
      }, 1500);
    }
  });

  // Redirect to verification
  continueBtn.addEventListener("click", async () => {
    if (enrollmentConfirmed) {
      window.location.href = `/api/auth/verify-totp`;
      return;
    }

    const userConfirmed = confirm("🛡️ Are you sure you have scanned the QR code or registered the enrollment code?");
  
    if (!userConfirmed) {
      return;
    }
  
    continueBtn.disabled = true;
    continueBtn.textContent = "Confirming...";
  
    const spinner = document.getElementById("spinner");
    if (spinner) spinner.style.display = "block";
  
    try {
      const res = await fetch("/api/auth/setup-totp/confirm", {
        method: "POST",
        credentials: "include",  //  Use cookie JWT
      });
  
      const data = await res.json();
  
      if (res.ok) {
        Toastify({
          text: "✅ TOTP enrollment confirmed! Proceeding to verification...",
          duration: 3000,
          close: true,
          gravity: "top",
          position: "center",
          backgroundColor: "#43a047"
        }).showToast();

        if (Array.isArray(data.recovery_codes) && data.recovery_codes.length) {
          recoveryList.innerHTML = "";
          data.recovery_codes.forEach((code) => {
            const item = document.createElement("div");
            item.className = "recovery-item";
            item.textContent = code;
            recoveryList.appendChild(item);
          });
          recoverySection.style.display = "block";
          enrollmentConfirmed = true;
          continueBtn.style.display = "none";
          if (spinner) spinner.style.display = "none";
          return;
        }

        setTimeout(() => {
          window.location.href = `/api/auth/verify-totp`;
        }, 1500);
  
      } else {
        throw new Error(data.detail || data.error || "TOTP confirmation failed.");
      }
  
    } catch (err) {
      console.error("❌ TOTP Confirm Error:", err);
  
      Toastify({
        text: err.message || "Something went wrong.",
        duration: 4000,
        close: true,
        gravity: "top",
        position: "center",
        backgroundColor: "red"
      }).showToast();
  
      continueBtn.disabled = false;
      continueBtn.textContent = "Continue";
      if (spinner) spinner.style.display = "none";
    }
  });

  copyRecoveryBtn?.addEventListener("click", async () => {
    const codes = Array.from(recoveryList?.children || []).map((node) => node.textContent || "");
    if (!codes.length) return;
    const payload = codes.join("\n");
    const setStatus = (label) => {
      copyRecoveryBtn.textContent = label;
      setTimeout(() => {
        copyRecoveryBtn.textContent = "Copy recovery codes";
      }, 1500);
    };

    try {
      if (navigator.clipboard?.writeText && window.isSecureContext) {
        await navigator.clipboard.writeText(payload);
        setStatus("Copied");
        return;
      }
    } catch (_) {
      // Fallback below
    }

    try {
      const textarea = document.createElement("textarea");
      textarea.value = payload;
      textarea.setAttribute("readonly", "");
      textarea.style.position = "absolute";
      textarea.style.left = "-9999px";
      document.body.appendChild(textarea);
      textarea.select();
      const ok = document.execCommand("copy");
      document.body.removeChild(textarea);
      setStatus(ok ? "Copied" : "Copy failed");
    } catch (_) {
      setStatus("Copy failed");
    }
  });

  continueToVerifyBtn?.addEventListener("click", () => {
    window.location.href = `/api/auth/verify-totp`;
  });
  
});
