document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('totp-setup-container');
    const manualKey = document.getElementById('manual-key');
    const continueBtn = document.getElementById('continue-btn');
  
    // ✅ JWT stored in cookie — no need for user ID from URL
    console.log("📡 Fetching /api/auth/setup-totp using cookie-based JWT...");
  
    fetch('/api/auth/setup-totp', {
        method: 'GET',
        credentials: 'include'
      })
      .then(async res => {
        const rawText = await res.text();  // ✅ Read only once
        let data;
      
        try {
          data = JSON.parse(rawText);      // ✅ Try parsing JSON manually
        } catch (err) {
          console.error("❌ Failed to parse JSON:", err);
          console.error("Raw response was:", rawText);
          throw new Error("Server returned an invalid response.");
        }
      
        if (!res.ok) {
          throw new Error(data.error || "TOTP setup failed.");
        }
      
        if (data.qr_code) {
          const img = document.createElement('img');
          img.src = data.qr_code;
          img.alt = "TOTP QR Code";
          container.innerHTML = '';
          container.appendChild(img);
          manualKey.innerText = data.manual_key;
          continueBtn.style.display = 'inline-block';
        } else {
          container.innerHTML = `<p>${data.message || "TOTP already configured."}</p>`;
          manualKey.innerText = "-";
          continueBtn.style.display = 'inline-block';
        }
      })
      .catch(err => {
        console.error("❌ TOTP Setup Error:", err);
        container.innerHTML = `<p style="color: red;">${err.message || "Something went wrong"}</p>`;
        manualKey.innerText = "-";
      });
      
    continueBtn.addEventListener('click', () => {
      continueBtn.style.display = 'none';
      const spinner = document.getElementById('spinner');
      if (spinner) spinner.style.display = 'block';
  
      setTimeout(() => {
        window.location.href = `/verify-totp`;  // ✅ Don't include user_id
      }, 3000);
    });
  });
  