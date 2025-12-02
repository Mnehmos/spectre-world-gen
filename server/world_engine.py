"""
World Engine

Core procedural world generation and management system.
"""

import random
import math
import json
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime

class WorldEngine:
    def __init__(self):
        self.world_state = {
            "seed": 42,
            "size": 64,
            "regions": {},
            "pois": {},
            "lore": []
        }
        self.db_path = "world.db"
        self._initialize_database()

    def _initialize_database(self):
        """Initialize SQLite database for world persistence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS worlds (
            id INTEGER PRIMARY KEY,
            seed INTEGER,
            size INTEGER,
            created_at TEXT,
            updated_at TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS regions (
            id INTEGER PRIMARY KEY,
            world_id INTEGER,
            x INTEGER,
            y INTEGER,
            biome TEXT,
            name TEXT,
            description TEXT,
            FOREIGN KEY (world_id) REFERENCES worlds (id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pois (
            id TEXT PRIMARY KEY,
            world_id INTEGER,
            x INTEGER,
            y INTEGER,
            poi_type TEXT,
            name TEXT,
            description TEXT,
            details TEXT,
            FOREIGN KEY (world_id) REFERENCES worlds (id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS lore (
            id INTEGER PRIMARY KEY,
            world_id INTEGER,
            lore_type TEXT,
            theme TEXT,
            content TEXT,
            created_at TEXT,
            FOREIGN KEY (world_id) REFERENCES worlds (id)
        )
        """)

        conn.commit()
        conn.close()

    def create_world(self, seed: int = 42, size: int = 64, island_mode: bool = True):
        """Generate a new procedural world"""
        self.world_state = {
            "seed": seed,
            "size": size,
            "regions": {},
            "pois": {},
            "lore": []
        }

        random.seed(seed)

        # Generate basic terrain (placeholder - will be enhanced by terrain module)
        for x in range(size):
            for y in range(size):
                region_id = f"{x},{y}"

                # Simple biome determination based on position
                distance_from_center = math.sqrt((x - size/2)**2 + (y - size/2)**2)
                center_distance_ratio = distance_from_center / (size * 0.707)

                if center_distance_ratio < 0.3:
                    biome = "grassland"
                elif center_distance_ratio < 0.6:
                    biome = "forest"
                elif center_distance_ratio < 0.8:
                    biome = "hills"
                else:
                    biome = "mountain"

                self.world_state["regions"][region_id] = {
                    "x": x,
                    "y": y,
                    "biome": biome,
                    "name": "",
                    "description": ""
                }

        # Add some initial POIs
        self._generate_initial_pois()

        # Save to database
        self._save_world_state()

        return {
            "status": "success",
            "world": self.world_state
        }

    def _generate_initial_pois(self):
        """Generate initial points of interest"""
        size = self.world_state["size"]
        poi_types = ["settlement", "ruins", "landmark", "dungeon"]

        for i in range(10):  # 10 initial POIs
            x = random.randint(0, size - 1)
            y = random.randint(0, size - 1)
            poi_type = random.choice(poi_types)

            poi_id = f"poi_{i}"
            self.world_state["pois"][poi_id] = {
                "id": poi_id,
                "type": poi_type,
                "x": x,
                "y": y,
                "name": f"Unnamed {poi_type}",
                "description": "",
                "details": {}
            }

    def _save_world_state(self):
        """Save current world state to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Save world metadata
        cursor.execute("""
        INSERT INTO worlds (seed, size, created_at, updated_at)
        VALUES (?, ?, ?, ?)
        """, (
            self.world_state["seed"],
            self.world_state["size"],
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))

        world_id = cursor.lastrowid

        # Save regions
        for region_id, region in self.world_state["regions"].items():
            cursor.execute("""
            INSERT INTO regions (world_id, x, y, biome, name, description)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                world_id,
                region["x"],
                region["y"],
                region["biome"],
                region["name"],
                region["description"]
            ))

        # Save POIs
        for poi_id, poi in self.world_state["pois"].items():
            cursor.execute("""
            INSERT INTO pois (id, world_id, x, y, poi_type, name, description, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                poi_id,
                world_id,
                poi["x"],
                poi["y"],
                poi["type"],
                poi["name"],
                poi["description"],
                json.dumps(poi.get("details", {}))
            ))

        conn.commit()
        conn.close()

    def get_world_state(self):
        """Get current world state"""
        return self.world_state

    def get_regions(self):
        """Get all regions"""
        return list(self.world_state["regions"].values())

    def get_pois(self):
        """Get all points of interest"""
        return list(self.world_state["pois"].values())

    def get_region(self, x: int, y: int):
        """Get region details"""
        region_id = f"{x},{y}"
        return self.world_state["regions"].get(region_id, {})

    def name_region(self, x: int, y: int, name: str, biome: str):
        """Name a region"""
        region_id = f"{x},{y}"
        if region_id in self.world_state["regions"]:
            self.world_state["regions"][region_id]["name"] = name
            self.world_state["regions"][region_id]["biome"] = biome

            # Save to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE regions
            SET name = ?, biome = ?
            WHERE world_id = (SELECT MAX(id) FROM worlds)
            AND x = ? AND y = ?
            """, (name, biome, x, y))
            conn.commit()
            conn.close()

            return {"status": "success", "region": self.world_state["regions"][region_id]}

        return {"status": "error", "message": "Region not found"}

    def create_poi(self, poi_type: str, x: int, y: int, name: str = ""):
        """Create a new point of interest"""
        poi_id = f"poi_{len(self.world_state['pois'])}"
        poi_name = name if name else f"Unnamed {poi_type}"

        self.world_state["pois"][poi_id] = {
            "id": poi_id,
            "type": poi_type,
            "x": x,
            "y": y,
            "name": poi_name,
            "description": "",
            "details": {}
        }

        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO pois (id, world_id, x, y, poi_type, name, description, details)
        VALUES (?, (SELECT MAX(id) FROM worlds), ?, ?, ?, ?, ?, ?)
        """, (poi_id, x, y, poi_type, poi_name, "", "{}"))
        conn.commit()
        conn.close()

        return self.world_state["pois"][poi_id]

    def update_poi(self, poi_id: str, updates: dict):
        """Update a point of interest"""
        if poi_id in self.world_state["pois"]:
            self.world_state["pois"][poi_id].update(updates)

            # Save to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE pois
            SET name = ?,
                description = ?,
                details = ?
            WHERE id = ?
            """, (
                self.world_state["pois"][poi_id]["name"],
                self.world_state["pois"][poi_id]["description"],
                json.dumps(self.world_state["pois"][poi_id].get("details", {})),
                poi_id
            ))
            conn.commit()
            conn.close()

            return self.world_state["pois"][poi_id]

        return {"status": "error", "message": "POI not found"}

    def detail_poi(self, poi_id: str):
        """Generate detailed information for a POI"""
        if poi_id not in self.world_state["pois"]:
            return {"status": "error", "message": "POI not found"}

        poi = self.world_state["pois"][poi_id]
        poi_type = poi["type"]

        # Generate NPCs
        npcs = []
        for i in range(random.randint(2, 5)):
            npcs.append({
                "id": f"npc_{i}",
                "name": f"{random.choice(['Eldrin', 'Thalindra', 'Gorim', 'Lysara', 'Borin'])} {random.choice(['Stoneheart', 'Swiftblade', 'Moonshadow', 'Ironvein', 'Stormcaller'])}",
                "role": random.choice(["Mayor", "Blacksmith", "Innkeeper", "Mage", "Guard", "Merchant"]),
                "description": f"A {random.choice(['wise', 'mysterious', 'friendly', 'grumpy', 'eccentric'])} {random.choice(['elf', 'dwarf', 'human', 'halfling', 'gnome'])}"
            })

        # Generate rumors
        rumors = []
        for i in range(random.randint(3, 6)):
            rumors.append({
                "id": f"rumor_{i}",
                "content": random.choice([
                    f"The old {random.choice(['temple', 'mine', 'fortress', 'library'])} beneath the {random.choice(['mountain', 'forest', 'lake', 'ruins'])} is said to contain {random.choice(['ancient treasures', 'forbidden knowledge', 'a sleeping dragon', 'the key to immortality'])}",
                    f"Strange lights have been seen near the {random.choice(['standing stones', 'abandoned tower', 'cursed swamp', 'whispering woods'])} at {random.choice(['midnight', 'dawn', 'dusk', 'the full moon'])}",
                    f"The {random.choice(['ghost', 'spirit', 'mysterious figure', 'ancient guardian'])} of {random.choice(['Lady Elara', 'Lord Malakar', 'the Forgotten King', 'the Sorceress Queen'])} is said to {random.choice(['protect', 'haunt', 'guide', 'test'])} travelers who pass through these lands",
                    f"Whispers speak of a {random.choice(['secret passage', 'hidden treasure', 'ancient artifact', 'forgotten prophecy'])} that could {random.choice(['save the kingdom', 'bring great power', 'unleash darkness', 'change the course of history'])}"
                ])
            })

        # Update POI details
        details = {
            "npcs": npcs,
            "rumors": rumors,
            "secrets": random.randint(0, 3)
        }

        self.world_state["pois"][poi_id]["details"] = details

        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE pois
        SET details = ?
        WHERE id = ?
        """, (json.dumps(details), poi_id))
        conn.commit()
        conn.close()

        return self.world_state["pois"][poi_id]

    def generate_world_lore(self, lore_type: str, theme: str = "fantasy"):
        """Generate world lore"""
        lore_content = ""

        if lore_type == "creation_myth":
            lore_content = (
                "In the beginning, there was only the Void. From the Void emerged the First Ones, "
                "who shaped the world with their dreams. The mountains were their thoughts, "
                "the rivers their tears, and the forests their laughter. But when the First Ones "
                "faded, they left behind the Echoes - the spirits that would become the first "
                "mortals, destined to shape the world anew."
            )
        elif lore_type == "historical_event":
            lore_content = (
                f"In the year {random.randint(100, 1000)} of the Third Age, the great {random.choice(['Battle of the Five Armies', 'War of the Shattered Crown', 'Siege of the Obsidian Keep', 'Rising of the Shadow King'])} "
                "took place in these lands. It was said that the very earth trembled as {random.choice(['dragons', 'ancient sorcerers', 'the gods themselves', 'forgotten beings'])} "
                "walked among mortals. The {random.choice(['blood', 'magic', 'destruction', 'courage'])} spilled that day would echo through the ages..."
            )
        elif lore_type == "local_legend":
            region = random.choice(list(self.world_state["regions"].values()))
            lore_content = (
                f"The {region['biome']} of {region.get('name', 'this land')} is said to be blessed - or cursed - "
                f"by {random.choice(['an ancient spirit', 'a forgotten god', 'the ghost of a long-dead hero', 'a powerful enchantment'])}. "
                f"Those who {random.choice(['respect the land', 'seek its secrets', 'disturb its peace', 'listen to the wind'])} "
                f"may find {random.choice(['wisdom', 'treasure', 'danger', 'their destiny'])} waiting for them."
            )

        lore_entry = {
            "id": f"lore_{len(self.world_state['lore'])}",
            "type": lore_type,
            "theme": theme,
            "content": lore_content
        }

        self.world_state["lore"].append(lore_entry)

        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO lore (world_id, lore_type, theme, content, created_at)
        VALUES ((SELECT MAX(id) FROM worlds), ?, ?, ?, ?)
        """, (lore_type, theme, lore_content, datetime.now().isoformat()))
        conn.commit()
        conn.close()

        return lore_entry

    def log_reflection(self, entry_type: str, content: str):
        """Log a reflection to the build diary"""
        # In a real implementation, this would write to the BUILD_DIARY.md
        # For now, we'll just store it in memory
        reflection = {
            "timestamp": datetime.now().isoformat(),
            "type": entry_type,
            "content": content
        }

        # This would be enhanced to actually write to the build diary file
        return {"status": "success", "reflection": reflection}