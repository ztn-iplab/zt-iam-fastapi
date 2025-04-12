document.addEventListener("DOMContentLoaded", async () => {
  const statusDiv = document.getElementById("biometric-status");

  function bufferToBase64url(buffer) {
    const bytes = new Uint8Array(buffer);
    let str = "";
    for (let b of bytes) str += String.fromCharCode(b);
    return btoa(str).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  }

  function base64urlToBuffer(base64url) {
    if (!base64url || typeof base64url !== "string") {
      throw new Error("Invalid base64url input");
    }
    const base64 = base64url.replace(/-/g, "+").replace(/_/g, "/");
    const pad = base64.length % 4 ? 4 - (base64.length % 4) : 0;
    const padded = base64 + "=".repeat(pad);
    const binary = atob(padded);
    const buffer = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      buffer[i] = binary.charCodeAt(i);
    }
    return buffer.buffer;
  }

  try {
    const res = await fetch("/webauthn/assertion-begin", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include"
    });

    const result = await res.json();
    if (!res.ok || !result.public_key || !result.public_key.challenge) {
      throw new Error(result.error || "Invalid WebAuthn response from server.");
    }

    const options = result.public_key;

    options.challenge = base64urlToBuffer(options.challenge);
    options.allowCredentials = (options.allowCredentials || []).map(c => ({
      ...c,
      id: base64urlToBuffer(c.id)
    }));

    // ✅ Prompt fingerprint/passkey
    const assertion = await navigator.credentials.get({ publicKey: options });

    const payload = {
      credentialId: bufferToBase64url(assertion.rawId),
      authenticatorData: bufferToBase64url(assertion.response.authenticatorData),
      clientDataJSON: bufferToBase64url(assertion.response.clientDataJSON),
      signature: bufferToBase64url(assertion.response.signature),
      userHandle: assertion.response.userHandle
        ? bufferToBase64url(assertion.response.userHandle)
        : null
    };

    const finalRes = await fetch("/webauthn/assertion-complete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      credentials: "include"
    });

    const finalResult = await finalRes.json();

    if (!finalRes.ok) {
      throw new Error(finalResult.error || "Passkey verification failed.");
    }

    statusDiv.textContent = "✅ Identity verified. Redirecting...";
    statusDiv.style.color = "green";
    window.location.href = finalResult.dashboard_url || "/";

  } catch (err) {
    console.error("❌ Fingerprint error:", err);
    statusDiv.textContent = "❌ " + err.message;
    statusDiv.style.color = "red";
  }
});
