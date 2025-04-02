document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('totp-setup-container');
    const manualKey = document.getElementById('manual-key');
    const continueBtn = document.getElementById('continue-btn');
  
    const urlParams = new URLSearchParams(window.location.search);
    const userId = urlParams.get('user_id');
  
    if (!userId) {
      container.innerHTML = `<p style="color: red;">Missing user ID. Please log in again.</p>`;
      continueBtn.style.display = 'none';
      return;
    }
  
    fetch('/api/auth/setup-totp', {
      method: 'GET',
      credentials: 'include'
  })
  .then(res => res.json())
  .then(data => {
      if (data.qr_code) {
          const img = document.createElement('img');
          img.src = data.qr_code;
          img.alt = "TOTP QR Code";
          container.innerHTML = '';
          container.appendChild(img);
          manualKey.innerText = data.manual_key;
          continueBtn.style.display = 'inline-block';  // ✅ Only show after setup
      } else {
          container.innerHTML = `<p>${data.message || "TOTP already configured."}</p>`;
          manualKey.innerText = "-";
          continueBtn.style.display = 'inline-block';
      }
  })
  .catch(err => {
      container.innerHTML = `<p style="color: red;">Failed to load TOTP setup. Please try again.</p>`;
      console.error("TOTP Setup Error:", err);
  });
  
      
    continueBtn.addEventListener('click', () => {
      continueBtn.style.display = 'none';
      document.getElementById('spinner').style.display = 'block';
  
      setTimeout(() => {
        window.location.href = `/verify-totp?user_id=${userId}`;
      }, 3000);
    });
  });
  