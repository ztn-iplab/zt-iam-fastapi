document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("totp-setup-container");
  const manualKey = document.getElementById("manual-key");
  const continueBtn = document.getElementById("continue-btn");
  const messageContainer = document.getElementById("totp-reason-message");

  // ✅ Handle reason message
  const urlParams = new URLSearchParams(window.location.search);
  const reason = urlParams.get("reason");

  if (reason === "reset") {
    messageContainer.textContent =
      "🔄 You've recently changed your email. For your security, please rescan the QR code.";
  } else if (reason === "setup") {
    messageContainer.textContent =
      "🔐 Two-Factor Authentication is required. Please scan the QR code to secure your login.";
  }

  // ✅ Fetch QR code and secret using JWT from cookie
  console.log("📡 Fetching /api/auth/setup-totp using cookie-based JWT...");

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
        throw new Error(data.error || "TOTP setup failed.");
      }

      if (data.qr_code) {
        const img = document.createElement("img");
        img.src = data.qr_code;
        img.alt = "TOTP QR Code";
        container.innerHTML = "";
        container.appendChild(img);
        manualKey.innerText = data.manual_key;
        continueBtn.style.display = "inline-block";
      } else {
        container.innerHTML = `<p>${
          data.message || "TOTP already configured."
        }</p>`;
        manualKey.innerText = "-";
        continueBtn.style.display = "inline-block";
      }
    })
    .catch((err) => {
      console.error("❌ TOTP Setup Error:", err);
      container.innerHTML = `<p style="color: red;">${
        err.message || "Something went wrong"
      }</p>`;
      manualKey.innerText = "-";
    });

  // ✅ Redirect to verification
  continueBtn.addEventListener("click", async () => {
    const userConfirmed = confirm("🛡️ Are you sure you have scanned the QR code or registered the manual key?");
  
    if (!userConfirmed) {
      console.log("🛑 User canceled TOTP confirmation.");
      return;  // 🔥 STOP: No spinner, no request, no toast
    }
  
    continueBtn.disabled = true;
    continueBtn.textContent = "Confirming...";
  
    const spinner = document.getElementById("spinner");
    if (spinner) spinner.style.display = "block";
  
    try {
      const res = await fetch("/api/auth/setup-totp/confirm", {
        method: "POST",
        credentials: "include",  // 🛡️ Use cookie JWT
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
  
        setTimeout(() => {
          window.location.href = `/api/auth/verify-totp`;
        }, 1500);
  
      } else {
        throw new Error(data.error || "TOTP confirmation failed.");
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
  
});
