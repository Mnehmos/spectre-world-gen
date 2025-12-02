import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GUI } from 'dat.gui';

// Global state
const state = {
    worldSize: 64,
    tileSize: 1,
    showWireframe: false,
    showPOIs: true,
    cameraPosition: { x: 0, y: 50, z: 50 },
    terrainColor: '#4a6fa5',
    waterColor: '#166088',
    mountainColor: '#5a5a5a',
    forestColor: '#2a5a3a',
    desertColor: '#c4a484'
};

// Initialize Three.js scene
let scene, camera, renderer, controls;
let terrainMesh, poiMarkers = [];
let worldData = {};

// Main initialization
function init() {
    // Create scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a1929);

    // Create camera
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(state.cameraPosition.x, state.cameraPosition.y, state.cameraPosition.z);

    // Create renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth * 0.7, window.innerHeight);
    renderer.shadowMap.enabled = true;
    document.getElementById('three-container').appendChild(renderer.domElement);

    // Add controls
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;

    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1, 1, 1);
    directionalLight.castShadow = true;
    scene.add(directionalLight);

    // Add skybox
    createSkybox();

    // Add grid helper
    const gridHelper = new THREE.GridHelper(100, 100, 0x333333, 0x222222);
    scene.add(gridHelper);

    // Initialize empty terrain
    createEmptyTerrain();

    // Handle window resize
    window.addEventListener('resize', onWindowResize);

    // Add event listeners
    setupEventListeners();

    // Start animation loop
    animate();
}

// Create skybox
function createSkybox() {
    const skyboxGeometry = new THREE.SphereGeometry(500, 60, 40);
    const skyboxMaterial = new THREE.MeshBasicMaterial({
        color: 0x111133,
        side: THREE.BackSide
    });

    const skybox = new THREE.Mesh(skyboxGeometry, skyboxMaterial);
    scene.add(skybox);
}

// Create empty terrain placeholder
function createEmptyTerrain() {
    const geometry = new THREE.PlaneGeometry(state.worldSize, state.worldSize, state.worldSize - 1, state.worldSize - 1);
    const material = new THREE.MeshStandardMaterial({
        color: parseInt(state.terrainColor.replace('#', '0x')),
        wireframe: state.showWireframe,
        side: THREE.DoubleSide
    });

    terrainMesh = new THREE.Mesh(geometry, material);
    terrainMesh.rotation.x = -Math.PI / 2;
    terrainMesh.position.y = -0.5;
    terrainMesh.receiveShadow = true;
    scene.add(terrainMesh);
}

// Update terrain from world data
function updateTerrain() {
    if (!worldData.heightmap || !worldData.biomes) return;

    const size = worldData.heightmap.length;
    const geometry = new THREE.PlaneGeometry(size, size, size - 1, size - 1);

    // Set vertex heights
    const position = geometry.attributes.position;
    for (let i = 0; i < position.count; i++) {
        const x = i % size;
        const z = Math.floor(i / size);
        const height = worldData.heightmap[z][x] || 0;
        position.setY(i, height * 5); // Scale height for visibility
    }

    // Calculate normals for lighting
    geometry.computeVertexNormals();

    // Create color map based on biomes
    const colors = [];
    const colorMap = createBiomeColorMap();

    for (let z = 0; z < size; z++) {
        for (let x = 0; x < size; x++) {
            const biome = worldData.biomes[z][x] || 'water';
            const color = colorMap[biome] || new THREE.Color(0x4a6fa5);
            colors.push(color.r, color.g, color.b);
        }
    }

    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

    const material = new THREE.MeshStandardMaterial({
        vertexColors: true,
        wireframe: state.showWireframe,
        side: THREE.DoubleSide
    });

    // Remove old terrain
    if (terrainMesh) {
        scene.remove(terrainMesh);
    }

    terrainMesh = new THREE.Mesh(geometry, material);
    terrainMesh.rotation.x = -Math.PI / 2;
    terrainMesh.position.y = -2.5; // Adjust for height scaling
    terrainMesh.receiveShadow = true;
    scene.add(terrainMesh);

    // Add water plane
    addWaterPlane(size);
}

// Add water plane
function addWaterPlane(size) {
    const waterGeometry = new THREE.PlaneGeometry(size, size);
    const waterMaterial = new THREE.MeshStandardMaterial({
        color: parseInt(state.waterColor.replace('#', '0x')),
        transparent: true,
        opacity: 0.7,
        side: THREE.DoubleSide
    });

    const water = new THREE.Mesh(waterGeometry, waterMaterial);
    water.rotation.x = -Math.PI / 2;
    water.position.y = -2.6; // Slightly below terrain
    scene.add(water);
}

// Create biome color mapping
function createBiomeColorMap() {
    return {
        water: new THREE.Color(state.waterColor.replace('#', '0x')),
        ocean: new THREE.Color(0x166088),
        beach: new THREE.Color(0xf1dbbf),
        forest: new THREE.Color(state.forestColor.replace('#', '0x')),
        grassland: new THREE.Color(0x6a994e),
        desert: new THREE.Color(state.desertColor.replace('#', '0x')),
        mountain: new THREE.Color(state.mountainColor.replace('#', '0x')),
        snow: new THREE.Color(0xffffff),
        tundra: new THREE.Color(0xa0d2eb),
        swamp: new THREE.Color(0x4a5d23),
        jungle: new THREE.Color(0x228b22),
        plains: new THREE.Color(0xadc178),
        hills: new THREE.Color(0x8b7355)
    };
}

// Add POI marker
function addPOIMarker(poi) {
    // Remove existing marker if it exists
    const existingMarker = poiMarkers.find(m => m.userData.poiId === poi.id);
    if (existingMarker) {
        scene.remove(existingMarker);
        poiMarkers = poiMarkers.filter(m => m.userData.poiId !== poi.id);
    }

    const geometry = new THREE.ConeGeometry(1, 2, 8);
    const material = new THREE.MeshStandardMaterial({
        color: 0xff5555,
        emissive: 0xff2222,
        emissiveIntensity: 0.5
    });

    const marker = new THREE.Mesh(geometry, material);
    marker.position.set(poi.x, 0, poi.z);
    marker.position.y = getTerrainHeight(poi.x, poi.z) + 1; // Position above terrain
    marker.userData = { poiId: poi.id, poiData: poi };
    marker.castShadow = true;

    scene.add(marker);
    poiMarkers.push(marker);

    // Add label
    addPOILabel(poi, marker.position);
}

// Add POI label
function addPOILabel(poi, position) {
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 64;
    const context = canvas.getContext('2d');

    context.fillStyle = 'rgba(0, 0, 0, 0.7)';
    context.fillRect(0, 0, canvas.width, canvas.height);

    context.fillStyle = 'white';
    context.font = 'Bold 16px Arial';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(poi.name || 'Unnamed POI', canvas.width / 2, canvas.height / 2);

    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.SpriteMaterial({ map: texture });
    const sprite = new THREE.Sprite(material);

    sprite.position.copy(position);
    sprite.position.y += 3; // Position above marker
    sprite.scale.set(10, 2.5, 1);
    sprite.userData = { poiId: poi.id };

    scene.add(sprite);
}

// Get terrain height at position
function getTerrainHeight(x, z) {
    if (!worldData.heightmap || !worldData.heightmap[z] || !worldData.heightmap[z][x]) {
        return 0;
    }
    return worldData.heightmap[z][x] * 5;
}

// Update region visualization
function updateRegionVisualization(region) {
    // This would highlight the specific region
    console.log('Region updated:', region);
}

// Handle window resize
function onWindowResize() {
    const container = document.getElementById('three-container');
    camera.aspect = container.clientWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, window.innerHeight);
}

// Setup event listeners
function setupEventListeners() {
    // Reset camera button
    document.getElementById('reset-camera').addEventListener('click', () => {
        controls.reset();
    });

    // Toggle wireframe button
    document.getElementById('toggle-wireframe').addEventListener('click', () => {
        state.showWireframe = !state.showWireframe;
        if (terrainMesh && terrainMesh.material) {
            terrainMesh.material.wireframe = state.showWireframe;
            terrainMesh.material.needsUpdate = true;
        }
    });

    // Connect button
    document.getElementById('connect-btn').addEventListener('click', () => {
        window.dispatchEvent(new CustomEvent('connect-server'));
    });

    // Generate world button
    document.getElementById('generate-world').addEventListener('click', () => {
        window.dispatchEvent(new CustomEvent('generate-world'));
    });

    // Clear events button
    document.getElementById('clear-events').addEventListener('click', () => {
        document.getElementById('event-feed').innerHTML = '';
    });

    // Tab switching
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', () => {
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

            button.classList.add('active');
            document.getElementById(button.dataset.tab + '-tab').classList.add('active');
        });
    });
}

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);

    // Update FPS counter
    updateFPSCounter();
}

// Update FPS counter
let lastTime = performance.now();
let frameCount = 0;
let fps = 0;

function updateFPSCounter() {
    frameCount++;
    const now = performance.now();
    const delta = now - lastTime;

    if (delta >= 1000) {
        fps = Math.round((frameCount * 1000) / delta);
        document.getElementById('fps-counter').textContent = `FPS: ${fps}`;
        frameCount = 0;
        lastTime = now;
    }
}

// Public API
export function updateWorldData(data) {
    worldData = data;
    updateTerrain();

    // Update stats
    document.getElementById('world-size').textContent = `${data.width || 0}x${data.height || 0}`;
    document.getElementById('biome-count').textContent = Object.keys(data.biomes || {}).length;
}

// Public API for adding events
export function addEvent(message, type = 'info') {
    const eventFeed = document.getElementById('event-feed');
    const eventItem = document.createElement('div');
    eventItem.className = 'event-item';
    eventItem.textContent = message;
    eventFeed.appendChild(eventItem);
    eventFeed.scrollTop = eventFeed.scrollHeight;
}

// Public API for updating connection status
export function setConnectionStatus(connected) {
    const statusElement = document.getElementById('connection-status');
    if (connected) {
        statusElement.textContent = '🟢 Connected';
        statusElement.className = 'connected';
    } else {
        statusElement.textContent = '🔴 Disconnected';
        statusElement.className = 'disconnected';
    }
}

// Initialize when imported
init();

// Export state for debugging
export { state, scene, camera, controls };