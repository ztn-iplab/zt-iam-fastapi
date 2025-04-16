document.addEventListener("DOMContentLoaded", async () => {
  const statusDiv = document.getElementById("biometric-status");

  // 🔧 Utility: Buffer → Base64URL
  function bufferToBase64url(buffer) {
    const bytes = new Uint8Array(buffer);
    let str = "";
    for (let b of bytes) str += String.fromCharCode(b);
    return btoa(str).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  }

  // 🔧 Utility: Base64URL → Buffer
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
    // 🟢 Step 1: Begin WebAuthn assertion
    const res = await fetch("/webauthn/assertion-begin", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include"
    });

    const result = await res.json();
    if (!res.ok || !result.public_key || !result.public_key.challenge) {
      throw new Error(result.error || "Invalid WebAuthn response from server.");
    }

    const publicKey = result.public_key;

    // 🔁 Convert challenge & credential IDs
    publicKey.challenge = base64urlToBuffer(publicKey.challenge);
    publicKey.allowCredentials = (publicKey.allowCredentials || []).map(c => ({
      ...c,
      id: base64urlToBuffer(c.id)
    }));

    console.log("🟢 WebAuthn assertion options ready:", publicKey);

    // 👆 Step 2: Prompt for fingerprint or USB key
    const assertion = await navigator.credentials.get({ publicKey });

    console.log("✅ WebAuthn assertion successful:", assertion);

    // 🧾 Step 3: Build payload
    const payload = {
      credentialId: bufferToBase64url(assertion.rawId),
      authenticatorData: bufferToBase64url(assertion.response.authenticatorData),
      clientDataJSON: bufferToBase64url(assertion.response.clientDataJSON),
      signature: bufferToBase64url(assertion.response.signature),
      userHandle: assertion.response.userHandle
        ? bufferToBase64url(assertion.response.userHandle)
        : null
    };

    console.log("🛂 WebAuthn Assertion Payload:", payload);

    // 📨 Step 4: Send to server
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

    // ✅ Step 5: Show success
    statusDiv.textContent = "✅ Identity verified. Redirecting...";
    statusDiv.style.color = "green";
    window.location.href = finalResult.dashboard_url || "/";

  } catch (err) {
    let readableReason = "Unknown client-side WebAuthn error.";
    switch (err.name) {
      case "NotAllowedError":
        readableReason = "User cancelled or did not interact with WebAuthn prompt in time.";
        break;
      case "AbortError":
        readableReason = "WebAuthn operation was aborted (maybe navigated away or tab closed).";
        break;
      case "SecurityError":
        readableReason = "WebAuthn blocked due to insecure context or permissions.";
        break;
      case "InvalidStateError":
        readableReason = "Authenticator is not in a valid state to complete the operation.";
        break;
      case "UnknownError":
        readableReason = "WebAuthn failed due to an unknown browser error.";
        break;
    }
  
    console.warn(`❌ ${readableReason} (${err.name}: ${err.message})`);
    statusDiv.textContent = "❌ " + readableReason;
    statusDiv.style.color = "red";
  
    await fetch("/api/auth/log-webauthn-failure", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        error: `${readableReason} (${err.name}: ${err.message})`
      })
    });
  } 
});
