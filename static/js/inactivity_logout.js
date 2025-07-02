// ---------------------------
// 💤 Inactivity Logout
// ---------------------------
const INACTIVITY_LIMIT = 60 * 60 * 1000; // 1 hour
let lastActivityTime = Date.now();

["mousemove", "keydown", "click", "scroll"].forEach((event) => {
  document.addEventListener(event, () => {
    lastActivityTime = Date.now();
  });
});

setInterval(() => {
  if (Date.now() - lastActivityTime > INACTIVITY_LIMIT) {
    alert("You've been inactive for too long. Logging out.");
    fetch("/api/auth/logout", { method: "POST" }).then(() => {
      window.location.href = "/api/auth/login_form";
    });
  }
}, 60 * 1000); // Check every minute
