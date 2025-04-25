console.log("Register JS loaded");

document
  .getElementById("register-form")
  .addEventListener("submit", function (e) {
    e.preventDefault();

    const iccid = document.getElementById("iccid").value.trim();
    const email = document.getElementById("email").value.trim();
    const firstName = document.getElementById("first-name").value.trim();
    const lastName = document.getElementById("last-name").value.trim();
    const country = document.getElementById("country").value;
    const password = document.getElementById("password").value.trim();

    if (!iccid || !email || !firstName || !password) {
      showToast("❌ ICCID, email, first name, and password are required.", "error");
      return;
    }

    const strongPasswordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).{8,}$/;
    if (!strongPasswordRegex.test(password)) {
      showToast(
        "❌ Password must be at least 8 characters and include uppercase, lowercase, number, and special character.",
        "error"
      );
      return;
    }

    console.log("Form submission intercepted");

    fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        iccid,
        email,
        first_name: firstName,
        last_name: lastName,
        country,
        password,
      }),
      credentials: "include",
    })
      .then(async (res) => {
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.error || "Registration failed");
        }
        return data;
      })
      .then((data) => {
        console.log("Registration successful, received data:", data);
        showToast("✅ Registration successful! Redirecting...", "success");
        setTimeout(() => {
          window.location.href = "/api/auth/login_form?registered=1";
        }, 1500);
      })
      .catch((err) => {
        console.error("Registration error:", err);
        showToast(`❌ ${err.message}`, "error");
      });
  });

// 🔹 Toastify wrapper
function showToast(message, type = "info") {
  Toastify({
    text: message,
    duration: 3000,
    gravity: "top",
    position: "right",
    backgroundColor:
      type === "success"
        ? "#43a047"
        : type === "error"
        ? "#e53935"
        : "#2196f3",
  }).showToast();
}
