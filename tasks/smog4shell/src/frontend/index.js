document.addEventListener("DOMContentLoaded", () => {
  const generateBtn = document.getElementById("generateBtn");
  const btnText = document.getElementById("btnText");
  const spinner = document.getElementById("spinner");
  const resultContainer = document.getElementById("resultContainer");
  const resultUrl = document.getElementById("resultUrl");
  const resultTtl = document.getElementById("resultTtl");
  const releaseBtn = document.getElementById("releaseBtn");
  const errorContainer = document.getElementById("errorContainer");

  async function login() {
    try {
      await fetch("/api/login", { method: "POST", credentials: "include" })
    } catch {
      console.error("login failed");
    }
  }

  login()

  generateBtn.addEventListener("click", async () => {
    generateBtn.disabled = true;
    btnText.textContent = "Generowanie...";
    spinner.classList.remove("hidden");
    resultContainer.classList.add("hidden");
    errorContainer.classList.add("hidden");

    try {
      const response = await fetch("/api/create", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        credentials: "include"
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Nie udało się wygenerować instancji.");
      }

      if (data.url) {
        const urlStr = data.url.startsWith("http") ? data.url : `http://${data.url}`;
        resultUrl.href = urlStr;
        resultUrl.textContent = urlStr;
        const ttlMinutes = Math.max(1, Math.floor((data.ttlSeconds || 300) / 60));
        resultTtl.textContent = `Ta instancja będzie dostępna przez ${ttlMinutes} minut.`;
        resultContainer.classList.remove("hidden");
      } else {
        throw new Error("Nieprawidłowa odpowiedź serwera.");
      }
    } catch (err) {
      errorContainer.textContent = err.message;
      errorContainer.classList.remove("hidden");
    } finally {
      generateBtn.disabled = false;
      btnText.textContent = "Generuj instancję";
      spinner.classList.add("hidden");
    }
  });

  releaseBtn.addEventListener("click", async () => {
    releaseBtn.disabled = true;
    errorContainer.classList.add("hidden");

    try {
      const response = await fetch("/api/release", {
        method: "POST",
        credentials: "include"
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Nie udało się zwolnić instancji.");
      }

      resultContainer.classList.add("hidden");
      resultUrl.href = "#";
      resultUrl.textContent = "";
      resultTtl.textContent = "";
    } catch (err) {
      errorContainer.textContent = err.message;
      errorContainer.classList.remove("hidden");
    } finally {
      releaseBtn.disabled = false;
    }
  });
});
