console.log("TOTP Verification JS loaded");

const urlParams = new URLSearchParams(window.location.search);
const user_id = urlParams.get('user_id');
const totpForm = document.getElementById('totp-form');

if (totpForm && user_id) {
  totpForm.addEventListener('submit', function (e) {
    e.preventDefault();

    const totpCode = document.getElementById('totp-code').value;

    fetch('/api/auth/verify-totp-login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ user_id, totp: totpCode })
    })
    .then(async res => {
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "TOTP verification failed");
      }

      window.location.href = data.dashboard_url;
    })
    .catch(err => {
      const errorDiv = document.getElementById('totp-error');
      errorDiv.textContent = "TOTP error: " + err.message;
    });
  });
}
