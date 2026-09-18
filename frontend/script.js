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
    // Limpiar localStorage
    localStorage.removeItem("auth_token");
    localStorage.removeItem("player_id");

    // Limpiar variables globales
    PLAYER_ID = null;

    // Limpiar caché
    invalidateAllCache();

    // Mostrar modal de login y recargar
    document.getElementById("loginModal").classList.add("active");
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
// DASHBOARD
// ════════════════════════════════════════════════════════════════

async function loadDashboard() {
    try {
        // Obtener data del jugador
        const playerRes = await fetchWithAuth(`${API_BASE}/player/${PLAYER_ID}`);
        const player = await playerRes.json();

        // Obtener casas del jugador
        const housesRes = await fetchWithAuth(`${API_BASE}/player/${PLAYER_ID}/houses`);
        const houses = await housesRes.json();

        // Obtener cultivos cosechados
        const inventoryRes = await fetchWithAuth(`${API_BASE}/player/${PLAYER_ID}/inventory`);
        const inventory = await inventoryRes.json();

        let html = `
            <div class="section">
                <div class="section-title">📊 Dashboard</div>

                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 20px;">
                    <!-- Dinero -->
                    <div style="background: linear-gradient(135deg, #4CAF50, #45a049); padding: 20px; border-radius: 10px; color: white;">
                        <div style="font-size: 0.9em; opacity: 0.9; margin-bottom: 8px;">💰 Dinero</div>
                        <div style="font-size: 2em; font-weight: 800;">$${player.money.toLocaleString()}</div>
                    </div>

                    <!-- Nivel -->
                    <div style="background: linear-gradient(135deg, #2196F3, #1976D2); padding: 20px; border-radius: 10px; color: white;">
                        <div style="font-size: 0.9em; opacity: 0.9; margin-bottom: 8px;">📈 Nivel</div>
                        <div style="font-size: 2em; font-weight: 800;">${player.level}</div>
                    </div>

                    <!-- Casas -->
                    <div style="background: linear-gradient(135deg, #FF9800, #F57C00); padding: 20px; border-radius: 10px; color: white;">
                        <div style="font-size: 0.9em; opacity: 0.9; margin-bottom: 8px;">🏡 Casas</div>
                        <div style="font-size: 2em; font-weight: 800;">${houses.length}</div>
                    </div>

                    <!-- Cultivos Cosechados -->
                    <div style="background: linear-gradient(135deg, #E91E63, #C2185B); padding: 20px; border-radius: 10px; color: white;">
                        <div style="font-size: 0.9em; opacity: 0.9; margin-bottom: 8px;">🌾 Cultivos</div>
                        <div style="font-size: 2em; font-weight: 800;">${inventory.length}</div>
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 30px;">
                    <!-- Leaderboard -->
                    <div style="padding: 20px; background: var(--bg-secondary); border-radius: 8px;">
                        <h3 style="margin-top: 0; color: var(--green-dark);">🏆 Top Jugadores</h3>
                        <div style="max-height: 250px; overflow-y: auto; color: var(--text-secondary);">
                            <p>Próximamente...</p>
                        </div>
                    </div>

                    <!-- Activity Log -->
                    <div style="padding: 20px; background: var(--bg-secondary); border-radius: 8px;">
                        <h3 style="margin-top: 0; color: var(--green-dark);">📝 Actividad Reciente</h3>
                        <div style="max-height: 250px; overflow-y: auto; color: var(--text-secondary);" id="activityLog">
                            <p>Sin actividad aún</p>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.getElementById("farms-section").innerHTML = html;
        // Renderizar activity log
        const activityLog = getActivityLog();
        const logHtml = activityLog.length > 0 ? activityLog.map(log => `
            <div style="padding: 8px 0; border-bottom: 1px solid var(--border-color); font-size: 0.9em;">
                <div>${log.emoji} ${log.text}</div>
                <div style="font-size: 0.8em; opacity: 0.7;">${log.time}</div>
            </div>
        `).join('') : '<p>Sin actividad aún</p>';

        const logElement = document.getElementById("activityLog");
        if (logElement) {
            logElement.innerHTML = logHtml;
        }
    } catch (error) {
        console.error("Error loading dashboard:", error);
        showMessage("❌ Error: " + error.message, "error");
    }
}

function logActivity(emoji, text) {
    const log = localStorage.getItem("activityLog");
    const activities = log ? JSON.parse(log) : [];

    const now = new Date();
    const timeStr = now.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });

    activities.unshift({
        emoji: emoji,
        text: text,
        time: timeStr,
        timestamp: now.getTime()
    });

    // Guardar solo últimas 50 actividades
    if (activities.length > 50) {
        activities.pop();
    }

    localStorage.setItem("activityLog", JSON.stringify(activities));
}

function getActivityLog() {
    const log = localStorage.getItem("activityLog");
    return log ? JSON.parse(log) : [];
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
        // Cargar dashboard por defecto
        await loadDashboard();
        console.log("[init] ✓ Dashboard cargado");
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

        // Obtener todos los crops de la casa en una sola petición (optimizado)
        const cropsResponse = await fetchWithAuth(`${API_BASE}/house/${house.id}/crops`);
        const allCrops = await cropsResponse.json();

        farmsHTML += `
            <div class="section">
                <div class="section-title">🌾 ${house.name}</div>
                <div class="plots-grid">
        `;

        for (const plot of plots) {
            const crop = allCrops[plot.id];

            if (crop && crop.crop_types) {
                const cropType = crop.crop_types.name || "Unknown Crop";
                const readyAt = parseUTCDate(crop.ready_at);
                const now = new Date();
                const isReady = now >= readyAt;

                if (isReady) {
                    const cropPrice = prices[crop.crop_type_id]?.crop_price || 0;
                    const totalValue = (crop.yield_amount || 0) * cropPrice;

                    farmsHTML += `
                        <div class="plot-card ready" onclick="harvestCrop(${crop.id}, '${cropType}', ${(crop.yield_amount || 0)})">
                            <div class="plot-name">${plot.name}</div>
                            <div class="plot-emoji">🌾</div>
                            <div class="plot-crop-name">${cropType}</div>
                            <div class="plot-yield">📦 ${(crop.yield_amount || 0)} unidades</div>
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
                    const totalValue = (crop.yield_amount || 0) * cropPrice;

                    farmsHTML += `
                        <div class="plot-card with-crop" id="plot-${crop.id}" data-crop-id="${crop.id}" data-crop-name="${cropType}" data-yield="${(crop.yield_amount || 0)}" data-price="${cropPrice}" data-total="${totalValue}">
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

    // Crear plots faltantes (en caso de casas compradas sin plots)
    try {
        await fetchWithAuth(`${API_BASE}/player/${PLAYER_ID}/create-missing-plots`, {
            method: "POST"
        });
    } catch (e) {
        console.error("Error creating missing plots:", e);
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
                <div class="section-title">🌾 ${house.name}</div>
                <div class="plots-grid">
        `;

        // Cargar todos los crops de la casa en una sola petición
        const cropsResponse = await fetchWithAuth(`${API_BASE}/house/${house.id}/crops`);
        const allCrops = await cropsResponse.json();

        for (const plot of plots) {
            const crop = allCrops[plot.id];
            if (crop && crop.crop_types) {
                const cropType = crop.crop_types.name || "Unknown Crop";
                const readyAt = parseUTCDate(crop.ready_at);
                const now = new Date();
                const isReady = now >= readyAt;

                if (isReady) {
                    const cropPrice = prices[crop.crop_type_id]?.crop_price || 0;
                    const totalValue = (crop.yield_amount || 0) * cropPrice;

                    farmsHTML += `
                        <div class="plot-card ready" onclick="harvestCrop(${crop.id}, '${cropType}', ${(crop.yield_amount || 0)})">
                            <div class="plot-name">${plot.name}</div>
                            <div class="plot-emoji">🌾</div>
                            <div class="plot-crop-name">${cropType}</div>
                            <div class="plot-yield">📦 ${(crop.yield_amount || 0)} unidades</div>
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
                    const totalValue = (crop.yield_amount || 0) * cropPrice;

                    farmsHTML += `
                        <div class="plot-card with-crop" id="plot-${crop.id}" data-crop-id="${crop.id}" data-crop-name="${cropType}" data-yield="${(crop.yield_amount || 0)}" data-price="${cropPrice}" data-total="${totalValue}">
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

    const data = await response.json();
    const crops = data.crops || [];
    const items = data.items || [];
    const totalValue = data.total_value || 0;

    if (crops.length === 0 && items.length === 0) {
        document.getElementById("farms-section").innerHTML = `
            <div class="section">
                <div class="section-title">🎒 Inventario</div>
                <p style="color: var(--text-secondary);">No tienes cultivos ni items aún.</p>
            </div>
        `;
        return;
    }

    let inventoryHTML = `
        <div class="section">
            <div class="section-title">🎒 Inventario</div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 20px;">
                <div style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 15px; border-radius: 8px; color: white;">
                    <div style="font-size: 0.9em; opacity: 0.9;">📦 Total Items</div>
                    <div style="font-size: 1.8em; font-weight: 800;">${crops.reduce((a, c) => a + c.quantity, 0) + items.reduce((a, i) => a + i.quantity, 0)}</div>
                </div>
                <div style="background: linear-gradient(135deg, #f093fb, #f5576c); padding: 15px; border-radius: 8px; color: white;">
                    <div style="font-size: 0.9em; opacity: 0.9;">💰 Valor Total</div>
                    <div style="font-size: 1.8em; font-weight: 800;">$${totalValue.toLocaleString()}</div>
                </div>
            </div>

            <div class="inventory-grid">
    `;

    // Mostrar cultivos cosechados
    crops.forEach(crop => {
        const cropType = crop.name;
        const cropPrice = crop.price || 0;
        const quantity = crop.quantity;
        const itemTotal = quantity * cropPrice;
        const itemId = `sell-${crop.crop_type_id}`;

        inventoryHTML += `
            <div class="inventory-item">
                <div class="item-header">
                    <div class="item-name">🌾 ${cropType}</div>
                    <div class="item-yield">x${quantity}</div>
                </div>

                <div style="background: var(--bg-tertiary); padding: 8px; border-radius: 4px; margin: 12px 0;">
                    <div style="font-size: 0.85em; color: var(--text-secondary); margin-bottom: 4px;">Precio por unidad</div>
                    <div style="font-size: 1.1em; font-weight: 600; color: var(--green-light);">$${cropPrice.toLocaleString()}</div>
                </div>

                <div style="margin: 12px 0;">
                    <label style="font-size: 0.8em; color: var(--text-secondary); display: block; margin-bottom: 6px;">
                        Vender cantidad:
                    </label>
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <input type="range" id="${itemId}-qty" min="1" max="${quantity}" value="${quantity}"
                               style="flex: 1; cursor: pointer;"
                               oninput="
                                   const qty = this.value;
                                   document.getElementById('${itemId}-num').textContent = qty;
                                   document.getElementById('${itemId}-total').textContent = '💰 $' + (qty * ${cropPrice}).toLocaleString();
                                   document.getElementById('${itemId}-btn-qty').textContent = qty;
                               ">
                        <span id="${itemId}-num" style="font-weight: 700; min-width: 30px; text-align: right;">${quantity}</span>
                    </div>
                </div>

                <div class="item-value" id="${itemId}-total" style="margin-bottom: 10px;">💰 $${itemTotal.toLocaleString()}</div>
                <button class="btn btn-sell" onclick="sellBatch('${crop.crop_type_id}', '${cropType}', ${cropPrice})" style="width: 100%;">
                    Vender <span id="${itemId}-btn-qty">${quantity}</span>x
                </button>
            </div>
        `;
    });

    // Mostrar items comprados
    items.forEach(item => {
        const itemName = item.name;
        const itemCategory = item.category;
        const quantity = item.quantity;
        const price = item.price || 0;

        let categoryIcon = "📦";
        if (itemCategory === "semilla") categoryIcon = "🌱";
        else if (itemCategory === "herramienta") categoryIcon = "🔧";
        else if (itemCategory === "objeto") categoryIcon = "✨";

        inventoryHTML += `
            <div class="inventory-item">
                <div class="item-header">
                    <div class="item-name">${categoryIcon} ${itemName}</div>
                    <div class="item-yield">x${quantity}</div>
                </div>

                <div style="background: var(--bg-tertiary); padding: 8px; border-radius: 4px; margin: 12px 0;">
                    <div style="font-size: 0.85em; color: var(--text-secondary); margin-bottom: 4px;">Precio</div>
                    <div style="font-size: 1.1em; font-weight: 600; color: var(--yellow-gold);">$${price.toLocaleString()}</div>
                </div>

                <div style="padding: 8px; background: rgba(114, 175, 196, 0.1); border-radius: 4px; font-size: 0.85em;">
                    <span style="color: var(--text-secondary);">Adquirido de:</span>
                    <span style="font-weight: 600; color: var(--blue-sky);">
                        ${item.acquired_from === "npc" ? "🏪 Tienda NPC" : "🤝 Jugador"}
                    </span>
                </div>
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
        console.log("[loadProperties] Player houses:", playerHouses.length, playerHouses);

        // Load available houses for purchase
        const availableRes = await fetchWithAuth(`${API_BASE}/houses/available/${PLAYER_ID}`);
        if (!availableRes.ok) throw new Error("Error cargando casas disponibles");
        const availableHouses = await availableRes.json();
        console.log("[loadProperties] Available houses:", availableHouses.length, availableHouses);

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
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h3 style="font-size: 1.1em; font-weight: 600; color: var(--green-ag); margin: 0;">Tus Casas</h3>
            </div>
            <div class="properties-grid">`;

        playerHouses.forEach(house => {
            html += `
                <div class="property-card owned">
                    <div class="property-name">${house.name}</div>
                    <div class="property-icon">🏠</div>
                    <div class="property-plots">📍 ${house.plot_count} parcelas</div>
                    <div class="property-price" style="color: var(--green-ag);">✓ Tuya</div>
                    <button class="btn btn-sell" onclick="openSellHouseModal(${house.id}, '${house.name}')">Sell 💰</button>
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

        // Registrar actividad
        logActivity(`🏡`, `Compró ${houseName}`);

        invalidatePlayerCache();
        invalidateFarmsCache();
        invalidatePropertiesCache();
        await loadPlayer(true);
        await loadFarms(true);
        await loadProperties(true);
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
            let errorMsg = error.error || "Error al vender";

            // Mensajes más claros para errores específicos
            if (errorMsg.includes("active crops")) {
                errorMsg = "❌ No puedes vender esta casa. Primero cosecha todos los cultivos plantados.";
            }

            throw new Error(errorMsg);
        }

        const result = await response.json();
        showMessage(`✅ ¡${houseName} vendida! Recibiste $${result.refund_amount.toLocaleString()}. Nuevo balance: $${result.new_balance.toLocaleString()}`, "success");

        // Registrar actividad
        logActivity(`💰`, `Vendió ${houseName} por $${result.refund_amount.toLocaleString()}`);

        invalidatePlayerCache();
        invalidateFarmsCache();
        invalidatePropertiesCache();

        await loadPlayer(true);
        await loadProperties(true);

        // Cambiar a pestaña de Properties
        currentPage = "properties";
        document.querySelectorAll(".nav-link").forEach(link => link.classList.remove("active"));
        document.querySelector("[onclick=\"setPage('properties')\"]").classList.add("active");
        document.getElementById("pageTitle").textContent = "Properties";
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

        // Registrar actividad
        logActivity(`💰`, `Vendió ${result.sold_yield} ${cropName} por $${result.total_revenue}`);

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

        // Registrar actividad
        const plantedCropName = cropTypes.find(c => c.id === cropTypeId)?.name || "Cultivo";
        logActivity(`🌱`, `Plantó ${plantedCropName}`);

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

        // Registrar actividad
        logActivity(`🌾`, `Cosechó ${cropName} (${actualYield} unidades)`);

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
        if (page === "dashboard") {
            await loadDashboard();
        } else if (page === "farm") {
            await loadFarms();
        } else if (page === "inventory") {
            await loadInventory();
        } else if (page === "properties") {
            await loadProperties();
        } else if (page === "market") {
            await openMarketModal();
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

// ════════════════════════════════════════════════════════════════
// MARKET FUNCTIONS
// ════════════════════════════════════════════════════════════════

async function openMarketModal() {
    await loadNpcShop();
    document.getElementById("marketModal").classList.add("active");
}

function closeMarketModal() {
    document.getElementById("marketModal").classList.remove("active");
}

function switchMarketTab(tabName) {
    document.querySelectorAll(".market-tab-content").forEach(tab => {
        tab.classList.remove("active");
    });
    document.querySelectorAll(".market-tab").forEach(tab => {
        tab.classList.remove("active");
    });

    document.getElementById(tabName + "Tab").classList.add("active");
    event.target.classList.add("active");

    if (tabName === "npc") {
        loadNpcShop();
    } else if (tabName === "player") {
        loadPlayerMarket();
    } else if (tabName === "global") {
        loadGlobalMarket();
    }
}

async function loadNpcShop() {
    try {
        const response = await fetch(`${API_BASE}/market/npc-shop/items`);
        const items = await response.json();

        const grid = document.getElementById("npcShopGrid");
        grid.innerHTML = "";

        items.forEach(item => {
            const itemCard = document.createElement("div");
            itemCard.className = "npc-item-card";
            itemCard.innerHTML = `
                <div class="item-category">${item.category}</div>
                <div class="item-name">${item.name}</div>
                <div class="item-description">${item.description || ""}</div>
                <div class="item-price">💰 ${item.price}</div>
                <button class="btn btn-primary" onclick="openBuyNpcModal(${item.id}, '${item.name}', ${item.price})">
                    Comprar
                </button>
            `;
            grid.appendChild(itemCard);
        });
    } catch (error) {
        showMessage("❌ Error cargando tienda: " + error.message, "error");
    }
}

async function loadPlayerMarket() {
    try {
        await loadPlayerListings();
        await loadMyOffers();
    } catch (error) {
        showMessage("❌ Error cargando mercado: " + error.message, "error");
    }
}

async function loadPlayerListings() {
    try {
        const cropTypeId = document.getElementById("cropFilterSelect").value || "";
        const url = cropTypeId
            ? `${API_BASE}/market/player/listings?crop_type_id=${cropTypeId}`
            : `${API_BASE}/market/player/listings`;

        const response = await fetch(url);
        const listings = await response.json();

        const container = document.getElementById("playerListings");
        container.innerHTML = "";

        if (listings.length === 0) {
            container.innerHTML = "<p class='empty-state'>No hay ofertas disponibles</p>";
            return;
        }

        listings.forEach(listing => {
            const card = document.createElement("div");
            card.className = "market-card";
            const totalPrice = listing.quantity * listing.price_per_unit;
            const commission = Math.ceil(totalPrice * 0.05);

            card.innerHTML = `
                <div class="market-card-header">
                    <h3>${listing.crop_types.name}</h3>
                    <span class="seller-name">Vendedor: ${listing.player.name}</span>
                </div>
                <div class="market-card-details">
                    <div>Cantidad: ${listing.quantity} unidades</div>
                    <div>Precio unitario: 💰 ${listing.price_per_unit}</div>
                    <div class="price-total">Precio total: 💰 ${totalPrice}</div>
                    <div class="commission-info">Comisión (5%): 💰 ${commission}</div>
                </div>
                <button class="btn btn-primary" onclick="confirmBuyListing(${listing.id}, ${totalPrice})">
                    Comprar
                </button>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        showMessage("❌ Error cargando ofertas: " + error.message, "error");
    }
}

async function loadMyOffers() {
    try {
        const response = await fetch(`${API_BASE}/market/player/my-offers`, {
            headers: { "Authorization": `Bearer ${getToken()}` }
        });

        if (!response.ok) throw new Error("Error cargando mis ofertas");

        const offers = await response.json();
        const container = document.getElementById("myOffers");
        container.innerHTML = "";

        if (offers.length === 0) {
            container.innerHTML = "<p class='empty-state'>No tienes ofertas activas</p>";
            return;
        }

        offers.forEach(offer => {
            const card = document.createElement("div");
            card.className = "market-card my-offer";
            const totalPrice = offer.quantity * offer.price_per_unit;

            card.innerHTML = `
                <div class="market-card-header">
                    <h3>${offer.crop_types.name}</h3>
                    <span class="offer-status">Estado: ${offer.status}</span>
                </div>
                <div class="market-card-details">
                    <div>Cantidad: ${offer.quantity} unidades</div>
                    <div>Precio unitario: 💰 ${offer.price_per_unit}</div>
                    <div class="price-total">Precio total: 💰 ${totalPrice}</div>
                </div>
                <button class="btn btn-secondary" onclick="cancelOffer(${offer.id})">
                    Cancelar Oferta
                </button>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        showMessage("❌ Error cargando mis ofertas: " + error.message, "error");
    }
}

async function loadGlobalMarket() {
    try {
        const response = await fetch(`${API_BASE}/market/global-prices`);
        const prices = await response.json();

        const grid = document.getElementById("globalPricesGrid");
        grid.innerHTML = "";

        prices.forEach(price => {
            const card = document.createElement("div");
            card.className = "global-price-card";

            const trendIcon = price.trend === "up" ? "📈" : price.trend === "down" ? "📉" : "➡️";

            card.innerHTML = `
                <div class="price-crop-name">${price.crop_types ? price.crop_types.name : "Cultivo"}</div>
                <div class="price-current">💰 ${price.current_price}</div>
                <div class="price-trend">${trendIcon} ${price.trend}</div>
                <div class="price-base">Base: 💰 ${price.base_price}</div>
            `;
            grid.appendChild(card);
        });
    } catch (error) {
        showMessage("❌ Error cargando precios: " + error.message, "error");
    }
}

function openBuyNpcModal(itemId, itemName, price) {
    window.currentNpcItemId = itemId;
    window.currentNpcItemPrice = price;
    window.currentNpcItemName = itemName;

    const info = document.getElementById("buyNpcInfo");
    info.innerHTML = `
        <div class="buy-form">
            <div class="form-group">
                <label>Item: <strong>${itemName}</strong></label>
                <label>Precio unitario: 💰 ${price}</label>
            </div>
            <div class="form-group">
                <label for="npcQuantity">Cantidad</label>
                <input type="number" id="npcQuantity" min="1" value="1"
                       onchange="updateNpcTotalPrice()" oninput="updateNpcTotalPrice()">
            </div>
            <div class="price-display">
                <strong>Total: 💰 <span id="npcTotalPrice">${price}</span></strong>
            </div>
        </div>
    `;

    document.getElementById("buyNpcModal").classList.add("active");
}

function updateNpcTotalPrice() {
    const quantity = parseInt(document.getElementById("npcQuantity").value) || 1;
    const total = quantity * window.currentNpcItemPrice;
    document.getElementById("npcTotalPrice").textContent = total;
}

function closeBuyNpcModal() {
    document.getElementById("buyNpcModal").classList.remove("active");
}

async function confirmBuyNpc() {
    try {
        const quantity = parseInt(document.getElementById("npcQuantity").value) || 1;

        const response = await fetchWithAuth(`${API_BASE}/market/npc-shop/buy`, {
            method: "POST",
            body: JSON.stringify({
                item_id: window.currentNpcItemId,
                quantity: quantity
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || "Error en la compra");
        }

        const result = await response.json();
        showMessage(`✅ Compraste ${result.quantity}x ${result.item_name} por 💰 ${result.total_price}`, "success");
        invalidatePlayerCache();
        await loadPlayer();
        closeBuyNpcModal();
        await loadNpcShop();
    } catch (error) {
        showMessage("❌ " + error.message, "error");
    }
}

async function confirmBuyListing(listingId, totalPrice) {
    if (!confirm(`¿Comprar esta oferta por 💰 ${totalPrice}?`)) return;

    try {
        const response = await fetchWithAuth(`${API_BASE}/market/player/accept-offer/${listingId}`, {
            method: "POST"
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || "Error en la compra");
        }

        const result = await response.json();
        showMessage(`✅ Compraste ${result.quantity} unidades por 💰 ${result.total_price}`, "success");
        invalidatePlayerCache();
        await loadPlayer();
        await loadPlayerMarket();
    } catch (error) {
        showMessage("❌ " + error.message, "error");
    }
}

async function cancelOffer(offerId) {
    if (!confirm("¿Cancelar esta oferta?")) return;

    try {
        const response = await fetchWithAuth(`${API_BASE}/market/player/cancel-offer/${offerId}`, {
            method: "POST"
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || "Error cancelando oferta");
        }

        showMessage("✅ Oferta cancelada", "success");
        await loadMyOffers();
    } catch (error) {
        showMessage("❌ " + error.message, "error");
    }
}

function filterPlayerListings() {
    loadPlayerListings();
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
