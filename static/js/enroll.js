document.addEventListener("DOMContentLoaded", () => {
    const enrollBtn = document.getElementById("enroll-biometric");
    const statusDiv = document.getElementById("biometric-status");
  
    if (!enrollBtn || !statusDiv) return;
  
    // Check for WebAuthn support
    if (!window.PublicKeyCredential) {
      statusDiv.textContent = "❌ This browser does not support WebAuthn.";
      statusDiv.style.color = "red";
      return;
    }
  
    enrollBtn.addEventListener("click", async () => {
      try {
        enrollBtn.disabled = true;
        statusDiv.textContent = "⌛ Waiting for fingerprint or security key...";
        statusDiv.style.color = "gray";
  
        // Step 1: Start registration
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
  
        // Step 2: Prepare options
        options.challenge = base64urlToBuffer(options.challenge);
        options.user.id = base64urlToBuffer(options.user.id);
  
        if (options.excludeCredentials) {
          options.excludeCredentials = options.excludeCredentials.map(c => ({
            ...c,
            id: base64urlToBuffer(c.id)
          }));
        }
  
        // Optional: enforce platform-only auth (e.g., fingerprint)
        // options.authenticatorSelection = {
        //   authenticatorAttachment: "platform",
        //   userVerification: "required"
        // };
  
        // Step 3: Prompt biometric/passkey registration
        const credential = await navigator.credentials.create({ publicKey: options });
  
        // Step 4: Send response to server
        console.log("🧪 rawId (browser id):", credential.id);

        const payload = {
            id: credential.id,
            rawId: credential.id, // must match exactly
            type: credential.type,
            response: {
              attestationObject: bufferToBase64url(credential.response.attestationObject),
              clientDataJSON: bufferToBase64url(credential.response.clientDataJSON)
            },
            transports: credential.response.getTransports?.() || []
          };
          
          
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
  
        statusDiv.textContent = "✅ Fingerprint/passkey registered successfully!";
        statusDiv.style.color = "green";
        enrollBtn.disabled = true;
  
      } catch (err) {
        console.error("❌ Enrollment failed:", err);
        statusDiv.textContent = "❌ " + err.message;
        statusDiv.style.color = "red";
        enrollBtn.disabled = false;
      }
    });
  
    // Utility: base64url → ArrayBuffer
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
  
    // Utility: ArrayBuffer → base64url
    function bufferToBase64url(buffer) {
      const bytes = new Uint8Array(buffer);
      let str = "";
      for (let byte of bytes) str += String.fromCharCode(byte);
      return btoa(str).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
    }
  });
  