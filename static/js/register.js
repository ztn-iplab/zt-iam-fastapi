console.log("Register JS loaded");

document
  .getElementById("register-form")
  .addEventListener("submit", function (e) {
    e.preventDefault();

    // Get the values from the registration form
    const iccid = document.getElementById("iccid").value.trim();
    const email = document.getElementById("email").value.trim();
    const firstName = document.getElementById("first-name").value.trim();
    const lastName = document.getElementById("last-name").value.trim();
    const country = document.getElementById("country").value;
    const password = document.getElementById("password").value.trim();

    // Ensure all required fields are provided
    if (!iccid || !email || !firstName || !password) {
      displayError("❌ ICCID, email, first name, and password are required.");
      return;
    }

    // Password strength validation
    const strongPasswordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$/;
    if (!strongPasswordRegex.test(password)) {
      displayError("❌ Password must be at least 8 characters and include uppercase, lowercase, number, and special character.");
      return;
    }

    console.log("Form submission intercepted");

    // Send the registration data to the backend
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
        // Clear any previous errors
        displayError("");
        // Redirect to the user's dashboard or login page
        window.location.href = "/api/auth/login_form?registered=1";
      })
      .catch((err) => {
        console.error("Registration error:", err);
        displayError(`❌ ${err.message}`);
      });
  });

// 🔹 Function to display errors dynamically below the register button
function displayError(message) {
  const errorDiv = document.getElementById("register-error");
  if (errorDiv) {
    errorDiv.textContent = message;
    errorDiv.style.display = message ? "block" : "none";
  }
}
