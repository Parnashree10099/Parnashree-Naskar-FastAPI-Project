document.getElementById("verifyForm").addEventListener("submit", async function(event) {

    event.preventDefault();

    const email = document.getElementById("verifyEmail").value;
    const otp = document.getElementById("otp").value;

    const response = await fetch("/verify-email", {
        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            email: email,
            otp: otp
        })
    });

    const result = await response.json();

    document.getElementById("message").innerText = result.message;
});