const API_BASE = "http://localhost:5000/api";
const PLAYER_ID = 2;

let currentPlotId = null;
let currentCropId = null;
let cropTypes = [];
let prices = {};
let currentPage = "dashboard";
let harvestingCrops = new Set();

// ════════════════════════════════════════════════════════════════
// INICIALIZACIÓN
// ════════════════════════════════════════════════════════════════

async function init() {
    try {
        await loadPlayer();
        await loadPrices();
        await loadCropTypes();
        await loadFarms();
    } catch (error) {
        showMessage("Error: " + error.message, "error");
    }
}

// ════════════════════════════════════════════════════════════════
// CARGAR DATOS
// ════════════════════════════════════════════════════════════════

async function loadPlayer() {
    const response = await fetch(`${API_BASE}/player/${PLAYER_ID}`);
    if (!response.ok) throw new Error("No se pudo cargar el jugador");

    const player = await response.json();
    document.getElementById("sidebarName").textContent = player.name;
    document.getElementById("sidebarMoney").textContent = `$${player.money.toLocaleString()}`;
    document.getElementById("sidebarLevel").textContent = `Level ${player.level}`;
    document.getElementById("headerMoney").textContent = player.money.toLocaleString();
    document.getElementById("headerLevel").textContent = player.level;
}

async function loadPrices() {
    const response = await fetch(`${API_BASE}/prices`);
    if (!response.ok) throw new Error("No se pudo cargar precios");

    const pricesData = await response.json();
    pricesData.forEach(p => {
        prices[p.crop_type_id] = {
            seed_price: p.seed_price,
            crop_price: p.crop_price
        };
    });
}

async function loadCropTypes() {
    const response = await fetch(`${API_BASE}/crop-types`);
    if (!response.ok) throw new Error("No se pudo cargar tipos de cultivos");
    cropTypes = await response.json();
}

// Helper: Parse timestamp as UTC
function parseUTCDate(dateString) {
    if (!dateString.includes('Z') && !dateString.includes('+')) {
        dateString += 'Z';
    }
    return new Date(dateString);
}

async function loadFarms() {
    const response = await fetch(`${API_BASE}/player/${PLAYER_ID}/houses`);
    if (!response.ok) throw new Error("No se pudo cargar las casas");

    const houses = await response.json();

    if (houses.length === 0) {
        document.getElementById("farms-section").innerHTML = `
            <div class="section">
                <div class="section-title">🌾 My Farms</div>
                <p style="color: var(--text-secondary);">No tienes granjas aún.</p>
            </div>
        `;
        return;
    }

    let farmsHTML = '';

    for (const house of houses) {
        const plotsResponse = await fetch(`${API_BASE}/house/${house.id}/plots`);
        const plots = await plotsResponse.json();

        farmsHTML += `
            <div class="section">
                <div class="section-title">🌾 ${house.name}</div>
                <div class="plots-grid">
        `;

        for (const plot of plots) {
            const cropResponse = await fetch(`${API_BASE}/plot/${plot.id}/crop`);
            const { crop } = await cropResponse.json();

            if (crop) {
                const cropType = crop.crop_types.name;
                const readyAt = parseUTCDate(crop.ready_at);
                const now = new Date();
                const isReady = now >= readyAt;

                if (isReady) {
                    farmsHTML += `
                        <div class="plot-card ready" onclick="harvestCrop(${crop.id}, '${cropType}', ${crop.yield_amount})">
                            <div class="plot-name">${plot.name}</div>
                            <div class="plot-emoji">🌾</div>
                            <div class="plot-crop-name">${cropType}</div>
                            <div class="plot-status">✨ Ready to Harvest!</div>
                        </div>
                    `;
                } else {
                    const timeLeftMs = readyAt - now;
                    const hours = Math.floor(timeLeftMs / 3600000);
                    const minutes = Math.floor((timeLeftMs % 3600000) / 60000);
                    const seconds = Math.floor((timeLeftMs % 60000) / 1000);
                    const timeStr = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

                    const cropPrice = prices[crop.crop_type_id]?.crop_price || 0;
                    const totalValue = crop.yield_amount * cropPrice;

                    farmsHTML += `
                        <div class="plot-card with-crop" id="plot-${crop.id}" data-crop-id="${crop.id}" data-crop-name="${cropType}" data-yield="${crop.yield_amount}" data-price="${cropPrice}" data-total="${totalValue}">
                            <div class="plot-name">${plot.name}</div>
                            <div class="plot-emoji">🌱</div>
                            <div class="plot-crop-name">${cropType}</div>
                            <div class="plot-time countdown" id="time-${crop.id}">${timeStr}</div>
                        </div>
                    `;
                }
            } else {
                farmsHTML += `
                    <div class="plot-card" onclick="openPlantModal(${plot.id})">
                        <div class="plot-name">${plot.name}</div>
                        <div class="plot-emoji">🌱</div>
                        <div class="plot-status">Click to plant</div>
                    </div>
                `;
            }
        }

        farmsHTML += `</div></div>`;
    }

    document.getElementById("farms-section").innerHTML = farmsHTML;
}

// ════════════════════════════════════════════════════════════════
// ACCIONES - PLANTAR
// ════════════════════════════════════════════════════════════════

function openPlantModal(plotId) {
    currentPlotId = plotId;

    const cropsListHTML = cropTypes.map(crop => {
        const seedPrice = prices[crop.id]?.seed_price || 0;
        return `
        <li class="crop-item" onclick="plantCrop(${crop.id}, ${seedPrice})">
            <div class="crop-name">🌾 ${crop.name}</div>
            <div class="crop-info">
                <span>⏱️ ${Math.floor(crop.growth_time / 60)}m</span>
                <span class="crop-price">🌱 $${seedPrice}</span>
            </div>
        </li>
    `}).join("");

    document.getElementById("cropsList").innerHTML = cropsListHTML;
    document.getElementById("plantModal").classList.add("active");
}

function closePlantModal() {
    document.getElementById("plantModal").classList.remove("active");
}

async function plantCrop(cropTypeId, seedPrice) {
    try {
        const buyResponse = await fetch(`${API_BASE}/player/${PLAYER_ID}/buy-seeds`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ crop_type_id: cropTypeId, quantity: 1 })
        });

        if (!buyResponse.ok) {
            const error = await buyResponse.json();
            throw new Error(error.error || "Error buying seeds");
        }

        const buyResult = await buyResponse.json();

        const plantResponse = await fetch(`${API_BASE}/plot/${currentPlotId}/plant`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ crop_type_id: cropTypeId })
        });

        if (!plantResponse.ok) throw new Error("Error al plantar");

        showMessage(`✅ ¡Semilla plantada! -$${seedPrice}`, "success");
        closePlantModal();
        setTimeout(() => {
            loadPlayer();
            loadFarms();
        }, 500);

    } catch (error) {
        showMessage("❌ " + error.message, "error");
    }
}

// ════════════════════════════════════════════════════════════════
// ACCIONES - COSECHAR Y VENDER
// ════════════════════════════════════════════════════════════════

async function harvestCrop(cropId, cropName, yieldAmount) {
    if (harvestingCrops.has(cropId)) return;
    harvestingCrops.add(cropId);

    try {
        const harvestResponse = await fetch(`${API_BASE}/crop/${cropId}/harvest`, {
            method: "POST"
        });

        if (!harvestResponse.ok) {
            const error = await harvestResponse.json();
            throw new Error(error.error || "Error al cosechar");
        }

        showMessage(`✅ ¡Cosechado! ${yieldAmount} unidades guardadas en el inventario`, "success");

        setTimeout(() => {
            loadPlayer();
            loadFarms();
        }, 500);

    } catch (error) {
        showMessage("❌ " + error.message, "error");
    } finally {
        harvestingCrops.delete(cropId);
    }
}

function openSellModal(cropId, cropName, yieldAmount, cropPrice) {
    currentCropId = cropId;
    const totalValue = yieldAmount * cropPrice;

    document.getElementById("sellInfo").innerHTML = `
        <div style="text-align: center; margin-bottom: 30px;">
            <div style="font-size: 3em; margin-bottom: 15px;">🌾</div>
            <div style="font-size: 1.2em; font-weight: 700; color: var(--text-primary); margin-bottom: 10px;">${cropName}</div>
            <div style="font-size: 1em; color: var(--text-secondary); margin-bottom: 20px;">
                ${yieldAmount} units × $${cropPrice} = <strong style="color: var(--yellow-gold); font-size: 1.3em;">$${totalValue}</strong>
            </div>
        </div>
        <button class="btn btn-sell" onclick="sellCrop()" style="width: 100%; margin-bottom: 10px;">
            💰 Sell for $${totalValue}
        </button>
        <button class="btn btn-secondary" onclick="closeSellModal()" style="width: 100%;">
            Cancel
        </button>
    `;

    document.getElementById("sellModal").classList.add("active");
}

function closeSellModal() {
    document.getElementById("sellModal").classList.remove("active");
}

async function sellCrop() {
    try {
        const response = await fetch(`${API_BASE}/crop/${currentCropId}/sell`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ player_id: PLAYER_ID })
        });

        if (!response.ok) throw new Error("Error al vender");

        const result = await response.json();
        showMessage(`✅ ¡Vendido! +$${result.total_revenue} 💸`, "success");

        try {
            await loadPlayer();
            await loadFarms();
        } catch (error) {
            console.error("Error reloading after sell:", error);
        }

        closeSellModal();

    } catch (error) {
        showMessage("❌ " + error.message, "error");
    }
}

// ════════════════════════════════════════════════════════════════
// UI HELPERS
// ════════════════════════════════════════════════════════════════

function setPage(page) {
    currentPage = page;
    document.querySelectorAll(".nav-link").forEach(link => link.classList.remove("active"));
    event.target.closest(".nav-link").classList.add("active");

    const titles = {
        dashboard: "Dashboard",
        farm: "My Farm",
        properties: "Properties",
        market: "Market",
        inventory: "Inventory"
    };

    document.getElementById("pageTitle").textContent = titles[page];
}

function showMessage(text, type = "info") {
    const msgDiv = document.getElementById("message");
    msgDiv.textContent = text;
    msgDiv.className = `message ${type} show`;
    setTimeout(() => msgDiv.classList.remove("show"), 3500);
}

// ════════════════════════════════════════════════════════════════
// COUNTDOWN TIMER
// ════════════════════════════════════════════════════════════════

function updateCountdowns() {
    const countdowns = document.querySelectorAll('.countdown');
    countdowns.forEach(el => {
        const id = el.id.replace('time-', '');
        const currentText = el.textContent;
        const parts = currentText.split(':').map(p => parseInt(p));

        let totalSeconds = parts[0] * 3600 + parts[1] * 60 + parts[2];
        totalSeconds = Math.max(0, totalSeconds - 1);

        const h = Math.floor(totalSeconds / 3600);
        const m = Math.floor((totalSeconds % 3600) / 60);
        const s = totalSeconds % 60;

        const newTime = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
        el.textContent = newTime;

        if (totalSeconds === 0) {
            const plotCard = document.getElementById(`plot-${id}`);
            if (plotCard) {
                const cropId = plotCard.dataset.cropId;
                const cropName = plotCard.dataset.cropName;
                const yieldAmount = plotCard.dataset.yield;

                plotCard.classList.remove('with-crop');
                plotCard.classList.add('ready');
                plotCard.onclick = () => harvestCrop(parseInt(cropId), cropName, parseInt(yieldAmount));

                plotCard.innerHTML = `
                    <div class="plot-name">${plotCard.querySelector('.plot-name').textContent}</div>
                    <div class="plot-emoji">🌾</div>
                    <div class="plot-crop-name">${cropName}</div>
                    <div class="plot-status">✨ Ready to Harvest!</div>
                `;
            }
        }
    });
}

setInterval(updateCountdowns, 1000);

// Modal close on outside click
document.getElementById("plantModal").addEventListener("click", (e) => {
    if (e.target.id === "plantModal") closePlantModal();
});

document.getElementById("sellModal").addEventListener("click", (e) => {
    if (e.target.id === "sellModal") closeSellModal();
});

// ════════════════════════════════════════════════════════════════
// START
// ════════════════════════════════════════════════════════════════

init();
