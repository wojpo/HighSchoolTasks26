const logoutButton = document.getElementById("logoutButton")
const flagButton = document.getElementById("flagButton")

logoutButton?.addEventListener("click", async (e) => {
    e.preventDefault();
    document.cookie = "session=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;"
    window.location.href = "/";
});

flagButton?.addEventListener("click", async (e) => {
    e.preventDefault();
    try{
        const response = await fetch("/api/flag")
        if(!response.ok) {
            throw new Error("Request failed")
        }
        const { flag } = await response.json()
        const flagParagraph = document.createElement("p")
        flagParagraph.textContent = flag
        flagParagraph.className = "mx-auto text-center text-2xl font-bold"
        window.alert("Proszę czekać flaga spóźni się o 15s")
        setTimeout(() => {
            flagButton.replaceWith(flagParagraph)
        }, 60000);
    }
    catch{
        window.alert("Coś poszło nie tak, spróbuj ponownie później...")
    }

});