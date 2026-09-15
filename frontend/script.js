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
                    const cropPrice = prices[crop.crop_type_id]?.crop_price || 0;
                    const totalValue = crop.yield_amount * cropPrice;

                    farmsHTML += `
                        <div class="plot-card ready" onclick="harvestCrop(${crop.id}, '${cropType}', ${crop.yield_amount})">
                            <div class="plot-name">${plot.name}</div>
                            <div class="plot-emoji">🌾</div>
                            <div class="plot-crop-name">${cropType}</div>
                            <div class="plot-yield">📦 ${crop.yield_amount} unidades</div>
                            <div class="plot-value">💰 $${totalValue}</div>
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

async function loadInventory() {
    const response = await fetch(`${API_BASE}/player/${PLAYER_ID}/inventory`);
    if (!response.ok) throw new Error("No se pudo cargar inventario");

    const crops = await response.json();

    if (crops.length === 0) {
        document.getElementById("farms-section").innerHTML = `
            <div class="section">
                <div class="section-title">🎒 Inventario</div>
                <p style="color: var(--text-secondary);">No tienes cultivos cosechados aún.</p>
            </div>
        `;
        return;
    }

    let inventoryHTML = `
        <div class="section">
            <div class="section-title">🎒 Inventario (${crops.length})</div>
            <div class="inventory-grid">
    `;

    crops.forEach(crop => {
        const cropType = crop.crop_types.name;
        const cropPrice = prices[crop.crop_type_id]?.crop_price || 0;
        const totalYield = crop.total_yield;
        const itemId = `sell-${crop.crop_type_id}`;

        inventoryHTML += `
            <div class="inventory-item">
                <div class="item-header">
                    <div class="item-name">${cropType}</div>
                    <div class="item-yield">x${totalYield}</div>
                </div>
                <div style="margin: 12px 0;">
                    <label style="font-size: 0.8em; color: var(--text-secondary); display: block; margin-bottom: 6px;">
                        Quantity:
                    </label>
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <input type="range" id="${itemId}-qty" min="1" max="${totalYield}" value="${totalYield}"
                               style="flex: 1; cursor: pointer;"
                               onchange="updateBatchTotal('${crop.crop_type_id}', ${cropPrice})">
                        <span id="${itemId}-num" style="font-weight: 700; min-width: 30px; text-align: right;">${totalYield}</span>
                    </div>
                </div>
                <div class="item-value" id="${itemId}-total">💰 $${(totalYield * cropPrice).toLocaleString()}</div>
                <button class="btn btn-sell" onclick="sellBatch('${crop.crop_type_id}', '${cropType}', ${cropPrice})" style="width: 100%; margin-top: 10px;">
                    Sell <span id="${itemId}-btn-qty">${totalYield}</span>x
                </button>
            </div>
        `;
    });

    inventoryHTML += `</div></div>`;
    document.getElementById("farms-section").innerHTML = inventoryHTML;
}

function updateBatchTotal(cropTypeId, cropPrice) {
    const itemId = `sell-${cropTypeId}`;
    const qtyInput = document.getElementById(`${itemId}-qty`);
    const qtyDisplay = document.getElementById(`${itemId}-num`);
    const totalDisplay = document.getElementById(`${itemId}-total`);
    const btnQty = document.getElementById(`${itemId}-btn-qty`);

    if (qtyInput) {
        const qty = parseInt(qtyInput.value) || 1;
        const total = qty * cropPrice;
        qtyDisplay.textContent = qty;
        totalDisplay.textContent = `💰 $${total.toLocaleString()}`;
        btnQty.textContent = qty;
    }
}

async function sellBatch(cropTypeId, cropName, cropPrice) {
    try {
        const itemId = `sell-${cropTypeId}`;
        const qtyInput = document.getElementById(`${itemId}-qty`);
        const quantity = parseInt(qtyInput.value) || 1;

        const response = await fetch(`${API_BASE}/crops/sell-batch`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                player_id: PLAYER_ID,
                crop_type_id: cropTypeId,
                quantity: quantity
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || "Error al vender");
        }

        const result = await response.json();
        showMessage(`✅ ¡Vendidos ${result.sold_yield} unidades de ${cropName}! +$${result.total_revenue} 💸`, "success");

        await loadPlayer();
        await loadInventory();
    } catch (error) {
        console.error("Batch sell error:", error);
        showMessage(`❌ Error: ${error.message}`, "error");
    }
}

async function sellAllCrops(cropTypeId, cropName, totalYield, cropPrice) {
    try {
        // Get all crops of this type from the plot data
        const farmsResponse = await fetch(`${API_BASE}/player/${PLAYER_ID}/houses`);
        const houses = await farmsResponse.json();

        let cropToSell = null;

        for (const house of houses) {
            const plotsResponse = await fetch(`${API_BASE}/house/${house.id}/plots`);
            const plots = await plotsResponse.json();

            for (const plot of plots) {
                const cropResponse = await fetch(`${API_BASE}/plot/${plot.id}/crop`);
                const { crop } = await cropResponse.json();

                if (crop && crop.crop_type_id == cropTypeId && crop.harvested_at) {
                    cropToSell = crop;
                    break;
                }
            }
            if (cropToSell) break;
        }

        if (!cropToSell) {
            showMessage("❌ No hay cultivos para vender", "error");
            return;
        }

        const sellResponse = await fetch(`${API_BASE}/crop/${cropToSell.id}/sell`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ player_id: PLAYER_ID })
        });

        if (!sellResponse.ok) throw new Error("Error al vender");

        const result = await sellResponse.json();
        showMessage(`✅ ¡Vendido! +$${result.total_revenue} 💸`, "success");

        await loadPlayer();
        await loadInventory();

    } catch (error) {
        showMessage("❌ " + error.message, "error");
    }
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

        const result = await harvestResponse.json();
        const actualYield = result.yield_amount || yieldAmount;

        showMessage(`✅ ¡Cosechado! ${actualYield} unidades guardadas en el inventario`, "success");

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

async function setPage(page) {
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

    try {
        if (page === "dashboard" || page === "farm") {
            await loadFarms();
        } else if (page === "inventory") {
            await loadInventory();
        }
    } catch (error) {
        showMessage("❌ " + error.message, "error");
    }
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
                const cropId = parseInt(plotCard.dataset.cropId);
                const cropName = plotCard.dataset.cropName;
                const yieldAmount = parseInt(plotCard.dataset.yield) || 10;

                plotCard.classList.remove('with-crop');
                plotCard.classList.add('ready');
                plotCard.onclick = () => harvestCrop(cropId, cropName, yieldAmount);

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
