// ---------------------------
// Role Mapping
// ---------------------------

const roleMapping = {
    "1": "Admin",
    "2": "Agent",
    "3": "User"
  };

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
            // Map the role value to a name; if no mapping exists, fall back to what is returned.
            const roleName = roleMapping[user.role] || user.role;
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${user.id}</td>
                <td>${user.first_name} ${user.last_name || ""}</td>
                <td>${user.mobile_number}</td>
                <td>${user.email}</td>
                <td>${roleName}</td>
                <td>
                    <button class="btn btn-primary assign-role" data-user-id="${user.id}">Assign Role</button>
                    <button class="btn btn-primary verify-user" data-user-id="${user.id}">Verify</button>
                    <button class="btn btn-danger suspend-user" data-user-id="${user.id}">Suspend</button>
                    <button class="btn btn-secondary delete-user" data-user-id="${user.id}">Delete</button>
                    <button class="btn btn-primary edit-user" data-user-id="${user.id}">Edit</button>
                </td>
            `;
            userList.appendChild(row);
        });
      
      // Attach event listeners
      document.querySelectorAll(".assign-role").forEach(button => {
          button.addEventListener("click", function () {
              let newRole = prompt("Enter new role (user, agent, admin):");
              if(newRole) {
                  updateUserRole(this.dataset.userId, newRole);
              }
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
// Search Users Function
// ---------------------------
function searchUsers(searchTerm) {
    // Simple validation: if search term is empty, show a message and do nothing.
    if (!searchTerm) {
      alert("Please enter a search term.");
      return;
    }
    
    const rows = document.querySelectorAll("#admin-user-list tr");
    let found = false;
    rows.forEach(row => {
      const rowText = row.textContent.toLowerCase();
      if (rowText.indexOf(searchTerm.toLowerCase()) !== -1) {
        row.style.display = "";
        found = true;
      } else {
        row.style.display = "none";
      }
    });
    
    if (!found) {
      alert("No user found with the provided search term.");
    }
  }
  
  
  // Bind the search events in your DOMContentLoaded handler
  document.addEventListener("DOMContentLoaded", function(){
    const searchBtn = document.getElementById("search-user-btn");
    const searchInput = document.getElementById("user-search");
    if (searchBtn && searchInput) {
      searchBtn.addEventListener("click", function(){
        const searchTerm = searchInput.value.trim();
        searchUsers(searchTerm);
      });
      // Also bind the Enter key on the input field
      searchInput.addEventListener("keypress", function(e){
        if(e.key === "Enter"){
          e.preventDefault();
          const searchTerm = searchInput.value.trim();
          searchUsers(searchTerm);
        }
      });
    }
  });
  


   // ---------------------------
// Function for Logout
// ---------------------------

const logoutLink = document.getElementById('logout-link');
if (logoutLink) {
  logoutLink.addEventListener('click', function(e) {
    e.preventDefault();
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_id');
    window.location.href = '/';
  });
}
  
