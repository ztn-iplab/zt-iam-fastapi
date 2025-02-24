console.log("Admin Dashboard JS loaded");

// ---------------------------
// Inactivity Timeout Logic
// ---------------------------
const INACTIVITY_LIMIT = 15 * 60 * 1000; // 15 minutes in milliseconds
let lastActivityTime = Date.now();
["mousemove", "keydown", "click", "scroll"].forEach(evt =>
  document.addEventListener(evt, () => { lastActivityTime = Date.now(); })
);
setInterval(() => {
  if (Date.now() - lastActivityTime > INACTIVITY_LIMIT) {
    alert("You've been inactive. Logging out.");
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_id');
    window.location.href = '/api/auth/login_form';
  }
}, 60000);

// ---------------------------
// Admin Functions: Fetch Users & Bind Actions
// ---------------------------
function fetchUsersForAdmin() {
  const token = localStorage.getItem("access_token");
  fetch("/api/admin/users", {
      method: "GET",
      headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
      }
  })
  .then(res => res.json())
  .then(users => {
      const userList = document.getElementById("admin-user-list");
      userList.innerHTML = "";
      users.forEach(user => {
          const row = document.createElement("tr");
          row.innerHTML = `
              <td>${user.id}</td>
              <td>${user.first_name} ${user.last_name || ""}</td>
              <td>${user.mobile_number}</td>
              <td>${user.email}</td>
              <td>
                  <select class="role-select" data-user-id="${user.id}">
                      <option value="user" ${user.role === "user" ? "selected" : ""}>User</option>
                      <option value="agent" ${user.role === "agent" ? "selected" : ""}>Agent</option>
                      <option value="admin" ${user.role === "admin" ? "selected" : ""}>Admin</option>
                  </select>
              </td>
              <td>
                  <button class="btn btn-primary verify-user" data-user-id="${user.id}">Verify</button>
                  <button class="btn btn-danger suspend-user" data-user-id="${user.id}">Suspend</button>
                  <button class="btn btn-secondary delete-user" data-user-id="${user.id}">Delete</button>
                  <button class="btn btn-primary edit-user" data-user-id="${user.id}">Edit</button>
              </td>
          `;
          userList.appendChild(row);
      });
      // Attach event listeners
      document.querySelectorAll(".role-select").forEach(select => {
          select.addEventListener("change", function () {
              updateUserRole(this.dataset.userId, this.value);
          });
      });
      document.querySelectorAll(".suspend-user").forEach(button => {
          button.addEventListener("click", function () {
              suspendUser(this.dataset.userId);
          });
      });
      document.querySelectorAll(".verify-user").forEach(button => {
          button.addEventListener("click", function () {
              verifyUser(this.dataset.userId);
          });
      });
      document.querySelectorAll(".delete-user").forEach(button => {
          button.addEventListener("click", function () {
              deleteUser(this.dataset.userId);
          });
      });
      document.querySelectorAll(".edit-user").forEach(button => {
          button.addEventListener("click", function () {
              editUser(this.dataset.userId);
          });
      });
  })
  .catch(error => console.error("Error fetching users:", error));
}

// ---------------------------
// Admin User Actions
// ---------------------------

// Update User Role
function updateUserRole(userId, newRole) {
  const token = localStorage.getItem("access_token");
  fetch("/api/admin/assign_role", {
      method: "POST",
      headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({ user_id: userId, role_id: newRole })
  })
  .then(response => response.json())
  .then(data => {
      alert("Role updated successfully!");
      fetchUsersForAdmin();
  })
  .catch(error => console.error("Error updating role:", error));
}

// Suspend User
function suspendUser(userId) {
  const token = localStorage.getItem("access_token");
  fetch(`/api/admin/suspend_user/${userId}`, {
      method: "POST",
      headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
      }
  })
  .then(response => response.json())
  .then(data => {
      alert("User suspended successfully!");
      fetchUsersForAdmin();
  })
  .catch(error => console.error("Error suspending user:", error));
}

// Verify User
function verifyUser(userId) {
  const token = localStorage.getItem("access_token");
  fetch(`/api/admin/verify_user/${userId}`, {
      method: "POST",
      headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
      }
  })
  .then(response => response.json())
  .then(data => {
      alert("User verified successfully!");
      fetchUsersForAdmin();
  })
  .catch(error => console.error("Error verifying user:", error));
}

// Delete User (Admin-Initiated Deletion)
function deleteUser(userId) {
  const token = localStorage.getItem("access_token");
  if (!confirm("Are you sure you want to permanently delete this user account? This action cannot be undone.")) {
      return;
  }
  fetch(`/api/admin_delete_user/${userId}`, {
      method: "DELETE",
      headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({ confirmed: true })
  })
  .then(response => response.json())
  .then(data => {
      if (data.error) {
          alert("Error deleting user: " + data.error);
      } else {
          alert(data.message);
          fetchUsersForAdmin();
      }
  })
  .catch(error => console.error("Error deleting user:", error));
}

// Edit User
function editUser(userId) {
  const token = localStorage.getItem("access_token");
  let firstName = prompt("Enter new first name (leave blank to keep unchanged):");
  let lastName = prompt("Enter new last name (leave blank to keep unchanged):");
  let email = prompt("Enter new email (leave blank to keep unchanged):");
  let mobileNumber = prompt("Enter new mobile number (leave blank to keep unchanged):");

  const payload = {};
  if (firstName) payload.first_name = firstName;
  if (lastName) payload.last_name = lastName;
  if (email) payload.email = email;
  if (mobileNumber) payload.mobile_number = mobileNumber;
  
  if (Object.keys(payload).length === 0) {
      alert("No changes provided.");
      return;
  }
  
  fetch(`/api/admin/edit_user/${userId}`, {
      method: "PUT",
      headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify(payload)
  })
  .then(response => response.json())
  .then(data => {
      if (data.error) {
          alert("Error updating user: " + data.error);
      } else {
          alert(data.message);
          fetchUsersForAdmin();
      }
  })
  .catch(error => console.error("Error editing user:", error));
}

// ---------------------------
// Initialize Admin Dashboard
// ---------------------------
document.addEventListener("DOMContentLoaded", function() {
  fetchUsersForAdmin();
});
