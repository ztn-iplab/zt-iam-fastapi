document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('reset-webauthn-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const password = form.querySelector('[name="password"]').value.trim();

    try {
      const res = await fetch('/api/auth/request-reset-webauthn', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password }),
        credentials: 'include'
      });

      const data = await res.json();

      if (!res.ok) {
        Toastify({
          text: `❌ ${data.error || 'Reset failed.'}`,
          duration: 3000,
          gravity: "top",
          position: "right",
          backgroundColor: "#e53935"
        }).showToast();
        return;
      }

      Toastify({
        text: "✅ " + data.message,
        duration: 3000,
        gravity: "top",
        position: "right",
        backgroundColor: "#43a047"
      }).showToast();

      form.reset();

      setTimeout(() => {
        window.location.href = data.redirect || "/dashboard";
      }, 2000);

    } catch (err) {
      console.error('Reset WebAuthn Error:', err);
      Toastify({
        text: "❌ Something went wrong. Please try again.",
        duration: 3000,
        gravity: "top",
        position: "right",
        backgroundColor: "#f44336"
      }).showToast();
    }
  });
});
