const logoutButton = document.getElementById("logoutButton")
const chart1div = document.getElementById("chart1")
const chart2div = document.getElementById("chart2")
const purchaseTableBody = document.getElementById("purchaseTableBody")

logoutButton?.addEventListener("click", async (e) => {
    e.preventDefault();
    document.cookie = "session=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;"
    window.location.href = "/";
});

new Chart(chart1div, {
    type: "bar",
    data: {
        labels: ["Złapanych pasażerów", "Wystawione mandaty", "Skuteczność kontroli", "Poziom strachu", "Ucieczki"],
        datasets: [{
            data: [142, 130, 95, 100, 12],
            backgroundColor: ["#60A5FA", "#34D399", "#FBBF24", "#F87171", "#A78BFA"],
            borderWidth: 0,
            borderRadius: 4,
            borderSkipped: false
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: "rgba(0,0,0,0.7)",
                borderColor: "rgba(255,255,255,0.1)",
                borderWidth: 1
            }
        },
        scales: {
            x: {
                grid: { color: "rgba(255,255,255,0.1)" },
                ticks: { color: "#9CA3AF" }
            },
            y: {
                grid: { color: "rgba(255,255,255,0.1)" },
                ticks: { color: "#9CA3AF" }
            }
        }
    }
});

new Chart(chart2div, {
    type: "line",
    data: {
        labels: ["6:00", "8:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00", "22:00"],
        datasets: [{
            label: "Wolne cm³ w tramwajach",
            data: [2000, -500, 1500, 1000, 500, -1200, 0, 3000, 5000],
            borderColor: "#F87171",
            backgroundColor: "rgba(248, 113, 113, 0.1)",
            tension: 0.4,
            fill: true
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: "rgba(0,0,0,0.7)",
                borderColor: "rgba(255,255,255,0.1)",
                borderWidth: 1
            }
        },
        scales: {
            x: {
                grid: { color: "rgba(255,255,255,0.1)" },
                ticks: { color: "#9CA3AF" }
            },
            y: {
                grid: { color: "rgba(255,255,255,0.1)" },
                ticks: { color: "#9CA3AF" }
            }
        }
    }
});

// Populate purchase table with fake data
const purchases = [
    {
        linia: "52",
        kierunek: "Czerwone Maki P+R",
        opoznienie: "+ 124 min",
        status: "delayed"
    },
    {
        linia: "50",
        kierunek: "Kurdwanów P+R",
        opoznienie: "+ 45 min",
        status: "delayed"
    },
    {
        linia: "18",
        kierunek: "Czerwone Maki P+R",
        opoznienie: "+ 12 min",
        status: "delayed"
    },
    {
        linia: "4",
        kierunek: "Wzgórza Krzesławickie",
        opoznienie: "Brak opóźnienia",
        status: "ontime"
    },
    {
        linia: "20",
        kierunek: "Mały Płaszów P+R",
        opoznienie: "+ 212 min",
        status: "delayed"
    },
    {
        linia: "8",
        kierunek: "Borek Fałęcki",
        opoznienie: "+ 89 min",
        status: "delayed"
    },
    {
        linia: "13",
        kierunek: "Nowy Bieżanów P+R",
        opoznienie: "+ 14 min",
        status: "delayed"
    },
    {
        linia: "24",
        kierunek: "Kurdwanów P+R",
        opoznienie: "+ 60 min",
        status: "delayed"
    },
    {
        linia: "3",
        kierunek: "Nowy Bieżanów P+R",
        opoznienie: "Brak opóźnienia",
        status: "ontime"
    },
    {
        linia: "14",
        kierunek: "Mistrzejowice",
        opoznienie: "+ 33 min",
        status: "delayed"
    },
    {
        linia: "9",
        kierunek: "Nowy Bieżanów P+R",
        opoznienie: "+ 67 min",
        status: "delayed"
    },
    {
        linia: "22",
        kierunek: "Borek Fałęcki",
        opoznienie: "+ 19 min",
        status: "delayed"
    },
    {
        linia: "1",
        kierunek: "Wzgórza Krzesławickie",
        opoznienie: "+ 41 min",
        status: "delayed"
    },
    {
        linia: "5",
        kierunek: "Wzgórza Krzesławickie",
        opoznienie: "+ 24 min",
        status: "delayed"
    },
    {
        linia: "17",
        kierunek: "Czerwone Maki P+R",
        opoznienie: "Brak opóźnienia",
        status: "ontime"
    },
    {
        linia: "74",
        kierunek: "Mistrzejowice",
        opoznienie: "+ 55 min",
        status: "delayed"
    },
    {
        linia: "11",
        kierunek: "Czerwone Maki P+R",
        opoznienie: "+ 11 min",
        status: "delayed"
    },
    {
        linia: "19",
        kierunek: "Borek Fałęcki",
        opoznienie: "+ 99 min",
        status: "delayed"
    },
    {
        linia: "21",
        kierunek: "Os. Piastów",
        opoznienie: "+ 38 min",
        status: "delayed"
    },
    {
        linia: "72",
        kierunek: "Cmentarz Rakowicki",
        opoznienie: "+ 8 min",
        status: "delayed"
    }
];

purchases.forEach(purchase => {
    const row = document.createElement("tr")
    row.className = "border-b border-gray-700"
    const colorClass = purchase.status === "ontime" ? "text-green-500" : "text-red-500";
    row.innerHTML = `
        <td class="py-2">${purchase.linia}</td>
        <td class="py-2">${purchase.kierunek}</td>
        <td class="py-2 font-bold ${colorClass}">${purchase.opoznienie}</td>
    `
    purchaseTableBody.appendChild(row)
})
