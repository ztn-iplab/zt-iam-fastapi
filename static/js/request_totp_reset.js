document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('request-totp-form');
    if (!form) return;
  
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
  
      const identifier = form.querySelector('[name="identifier"]').value.trim();
  
      try {
        const res = await fetch('/api/auth/request-totp-reset', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ identifier })
        });
  
        const data = await res.json();
  
        if (!res.ok) {
          Toastify({
            text: `❌ ${data.error || 'TOTP reset request failed.'}`,
            duration: 3000,
            gravity: "top",
            position: "right",
            backgroundColor: "#e53935"
          }).showToast();
          return;
        }
  
        Toastify({
          text: data.message || "✅ Reset link sent.",
          duration: 3000,
          gravity: "top",
          position: "right",
          backgroundColor: "#43a047"
        }).showToast();
  
        form.reset();
      } catch (err) {
        console.error("TOTP Reset Error:", err);
        Toastify({
          text: "❌ Something went wrong.",
          duration: 3000,
          gravity: "top",
          position: "right",
          backgroundColor: "#f44336"
        }).showToast();
      }
    });
  });
  