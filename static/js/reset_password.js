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

      if (res.status === 202 && data.require_webauthn) {
        Toastify({
          text: "🔐 WebAuthn verification required before reset.",
          duration: 3000,
          gravity: "top",
          position: "right",
          backgroundColor: "#2962ff"
        }).showToast();

        return await performWebAuthnReset(token, newPassword); // just verify, then retry
      }

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

  async function performWebAuthnReset(token, newPassword) {
    try {
      const beginRes = await fetch('/api/auth/webauthn/reset-assertion-begin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token }),
        credentials: 'include'
      });

      const beginData = await beginRes.json();
      if (!beginRes.ok) throw new Error(beginData.error);

      const publicKey = {
        ...beginData,
        challenge: Uint8Array.from(atob(beginData.challenge), c => c.charCodeAt(0)),
        allowCredentials: beginData.allowCredentials.map(cred => ({
          ...cred,
          id: Uint8Array.from(atob(cred.id), c => c.charCodeAt(0))
        }))
      };

      const assertion = await navigator.credentials.get({ publicKey });

      const credential = {
        id: assertion.id,
        rawId: btoa(String.fromCharCode(...new Uint8Array(assertion.rawId))),
        response: {
          authenticatorData: btoa(String.fromCharCode(...new Uint8Array(assertion.response.authenticatorData))),
          clientDataJSON: btoa(String.fromCharCode(...new Uint8Array(assertion.response.clientDataJSON))),
          signature: btoa(String.fromCharCode(...new Uint8Array(assertion.response.signature))),
          userHandle: assertion.response.userHandle
            ? btoa(String.fromCharCode(...new Uint8Array(assertion.response.userHandle)))
            : null
        },
        type: assertion.type,
        token
      };

      const completeRes = await fetch('/api/auth/webauthn/reset-assertion-complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, credential }),
        credentials: 'include'
      });

      const completeData = await completeRes.json();
      if (!completeRes.ok) throw new Error(completeData.error);

      // ✅ Now retry the password reset after successful WebAuthn
      const retryRes = await fetch('/api/auth/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password: newPassword }),
      });

      const retryData = await retryRes.json();
      if (!retryRes.ok) throw new Error(retryData.error || "Final password reset failed.");

      Toastify({
        text: retryData.message || "✅ Password reset complete.",
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
      console.error("WebAuthn Reset Error:", err);
      Toastify({
        text: `❌ ${err.message || 'WebAuthn failed.'}`,
        duration: 3000,
        gravity: "top",
        position: "right",
        backgroundColor: "#e53935"
      }).showToast();
    }
  }
});
