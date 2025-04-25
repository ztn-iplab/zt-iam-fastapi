document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('change-password-form');
    if (!form) return;
  
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
  
      const current = form.querySelector('[name="current_password"]').value.trim();
      const newPass = form.querySelector('[name="new_password"]').value.trim();
      const confirm = form.querySelector('[name="confirm_password"]').value.trim();
  
      if (newPass !== confirm) {
        Toastify({
          text: "❌ New passwords do not match.",
          duration: 3000,
          gravity: "top",
          position: "right",
          backgroundColor: "#e53935"
        }).showToast();
        return;
      }
      
      // 💪 Check for strong password before sending request
    const strongRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$/;
    if (!strongRegex.test(newPass)) {
      Toastify({
        text: "❌ Password must be at least 8 characters long and include uppercase, lowercase, number, and special character.",
        duration: 4000,
        gravity: "top",
        position: "right",
        backgroundColor: "#fb8c00"
      }).showToast();
      return;
    }
    
      try {
        const res = await fetch('/api/auth/change-password', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            current_password: current,
            new_password: newPass
          }),
          credentials: 'include'
        });
  
        const data = await res.json();
  
        if (!res.ok) {
          Toastify({
            text: `❌ ${data.error || 'Password change failed.'}`,
            duration: 3000,
            gravity: "top",
            position: "right",
            backgroundColor: "#f44336"
          }).showToast();
        } else {
          Toastify({
            text: "✅ Password changed successfully.",
            duration: 3000,
            gravity: "top",
            position: "right",
            backgroundColor: "#43a047"
          }).showToast();
          form.reset();
        }
  
      } catch (err) {
        console.error('Error:', err);
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
  