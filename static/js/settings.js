console.log("Settings JS loaded");

document.addEventListener("DOMContentLoaded", function () {
  const token = localStorage.getItem("access_token");
  if (!token) {
    window.location.href = "/api/auth/login_form";
    return;
  }

  // Personal Info Form Submission
  const personalInfoForm = document.getElementById("personal-info-form");
  if (personalInfoForm) {
    personalInfoForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const country = document.getElementById("country").value;
      const payload = { country };

      fetch("/api/user/settings", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      })
        .then((response) => {
          if (!response.ok)
            throw new Error("Failed to update personal information");
          return response.json();
        })
        .then((data) => {
          alert("Personal information updated successfully!");
        })
        .catch((error) => {
          console.error("Error updating personal information:", error);
          alert("Error updating information: " + error.message);
        });
    });
  }

  // Change Password Form Submission
  const changePasswordForm = document.getElementById("change-password-form");
  if (changePasswordForm) {
    changePasswordForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const currentPassword = document.getElementById("current-password").value;
      const newPassword = document.getElementById("new-password").value;
      const confirmPassword = document.getElementById("confirm-password").value;

      if (newPassword !== confirmPassword) {
        alert("New password and confirmation do not match.");
        return;
      }

      const payload = {
        current_password: currentPassword,
        new_password: newPassword,
      };

      fetch("/api/user/change_password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      })
        .then((response) => {
          if (!response.ok) throw new Error("Failed to change password");
          return response.json();
        })
        .then((data) => {
          alert("Password changed successfully!");
          changePasswordForm.reset();
        })
        .catch((error) => {
          console.error("Error changing password:", error);
          alert("Error changing password: " + error.message);
        });
    });
  }

  // Account Deletion Request
  const deleteAccountButton = document.getElementById("delete-account-button");
  if (deleteAccountButton) {
    deleteAccountButton.addEventListener("click", function (e) {
      e.preventDefault();
      if (
        confirm(
          "Are you sure you want to request account deletion? This action cannot be undone and will require admin verification."
        )
      ) {
        fetch("/api/user/request_deletion", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        })
          .then((response) => {
            if (!response.ok)
              throw new Error("Failed to submit account deletion request");
            return response.json();
          })
          .then((data) => {
            alert(
              data.message || "Account deletion request submitted successfully."
            );
          })
          .catch((error) => {
            console.error("Error submitting account deletion request:", error);
            alert("Error submitting deletion request: " + error.message);
          });
      }
    });
  }

  // Logout Functionality
  const logoutButton = document.getElementById("logout-button");
  if (logoutButton) {
    logoutButton.addEventListener("click", function (e) {
      e.preventDefault();
      localStorage.removeItem("access_token");
      localStorage.removeItem("user_id");
      window.location.href = "/";
    });
  }
});
