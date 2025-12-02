
"""
SPECTRE World Generation - World Engine

Core world generation and management engine.
"""

import uuid
import random
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import numpy as np
from terrain.noise import PerlinNoise
from terrain.biomes import BiomeClassifier
from terrain.mesh import TerrainMeshGenerator

class WorldEngine:
    """
    Core world generation and management engine.
    """

    def __init__(self):
        self.worlds: Dict[str, Dict] = {}
        self.poi_counter = 0
        self.event_counter = 0
        self.lore_counter = 0

        # Initialize terrain components
        self.noise_gen = PerlinNoise()
        self.biome_classifier = BiomeClassifier()
        self.mesh_gen = TerrainMeshGenerator()

    def create_world(self, width: int = 64, height: int = 64, seed: Optional[str] = None, island_mode: bool = True) -> Dict[str, Any]:
        """
        Create a new procedural world.

        Args:
            width: World width
            height: World height
            seed: Random seed for reproducibility
            island_mode: Generate island-style terrain

        Returns:
            World data dictionary
        """
        world_id = str(uuid.uuid4())
        seed_value = seed or str(random.randint(0, 1000000))

        # Generate terrain
        if island_mode:
            heightmap = self.noise_gen.generate_island_heightmap(width, height, seed=int(seed_value))
        else:
            heightmap = self.noise_gen.generate_heightmap(width, height, seed=int(seed_value))

        # Classify biomes
        moisture_map = self.biome_classifier.generate_moisture_map(heightmap, seed=int(seed_value))
        biome_grid, biome_stats = self.biome_classifier.classify_heightmap(heightmap, moisture_map)

        # Generate mesh data
        mesh_data = self.mesh_gen.generate_biome_mesh_data(heightmap, biome_grid)

        # Create world data
        world_data = {
            "id": world_id,
            "width": width,
            "height": height,
            "seed": seed_value,
            "island_mode": island_mode,
            "created_at": datetime.now().isoformat(),
            "heightmap": heightmap.tolist(),
            "biomes": biome_grid.tolist(),
            "moisture": moisture_map.tolist(),
            "mesh": mesh_data,
            "statistics": {
                "biome_distribution": biome_stats,
                "poi_count": 0,
                "named_regions": 0,
                "lore_entries": 0
            },
            "regions": {},
            "pois": {},
            "lore": {},
            "timeline": []
        }

        # Store world
        self.worlds[world_id] = world_data

        return world_data

    def get_world(self, world_id: str) -> Optional[Dict[str, Any]]:
        """
        Get world data by ID.

        Args:
            world_id: World identifier

        Returns:
            World data or None if not found
        """
        return self.worlds.get(world_id)

    def get_statistics(self, world_id: str) -> Optional[Dict[str, Any]]:
        """
        Get world statistics.

        Args:
            world_id: World identifier

        Returns:
            Statistics dictionary or None
        """
        world = self.get_world(world_id)
        if not world:
            return None

        return world.get("statistics", {})

    def get_region(self, world_id: str, x: int, y: int) -> Optional[Dict[str, Any]]:
        """
        Get region details at specific coordinates.

        Args:
            world_id: World identifier
            x: X coordinate
            y: Y coordinate

        Returns:
            Region data or None
        """
        world = self.get_world(world_id)
        if not world:
            return None

        # Create region key
        region_key = f"{x},{y}"

        # Get or create region
        if region_key not in world["regions"]:
            biome = world["biomes"][y][x]
            height = world["heightmap"][y][x]

            world["regions"][region_key] = {
                "x": x,
                "y": y,
                "biome": biome,
                "height": height,
                "name": None,
                "description": None,
                "discovered": False,
                "explored": False
            }

        return world["regions"][region_key]

    def name_region(self, world_id: str, x: int, y: int, name: str, style: str = "fantasy") -> Dict[str, Any]:
        """
        Name a region.

        Args:
            world_id: World identifier
            x: X coordinate
            y: Y coordinate
            name: Region name
            style: Naming style

        Returns:
            Updated region data
        """
        world = self.get_world(world_id)
        if not world:
            raise ValueError("World not found")

        region = self.get_region(world_id, x, y)
        if not region:
            raise ValueError("Region not found")

        region_key = f"{x},{y}"

        # Update region
        world["regions"][region_key]["name"] = name
        world["regions"][region_key]["discovered"] = True

        # Update statistics
        world["statistics"]["named_regions"] = world["statistics"].get("named_regions", 0) + 1

        return world["regions"][region_key]

    def describe_region(self, world_id: str, x: int, y: int) -> str:
        """
        Generate rich description for a region.

        Args:
            world_id: World identifier
            x: X coordinate
            y: Y coordinate

        Returns:
            Descriptive text
        """
        region = self.get_region(world_id, x, y)
        if not region:
            raise ValueError("Region not found")

        biome = region["biome"]
        region_name = region.get("name", f"Region at ({x}, {y})")

        # Generate biome-specific description
        description = self.biome_classifier.generate_biome_description(biome, region_name)

        # Update region
        region_key = f"{x},{y}"
        world = self.get_world(world_id)
        world["regions"][region_key]["description"] = description
        world["regions"][region_key]["explored"] = True

        return description

    def batch_name_regions(self, world_id: str, regions: List[Dict], style: str = "fantasy") -> List[Dict]:
        """
        Name multiple regions at once.

        Args:
            world_id: World identifier
            regions: List of region data
            style: Naming style

        Returns:
            List of updated regions
        """
        results = []

        for region_data in regions:
            x = region_data.get("x")
            y = region_data.get("y")
            name = region_data.get("name")

            if x is None or y is None or name is None:
                continue

            result = self.name_region(world_id, x, y, name, style)
            results.append(result)

        return results

    def list_pois(self, world_id: str) -> List[Dict]:
        """
        List all points of interest in a world.

        Args:
            world_id: World identifier

        Returns:
            List of POI dictionaries
        """
        world = self.get_world(world_id)
        if not world:
            return []

        return list(world["pois"].values())

    def create_poi(self, world_id: str, poi_type: str, x: int, y: int, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new point of interest.

        Args:
            world_id: World identifier
            poi_type: Type of POI
            x: X coordinate
            y: Y coordinate
            name: Optional POI name

        Returns:
            Created POI data
        """
        world = self.get_world(world_id)
        if not world:
            raise ValueError("World not found")

        # Generate POI ID
        self.poi_counter += 1
        poi_id = f"poi_{self.poi_counter}"

        # Generate name if not provided
        if not name:
            name = self._generate_poi_name(poi_type)

        # Create POI data
        poi_data = {
            "id": poi_id,
            "type": poi_type,
            "x": x,
            "y": y,
            "name": name,
            "biome": world["biomes"][y][x],
            "height": world["heightmap"][y][x],
            "description": self._generate_poi_description(poi_type, name),
            "npcs": [],
            "rumors": [],
            "secrets": [],
            "connections": [],
            "discovered": False,
            "explored": False,
            "created_at": datetime.now().isoformat()
        }

        # Add to world
        world["pois"][poi_id] = poi_data
        world["statistics"]["poi_count"] = len(world["pois"])

        return poi_data

    def update_poi(self, world_id: str, poi_id: str, updates: Dict) -> Dict[str, Any]:
        """
        Update an existing POI.

        Args:
            world_id: World identifier
            poi_id: POI identifier
            updates: Dictionary of updates

        Returns:
            Updated POI data
        """
        world = self.get_world(world_id)
        if not world or poi_id not in world["pois"]:
            raise ValueError("POI not found")

        # Apply updates
        for key, value in updates.items():
            if key in world["pois"][poi_id]:
                world["pois"][poi_id][key] = value

        return world["pois"][poi_id]

    def detail_poi(self, world_id: str, poi_id: str, detail_level: str = "medium") -> Dict[str, Any]:
        """
        Generate detailed content for a POI.

        Args:
            world_id: World identifier
            poi_id: POI identifier
            detail_level: Level of detail

        Returns:
            Detailed POI data
        """
        world = self.get_world(world_id)
        if not world or poi_id not in world["pois"]:
            raise ValueError("POI not found")

        poi = world["pois"][poi_id]
        poi_type = poi["type"]

        # Generate NPCs
        npc_count = 3 if detail_level == "high" else 2 if detail_level == "medium" else 1
        poi["npcs"] = [self._generate_npc(poi_type) for _ in range(npc_count)]

        # Generate rumors
        rumor_count = 5 if detail_level == "high" else 3 if detail_level == "medium" else 1
        poi["rumors"] = [self._generate_rumor(poi_type, poi["name"]) for _ in range(rumor_count)]

        # Generate secrets
        if detail_level in ["medium", "high"]:
            secret_count = 2 if detail_level == "high" else 1
            poi["secrets"] = [self._generate_secret(poi_type) for _ in range(secret_count)]

        poi["explored"] = True

        return poi

    def generate_world_lore(self, world_id: str, lore_type: str, themes: List[str] = []) -> Dict[str, Any]:
        """
        Generate world lore and mythology.

        Args:
            world_id: World identifier
            lore_type: Type of lore to generate
            themes: Optional themes to incorporate

        Returns:
            Generated lore data
        """
        world = self.get_world(world_id)
        if not world:
            raise ValueError("World not found")

        self.lore_counter += 1
        lore_id = f"lore_{self.lore_counter}"

        lore_content = self._generate_lore_content(lore_type, themes, world)

        lore_data = {
            "id": lore_id,
            "type": lore_type,
            "title": self._generate_lore_title(lore_type),
            "content": lore_content,
            "themes": themes,
            "created_at": datetime.now().isoformat()
        }

        world["lore"][lore_id] = lore_data
        world["statistics"]["lore_entries"] = len(world["lore"])

        return lore_data

    def add_historical_event(self, world_id: str, event_type: str, description: str, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a historical event to world timeline.

        Args:
            world_id: World identifier
            event_type: Type of event
            description: Event description
            date: Optional event date

        Returns:
            Created event data
        """
        world = self.get_world(world_id)
        if not world:
            raise ValueError("World not found")

        self.event_counter += 1
        event_id = f"event_{self.event_counter}"

        event_date = date or self._generate_event_date()

        event_data = {
            "id": event_id,
            "type": event_type,
            "description": description,
            "date": event_date,
            "created_at": datetime.now().isoformat()
        }

        world["timeline"].append(event_data)
        world["timeline"].sort(key=lambda e: e["date"])

        return event_data

    # Helper methods

    def _generate_poi_name(self, poi_type: str) -> str:
        """Generate a name for a POI based on its type."""
        prefixes = {
            "settlement": ["Vale", "Haven", "Keep", "Watch", "Rest", "Ford"],
            "ruin": ["Elden", "Forgotten", "Ancient", "Lost", "Crumbled", "Fallen"],
            "temple": ["Sanctum", "Shrine", "Altar", "Monastery", "Abbey", "Cathedral"],
            "cave": ["Gloom", "Echo", "Whisper", "Dark", "Deep", "Hollow"],
            "fortress": ["Iron", "Stone", "Black", "White", "Eagle", "Wolf"],
            "mine": ["Deeprock", "Ironvein", "Gold", "Silver", "Crystal", "Ore"]
        }

        suffixes = {
            "settlement": ["wood", "brook", "field", "hill", "dale", "mere"],
            "ruin": ["tower", "hall", "citadel", "bastion", "spire", "keep"],
            "temple": ["of Light", "of Shadows", "of the Moon", "of the Sun", "of Stars", "of Dawn"],
            "cave": ["delve", "pit", "maw", "abyss", "chasm", "depths"],
            "fortress": ["hold", "keep", "fort", "castle", "stronghold", "citadel"],
            "mine": ["pit", "shaft", "delve", "tunnel", "gallery", "works"]
        }

        base = random.choice(prefixes.get(poi_type, ["Mystic"]))
        end = random.choice(suffixes.get(poi_type, ["Place"]))

        return f"{base}{end}"

    def _generate_poi_description(self, poi_type: str, name: str) -> str:
        """Generate description for a POI."""
        descriptions = {
            "settlement": f"{name} is a bustling settlement known for its {random.choice(['friendly inhabitants', 'vibrant market', 'ancient traditions', 'strategic location'])}.",
            "ruin": f"The crumbling remains of {name} whisper tales of {random.choice(['ancient glory', 'forgotten magic', 'lost knowledge', 'past tragedies'])}.",
            "temple": f"{name} stands as a sacred site where {random.choice(['pilgrims gather', 'mysteries unfold', 'ancient rituals persist', 'divine presence lingers'])}.",
            "cave": f"Dark and foreboding, {name} hides {random.choice(['untold treasures', 'dangerous creatures', 'ancient secrets', 'forgotten pathways'])} within its depths.",
            "fortress": f"{name} looms as an impregnable bastion, its walls bearing the scars of {random.choice(['countless battles', 'ancient sieges', 'generations of defenders', 'legendary conflicts'])}.",
            "mine": f"Deep within {name}, miners toil to extract {random.choice(['precious ores', 'rare crystals', 'ancient artifacts', 'mystical minerals'])} from the earth."
        }

        return descriptions.get(poi_type, f"{name} is a place of mystery and wonder.")

    def _generate_npc(self, poi_type: str) -> Dict[str, Any]:
        """Generate an NPC for a POI."""
        first_names = ["Aelric", "Brianna", "Cedric", "Daria", "Eamon", "Fiona", "Garrick", "Hilda"]
        last_names = ["Ironwood", "Stormborn", "Frostveil", "Darkleaf", "Brightforge", "Shadowmere"]

        roles = {
            "settlement": ["Mayor", "Blacksmith", "Innkeeper", "Healer", "Guard", "Merchant"],
            "ruin": ["Ghost", "Scholar", "Adventurer", "Guardian", "Looter", "Historian"],
            "temple": ["High Priest", "Acolyte", "Paladin", "Seer", "Monk", "Confessor"],
            "cave": ["Explorer", "Miner", "Bandit", "Hermit", "Beast", "Treasure Hunter"],
            "fortress": ["Captain", "Soldier", "Armsmaster", "Scout", "Prisoner", "Spymaster"],
            "mine": ["Foreman", "Miner", "Assayer", "Engineer", "Slave", "Prospector"]
        }

        return {
            "id": f"npc_{uuid.uuid4().hex[:8]}",
            "name": f"{random.choice(first_names)} {random.choice(last_names)}",
            "role": random.choice(roles.get(poi_type, ["Mysterious Figure"])),
            "description": self._generate_npc_description(poi_type),
            "alignment": random.choice(["friendly", "neutral", "hostile", "unpredictable"])
        }

    def _generate_npc_description(self, poi_type: str) -> str:
        """Generate description for an NPC."""
        traits = {
            "settlement": ["welcoming", "hardworking", "wise", "cunning", "generous", "suspicious"],
            "ruin": ["haunted", "knowledgeable", "brave", "greedy", "cursed", "obsessed"],
            "temple": ["devout", "mysterious", "peaceful", "fanatical", "enlightened", "ascetic"],
            "cave": ["tough", "resourceful", "paranoid", "ruthless", "lonely", "determined"],
            "fortress": ["disciplined", "vigilant", "loyal", "brutal", "strategic", "honorable"],
            "mine": ["strong", "practical", "greedy", "skilled", "weary", "ambitious"]
        }

        return f"A {random.choice(traits.get(poi_type, ['mysterious']))} individual with {random.choice([' piercing eyes', ' a scarred face', ' an air of authority', ' a quiet demeanor'])}."

    def _generate_rumor(self, poi_type: str, poi_name: str) -> str:
        """Generate a rumor about a POI."""
        rumor_types = {
            "settlement": [
                f"They say {poi_name} was built on {random.choice(['ancient ruins', 'a buried treasure', 'a sacred site', 'a dragon's hoard'])}.",
                f"The {random.choice(['mayor', 'blacksmith', 'innkeeper'])} of {poi_name} is said to be {random.choice(['a spy', 'a wizard', 'a vampire', 'a saint'])}.",
                f"Travelers whisper that {poi_name} hides {random.choice(['a secret tunnel', 'a magical artifact', 'a cursed relic', 'a portal to another world'])}."
            ],
            "ruin": [
                f"{poi_name} is haunted by the ghost of {random.choice(['a betrayed king', 'a murdered priestess', 'a fallen warrior', 'a heartbroken lover'])}.",
                f"They say {poi_name} was destroyed by {random.choice(['a dragon', 'a curse', 'an ancient weapon', 'divine wrath'])}.",
                f"At midnight, the ruins of {poi_name} {random.choice(['glow with eerie light', 'echo with ghostly voices', 'reveal hidden passages', 'come alive with shadows'])}."
            ],
            "temple": [
                f"{poi_name} is said to grant {random.choice(['visions', 'healing', 'curses', 'blessings'])} to those who {random.choice(['pray sincerely', 'offer sacrifices', 'solve its riddles', 'pass its trials'])}.",
