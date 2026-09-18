const API_BASE = "http://localhost:5000/api";

let PLAYER_ID = null;
let currentPlotId = null;
let currentCropId = null;
let cropTypes = [];
let prices = {};
let currentPage = "dashboard";
let harvestingCrops = new Set();

// ════════════════════════════════════════════════════════════════
// CACHE EN MEMORIA - Evita requests innecesarias
// ════════════════════════════════════════════════════════════════

const cache = {
    player: null,
    prices: null,
    cropTypes: null,
    houses: null,
    properties: null,
    plots: new Map() // plotId -> plot data
};

function invalidatePlayerCache() {
    cache.player = null;
}

function invalidatePlotsCache() {
    cache.plots.clear();
}

function invalidateFarmsCache() {
    cache.houses = null;
    cache.plots.clear();
}

function invalidatePropertiesCache() {
    cache.properties = null;
}

function invalidateAllCache() {
    cache.player = null;
    cache.prices = null;
    cache.cropTypes = null;
    cache.houses = null;
    cache.properties = null;
    cache.plots.clear();
}

// ════════════════════════════════════════════════════════════════
// AUTENTICACIÓN
// ════════════════════════════════════════════════════════════════

function getToken() {
    return localStorage.getItem("auth_token");
}

function setToken(token) {
    localStorage.setItem("auth_token", token);
}

function setPlayerId(playerId) {
    PLAYER_ID = playerId;
    localStorage.setItem("player_id", playerId);
}

// Fetch con JWT automático + validación de autenticación
async function fetchWithAuth(url, options = {}) {
    const token = getToken();
    const headers = {
        "Content-Type": "application/json",
        ...options.headers,
        ...(token && { "Authorization": `Bearer ${token}` })
    };

    const fetchOptions = { ...options };
    delete fetchOptions.headers;  // Quitar headers de options para evitar duplicado

    console.log("[fetchWithAuth]", url, "| Token:", token ? "SÍ" : "NO", "| Headers:", headers);

    const response = await fetch(url, { ...fetchOptions, headers });

    // Si token expiró (401), logout automáticamente
    if (response.status === 401) {
        logout();
        throw new Error("Sesión expirada. Por favor inicia sesión de nuevo.");
    }

    return response;
}

function getPlayerId() {
    return localStorage.getItem("player_id");
}

function logout() {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("player_id");
    PLAYER_ID = null;
    location.reload();
}

function switchLoginTab(tab) {
    document.querySelectorAll(".login-tab").forEach(el => el.classList.remove("active"));
    document.querySelectorAll(".login-form").forEach(el => el.classList.remove("active"));

    if (tab === "login") {
        document.querySelector(".login-tab:nth-child(1)").classList.add("active");
        document.getElementById("loginForm").classList.add("active");
    } else {
        document.querySelector(".login-tab:nth-child(2)").classList.add("active");
        document.getElementById("registerForm").classList.add("active");
    }
}

async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPassword").value;

    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const error = await response.json();
            document.getElementById("loginError").textContent = error.error;
            return;
        }

        const result = await response.json();
        setToken(result.token);
        setPlayerId(result.player_id);
        document.getElementById("loginModal").classList.remove("active");

        await init();
    } catch (error) {
        document.getElementById("loginError").textContent = "Error al conectar";
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const name = document.getElementById("registerName").value;
    const email = document.getElementById("registerEmail").value;
    const password = document.getElementById("registerPassword").value;
    const confirm = document.getElementById("registerConfirm").value;

    if (password !== confirm) {
        document.getElementById("registerError").textContent = "Las contraseñas no coinciden";
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, name, password })
        });

        if (!response.ok) {
            const error = await response.json();
            document.getElementById("registerError").textContent = error.error;
            return;
        }

        const result = await response.json();
        setToken(result.token);
        setPlayerId(result.player_id);
        document.getElementById("loginModal").classList.remove("active");

        await init();
    } catch (error) {
        document.getElementById("registerError").textContent = "Error al registrarse";
    }
}

// ════════════════════════════════════════════════════════════════
// INICIALIZACIÓN
// ════════════════════════════════════════════════════════════════

async function init() {
    try {
        console.log("[init] Iniciando carga de datos...");
        await loadPlayer();
        console.log("[init] ✓ Player cargado");
        await loadPrices();
        console.log("[init] ✓ Prices cargado");
        await loadCropTypes();
        console.log("[init] ✓ CropTypes cargado");
        await loadFarms();
        console.log("[init] ✓ Farms cargado");
    } catch (error) {
        console.error("[init] Error:", error);
        showMessage("Error: " + error.message, "error");
    }
}

// Check if user is logged in
window.addEventListener("DOMContentLoaded", () => {
    const token = getToken();
    const playerId = getPlayerId();

    if (token && playerId) {
        PLAYER_ID = parseInt(playerId);
        document.getElementById("loginModal").classList.remove("active");
        init();
    } else {
        document.getElementById("loginModal").classList.add("active");
    }
});

// ════════════════════════════════════════════════════════════════
// CARGAR DATOS
// ════════════════════════════════════════════════════════════════

async function loadPlayer(force = false) {
    // Si está en caché y no forzamos reload, usar caché
    if (cache.player && !force) {
        const player = cache.player;
        document.getElementById("sidebarName").textContent = player.name;
        document.getElementById("sidebarMoney").textContent = `$${player.money.toLocaleString()}`;
        document.getElementById("sidebarLevel").textContent = `Level ${player.level}`;
        document.getElementById("headerMoney").textContent = player.money.toLocaleString();
        document.getElementById("headerLevel").textContent = player.level;
        return;
    }

    const response = await fetchWithAuth(`${API_BASE}/player/${PLAYER_ID}`);
    if (!response.ok) throw new Error("No se pudo cargar el jugador");

    const player = await response.json();
    cache.player = player; // Guardar en caché

    document.getElementById("sidebarName").textContent = player.name;
    document.getElementById("sidebarMoney").textContent = `$${player.money.toLocaleString()}`;
    document.getElementById("sidebarLevel").textContent = `Level ${player.level}`;
    document.getElementById("headerMoney").textContent = player.money.toLocaleString();
    document.getElementById("headerLevel").textContent = player.level;
}

async function loadPrices(force = false) {
    // Precios casi nunca cambian, cachear agresivamente
    if (cache.prices && !force) {
        prices = cache.prices;
        return;
    }

    const response = await fetchWithAuth(`${API_BASE}/prices`);
    if (!response.ok) throw new Error("No se pudo cargar precios");

    const pricesData = await response.json();
    const pricesMap = {};
    pricesData.forEach(p => {
        pricesMap[p.crop_type_id] = {
            seed_price: p.seed_price,
            crop_price: p.crop_price
        };
    });

    cache.prices = pricesMap;
    prices = pricesMap;
}

async function loadCropTypes(force = false) {
    // Tipos de cultivo nunca cambian, cachear siempre
    if (cache.cropTypes && !force) {
        cropTypes = cache.cropTypes;
        return;
    }

    const response = await fetchWithAuth(`${API_BASE}/crop-types`);
    if (!response.ok) throw new Error("No se pudo cargar tipos de cultivos");

    const types = await response.json();
    cache.cropTypes = types;
    cropTypes = types;
}

// Helper: Parse timestamp as UTC
function parseUTCDate(dateString) {
    if (!dateString.includes('Z') && !dateString.includes('+')) {
        dateString += 'Z';
    }
    return new Date(dateString);
}

// Renderizar granjas desde caché (sin hacer requests)
async function renderFarmsFromCache(houses) {
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
        // Obtener plots del caché si existe, sino hacer request
        let plots;
        if (cache.plots.has(house.id)) {
            plots = cache.plots.get(house.id);
        } else {
            const plotsResponse = await fetchWithAuth(`${API_BASE}/house/${house.id}/plots`);
            plots = await plotsResponse.json();
            cache.plots.set(house.id, plots);
        }

        // Asegurar que plots es un array
        if (!Array.isArray(plots)) {
            plots = [];
        }

        farmsHTML += `
            <div class="section">
                <div class="section-title">🌾 ${house.name}</div>
                <div class="plots-grid">
        `;

        for (const plot of plots) {
            // Obtener cultivo del caché si existe, sino hacer request
            let crop;
            if (cache.plots.has(plot.id)) {
                crop = cache.plots.get(plot.id);
            } else {
                const cropResponse = await fetchWithAuth(`${API_BASE}/plot/${plot.id}/crop`);
                const data = await cropResponse.json();
                crop = data.crop;
                if (crop) cache.plots.set(plot.id, crop);
            }

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

async function loadFarms(force = false) {
    // Si está en caché y no forzamos reload, usar caché
    if (cache.houses && !force) {
        const houses = cache.houses;
        // Renderizar desde caché
        await renderFarmsFromCache(houses);
        return;
    }

    const response = await fetchWithAuth(`${API_BASE}/player/${PLAYER_ID}/houses`);
    if (!response.ok) throw new Error("No se pudo cargar las casas");

    const houses = await response.json();
    cache.houses = houses; // Guardar en caché

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
        const plotsResponse = await fetchWithAuth(`${API_BASE}/house/${house.id}/plots`);
        let plots = await plotsResponse.json();

        // Asegurar que plots es un array
        if (!Array.isArray(plots)) {
            plots = [];
        }

        farmsHTML += `
            <div class="section">
                <div class="section-title">
                    🌾 ${house.name}
                    <button class="btn-sell" onclick="openSellHouseModal(${house.id}, '${house.name}')">Sell 💰</button>
                </div>
                <div class="plots-grid">
        `;

        for (const plot of plots) {
            const cropResponse = await fetchWithAuth(`${API_BASE}/plot/${plot.id}/crop`);
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
    const response = await fetchWithAuth(`${API_BASE}/player/${PLAYER_ID}/inventory`);
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

async function loadProperties(force = false) {
    try {
        console.log("[loadProperties] force=", force);
        // Usar caché si está disponible y no forzamos reload
        if (cache.properties && !force) {
            console.log("[loadProperties] Usando caché");
            renderProperties(cache.properties);
            return;
        }

        console.log("[loadProperties] Cargando desde API");
        // Load player's houses
        const playerHousesRes = await fetchWithAuth(`${API_BASE}/player/${PLAYER_ID}/houses`);
        if (!playerHousesRes.ok) throw new Error("Error cargando casas propias");
        const playerHouses = await playerHousesRes.json();
        console.log("[loadProperties] Player houses:", playerHouses.length);

        // Load available houses for purchase
        const availableRes = await fetchWithAuth(`${API_BASE}/houses/available/${PLAYER_ID}`);
        if (!availableRes.ok) throw new Error("Error cargando casas disponibles");
        const availableHouses = await availableRes.json();
        console.log("[loadProperties] Available houses:", availableHouses.length);

        // Guardar en caché
        cache.properties = { playerHouses, availableHouses };
        console.log("[loadProperties] Renderizando");

        renderProperties(cache.properties);
        console.log("[loadProperties] Completado");

    } catch (error) {
        console.error("Error loading properties:", error);
        showMessage("❌ Error: " + error.message, "error");
    }
}

function renderProperties(data) {
    const { playerHouses, availableHouses } = data;

    let html = `<div class="section">
        <div class="section-title">🏡 My Properties</div>`;

    if (playerHouses.length > 0) {
        html += `<div style="margin-bottom: 30px;">
            <h3 style="font-size: 1.1em; font-weight: 600; color: var(--green-ag); margin-bottom: 12px;">Tus Casas</h3>
            <div class="properties-grid">`;

        playerHouses.forEach(house => {
            html += `
                <div class="property-card owned">
                    <div class="property-name">${house.name}</div>
                    <div class="property-icon">🏠</div>
                    <div class="property-plots">📍 ${house.plot_count} parcelas</div>
                    <div class="property-price" style="color: var(--green-ag);">✓ Tuya</div>
                </div>
            `;
        });

        html += `</div></div>`;
    }

    if (availableHouses.length > 0) {
        html += `<h3 style="font-size: 1.1em; font-weight: 600; color: var(--text-primary); margin-bottom: 12px;">Disponibles para Comprar</h3>
            <div class="properties-grid">`;

        availableHouses.forEach(house => {
            const playerBalance = parseInt(document.getElementById("headerMoney").textContent.replace(/,/g, ''));
            const canAfford = playerBalance >= house.price;

            html += `
                <div class="property-card">
                    <div class="property-name">${house.name}</div>
                    <div class="property-icon">🏡</div>
                    <div class="property-plots">📍 ${house.plot_count} parcelas</div>
                    <div class="property-price">💰 $${house.price.toLocaleString()}</div>
                    <button class="btn ${canAfford ? 'btn-buy' : 'btn-disabled'}"
                            onclick="${canAfford ? `buyHouse(${house.id}, '${house.name}')` : ''}"
                            ${!canAfford ? 'disabled' : ''}>
                        ${canAfford ? 'Comprar' : 'Sin dinero'}
                    </button>
                </div>
            `;
        });

        html += `</div>`;
    }

    html += `</div>`;
    document.getElementById("farms-section").innerHTML = html;
}

async function buyHouse(houseId, houseName) {
    try {
        const response = await fetchWithAuth(`${API_BASE}/player/${PLAYER_ID}/buy-house`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ house_id: houseId })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || "Error al comprar");
        }

        const result = await response.json();
        showMessage(`✅ ¡${houseName} comprada! Tu nuevo balance: $${result.new_balance.toLocaleString()}`, "success");

        invalidatePlayerCache();
        invalidateFarmsCache();
        await loadPlayer(true);
        await loadFarms(true);
        await loadProperties();
    } catch (error) {
        showMessage("❌ " + error.message, "error");
    }
}

let pendingSellHouse = { id: null, name: null };

function openSellHouseModal(houseId, houseName) {
    pendingSellHouse = { id: houseId, name: houseName };

    // Obtener precio estimado (80% del valor)
    // Necesitaríamos buscar el precio de la casa en el caché
    const refundInfo = `
        <div class="sell-house-info-item">
            <span class="sell-house-info-label">Casa:</span>
            <span class="sell-house-info-value">${houseName}</span>
        </div>
        <div class="sell-house-info-item">
            <span class="sell-house-info-label">Tipo:</span>
            <span class="sell-house-info-value">Propiedad</span>
        </div>
        <div class="sell-house-info-item">
            <span class="sell-house-info-label">Compensación:</span>
            <span class="sell-house-info-value">80% del valor original</span>
        </div>
    `;

    document.getElementById("sellHouseInfo").innerHTML = refundInfo;
    document.getElementById("sellHouseModal").classList.add("active");
}

function closeSellHouseModal() {
    document.getElementById("sellHouseModal").classList.remove("active");
    pendingSellHouse = { id: null, name: null };
}

async function confirmSellHouse() {
    const { id: houseId, name: houseName } = pendingSellHouse;

    if (!houseId) return;

    closeSellHouseModal();

    try {
        const response = await fetchWithAuth(`${API_BASE}/player/${PLAYER_ID}/sell-house`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ house_id: houseId })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || "Error al vender");
        }

        const result = await response.json();
        showMessage(`✅ ¡${houseName} vendida! Recibiste $${result.refund_amount.toLocaleString()}. Nuevo balance: $${result.new_balance.toLocaleString()}`, "success");

        invalidatePlayerCache();
        invalidateFarmsCache();
        invalidatePropertiesCache();

        await loadPlayer(true);
        await loadProperties(true);

        // Cambiar a pestaña de Properties y recargar
        currentPage = "properties";
        document.querySelectorAll(".nav-link").forEach(link => link.classList.remove("active"));
        document.querySelector("[onclick=\"setPage('properties')\"]").classList.add("active");
        document.getElementById("pageTitle").textContent = "Properties";

        // Pequeño delay para asegurar que la UI se actualice
        setTimeout(() => {
            document.getElementById("farms-section").innerHTML = `
                <div class="section">
                    <div class="section-title">🏡 Properties</div>
                    <p style="color: var(--text-secondary);">Cargando...</p>
                </div>
            `;
        }, 100);
    } catch (error) {
        showMessage("❌ " + error.message, "error");
    }
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

        const response = await fetchWithAuth(`${API_BASE}/crops/sell-batch`, {
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
        const farmsResponse = await fetchWithAuth(`${API_BASE}/player/${PLAYER_ID}/houses`);
        const houses = await farmsResponse.json();

        let cropToSell = null;

        for (const house of houses) {
            const plotsResponse = await fetchWithAuth(`${API_BASE}/house/${house.id}/plots`);
            const plots = await plotsResponse.json();

            for (const plot of plots) {
                const cropResponse = await fetchWithAuth(`${API_BASE}/plot/${plot.id}/crop`);
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

        const sellResponse = await fetchWithAuth(`${API_BASE}/crop/${cropToSell.id}/sell`, {
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
        const buyResponse = await fetchWithAuth(`${API_BASE}/player/${PLAYER_ID}/buy-seeds`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ crop_type_id: cropTypeId, quantity: 1 })
        });

        if (!buyResponse.ok) {
            const error = await buyResponse.json();
            throw new Error(error.error || "Error buying seeds");
        }

        const buyResult = await buyResponse.json();

        const plantResponse = await fetchWithAuth(`${API_BASE}/plot/${currentPlotId}/plant`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ crop_type_id: cropTypeId })
        });

        if (!plantResponse.ok) throw new Error("Error al plantar");

        showMessage(`✅ ¡Semilla plantada! -$${seedPrice}`, "success");
        closePlantModal();

        // Invalidar caché porque el dinero y las parcelas cambiaron
        invalidatePlayerCache();
        invalidatePlotsCache();

        setTimeout(() => {
            loadPlayer(true);  // true = forzar reload desde servidor
            loadFarms(true);
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
        const harvestResponse = await fetchWithAuth(`${API_BASE}/crop/${cropId}/harvest`, {
            method: "POST"
        });

        if (!harvestResponse.ok) {
            const error = await harvestResponse.json();
            throw new Error(error.error || "Error al cosechar");
        }

        const result = await harvestResponse.json();
        const actualYield = result.yield_amount || yieldAmount;

        showMessage(`✅ ¡Cosechado! ${actualYield} unidades guardadas en el inventario`, "success");

        // Invalidar caché porque las parcelas cambiaron
        invalidatePlotsCache();

        setTimeout(() => {
            loadPlayer(true);
            loadFarms(true);
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
        const response = await fetchWithAuth(`${API_BASE}/crop/${currentCropId}/sell`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ player_id: PLAYER_ID })
        });

        if (!response.ok) throw new Error("Error al vender");

        const result = await response.json();
        showMessage(`✅ ¡Vendido! +$${result.total_revenue} 💸`, "success");

        // Invalidar caché porque el dinero e inventario cambiaron
        invalidatePlayerCache();
        invalidatePlotsCache();

        try {
            await loadPlayer(true);
            await loadFarms(true);
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
        } else if (page === "properties") {
            await loadProperties();
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
// START - La inicialización ocurre en DOMContentLoaded
// ════════════════════════════════════════════════════════════════
