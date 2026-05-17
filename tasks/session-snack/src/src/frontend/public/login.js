const username = document.getElementById("username")
const password = document.getElementById("password")
const loginButton = document.getElementById("loginButton")

loginButton.addEventListener("click", async (e) => {
    e.preventDefault()
    const response = await fetch("/api/login", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({username: username.value, password: password.value})})
    if (response.ok) {
        window.location.href = '/app/panel'
    }
    else {
        window.alert("Niepoprawne dane logowania")
    }
})