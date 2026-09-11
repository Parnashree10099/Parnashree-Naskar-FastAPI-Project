document.getElementById("forgotPasswordForm").addEventListener("submit", async function(event) {

    event.preventDefault();

    const email = document.getElementById("email").value;

    document.getElementById("message").innerText = "Sending OTP...";

    try {

        const response = await fetch("/forgot-password", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                email: email
            })
        });

        const result = await response.json();

        document.getElementById("message").innerText = result.message;

        if (result.success === true) {

            localStorage.setItem("resetEmail", email);

            window.location.href = "/reset-password";
        }

    } catch (error) {

        document.getElementById("message").innerText =
            "Error: " + error.message;

    }
});