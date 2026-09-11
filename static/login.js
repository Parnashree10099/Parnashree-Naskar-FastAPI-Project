document.getElementById("loginForm").addEventListener("submit", async function(event) {

    event.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const response = await fetch("/login", {
        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            email: email,
            password: password
        })
    });

const result = await response.json();

document.getElementById("message").innerText = result.message;

if (result.redirect === "/dashboard") {
    localStorage.setItem("userEmail", email);
    window.location.href = "/dashboard";
}

else if (result.redirect === "/verify") {
    localStorage.setItem("userEmail", email);
    window.location.href = "/verify";
}
});