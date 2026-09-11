document.getElementById("resetPasswordForm").addEventListener("submit", async function(event) {

    event.preventDefault();

    const otp = document.getElementById("otp").value;

    const newPassword = document.getElementById("newPassword").value;

    const confirmPassword =
        document.getElementById("confirmPassword").value;

    if (newPassword !== confirmPassword) {

        document.getElementById("message").innerText =
            "Passwords do not match!";

        return;
    }

    const email = localStorage.getItem("resetEmail");

    const response = await fetch("/reset-password", {

        method: "PUT",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            email: email,
            otp: otp,
            new_password: newPassword
        })
    });

    const result = await response.json();

    document.getElementById("message").innerText = result.message;

    if (result.success === true) {

        localStorage.removeItem("resetEmail");

        setTimeout(function() {
            window.location.href = "/login";
        }, 1500);
    }
});