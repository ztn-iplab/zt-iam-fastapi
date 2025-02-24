console.log("Login JS loaded");

document.querySelector("#login-form").addEventListener("submit", function(e) {
    e.preventDefault();
    console.log("Form submission intercepted");

    // Retrieve values from the form inputs
    const mobile = document.querySelector("#mobile-number").value;
    const password = document.querySelector("#password").value;
    console.log("Mobile Number:", mobile, "Password:", password);

    fetch("/api/auth/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ mobile_number: mobile, password: password })
    })
    .then(res => res.json().then(data => ({ status: res.status, data })))
    .then(response => {
        console.log("Response status:", response.status);
        if (response.status === 200) {
            console.log("Login successful, received data:", response.data);
            // Use the returned dashboard URL from the JSON response
            let dashboardUrl = response.data.dashboard_url;
            window.location.href = dashboardUrl;
        } else {
            console.error("Login error:", response.data.error);
            alert("Login error: " + response.data.error);
        }
    })
    .catch(error => {
        console.error("Error during login:", error);
    });
});
