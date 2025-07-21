// ---------------------------
//  Silent Token Refresh
// ---------------------------
const AUTO_REFRESH_INTERVAL = 60 * 60 * 1000; // Every 

setInterval(() => {
  fetch("/api/auth/refresh", {
    method: "POST",
    credentials: "include", // Required for sending refresh cookie
  })
    .then((res) => {
      if (res.ok) {
      } else {
        console.warn("⚠️ Refresh failed. Redirecting to login...");
        window.location.href = "/api/auth/login_form";
      }
    })
    .catch((err) => {
      console.error("❌ Token refresh error:", err);
      window.location.href = "/api/auth/login_form";
    });
}, AUTO_REFRESH_INTERVAL);
