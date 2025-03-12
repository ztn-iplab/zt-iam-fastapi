
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
    fetch("/api/auth/logout", { method: "POST" })
      .then(() => {
        window.location.href = '/api/auth/login_form';
          });
    }
}, 60000);


// ---------------------------
// Admin Functions: Fetch Users & Bind Actions
// ---------------------------
function fetchUsersForAdmin() {
  fetch("/admin/users", {
      method: "GET",
      headers: { "Content-Type": "application/json" }
  })
  .then(res => res.json())
  .then(users => {
      const userList = document.getElementById("admin-user-list");
      userList.innerHTML = "";

      users.forEach(user => {
          const roleName = roleMapping[user.role] || user.role;
          const fullName = user.name || "N/A";
          const mobileNumber = user.mobile_number || "N/A"; // ✅ Fetch from backend (SIM-based)
          const email = user.email || "N/A";

          
          const row = document.createElement("tr");
          row.innerHTML = `
              <td>${user.id}</td>
              <td>${fullName}</td>
              <td>${mobileNumber}</td>
              <td class="user-email">${email}</td>
              <td>${roleName}</td>
              <td class="action-buttons">
                  <button class="btn btn-sm btn-primary assign-role" data-user-id="${user.id}">Role</button>
                  <button class="btn btn-sm btn-success verify-user" data-user-id="${user.id}">Verify</button>
                  <button class="btn btn-sm btn-danger suspend-user" data-user-id="${user.id}">Suspend</button>
                  <button class="btn btn-sm btn-danger delete-user" data-user-id="${user.id}">Delete</button>
                  <button class="btn btn-sm btn-secondary edit-user" data-user-id="${user.id}">Edit</button>
              </td>
          `;
          userList.appendChild(row);
      });

      // Attach event listeners for each action
      document.querySelectorAll(".assign-role").forEach(button => {
          button.addEventListener("click", function () {
              let newRole = prompt("Enter new role (user, agent, admin):");
              if (newRole) {
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
  fetch("/admin/assign_role", {
      method: "POST",
      headers: { 
          "Content-Type": "application/json"
      },
      credentials: "include", // Ensures cookies are sent with the request
      body: JSON.stringify({ user_id: userId, role_name: newRole }) // Ensure you're sending role_name
  })
  .then(response => response.json())
  .then(data => {
      if (data.error) {
          alert("Error: " + data.error);
      } else {
          alert("Role updated successfully!");
          fetchUsersForAdmin(); // Refresh the list to reflect changes
      }
  })
  .catch(error => console.error("Error updating role:", error));
}

// -------------------------
// Suspend the user
//--------------------------

function suspendUser(userId) {
  if (!confirm("Are you sure you want to suspend this user? Their account will be disabled and marked for deletion.")) {
    return;
  }

  fetch(`/admin/suspend_user/${userId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include" // Ensure cookies are included for authentication
  })
  .then(response => response.json())
  .then(data => {
      if (data.error) {
          alert("Error: " + data.error);
      } else {
          alert(data.message); // Correctly display the returned message
          fetchUsersForAdmin(); // Refresh the user list
      }
  })
  .catch(error => console.error("Error suspending user:", error));
}



// verify the user

function verifyUser(userId) {
  if (!confirm("Are you sure you want to verify this user?")) {
    return;
  }

  fetch(`/admin/verify_user/${userId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include" // Ensures authentication cookies are sent
  })
  .then(response => response.json())
  .then(data => {
      if (data.error) {
          alert("Error: " + data.error);
      } else {
          alert("User has been verified and activated.");
          fetchUsersForAdmin(); // Refresh the user list
      }
  })
  .catch(error => console.error("Error verifying user:", error));
}


// -------------------------
// permanently Delete the user
//--------------------------

function deleteUser(userId) {
  if (!confirm("Are you sure you want to permanently delete this user? This action CANNOT be undone!")) {
    return;
  }

  fetch(`/admin/delete_user/${userId}`, {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    credentials: "include" // Include authentication cookies
  })
  .then(response => response.json())
  .then(data => {
      if (data.error) {
          alert("Error: " + data.error);
      } else {
          alert("User permanently deleted.");
          fetchUsersForAdmin(); // Refresh the user list
      }
  })
  .catch(error => console.error("Error deleting user:", error));
}


// -------------------------
// Edit the user
//--------------------------

function editUser(userId) {
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
  
  fetch(`/admin/edit_user/${userId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include", // Ensure cookies are included
      body: JSON.stringify(payload)
  })
  .then(response => response.json())
  .then(data => {
      if (data.error) {
          alert("Error updating user: " + data.error);
      } else {
          alert(data.message || "User updated successfully!");
          fetchUsersForAdmin(); // Refresh the list
      }
  })
  .catch(error => console.error("Error editing user:", error));
}


// ---------------------------
// Search Users Function
// ---------------------------
function searchUsers(searchTerm) {
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

/// ---------------------------
// Bind All Events on DOMContentLoaded
// ---------------------------
document.addEventListener("DOMContentLoaded", function(){
  // Bind search events
  const searchBtn = document.getElementById("search-user-btn");
  const searchInput = document.getElementById("user-search");
  if (searchBtn && searchInput) {
    searchBtn.addEventListener("click", function(){
      const searchTerm = searchInput.value.trim();
      searchUsers(searchTerm);
    });
    searchInput.addEventListener("keypress", function(e){
      if(e.key === "Enter"){
        e.preventDefault();
        const searchTerm = searchInput.value.trim();
        searchUsers(searchTerm);
      }
    });
  }

  // ---------------------------
  // 🎯 Open Add User Modal
  // ---------------------------
  const addUserBtn = document.getElementById("add-user-btn");
  if (addUserBtn) {
    addUserBtn.addEventListener("click", function() {
      console.log("✅ Add User button clicked");

      const modalEl = document.getElementById("addUserModal");
      if (!modalEl) {
        console.error("❌ Modal element with id 'addUserModal' not found.");
        return;
      }

      // ✅ Bootstrap 5 API to show the modal
      const addUserModal = new bootstrap.Modal(modalEl);
      addUserModal.show();

      // ✅ Ensure fetchGeneratedSIM() only runs if function exists
      if (typeof fetchGeneratedSIM === "function") {
        fetchGeneratedSIM();
      } else {
        console.error("❌ fetchGeneratedSIM() function is not defined!");
      }
    });
  } else {
    console.error("❌ Add User button (id 'add-user-btn') not found in the DOM.");
  }

  // ---------------------------
// 🎯 Handle Manual SIM Refresh
// ---------------------------
document.getElementById("generate-mobile-btn").addEventListener("click", function() {
  fetchGeneratedSIM(); // ✅ Call the function to get new SIM details
});

  // ---------------------------
// 🎯 Fetch Auto-Generated SIM Details & Update Input Fields
// ---------------------------
function fetchGeneratedSIM() {
  fetch("/admin/generate_sim", { method: "GET", credentials: "include" })
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        alert("❌ Error fetching SIM details: " + data.error);
      } else {
        // ✅ Update the input fields with generated values
        document.getElementById("generated-mobile").value = data.mobile_number;
        document.getElementById("generated-iccid").value = data.iccid;

        // ✅ Store values globally for form submission
        window.generatedSIM = {
          mobile_number: data.mobile_number,
          iccid: data.iccid
        };

        console.log(`✅ SIM Updated: ICCID ${data.iccid}, Mobile ${data.mobile_number}`);
      }
    })
    .catch(error => {
      console.error("❌ Error generating SIM:", error);
      alert("❌ Unexpected error occurred while generating SIM.");
    });
}



  // ---------------------------
// Admin: Add New User Form Submission (Modal)
// ---------------------------
const addUserForm = document.getElementById("add-user-form");
if (addUserForm) {
  addUserForm.addEventListener("submit", async function(e) {
    e.preventDefault();

    // ✅ Get values from the form fields (not from background storage)
    const firstName = document.getElementById("add-first-name").value.trim();
    const lastName = document.getElementById("add-last-name").value.trim();
    const email = document.getElementById("add-email").value.trim();
    const country = document.getElementById("add-country").value.trim();
    const password = document.getElementById("add-password").value.trim();
    const mobileNumber = document.getElementById("generated-mobile").value.trim(); // ✅ Use the visible input field
    const iccid = document.getElementById("generated-iccid").value.trim(); // ✅ Use the visible input field

    if (!firstName || !email || !country || !password || !mobileNumber || !iccid) {
      alert("❌ Please fill in all required fields.");
      return;
    }

    // ✅ Build user payload with displayed values
    const payload = {
      first_name: firstName,
      last_name: lastName,
      email: email,
      password: password,
      country: country,
      mobile_number: mobileNumber, // ✅ Now using displayed input value
      iccid: iccid  // ✅ Now using displayed input value
    };

    console.log("📡 Sending registration payload:", payload); // Debugging step

    // ✅ Step 3: Send registration request
    const registerResponse = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(payload)
    });

    const registerData = await registerResponse.json();
    console.log("✅ Server Response:", registerData);

    if (registerData.error) {
      alert("❌ Error registering user: " + registerData.error);
    } else {
      alert(`✅ User registered successfully with Mobile: ${registerData.mobile_number}, ICCID: ${registerData.iccid}`);
      fetchUsersForAdmin(); // ✅ Refresh user list

      // ✅ Hide the modal after successful registration
      const addUserModal = bootstrap.Modal.getOrCreateInstance(document.getElementById("addUserModal"));
      addUserModal.hide();
      addUserForm.reset();
    }
  });
}



  // ---------------------------
  // Logout Functionality
  // ---------------------------
  const logoutLink = document.getElementById("logout-link");
  if (logoutLink) {
    logoutLink.addEventListener("click", function(e){
      e.preventDefault();
      fetch("/api/auth/logout", { method: "POST" })
          .then(() => {
              window.location.href = "/api/auth/login_form";
          });
    });
  }
});
