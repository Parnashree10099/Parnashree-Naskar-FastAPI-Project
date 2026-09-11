document.getElementById("changePasswordForm").addEventListener("submit", async function(event) {

    event.preventDefault();

    const currentPassword =
        document.getElementById("currentPassword").value;

    const newPassword =
        document.getElementById("newPassword").value;

    const confirmPassword =
        document.getElementById("confirmPassword").value;

    if (newPassword !== confirmPassword) {
        document.getElementById("message").innerText =
            "New passwords do not match!";
        return;
    }

    const userEmail = localStorage.getItem("userEmail");

    const response = await fetch("/change-password", {
        method: "PUT",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            email: userEmail,
            current_password: currentPassword,
            new_password: newPassword
        })
    });

    const result = await response.json();

    document.getElementById("message").innerText = result.message;
});