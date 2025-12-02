# SPECTRE Usage Examples & Tutorials

Comprehensive guide to using the SPECTRE World Generation System with practical examples and step-by-step tutorials.

---

## 📚 Table of Contents

1. [Quick Start Guide](#-quick-start-guide)
2. [MCP Protocol Examples](#-mcp-protocol-examples)
3. [WebSocket Integration](#-websocket-integration)
4. [REST API Usage](#-rest-api-usage)
5. [Advanced Workflows](#-advanced-workflows)
6. [Troubleshooting](#-troubleshooting)
7. [Performance Tips](#-performance-tips)

---

## 🚀 Quick Start Guide

### 1. Starting the Server

```bash
# Navigate to project directory
cd spectre-world-gen

# Install dependencies
pip install -r requirements.txt

# Start the SPECTRE server
python server/main.py

# Server will be available at:
# - HTTP: http://localhost:8000
# - WebSocket: ws://localhost:8000/ws
# - MCP: stdin (ready for commands)
```

### 2. Basic Command Flow

```json
# Step 1: Create a world
{
  "tool": "create_world",
  "arguments": {
    "width": 64,
    "height": 64,
    "seed": "my_adventure",
    "island_mode": true
  }
}

# Step 2: Name some regions
{
  "tool": "name_region",
  "arguments": {
    "world_id": "your-world-id",
    "x": 10,
    "y": 10,
    "name": "Whispering Vale",
    "style": "fantasy"
  }
}

# Step 3: Create a POI
{
  "tool": "create_poi",
  "arguments": {
    "world_id": "your-world-id",
    "type": "settlement",
    "x": 20,
    "y": 20,
    "name": "Brightwood Keep"
  }
}

# Step 4: Generate lore
{
  "tool": "generate_world_lore",
  "arguments": {
    "world_id": "your-world-id",
    "type": "creation_myth",
    "themes": ["ancient", "magic"]
  }
}
```

---

## 📡 MCP Protocol Examples

### Comprehensive MCP Session

```json
// 1. Create a new world
{
  "tool": "create_world",
  "arguments": {
    "width": 128,
    "height": 128,
    "seed": "epic_adventure",
    "island_mode": false
  }
}

// 2. Get world statistics
{
  "tool": "get_statistics",
  "arguments": {
    "world_id": "your-world-id"
  }
}

// 3. Get region details
{
  "tool": "get_region",
  "arguments": {
    "world_id": "your-world-id",
    "x": 32,
    "y": 32
  }
}

// 4. Name the region
{
  "tool": "name_region",
  "arguments": {
    "world_id": "your-world-id",
    "x": 32,
    "y": 32,
    "name": "Eldermere Forest",
    "style": "fantasy"
  }
}

// 5. Describe the region
{
  "tool": "describe_region",
  "arguments": {
    "world_id": "your-world-id",
    "x": 32,
    "y": 32
  }
}

// 6. Create multiple POIs
{
  "tool": "create_poi",
  "arguments": {
    "world_id": "your-world-id",
    "type": "ruin",
    "x": 25,
    "y": 25,
    "name": "Ancient Temple"
  }
}

// 7. Detail a POI
{
  "tool": "detail_poi",
  "arguments": {
    "world_id": "your-world-id",
    "poi_id": "poi_123",
    "detail_level": "high"
  }
}

// 8. Generate comprehensive lore
{
  "tool": "generate_world_lore",
  "arguments": {
    "world_id": "your-world-id",
    "type": "creation_myth",
    "themes": ["ancient", "magic", "war"]
  }
}

// 9. Add historical events
{
  "tool": "add_historical_event",
  "arguments": {
    "world_id": "your-world-id",
    "type": "war",
    "description": "The Great Battle of Eldermere",
    "date": "Year 123 of the Third Age"
  }
}

// 10. Batch name regions
{
  "tool": "batch_name_regions",
  "arguments": {
    "world_id": "your-world-id",
    "regions": [
      {"x": 10, "y": 10, "name": "Whispering Vale"},
      {"x": 20, "y": 15, "name": "Blackstone Peaks"},
      {"x": 15, "y": 25, "name": "Silver Lake"}
    ],
    "style": "fantasy"
  }
}
```

---

## 🌐 WebSocket Integration

### JavaScript WebSocket Client

```javascript
// Connect to SPECTRE WebSocket
const socket = new WebSocket('ws://localhost:8000/ws');

// Event handlers
socket.onopen = () => {
  console.log('🟢 Connected to SPECTRE WebSocket');
  addEvent('WebSocket connection established');
};

socket.onclose = (event) => {
  console.log('🔴 WebSocket disconnected:', event.reason);
  addEvent('WebSocket disconnected');
};

socket.onerror = (error) => {
  console.error('⚠️ WebSocket error:', error);
  addEvent('WebSocket error occurred');
};

socket.onmessage = (event) => {
  try {
    const data = JSON.parse(event.data);
    handleSpectreEvent(data);
  } catch (error) {
    console.error('Error parsing message:', error);
  }
};

// Handle different event types
function handleSpectreEvent(data) {
  switch (data.type) {
    case 'world_created':
      console.log('🌍 World created:', data);
      updateWorldView(data);
      break;

    case 'region_named':
      console.log('📍 Region named:', data);
      updateRegionMarker(data);
      break;

    case 'region_described':
      console.log('📝 Region described:', data);
      showRegionDescription(data);
      break;

    case 'poi_created':
      console.log('🏰 POI created:', data);
      addPOIMarker(data);
      break;

    case 'poi_detailed':
      console.log('🎨 POI detailed:', data);
      showPOIDetails(data);
      break;

    case 'poi_updated':
      console.log('🔧 POI updated:', data);
      updatePOI(data);
      break;

    case 'lore_created':
      console.log('📜 Lore created:', data);
      addLoreEntry(data);
      break;

    case 'historical_event_added':
      console.log('📅 Event added:', data);
      addTimelineEvent(data);
      break;

    case 'statistics_updated':
      console.log('📊 Stats updated:', data);
      updateStatistics(data);
      break;

    case 'system':
      console.log('💻 System event:', data);
      handleSystemEvent(data);
      break;

    case 'error':
      console.error('❌ Error event:', data);
      showErrorNotification(data);
      break;

    default:
      console.warn('Unknown event type:', data.type);
      addEvent(`Unknown event: ${data.type}`);
  }
}

// Send MCP command via WebSocket (if supported)
function sendMCPCommand(command) {
  if (socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({
      type: 'mcp_command',
      command: command,
      timestamp: new Date().toISOString()
    }));
  } else {
    console.error('WebSocket not connected');
  }
}
```

---

## 🔗 REST API Usage

### API Endpoints Reference

```http
# Create a new world
POST /api/worlds
Content-Type: application/json

{
  "width": 64,
  "height": 64,
  "seed": "api_world",
  "island_mode": true
}

# Response:
{
  "status": "success",
  "world_id": "generated-world-id",
  "message": "World created successfully"
}

---

# Get world data
GET /api/worlds/{world_id}

# Response:
{
  "status": "success",
  "world": {
    "id": "world-id",
    "width": 64,
    "height": 64,
    "seed": "api_world",
    "island_mode": true,
    "created_at": "2025-12-02T00:00:00",
    "statistics": {...},
    "regions": {...},
    "pois": {...},
    "lore": {...},
    "timeline": [...]
  }
}

---

# Name a region
POST /api/worlds/regions/name
Content-Type: application/json

{
  "world_id": "your-world-id",
  "x": 10,
  "y": 10,
  "name": "Whispering Forest"
}

# Response:
{
  "status": "success",
  "region": {
    "x": 10,
    "y": 10,
    "biome": "forest",
    "name": "Whispering Forest",
    "description": null,
    "discovered": true,
    "explored": false
  }
}

---

# Create a POI
POST /api/worlds/{world_id}/pois
Content-Type: application/json

{
  "world_id": "your-world-id",
  "poi_type": "settlement",
  "x": 20,
  "y": 20,
  "name": "Brightwood Keep"
}

# Response:
{
  "status": "success",
  "poi": {
    "id": "poi_123",
    "type": "settlement",
    "x": 20,
    "y": 20,
    "name": "Brightwood Keep",
    "biome": "forest",
    "height": 0.45,
    "description": "Brightwood Keep is a bustling settlement...",
    "npcs": [],
    "rumors": [],
    "secrets": [],
    "connections": [],
    "discovered": false,
    "explored": false,
    "created_at": "2025-12-02T00:00:00"
  }
}

---

# Generate lore
POST /api/worlds/{world_id}/lore
Content-Type: application/json

{
  "world_id": "your-world-id",
  "lore_type": "creation_myth",
  "themes": ["ancient", "magic", "war"]
}

# Response:
{
  "status": "success",
  "lore": {
    "id": "lore_123",
    "type": "creation_myth",
    "title": "The Song of Creation",
    "content": "In the beginning, there was only the Void...",
    "themes": ["ancient", "magic", "war"],
    "created_at": "2025-12-02T00:00:00"
  }
}

---

# Get world statistics
GET /api/worlds/{world_id}/statistics

# Response:
{
  "status": "success",
  "statistics": {
    "biome_distribution": {
      "forest": 35,
      "mountain": 20,
      "plains": 15,
      "water": 12,
      "desert": 8,
      "hills": 5,
      "swamp": 3,
      "jungle": 2
    },
    "poi_count": 15,
    "named_regions": 42,
    "lore_entries": 3,
    "timeline_events": 8
  }
}

---

# Health check
GET /api/health

# Response:
{
  "status": "healthy",
  "timestamp": "2025-12-02T00:00:00",
  "worlds_in_memory": 2
}
```

---

## 🎯 Advanced Workflows

### Complete World Building Session

```python
import requests
import json
import time

# Configuration
SERVER_URL = "http://localhost:8000/api"
WORLD_NAME = "Epic Adventure World"
WORLD_SEED = "epic_adventure_2025"

def spectre_world_building_session():
    """Complete world building workflow using SPECTRE API"""

    # 1. Create the world
    print("🌍 Creating world...")
    world_response = requests.post(
        f"{SERVER_URL}/worlds",
        json={
            "width": 128,
            "height": 128,
            "seed": WORLD_SEED,
            "island_mode": False
        }
    ).json()

    world_id = world_response["world_id"]
    print(f"✅ World created: {world_id}")

    # 2. Get world statistics
    print("📊 Getting world statistics...")
    stats_response = requests.get(
        f"{SERVER_URL}/worlds/{world_id}/statistics"
    ).json()

    biome_dist = stats_response["statistics"]["biome_distribution"]
    print(f"🌲 Biome distribution: {json.dumps(biome_dist, indent=2)}")

    # 3. Name key regions strategically
    print("📍 Naming key regions...")

    key_regions = [
        {"x": 20, "y": 20, "name": "Whispering Vale", "biome": "forest"},
        {"x": 40, "y": 15, "name": "Blackstone Peaks", "biome": "mountain"},
        {"x": 15, "y": 25, "name": "Silver Lake", "biome": "water"},
        {"x": 30, "y": 30, "name": "Eldermere Forest", "biome": "forest"},
        {"x": 10, "y": 10, "name": "Sunscorch Desert", "biome": "desert"}
    ]

    for region in key_regions:
        response = requests.post(
            f"{SERVER_URL}/worlds/regions/name",
            json={
                "world_id": world_id,
                "x": region["x"],
                "y": region["y"],
                "name": region["name"]
            }
        ).json()

        if response["status"] == "success":
            print(f"  ✅ Named {region['name']} ({region['biome']})")
        else:
            print(f"  ❌ Failed to name {region['name']}")

    # 4. Create important POIs
    print("🏰 Creating important POIs...")

    important_pois = [
        {"type": "settlement", "x": 25, "y": 25, "name": "Brightwood Keep"},
        {"type": "ruin", "x": 35, "y": 15, "name": "Ancient Temple of Light"},
        {"type": "temple", "x": 45, "y": 30, "name": "Shrine of the Moon"},
        {"type": "cave", "x": 15, "y": 45, "name": "Echoing Delve"},
        {"type": "fortress", "x": 55, "y": 20, "name": "Ironwatch Citadel"}
    ]

    for poi in important_pois:
        response = requests.post(
            f"{SERVER_URL}/worlds/{world_id}/pois",
            json={
                "world_id": world_id,
                "poi_type": poi["type"],
                "x": poi["x"],
                "y": poi["y"],
                "name": poi["name"]
            }
        ).json()

        if response["status"] == "success":
            poi_id = response["poi"]["id"]
            print(f"  ✅ Created {poi['name']} (ID: {poi_id})")

            # Detail important POIs
            detail_response = requests.post(
                f"{SERVER_URL}/worlds/{world_id}/pois/{poi_id}/detail",
                params={"detail_level": "medium"}
            ).json()

            if detail_response["status"] == "success":
                print(f"    🎨 Detailed {poi['name']} with NPCs and lore")
            else:
                print(f"    ❌ Failed to detail {poi['name']}")

        else:
            print(f"  ❌ Failed to create {poi['name']}")

    # 5. Generate world lore and history
    print("📜 Generating world lore...")

    lore_types = [
        {"type": "creation_myth", "themes": ["ancient", "magic", "cosmic"]},
        {"type": "historical_event", "themes": ["war", "heroes", "ancient"]},
        {"type": "legend", "themes": ["quest", "magic", "heroic"]}
    ]

    for lore_type in lore_types:
        response = requests.post(
            f"{SERVER_URL}/worlds/{world_id}/lore",
            json={
                "world_id": world_id,
                "lore_type": lore_type["type"],
                "themes": lore_type["themes"]
            }
        ).json()

        if response["status"] == "success":
            lore_title = response["lore"]["title"]
            print(f"  ✅ Generated {lore_type['type']}: {lore_title}")
        else:
            print(f"  ❌ Failed to generate {lore_type['type']}")

    # 6. Add historical timeline events
    print("📅 Adding historical events...")

    historical_events = [
        {"type": "war", "description": "The Great Battle of Eldermere"},
        {"type": "discovery", "description": "Discovery of the Crystal Caverns"},
        {"type": "cataclysm", "description": "The Sundering of the Ancient Empire"},
        {"type": "foundation", "description": "Founding of Brightwood Keep"},
        {"type": "magic", "description": "The Awakening of the Moon Shrine"}
    ]

    for event in historical_events:
        response = requests.post(
            f"{SERVER_URL}/worlds/{world_id}/timeline",
            json={
                "world_id": world_id,
                "event_type": event["type"],
                "description": event["description"],
                "date": f"Year {random.randint(1, 5000)} of the {random.choice(['First', 'Second', 'Third', 'Fourth'])} Age"
            }
        ).json()

        if response["status"] == "success":
            print(f"  ✅ Added {event['type']}: {event['description']}")
        else:
            print(f"  ❌ Failed to add {event['type']}")

    # 7. Final statistics
    print("📊 Final world statistics...")
    final_stats = requests.get(
        f"{SERVER_URL}/worlds/{world_id}/statistics"
    ).json()

    print(f"🌍 World Summary:")
    print(f"  - Size: {final_stats['statistics'].get('width', 'N/A')}x{final_stats['statistics'].get('height', 'N/A')}")
    print(f"  - POIs: {final_stats['statistics'].get('poi_count', 0)}")
    print(f"  - Named Regions: {final_stats['statistics'].get('named_regions', 0)}")
    print(f"  - Lore Entries: {final_stats['statistics'].get('lore_entries', 0)}")
    print(f"  - Timeline Events: {len(final_stats['statistics'].get('timeline', []))}")

    print(f"\n🎉 World building complete! {WORLD_NAME} is ready for adventure!")

if __name__ == "__main__":
    spectre_world_building_session()
```

---

## 🛠️ Troubleshooting

### Common Issues & Solutions

#### 1. Server Won't Start
**Symptoms**: `python server/main.py` fails immediately
**Solutions**:
- Check Python version: `python --version` (requires 3.8+)
- Install dependencies: `pip install -r requirements.txt`
- Check for import errors in console
- Verify numpy installation: `pip install numpy`

#### 2. WebSocket Connection Fails
**Symptoms**: Cannot connect to `ws://localhost:8000/ws`
**Solutions**:
- Verify server is running
- Check firewall/antivirus settings
- Test with browser WebSocket tester
- Check server logs for errors

#### 3. MCP Commands Not Working
**Symptoms**: No response from MCP commands
**Solutions**:
- Verify command JSON format
- Check server console for errors
- Test with simple command first
- Ensure MCP handler is enabled

#### 4. Database Errors
**Symptoms**: Database-related errors in console
**Solutions**:
- Check `spectre_world.db` file permissions
- Verify database initialization
- Test with SQLite browser tool
- Check table schemas exist

#### 5. Terrain Generation Fails
**Symptoms**: World creation errors
**Solutions**:
- Install numpy: `pip install numpy`
- Check terrain module imports
- Test with smaller world sizes
- Verify biome classification logic

#### 6. Web Visualization Not Updating
**Symptoms**: 3D view not showing terrain
**Solutions**:
- Check WebSocket connection
- Verify Three.js initialization
- Test with browser console logs
- Check terrain data format

---

## ⚡ Performance Tips

### Server Optimization
- Use `--workers 4` with uvicorn for multi-core support
- Disable `--reload` in production
- Set appropriate timeouts
- Implement connection pooling for database

### World Generation
- Start with smaller sizes (32x32, 64x64)
- Use simpler terrain for testing
- Limit POI density initially
- Batch operations where possible

### Web Interface
- Simplify mesh complexity for large worlds
- Use level-of-detail techniques
- Limit WebSocket message frequency
- Implement client-side caching

### Database
- Add indexes for frequent queries
- Use transactions for batch operations
- Implement caching for read-heavy ops
- Regular database maintenance

### Development
- Use smaller test worlds
- Disable detailed logging in production
- Profile performance bottlenecks
- Optimize critical path operations

---

## 🎓 Advanced Techniques

### Custom Biome Creation
```python
# Extend biome classifier with custom biomes
class CustomBiomeClassifier(BiomeClassifier):
    def __init__(self):
        super().__init__()
        # Add custom biome rules
        self.biome_rules.append({
            'name': 'volcanic',
            'height_range': (0.8, 1.0),
            'moisture_range': (0.0, 0.3),
            'color': [0.8, 0.2, 0.1],
            'description': "Smoldering volcanic terrain with molten lava flows"
        })
```

### Extended Lore Generation
```json
{
  "tool": "generate_world_lore",
  "arguments": {
    "world_id": "your-world-id",
    "type": "historical_event",
    "themes": ["war", "magic", "ancient_civilization", "heroic_quest"],
    "custom_elements": {
      "important_characters": ["King Aldric the Wise", "The Oracle of Shadows"],
      "key_locations": ["The Obsidian Tower", "Whispering Woods", "Crystal Caverns"],
      "magical_artifacts": ["The Crystal of Truth", "Staff of Storms", "Amulet of Eternal Flame"],
      "factions": ["The Silver Covenant", "The Shadow Pact", "The Free Cities Alliance"]
    }
  }
}
```

### WebSocket Event Filtering
```javascript
// Client-side event filtering
const eventHandlers = {
    'world_created': handleWorldCreated,
    'region_named': handleRegionNamed,
    'poi_created': handlePOICreated,
    // ... other event types
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const handler = eventHandlers[data.type];

    if (handler) {
        handler(data);
    } else {
        console.log('Unhandled event:', data.type);
    }
};

// Only handle specific events
function handleWorldCreated(data) {
    if (data.width > 64) {
        console.log('Large world created:', data);
        // Special handling for large worlds
    }
}
```

### Batch Operations
```python
# Batch operations for efficiency
def batch_world_creation():
    """Create multiple worlds efficiently"""

    world_configs = [
        {"width": 64, "height": 64, "seed": "world1", "island_mode": True},
        {"width": 128, "height": 128, "seed": "world2", "island_mode": False},
        {"width": 32, "height": 32, "seed": "world3", "island_mode": True}
    ]

    created_worlds = []

    for config in world_configs:
        response = send_mcp_command({
            "tool": "create_world",
            "arguments": config
        })

        if response.get("status") == "success":
            created_worlds.append(response["world_id"])
            print(f"Created world: {response['world_id']}")

    return created_worlds
```

### Custom Event Handling
```javascript
// Enhanced WebSocket client with reconnection
class SpectreWebSocketClient {
    constructor(url) {
        this.url = url;
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        this.eventListeners = {};
        this.connected = false;
    }

    connect() {
        this.socket = new WebSocket(this.url);

        this.socket.onopen = () => {
            this.connected = true;
            this.reconnectAttempts = 0;
            console.log('🟢 Connected to SPECTRE');
            this.triggerEvent('connect');
        };

        this.socket.onclose = (event) => {
            this.connected = false;
            console.log('🔴 Disconnected:', event.reason);
            this.triggerEvent('disconnect');

            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                setTimeout(() => this.connect(), this.reconnectDelay);
                this.reconnectAttempts++;
            }
        };

        this.socket.onerror = (error) => {
            console.error('⚠️ WebSocket error:', error);
            this.triggerEvent('error', error);
        };

        this.socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.triggerEvent(data.type, data);
                this.triggerEvent('message', data);
            } catch (error) {
                console.error('Error parsing message:', error);
                this.triggerEvent('parse_error', {error, raw: event.data});
            }
        };
    }

    on(eventType, callback) {
        if (!this.eventListeners[eventType]) {
            this.eventListeners[eventType] = [];
        }
        this.eventListeners[eventType].push(callback);
    }

    triggerEvent(eventType, data) {
        const listeners = this.eventListeners[eventType] || [];
        listeners.forEach(callback => callback(data));
    }

    sendCommand(command) {
        if (this.connected && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(command));
            return true;
        }
        return false;
    }

    disconnect() {
        if (this.socket) {
            this.socket.close();
        }
    }
}

// Usage
const client = new SpectreWebSocketClient('ws://localhost:8000/ws');
client.connect();

// Listen for specific events
client.on('world_created', (data) => {
    console.log('World created:', data);
    updateWorldView(data);
});

client.on('region_named', (data) => {
    console.log('Region named:', data);
    updateRegion(data);
});

client.on('error', (error) => {
    console.error('WebSocket error:', error);
    showErrorNotification('Connection error');
});

// Send commands
client.on('connect', () => {
    client.sendCommand({
        tool: 'create_world',
        arguments: {
            width: 64,
            height: 64,
            seed: 'websocket_test',
            island_mode: true
        }
    });
});
```

---

## 📊 Monitoring & Analytics

### Server Monitoring
```python
# Health check endpoint
def monitor_server_health():
    """Monitor server health metrics"""

    while True:
        try:
            # Check server health
            health_response = requests.get('http://localhost:8000/api/health', timeout=5)
            health_data = health_response.json()

            print(f"💓 Server Health: {health_data['status']}")
            print(f"   Worlds in memory: {health_data['worlds_in_memory']}")
            print(f"   Timestamp: {health_data['timestamp']}")

            # Check database
            db_stats = get_database_stats()
            print(f"💾 Database: {db_stats['world_count']} worlds, {db_stats['poi_count']} POIs")

            # Check WebSocket connections
            ws_connections = get_websocket_connections()
            print(f"🔌 WebSocket: {ws_connections} active connections")

        except Exception as e:
            print(f"❌ Monitoring error: {e}")

        time.sleep(60)  # Check every minute
```

### Performance Profiling
```python
# Profile world generation performance
def profile_world_generation():
    """Profile terrain generation performance"""

    sizes = [32, 64, 128, 256]

    for size in sizes:
        start_time = time.time()

        # Generate world
        response = send_mcp_command({
            "tool": "create_world",
            "arguments": {
                "width": size,
                "height": size,
                "seed": f"perf_test_{size}",
                "island_mode": True
            }
        })

        end_time = time.time()
        generation_time = end_time - start_time

        if response.get("status") == "success":
            print(f"📊 {size}x{size} world: {generation_time:.2f}s")
            print(f"   Rate: {size*size/generation_time:.0f} tiles/second")

            # Clean up
            delete_response = requests.delete(
                f"http://localhost:8000/api/worlds/{response['world_id']}"
            )

        else:
            print(f"❌ Failed to generate {size}x{size} world")

        time.sleep(1)  # Cooldown between tests
```

---

## 🎓 Best Practices

### World Design
- Start with smaller worlds (32x32, 64x64) for testing
- Use meaningful seeds for reproducible worlds
- Balance biome distribution for interesting gameplay
- Cluster POIs around key regions

### Development Workflow
- Use BUILD_DIARY.md for all decisions
- Test changes incrementally
- Document MCP tool usage
- Profile performance regularly

### Error Handling
- Validate all inputs
- Handle WebSocket disconnections gracefully
- Provide meaningful error messages
- Log important events

### Performance
- Optimize critical path operations
- Cache frequent database queries
- Batch similar operations
- Monitor resource usage

---

## 📚 Additional Resources

### Learning Materials
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Three.js Documentation](https://threejs.org/docs/)
- [WebSocket API Guide](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Procedural Generation Wiki](https://pcg.wiki)

### Code Examples
- [GitHub Repository](https://github.com/spectre-world-gen)
- [JSFiddle Web Client](https://jsfiddle.net/spectre/websocket-client)
- [GitHub Gist Examples](https://gist.github.com/spectre/examples)

### Community
- [Discord Server](https://discord.gg/spectre)
- [GitHub Issues](https://github.com/spectre-world-gen/issues)
- [Feature Requests](https://github.com/spectre-world-gen/discussions)

---

**Documentation Complete**: ✅
**Last Updated**: 2025-12-02
**Version**: 1.0.0