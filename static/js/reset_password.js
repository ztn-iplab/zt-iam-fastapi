document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('reset-password-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const newPassword = form.querySelector('[name="new_password"]').value.trim();
    const confirmPassword = form.querySelector('[name="confirm_password"]').value.trim();
    const token = form.querySelector('[name="token"]').value.trim();

    if (newPassword !== confirmPassword) {
      Toastify({
        text: "❌ Passwords do not match.",
        duration: 3000,
        gravity: "top",
        position: "right",
        backgroundColor: "#e53935"
      }).showToast();
      return;
    }

    try {
      const res = await fetch('/api/auth/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password: newPassword }),
      });

      const data = await res.json();

      if (!res.ok) {
        Toastify({
          text: `❌ ${data.error || 'Password reset failed.'}`,
          duration: 3000,
          gravity: "top",
          position: "right",
          backgroundColor: "#f44336"
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
        window.location.href = "/api/auth/login_form";
      }, 2000);

    } catch (err) {
      console.error("Password Reset Error:", err);
      Toastify({
        text: "❌ Something went wrong. Please try again.",
        duration: 3000,
        gravity: "top",
        position: "right",
        backgroundColor: "#e53935"
      }).showToast();
    }
  });
});
