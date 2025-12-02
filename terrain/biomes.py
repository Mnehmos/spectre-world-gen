"""
SPECTRE Terrain Generation - Biome Classification Module

Classifies terrain into different biome types based on height and moisture.
"""

from typing import Dict, List, Tuple, Optional
import numpy as np

class BiomeClassifier:
    """
    Classifies terrain into different biome types based on elevation and moisture.
    """

    def __init__(self):
        # Define biome thresholds and characteristics
        self.biome_definitions = {
            'ocean': {
                'height': (0.0, 0.15),
                'moisture': (0.0, 1.0),
                'color': (0, 100, 200),
                'description': 'Deep ocean waters'
            },
            'beach': {
                'height': (0.15, 0.2),
                'moisture': (0.7, 1.0),
                'color': (240, 220, 180),
                'description': 'Sandy coastal areas'
            },
            'swamp': {
                'height': (0.1, 0.3),
                'moisture': (0.8, 1.0),
                'color': (80, 120, 60),
                'description': 'Wet, marshy areas with dense vegetation'
            },
            'forest': {
                'height': (0.2, 0.6),
                'moisture': (0.5, 1.0),
                'color': (40, 120, 60),
                'description': 'Dense woodland with tall trees'
            },
            'jungle': {
                'height': (0.1, 0.4),
                'moisture': (0.8, 1.0),
                'color': (30, 140, 30),
                'description': 'Tropical rainforest with lush vegetation'
            },
            'grassland': {
                'height': (0.2, 0.5),
                'moisture': (0.3, 0.7),
                'color': (100, 160, 80),
                'description': 'Open plains with grasses and scattered trees'
            },
            'plains': {
                'height': (0.1, 0.3),
                'moisture': (0.2, 0.6),
                'color': (160, 200, 120),
                'description': 'Flat, open landscapes'
            },
            'desert': {
                'height': (0.1, 0.4),
                'moisture': (0.0, 0.3),
                'color': (200, 180, 140),
                'description': 'Arid regions with sparse vegetation'
            },
            'hills': {
                'height': (0.4, 0.7),
                'moisture': (0.0, 1.0),
                'color': (140, 120, 90),
                'description': 'Rolling hills and elevated terrain'
            },
            'mountain': {
                'height': (0.7, 0.9),
                'moisture': (0.0, 1.0),
                'color': (120, 120, 120),
                'description': 'Rocky mountain peaks'
            },
            'snow': {
                'height': (0.9, 1.0),
                'moisture': (0.0, 1.0),
                'color': (240, 240, 240),
                'description': 'Snow-covered mountain peaks'
            },
            'tundra': {
                'height': (0.6, 0.8),
                'moisture': (0.0, 0.4),
                'color': (180, 200, 220),
                'description': 'Cold, treeless plains'
            }
        }

    def classify_tile(self, height: float, moisture: float) -> str:
        """
        Classify a tile based on height and moisture levels.

        Args:
            height: Normalized height value (0-1)
            moisture: Normalized moisture value (0-1)

        Returns:
            Biome type identifier
        """
        for biome_name, biome_data in self.biome_definitions.items():
            height_range = biome_data['height']
            moisture_range = biome_data['moisture']

            if (height_range[0] <= height <= height_range[1] and
                moisture_range[0] <= moisture <= moisture_range[1]):
                return biome_name

        return 'plains'  # Default biome

    def generate_moisture_map(self, heightmap: np.ndarray, seed: int = None) -> np.ndarray:
        """
        Generate moisture map based on heightmap.

        Args:
            heightmap: Input heightmap
            seed: Random seed

        Returns:
            2D moisture map
        """
        if seed is not None:
            np.random.seed(seed)

        # Base moisture is inversely related to height (higher = drier)
        moisture = 1.0 - heightmap

        # Add some random variation
        noise = np.random.normal(0, 0.1, heightmap.shape)
        moisture = np.clip(moisture + noise, 0, 1)

        return moisture

    def classify_heightmap(self, heightmap: np.ndarray, moisture_map: Optional[np.ndarray] = None) -> Tuple[np.ndarray, Dict]:
        """
        Classify entire heightmap into biomes.

        Args:
            heightmap: Input heightmap
            moisture_map: Optional moisture map

        Returns:
            Tuple of (biome_grid, biome_statistics)
        """
        if moisture_map is None:
            moisture_map = self.generate_moisture_map(heightmap)

        rows, cols = heightmap.shape
        biome_grid = np.empty((rows, cols), dtype=object)

        biome_counts = {}

        for y in range(rows):
            for x in range(cols):
                height = heightmap[y, x]
                moisture = moisture_map[y, x]
                biome = self.classify_tile(height, moisture)

                biome_grid[y, x] = biome

                # Count biomes
                if biome in biome_counts:
                    biome_counts[biome] += 1
                else:
                    biome_counts[biome] = 1

        return biome_grid, biome_counts

    def get_biome_info(self, biome_name: str) -> Dict:
        """
        Get information about a specific biome.

        Args:
            biome_name: Name of the biome

        Returns:
            Biome information dictionary
        """
        return self.biome_definitions.get(biome_name, {
            'color': (128, 128, 128),
            'description': 'Unknown biome'
        })

    def generate_biome_description(self, biome_name: str, region_name: str = None) -> str:
        """
        Generate a rich description for a biome region.

        Args:
            biome_name: Name of the biome
            region_name: Optional region name

        Returns:
            Descriptive text
        """
        biome_info = self.get_biome_info(biome_name)
        base_desc = biome_info['description']

        if region_name:
            descriptions = {
                'ocean': f"The endless {region_name} stretches as far as the eye can see, its dark waters hiding ancient secrets beneath the waves.",
                'beach': f"The golden sands of {region_name} glisten under the sun, where the tide whispers tales of distant lands.",
                'swamp': f"{region_name} is a misty labyrinth of stagnant waters and gnarled roots, where few dare to tread.",
                'forest': f"The ancient trees of {region_name} tower overhead, their canopy filtering the sunlight into dappled patterns on the forest floor.",
                'jungle': f"{region_name} teems with life, its dense foliage hiding both danger and wonder in equal measure.",
                'grassland': f"The rolling grasslands of {region_name} sway gently in the breeze, home to herds of wild creatures.",
                'plains': f"{region_name} offers unbroken vistas, where the wind carries stories across the open land.",
                'desert': f"The scorching sands of {region_name} shimmer under the relentless sun, a harsh land that tests all who enter.",
                'hills': f"{region_name} rises in gentle slopes, offering panoramic views of the surrounding countryside.",
                'mountain': f"The jagged peaks of {region_name} pierce the clouds, their slopes treacherous but rich with mineral wealth.",
                'snow': f"{region_name}'s frozen peaks glisten with eternal ice, a realm of silence and beauty.",
                'tundra': f"The vast, windswept expanse of {region_name} stretches endlessly, a harsh but beautiful wilderness."
            }

            return descriptions.get(biome_name, f"{region_name} is a region dominated by {base_desc}.")

        return base_desc.capitalize()

# Example usage
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from terrain.noise import PerlinNoise

    # Generate sample terrain
    noise_gen = PerlinNoise(seed=42)
    heightmap = noise_gen.generate_island_heightmap(50, 50)

    # Classify biomes
    classifier = BiomeClassifier()
    biome_grid, biome_stats = classifier.classify_heightmap(heightmap)

    print("Biome Statistics:")
    for biome, count in biome_stats.items():
        print(f"{biome}: {count} tiles")

    # Create biome visualization
    biome_colors = {
        'ocean': (0, 100, 200),
        'beach': (240, 220, 180),
        'swamp': (80, 120, 60),
        'forest': (40, 120, 60),
        'jungle': (30, 140, 30),
        'grassland': (100, 160, 80),
        'plains': (160, 200, 120),
        'desert': (200, 180, 140),
        'hills': (140, 120, 90),
        'mountain': (120, 120, 120),
        'snow': (240, 240, 240),
        'tundra': (180, 200, 220)
    }

    colored_biome = np.zeros((*biome_grid.shape, 3), dtype=np.uint8)
    for y in range(biome_grid.shape[0]):
        for x in range(biome_grid.shape[1]):
            biome = biome_grid[y, x]
            colored_biome[y, x] = biome_colors.get(biome, (128, 128, 128))

    plt.figure(figsize=(10, 10))
    plt.imshow(colored_biome)
    plt.title("SPECTRE Biome Classification")
    plt.axis('off')
    plt.show()