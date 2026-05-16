document.addEventListener("DOMContentLoaded", () => {
  const generateBtn = document.getElementById("generateBtn");
  const btnText = document.getElementById("btnText");
  const spinner = document.getElementById("spinner");
  const resultContainer = document.getElementById("resultContainer");
  const resultUrl = document.getElementById("resultUrl");
  const errorContainer = document.getElementById("errorContainer");

  generateBtn.addEventListener("click", async () => {
    generateBtn.disabled = true;
    btnText.textContent = "Generating...";
    spinner.classList.remove("hidden");
    resultContainer.classList.add("hidden");
    errorContainer.classList.add("hidden");

    try {
      const response = await fetch("/api/create", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        }
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to generate instance.");
      }

      if (data.url) {
        const urlStr = data.url.startsWith("http") ? data.url : `http://${data.url}`;
        resultUrl.href = urlStr;
        resultUrl.textContent = urlStr;
        resultContainer.classList.remove("hidden");
      } else {
        throw new Error("Invalid response from server.");
      }
    } catch (err) {
      errorContainer.textContent = err.message;
      errorContainer.classList.remove("hidden");
    } finally {
      generateBtn.disabled = false;
      btnText.textContent = "Generate Instance";
      spinner.classList.add("hidden");
    }
  });
});
