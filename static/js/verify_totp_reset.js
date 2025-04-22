document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('verify-totp-reset-form');
  if (!form) return;

  const token = form.querySelector('[name="token"]').value;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const password = form.querySelector('[name="password"]').value;

    try {
      const res = await fetch('/api/auth/verify-totp-reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, password }),
        credentials: 'include'
      });

      const data = await res.json();

      if (res.status === 202 && data.require_webauthn) {
        Toastify({
          text: "🔐 WebAuthn required. Please use your security key...",
          duration: 3500,
          gravity: "top",
          position: "right",
          backgroundColor: "#2962ff"
        }).showToast();

        return await triggerWebAuthnFlow(token);
      }

      if (!res.ok) {
        Toastify({
          text: `❌ ${data.error || 'Verification failed.'}`,
          duration: 3000,
          gravity: "top",
          position: "right",
          backgroundColor: "#e53935"
        }).showToast();
        return;
      }

      Toastify({
        text: data.message || "✅ TOTP has been reset.",
        duration: 3000,
        gravity: "top",
        position: "right",
        backgroundColor: "#43a047"
      }).showToast();

      form.reset();
      setTimeout(() => window.location.href = "/api/auth/login_form", 2000);

    } catch (err) {
      console.error("Error during verification:", err);
      Toastify({
        text: "❌ Something went wrong.",
        duration: 3000,
        gravity: "top",
        position: "right",
        backgroundColor: "#e53935"
      }).showToast();
    }
  });

  async function triggerWebAuthnFlow(token) {
    try {
      const challengeRes = await fetch('/api/auth/webauthn/challenge-reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token }),
        credentials: 'include'
      });

      const challengeData = await challengeRes.json();

      if (!challengeRes.ok) {
        throw new Error(challengeData.error || "Challenge failed.");
      }

      const publicKey = {
        ...challengeData,
        challenge: Uint8Array.from(atob(challengeData.challenge), c => c.charCodeAt(0)),
        allowCredentials: challengeData.allowCredentials.map(cred => ({
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
        type: assertion.type
      };

      const verifyRes = await fetch('/api/auth/webauthn/verify-reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credential),
        credentials: 'include'
      });

      const result = await verifyRes.json();

      if (verifyRes.ok) {
        Toastify({
          text: result.message || "✅ TOTP has been reset after WebAuthn.",
          duration: 3000,
          gravity: "top",
          position: "right",
          backgroundColor: "#43a047"
        }).showToast();
        setTimeout(() => window.location.href = "/login", 2000);
      } else {
        throw new Error(result.error || "WebAuthn verification failed.");
      }

    } catch (err) {
      console.error("WebAuthn Error:", err);
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
