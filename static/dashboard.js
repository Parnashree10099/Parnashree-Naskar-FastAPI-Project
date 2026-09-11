const userEmail = localStorage.getItem("userEmail");

async function loadProfile() {

    const response = await fetch(`/profile?email=${userEmail}`);

    const user = await response.json();

    document.getElementById("fullName").innerText = user.full_name;
    document.getElementById("email").innerText = user.email;
    document.getElementById("phone").innerText = user.phone;
    document.getElementById("dob").innerText = user.dob;

    document.getElementById("editFullName").value = user.full_name;
    document.getElementById("editEmail").value = user.email;
    document.getElementById("editPhone").value = user.phone;
    document.getElementById("editDob").value = user.dob;
}

loadProfile();


document.getElementById("profileForm").addEventListener("submit", async function(event) {

    event.preventDefault();

    const fullName = document.getElementById("editFullName").value;
    const phone = document.getElementById("editPhone").value;
    const dob = document.getElementById("editDob").value;

    const response = await fetch("/update-profile", {
        method: "PUT",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            email: userEmail,
            full_name: fullName,
            phone: phone,
            dob: dob
        })
    });

    const result = await response.json();

    document.getElementById("message").innerText = result.message;

    if (result.success) {
        loadProfile();
    }
});


document.getElementById("uploadButton").addEventListener("click", async function() {

    const fileInput = document.getElementById("profilePicture");
    const selectedFile = fileInput.files[0];

    if (!selectedFile) {
        document.getElementById("message").innerText =
            "Please select a picture first!";
        return;
    }

    const formData = new FormData();

    formData.append("email", userEmail);
    formData.append("file", selectedFile);

    try {
        const response = await fetch("/upload-profile-picture", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        console.log("BACKEND RESPONSE:", result);

        document.getElementById("message").innerText =
            result.message || "No message received";

        if (result.success === true && result.image_url) {
            document.getElementById("profileImage").src =
                result.image_url + "?t=" + new Date().getTime();
        } else {
            document.getElementById("message").innerText =
                JSON.stringify(result);
        }

    } catch (error) {
        console.log("UPLOAD ERROR:", error);

        document.getElementById("message").innerText =
            "Upload error: " + error.message;
    }
});

document.getElementById("deletePictureButton").addEventListener("click", async function() {

    const response = await fetch(
        `/delete-profile-picture?email=${encodeURIComponent(userEmail)}`,
        {
            method: "DELETE"
        }
    );

    const result = await response.json();

    document.getElementById("message").innerText = result.message;

    if (result.success === true) {
        document.getElementById("profileImage").src = "";
    }
});

function logoutUser() {
    localStorage.removeItem("userEmail");
    window.location.href = "/login";
};