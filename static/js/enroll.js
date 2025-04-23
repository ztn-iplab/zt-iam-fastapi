document.addEventListener("DOMContentLoaded", () => {
  const enrollBtn = document.getElementById("enroll-biometric");
  const statusDiv = document.getElementById("biometric-status");

  if (!enrollBtn || !statusDiv) return;

  // Check if WebAuthn is supported
  if (!window.PublicKeyCredential) {
    statusDiv.textContent = "❌ This browser does not support WebAuthn.";
    statusDiv.style.color = "red";
    return;
  }

  enrollBtn.addEventListener("click", async () => {
    try {
      enrollBtn.disabled = true;
      statusDiv.textContent = "⌛ Waiting for passkey, fingerprint, or security key...";
      statusDiv.style.color = "gray";

      // Step 1: Begin registration
      const res = await fetch("/webauthn/register-begin", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include"
      });

      const json = await res.json();
      const options = json.public_key;

      if (!res.ok || !options) {
        throw new Error(json.error || "Incomplete registration options from server");
      }

      console.log("🧬 WebAuthn register options:", options);

      // Step 2: Format binary fields
      options.challenge = base64urlToBuffer(options.challenge);
      options.user.id = base64urlToBuffer(options.user.id);

      if (options.excludeCredentials) {
        options.excludeCredentials = options.excludeCredentials.map(c => ({
          ...c,
          id: base64urlToBuffer(c.id)
        }));
      }

      // Step 3: Allow flexible authenticators (USB, phone, fingerprint)
      options.authenticatorSelection = {
        userVerification: "required"
      };

      // Step 4: Trigger WebAuthn prompt
      const credential = await navigator.credentials.create({ publicKey: options });

      // Step 5: Prepare payload
      const transports = credential.response.getTransports?.() || [];

      const payload = {
        id: credential.id,
        rawId: bufferToBase64url(credential.rawId),
        type: credential.type,
        response: {
          attestationObject: bufferToBase64url(credential.response.attestationObject),
          clientDataJSON: bufferToBase64url(credential.response.clientDataJSON)
        },
        transports
      };

      // Step 6: Send to server
      const completeRes = await fetch("/webauthn/register-complete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        credentials: "include"
      });

      const result = await completeRes.json();

      if (!completeRes.ok) {
        throw new Error(result.error || "Registration failed.");
      }

      // ✅ Display feedback based on transport type
      let methodUsed = "biometric/passkey";
      if (transports.includes("usb")) {
        methodUsed = "USB security key";
      } else if (transports.includes("internal")) {
        methodUsed = "fingerprint";
      } else if (transports.includes("hybrid")) {
        methodUsed = "cross-device passkey (e.g., phone)";
      }

      statusDiv.textContent = `✅ ${methodUsed} registered successfully!`;
      statusDiv.style.color = "green";
      enrollBtn.disabled = true;

      // ✅ If server gives redirect, go verify
      if (result.redirect) {
        setTimeout(() => {
          window.location.href = result.redirect;
        }, 1000);  // short delay for user feedback
      }

    } catch (err) {
      console.error("❌ Enrollment failed:", err);
      statusDiv.textContent = "❌ " + err.message;
      statusDiv.style.color = "red";
      enrollBtn.disabled = false;
    }
  });

  // 🔄 Helpers
  function base64urlToBuffer(base64url) {
    const base64 = base64url.replace(/-/g, "+").replace(/_/g, "/");
    const pad = base64.length % 4 ? 4 - (base64.length % 4) : 0;
    const padded = base64 + "=".repeat(pad);
    const binary = atob(padded);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
  }

  function bufferToBase64url(buffer) {
    const bytes = new Uint8Array(buffer);
    let str = "";
    for (let byte of bytes) str += String.fromCharCode(byte);
    return btoa(str).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  }
});
