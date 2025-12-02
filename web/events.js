import { addEvent, updateWorldData, setConnectionStatus } from './app.js';

// WebSocket connection state
let socket;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY = 3000;

// Connect to WebSocket server
export function connectWebSocket() {
    const wsUrl = `ws://${window.location.hostname}:8000/ws`;

    addEvent(`🔌 Attempting to connect to ${wsUrl}...`);

    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        addEvent('🟢 WebSocket connection established');
        setConnectionStatus(true);
        reconnectAttempts = 0;
    };

    socket.onclose = (event) => {
        addEvent(`🔴 WebSocket disconnected: ${event.reason || 'Unknown reason'}`);
        setConnectionStatus(false);

        if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
            reconnectAttempts++;
            addEvent(`⏳ Attempting to reconnect (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`);
            setTimeout(connectWebSocket, RECONNECT_DELAY);
        } else {
            addEvent('❌ Maximum reconnection attempts reached');
        }
    };

    socket.onerror = (error) => {
        addEvent(`⚠️ WebSocket error: ${error.message}`);
        console.error('WebSocket error:', error);
    };

    socket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        } catch (error) {
            addEvent(`⚠️ Error parsing message: ${error.message}`);
            console.error('Error parsing WebSocket message:', error);
        }
    };
}

// Handle incoming WebSocket messages
function handleWebSocketMessage(data) {
    if (!data || !data.type) {
        addEvent('⚠️ Received invalid message format');
        return;
    }

    console.log('WebSocket message:', data);

    switch (data.type) {
        case 'world_created':
            handleWorldCreated(data);
            break;

        case 'region_named':
            handleRegionNamed(data);
            break;

        case 'region_described':
            handleRegionDescribed(data);
            break;

        case 'poi_created':
            handlePOICreated(data);
            break;

        case 'poi_detailed':
            handlePOIDetailed(data);
            break;

        case 'lore_created':
            handleLoreCreated(data);
            break;

        case 'connection_created':
            handleConnectionCreated(data);
            break;

        case 'statistics_updated':
            handleStatisticsUpdated(data);
            break;

        case 'error':
            handleError(data);
            break;

        default:
            addEvent(`📡 Unknown message type: ${data.type}`);
            console.warn('Unknown WebSocket message type:', data.type);
    }
}

// Handle world creation
function handleWorldCreated(data) {
    addEvent(`🌍 World created: ${data.width}x${data.height}`);
    updateWorldData(data);

    // Update UI
    document.getElementById('world-size').textContent = `${data.width}x${data.height}`;
    document.getElementById('biome-count').textContent = data.biome_count || 'N/A';
    document.getElementById('poi-count').textContent = data.poi_count || '0';
}

// Handle region naming
function handleRegionNamed(data) {
    const message = `📍 Region named: ${data.name} (${data.x},${data.y}) - ${data.biome}`;
    addEvent(message);

    // Update region grid
    updateRegionGrid(data);
}

// Handle region description
function handleRegionDescribed(data) {
    const message = `📝 Region described: ${data.name}`;
    addEvent(message);

    // Add to regions panel
    addRegionToPanel(data);
}

// Handle POI creation
function handlePOICreated(data) {
    const message = `🏰 POI created: ${data.name} at (${data.x},${data.y})`;
    addEvent(message);

    // Add to POI list
    addPOIToList(data);
}

// Handle POI detailing
function handlePOIDetailed(data) {
    const message = `🎨 POI detailed: ${data.name} (${data.npcs?.length || 0} NPCs, ${data.rumors?.length || 0} rumors)`;
    addEvent(message);

    // Update POI in list
    updatePOIInList(data);
}

// Handle lore creation
function handleLoreCreated(data) {
    const message = `📜 Lore created: ${data.type} - "${data.title || data.content.substring(0, 30)}..."`;
    addEvent(message);

    // Add to lore section if needed
    addLoreToPanel(data);
}

// Handle connection creation
function handleConnectionCreated(data) {
    const message = `🔗 Connection created: ${data.type} between ${data.source} and ${data.target}`;
    addEvent(message);
}

// Handle statistics update
function handleStatisticsUpdated(data) {
    addEvent(`📊 Statistics updated: ${Object.keys(data.statistics).join(', ')}`);

    // Update stats panel
    updateStatsPanel(data.statistics);
}

// Handle errors
function handleError(data) {
    const message = `❌ Error: ${data.message}`;
    addEvent(message);
    console.error('Server error:', data);
}

// Update region grid
function updateRegionGrid(region) {
    const regionGrid = document.getElementById('region-grid');
    const existingRegion = document.querySelector(`[data-region-x="${region.x}"][data-region-y="${region.y}"]`);

    if (existingRegion) {
        existingRegion.textContent = region.name;
        existingRegion.title = `${region.name} (${region.biome})`;
    } else {
        const regionElement = document.createElement('div');
        regionElement.className = 'region-item';
        regionElement.textContent = region.name;
        regionElement.title = `${region.name} (${region.biome})`;
        regionElement.dataset.regionX = region.x;
        regionElement.dataset.regionY = region.y;

        regionElement.addEventListener('click', () => {
            showRegionDetails(region);
        });

        regionGrid.appendChild(regionElement);
    }
}

// Add region to panel
function addRegionToPanel(region) {
    const regionGrid = document.getElementById('region-grid');
    const regionElement = document.createElement('div');
    regionElement.className = 'region-item';
    regionElement.textContent = region.name;
    regionElement.title = region.description || `${region.name} (${region.biome})`;
    regionElement.dataset.regionX = region.x;
    regionElement.dataset.regionY = region.y;

    regionElement.addEventListener('click', () => {
        showRegionDetails(region);
    });

    regionGrid.appendChild(regionElement);
}

// Show region details
function showRegionDetails(region) {
    const regionGrid = document.getElementById('region-grid');
    regionGrid.innerHTML = `
        <div class="region-detail">
            <h3>${region.name}</h3>
            <p><strong>Biome:</strong> ${region.biome}</p>
            <p><strong>Location:</strong> (${region.x}, ${region.y})</p>
            ${region.description ? `<p><strong>Description:</strong> ${region.description}</p>` : ''}
            <button id="back-to-grid">← Back to Grid</button>
        </div>
    `;

    document.getElementById('back-to-grid').addEventListener('click', () => {
        // Reload region grid
        loadRegionGrid();
    });
}

// Add POI to list
function addPOIToList(poi) {
    const poiList = document.getElementById('poi-list');
    const poiElement = document.createElement('div');
    poiElement.className = 'poi-item';
    poiElement.dataset.poiId = poi.id;

    poiElement.innerHTML = `
        <div class="poi-header">
            <h4>${poi.name}</h4>
            <span class="poi-location">(${poi.x}, ${poi.y})</span>
        </div>
        <div class="poi-type">${poi.type || 'Unknown'}</div>
    `;

    poiElement.addEventListener('click', () => {
        showPOIDetails(poi);
    });

    poiList.appendChild(poiElement);
}

// Update POI in list
function updatePOIInList(poi) {
    const poiElement = document.querySelector(`[data-poi-id="${poi.id}"]`);
    if (poiElement) {
        poiElement.innerHTML = `
            <div class="poi-header">
                <h4>${poi.name}</h4>
                <span class="poi-location">(${poi.x}, ${poi.y})</span>
            </div>
            <div class="poi-type">${poi.type || 'Unknown'}</div>
            <div class="poi-stats">
                ${poi.npcs?.length || 0} NPCs • ${poi.rumors?.length || 0} Rumors
            </div>
        `;
    }
}

// Show POI details
function showPOIDetails(poi) {
    const poiList = document.getElementById('poi-list');
    poiList.innerHTML = `
        <div class="poi-detail">
            <h3>${poi.name}</h3>
            <p><strong>Type:</strong> ${poi.type}</p>
            <p><strong>Location:</strong> (${poi.x}, ${poi.y})</p>
            ${poi.description ? `<p><strong>Description:</strong> ${poi.description}</p>` : ''}
            ${poi.npcs?.length ? `<div><strong>NPCs:</strong> ${poi.npcs.map(n => `<div>${n.name} - ${n.role}</div>`).join('')}</div>` : ''}
            ${poi.rumors?.length ? `<div><strong>Rumors:</strong> ${poi.rumors.map(r => `<div>${r}</div>`).join('')}</div>` : ''}
            <button id="back-to-pois">← Back to POIs</button>
        </div>
    `;

    document.getElementById('back-to-pois').addEventListener('click', () => {
        // Reload POI list
        loadPOIList();
    });
}

// Add lore to panel
function addLoreToPanel(lore) {
    // This could be enhanced with a lore tab
    console.log('Lore added:', lore);
}

// Update stats panel
function updateStatsPanel(statistics) {
    Object.entries(statistics).forEach(([key, value]) => {
        const statElement = document.getElementById(key);
        if (statElement) {
            statElement.textContent = value;
        }
    });
}

// Load region grid (would be called from API)
function loadRegionGrid() {
    // Placeholder - would be replaced with actual API call
    console.log('Loading region grid...');
}

// Load POI list (would be called from API)
function loadPOIList() {
    // Placeholder - would be replaced with actual API call
    console.log('Loading POI list...');
}

// Send MCP command via WebSocket
export function sendMCPCommand(command, data = {}) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        addEvent('⚠️ Cannot send command: WebSocket not connected');
        return Promise.reject('WebSocket not connected');
    }

    const message = {
        type: 'mcp_command',
        command: command,
        data: data,
        timestamp: new Date().toISOString()
    };

    return new Promise((resolve, reject) => {
        const messageId = Date.now().toString();
        message.id = messageId;

        const timeout = setTimeout(() => {
            socket.removeEventListener('message', messageHandler);
            reject(new Error('Command timeout'));
        }, 10000);

        const messageHandler = (event) => {
            try {
                const response = JSON.parse(event.data);
                if (response.id === messageId) {
                    clearTimeout(timeout);
                    socket.removeEventListener('message', messageHandler);

                    if (response.error) {
                        reject(new Error(response.error));
                    } else {
                        resolve(response.data);
                    }
                }
            } catch (error) {
                console.error('Error handling response:', error);
            }
        };

        socket.addEventListener('message', messageHandler);
        socket.send(JSON.stringify(message));
        addEvent(`📤 Sent command: ${command}`);
    });
}

// Event listeners for UI buttons
function setupUIEventListeners() {
    // Connect button
    window.addEventListener('connect-server', () => {
        connectWebSocket();
    });

    // Generate world button
    window.addEventListener('generate-world', async () => {
        try {
            const result = await sendMCPCommand('create_world', {
                width: 64,
                height: 64,
                seed: Math.random().toString(36).substring(2, 8),
                island_mode: true
            });

            addEvent(`✅ World generation complete: ${result.width}x${result.height}`);
        } catch (error) {
            addEvent(`❌ World generation failed: ${error.message}`);
        }
    });

    // Auto-connect on page load
    if (window.location.protocol !== 'file:') {
        setTimeout(connectWebSocket, 1000);
    }
}

// Initialize event listeners
setupUIEventListeners();

// Export public functions
export { connectWebSocket, sendMCPCommand, handleWebSocketMessage };