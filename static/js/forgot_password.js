document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('forgot-password-form');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const identifier = form.identifier.value.trim();

    try {
      const res = await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier })
      });

      const raw = await res.text();
      let data = {};
      try {
        data = raw ? JSON.parse(raw) : {};
      } catch (err) {
        data = { error: raw || "Something went wrong." };
      }

      if (res.ok) {
        Toastify({
          text: data.message,
          duration: 5000,
          gravity: "top",
          position: "center",
          backgroundColor: "#43a047",
          stopOnFocus: true
        }).showToast();

        form.reset();
      } else {
        Toastify({
          text: data.detail || data.error || "Something went wrong.",
          duration: 5000,
          gravity: "top",
          position: "center",
          backgroundColor: "#e53935",
          stopOnFocus: true
        }).showToast();
      }
    } catch (err) {
      Toastify({
        text: "Network error. Please try again.",
        duration: 5000,
        gravity: "top",
        position: "center",
        backgroundColor: "#e53935",
        stopOnFocus: true
      }).showToast();
    }
  });
});
