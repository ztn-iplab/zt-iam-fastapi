document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('verify-sim-swap-form');
  if (!form) return;

  const tokenInput = form.querySelector('[name="token"]');
  if (!tokenInput) {
    console.error("Token input not found in form.");
    return;
  }
  const token = tokenInput.value;

  let submitting = false;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (submitting) return;
    submitting = true;

    const password = form.querySelector('[name="password"]').value;
    const totp_code = form.querySelector('[name="totp_code"]').value;

    try {
      const res = await fetch('/api/auth/verify-sim-swap', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, password, totp_code }),
        credentials: 'include'
      });

      const data = await res.json();

      if (res.status === 202 && data.require_webauthn) {
        Toastify({
          text: "🔐 WebAuthn required. Please use your security key...",
          duration: 3500,
          gravity: "top",
          position: "right",
          style: { background: "#2962ff" }
        }).showToast();

        return await triggerWebAuthnFlow(token, password, totp_code);
      }

      if (!res.ok) {
        Toastify({
          text: `❌ ${data.error || 'Verification failed.'}`,
          duration: 3000,
          gravity: "top",
          position: "right",
          style: { background: "#e53935" }
        }).showToast();
        submitting = false;
        return;
      }

      Toastify({
        text: data.message || "✅ Your SIM has been successfully swapped.",
        duration: 3000,
        gravity: "top",
        position: "right",
        style: { background: "#43a047" }
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
        style: { background: "#e53935" }
      }).showToast();
      submitting = false;
    }
  });

  async function triggerWebAuthnFlow(token, password, totp_code) {
    try {
      const challengeRes = await fetch('/webauthn/reset-assertion-begin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, context: 'sim_swap' }),
        credentials: 'include'
      });

      const beginData = await challengeRes.json();
      if (!challengeRes.ok) throw new Error(beginData.error || "Failed to begin WebAuthn reset.");

      const publicKey = {
        ...beginData.public_key,
        challenge: base64urlToUint8Array(beginData.public_key.challenge),
        allowCredentials: beginData.public_key.allowCredentials.map(cred => ({
          ...cred,
          id: base64urlToUint8Array(cred.id)
        }))
      };

      const assertion = await navigator.credentials.get({ publicKey });

      const responsePayload = {
        credentialId: toBase64Url(assertion.rawId),
        authenticatorData: toBase64Url(assertion.response.authenticatorData),
        clientDataJSON: toBase64Url(assertion.response.clientDataJSON),
        signature: toBase64Url(assertion.response.signature),
        userHandle: assertion.response.userHandle
          ? toBase64Url(assertion.response.userHandle)
          : null
      };

      const verifyRes = await fetch('/webauthn/reset-assertion-complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(responsePayload),
        credentials: 'include'
      });

      const result = await verifyRes.json();
      if (!verifyRes.ok) throw new Error(result.error || "WebAuthn reset verification failed.");

      // ✅ Retry SIM swap with WebAuthn verified
      const retry = await fetch('/api/auth/verify-sim-swap', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, password, totp_code, webauthn_done: true }),
        credentials: 'include'
      });

      const retryResult = await retry.json();
      if (!retry.ok) {
        console.error("Final SIM swap retry failed:", retryResult);
        throw new Error(retryResult.error || "Final SIM swap failed.");
      }

      Toastify({
        text: retryResult.message || "✅ SIM swap completed successfully.",
        duration: 3000,
        gravity: "top",
        position: "right",
        style: { background: "#43a047" }
      }).showToast();

      setTimeout(() => window.location.href = "/api/auth/login_form", 2000);

    } catch (err) {
      console.error("WebAuthn Error:", err);
      Toastify({
        text: `❌ ${err.message || 'WebAuthn failed.'}`,
        duration: 3000,
        gravity: "top",
        position: "right",
        style: { background: "#e53935" }
      }).showToast();
      submitting = false;
    }
  }

  function base64urlToUint8Array(base64urlString) {
    const padding = '='.repeat((4 - base64urlString.length % 4) % 4);
    const base64 = (base64urlString + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = atob(base64);
    return Uint8Array.from([...rawData].map(c => c.charCodeAt(0)));
  }

  function toBase64Url(buffer) {
    return btoa(String.fromCharCode(...new Uint8Array(buffer)))
      .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  }
});
