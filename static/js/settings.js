document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('settings-modal');
  const backdrop = document.getElementById('settings-backdrop');

  if (window.location.pathname === '/settings') {
    modal.style.display = 'block';
    backdrop.style.display = 'block';
  }

  // function getRedirectPath() {
  //   if (userRole === 'user') return '/user/dashboard';
  //   if (userRole === 'agent') return '/agent/dashboard';
  //   if (userRole === 'admin') return '/admin/dashboard';
  //   return '/';  // only fallback if role is undefined or mistyped
  // }
  
  // function closeModalAndRedirect() {
  //   document.getElementById('settings-modal').style.display = 'none';
  //   document.getElementById('settings-backdrop').style.display = 'none';
  //   window.location.href = getRedirectPath();  // ✅ this actually redirects
  // }
  
  const closeBtn = document.getElementById('close-settings-btn');
  if (closeBtn) {
    closeBtn.addEventListener('click', closeModalAndRedirect);
  }

  document.addEventListener('keydown', e => {
    if (e.key === "Escape") {
      closeModalAndRedirect();
    }
  });


  

  // 👤 Handle profile info update (optional section)
  const personalForm = document.getElementById('personal-info-form');
  if (personalForm) {
    personalForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(personalForm);
      const payload = Object.fromEntries(formData.entries());

      try {
        const res = await fetch('/settings/update-profile', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
          credentials: 'include'
        });

        const data = await res.json();
        alert(data.message || 'Profile updated.');
        personalForm.reset();
      } catch (err) {
        alert('Error updating profile.');
      }
    });
  }

  // 🔐 Change password form (on its dedicated subpage)
  const passwordForm = document.getElementById('change-password-form');
  if (passwordForm) {
    passwordForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const formData = new FormData(passwordForm);
      const data = Object.fromEntries(formData.entries());

      if (data.new_password !== data.confirm_password) {
        alert("Passwords do not match!");
        return;
      }

      try {
        const res = await fetch('/api/auth/change-password', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
          credentials: 'include'
        });

        const result = await res.json();
        if (res.ok) {
          alert(result.message);
          passwordForm.reset();
        } else {
          alert(result.error || 'Failed to change password.');
        }
      } catch (err) {
        alert('Error changing password.');
      }
    });
  }

  // 🔁 Reset TOTP (on reset_totp.html)
  const resetTOTPForm = document.getElementById('reset-totp-form');
  if (resetTOTPForm) {
    resetTOTPForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(resetTOTPForm);
      const data = Object.fromEntries(formData.entries());

      try {
        const res = await fetch('/api/auth/request-reset-totp', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
          credentials: 'include'
        });

        const result = await res.json();
        if (res.ok) {
          alert(result.message);
          window.location.href = result.redirect;
        } else {
          alert(result.error || 'TOTP reset failed.');
        }
      } catch (err) {
        alert('Network error resetting TOTP.');
      }
    });
  }

  // 🗝️ Reset WebAuthn (on reset_webauthn.html)
  const resetWebAuthnForm = document.getElementById('reset-webauthn-form');
  if (resetWebAuthnForm) {
    resetWebAuthnForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(resetWebAuthnForm);
      const data = Object.fromEntries(formData.entries());

      try {
        const res = await fetch('/api/auth/request-reset-webauthn', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
          credentials: 'include'
        });

        const result = await res.json();
        if (res.ok) {
          alert(result.message);
          window.location.href = result.redirect;
        } else {
          alert(result.error || 'WebAuthn reset failed.');
        }
      } catch (err) {
        alert('Network error resetting WebAuthn.');
      }
    });
  }

  // 🧨 Request account deletion (linked directly from settings.html)
  const deleteBtn = document.getElementById('delete-account-button');
  if (deleteBtn) {
    deleteBtn.addEventListener('click', async () => {
      const confirmed = confirm("Are you sure you want to request account deletion?");
      if (!confirmed) return;

      try {
        const res = await fetch('/settings/request-deletion', {
          method: 'POST',
          credentials: 'include'
        });

        const data = await res.json();
        if (res.ok) {
          alert(data.message || 'Account deletion requested.');
        } else {
          alert(data.error || 'Failed to process deletion request.');
        }
      } catch (err) {
        alert('Error processing deletion.');
      }
    });
  }

});
