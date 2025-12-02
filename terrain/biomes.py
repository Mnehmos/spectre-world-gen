"""
Biome Classifier

Classifies terrain regions into biomes based on elevation and moisture.
"""

from typing import Dict, List, Tuple
import math

class BiomeClassifier:
    def __init__(self):
        # Biome definitions
        self.biomes = {
            "ocean": {"elevation": (0.0, 0.1), "moisture": (0.0, 1.0), "color": "#1E88E5"},
            "beach": {"elevation": (0.1, 0.15), "moisture": (0.0, 1.0), "color": "#FFF176"},
            "desert": {"elevation": (0.15, 0.5), "moisture": (0.0, 0.3), "color": "#FFD54F"},
            "grassland": {"elevation": (0.15, 0.5), "moisture": (0.3, 0.7), "color": "#A5D6A7"},
            "forest": {"elevation": (0.15, 0.5), "moisture": (0.7, 1.0), "color": "#4CAF50"},
            "swamp": {"elevation": (0.15, 0.3), "moisture": (0.8, 1.0), "color": "#689F38"},
            "hills": {"elevation": (0.5, 0.7), "moisture": (0.0, 1.0), "color": "#8D6E63"},
            "mountain": {"elevation": (0.7, 1.0), "moisture": (0.0, 1.0), "color": "#795548"},
            "snow": {"elevation": (0.8, 1.0), "moisture": (0.0, 1.0), "color": "#FFFFFF"},
            "tundra": {"elevation": (0.7, 0.9), "moisture": (0.0, 0.5), "color": "#E0E0E0"}
        }

    def classify_biome(self, elevation: float, moisture: float) -> Tuple[str, str]:
        """Classify biome based on elevation and moisture"""
        for biome_name, biome_data in self.biomes.items():
            elev_min, elev_max = biome_data["elevation"]
            moist_min, moist_max = biome_data["moisture"]

            if elev_min <= elevation <= elev_max and moist_min <= moisture <= moist_max:
                return biome_name, biome_data["color"]

        # Default to grassland if no biome matches
        return "grassland", "#A5D6A7"

    def generate_moisture_map(self, width: int, height: int, seed: int = 42) -> List[List[float]]:
        """Generate moisture map using simple noise"""
        import random
        random.seed(seed)

        moisture_map = []
        for y in range(height):
            row = []
            for x in range(width):
                # Simple moisture based on distance from center
                center_x, center_y = width / 2, height / 2
                distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                distance_normalized = distance / math.sqrt(center_x**2 + center_y**2)

                # Add some randomness
                moisture = 1.0 - distance_normalized + random.uniform(-0.1, 0.1)
                moisture = max(0.0, min(1.0, moisture))  # Clamp to 0-1
                row.append(moisture)
            moisture_map.append(row)

        return moisture_map

    def classify_heightmap(self, heightmap: List[List[float]], moisture_map: List[List[float]] = None) -> Dict[str, Dict[str, any]]:
        """Classify entire heightmap into biomes"""
        if moisture_map is None:
            # Generate moisture map if not provided
            moisture_map = self.generate_moisture_map(len(heightmap), len(heightmap[0]))

        biome_grid = {}

        for y, row in enumerate(heightmap):
            for x, elevation in enumerate(row):
                moisture = moisture_map[y][x]
                biome_name, biome_color = self.classify_biome(elevation, moisture)

                biome_grid[f"{x},{y}"] = {
                    "x": x,
                    "y": y,
                    "elevation": elevation,
                    "moisture": moisture,
                    "biome": biome_name,
                    "color": biome_color
                }

        return biome_grid