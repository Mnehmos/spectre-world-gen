"""
SPECTRE Terrain Generation - 3D Mesh Module

Converts heightmaps to 3D mesh data for visualization.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import json

class TerrainMeshGenerator:
    """
    Generates 3D mesh data from heightmaps for Three.js visualization.
    """

    def __init__(self):
        pass

    def generate_mesh_data(self, heightmap: np.ndarray, scale: float = 1.0) -> Dict:
        """
        Generate Three.js compatible mesh data from heightmap.

        Args:
            heightmap: 2D heightmap array
            scale: Vertical scale factor

        Returns:
            Dictionary with mesh data (vertices, indices, normals, colors)
        """
        rows, cols = heightmap.shape
        vertices = []
        colors = []
        indices = []

        # Generate vertices and colors
        for z in range(rows):
            for x in range(cols):
                y = heightmap[z, x] * scale
                vertices.extend([x, y, z])

                # Simple color based on height
                color = self._get_height_color(y / scale)
                colors.extend(color)

        # Generate indices (two triangles per quad)
        for z in range(rows - 1):
            for x in range(cols - 1):
                # Triangle 1
                indices.extend([
                    z * cols + x,
                    z * cols + x + 1,
                    (z + 1) * cols + x
                ])

                # Triangle 2
                indices.extend([
                    (z + 1) * cols + x,
                    z * cols + x + 1,
                    (z + 1) * cols + x + 1
                ])

        return {
            'vertices': vertices,
            'colors': colors,
            'indices': indices,
            'width': cols,
            'height': rows,
            'scale': scale
        }

    def _get_height_color(self, height: float) -> List[float]:
        """Get color based on normalized height (0-1)."""
        # Water
        if height < 0.1:
            return [0, 0.4, 0.8]
        # Sand
        elif height < 0.2:
            return [0.9, 0.8, 0.6]
        # Grass
        elif height < 0.5:
            return [0.2, 0.6, 0.2]
        # Forest
        elif height < 0.7:
            return [0.1, 0.4, 0.1]
        # Mountain
        elif height < 0.9:
            return [0.5, 0.5, 0.5]
        # Snow
        else:
            return [0.9, 0.9, 0.9]

    def generate_biome_mesh_data(self, heightmap: np.ndarray, biome_grid: np.ndarray) -> Dict:
        """
        Generate mesh data with biome-based coloring.

        Args:
            heightmap: Heightmap array
            biome_grid: Biome classification grid

        Returns:
            Dictionary with biome-colored mesh data
        """
        rows, cols = heightmap.shape
        vertices = []
        colors = []
        indices = []

        biome_color_map = self._get_biome_color_map()

        # Generate vertices and biome-based colors
        for z in range(rows):
            for x in range(cols):
                y = heightmap[z, x] * 5  # Scale for visualization
                vertices.extend([x, y, z])

                biome = biome_grid[z, x]
                color = biome_color_map.get(biome, [0.5, 0.5, 0.5])
                colors.extend(color)

        # Generate indices (same as regular mesh)
        for z in range(rows - 1):
            for x in range(cols - 1):
                indices.extend([
                    z * cols + x,
                    z * cols + x + 1,
                    (z + 1) * cols + x,
                    (z + 1) * cols + x,
                    z * cols + x + 1,
                    (z + 1) * cols + x + 1
                ])

        return {
            'vertices': vertices,
            'colors': colors,
            'indices': indices,
            'width': cols,
            'height': rows,
            'biome_map': biome_color_map
        }

    def _get_biome_color_map(self) -> Dict[str, List[float]]:
        """Get color mapping for different biomes."""
        return {
            'ocean': [0.0, 0.4, 0.8],
            'beach': [0.9, 0.8, 0.6],
            'swamp': [0.3, 0.5, 0.2],
            'forest': [0.1, 0.4, 0.1],
            'jungle': [0.1, 0.5, 0.1],
            'grassland': [0.4, 0.6, 0.3],
            'plains': [0.6, 0.7, 0.4],
            'desert': [0.8, 0.7, 0.5],
            'hills': [0.5, 0.4, 0.3],
            'mountain': [0.5, 0.5, 0.5],
            'snow': [0.9, 0.9, 0.9],
            'tundra': [0.7, 0.8, 0.9]
        }

    def generate_simplified_mesh(self, heightmap: np.ndarray, simplification: int = 2) -> Dict:
        """
        Generate simplified mesh data for performance.

        Args:
            heightmap: Original heightmap
            simplification: Simplification factor (higher = fewer vertices)

        Returns:
            Simplified mesh data
        """
        if simplification < 1:
            simplification = 1

        # Downsample heightmap
        simplified_heightmap = heightmap[::simplification, ::simplification]

        return self.generate_mesh_data(simplified_heightmap)

    def save_mesh_to_json(self, mesh_data: Dict, filename: str):
        """
        Save mesh data to JSON file.

        Args:
            mesh_data: Mesh data dictionary
            filename: Output filename
        """
        with open(filename, 'w') as f:
            json.dump(mesh_data, f, indent=2)

    def load_mesh_from_json(self, filename: str) -> Dict:
        """
        Load mesh data from JSON file.

        Args:
            filename: Input filename

        Returns:
            Loaded mesh data
        """
        with open(filename, 'r') as f:
            return json.load(f)

    def generate_poi_positions(self, biome_grid: np.ndarray, poi_density: float = 0.01) -> List[Tuple[int, int, str]]:
        """
        Generate potential POI positions based on biome suitability.

        Args:
            biome_grid: Biome classification grid
            poi_density: Desired POI density (0-1)

        Returns:
            List of (x, z, biome) tuples for POI placement
        """
        rows, cols = biome_grid.shape
        total_cells = rows * cols
        target_pois = int(total_cells * poi_density)

        # Biome weights for POI likelihood
        biome_weights = {
            'ocean': 0.1,    # Few POIs in deep ocean
            'beach': 0.5,    # Good for ports, shipwrecks
            'swamp': 0.8,    # Great for ruins, hidden places
            'forest': 0.9,   # Excellent for settlements, temples
            'jungle': 1.0,   # Best for ancient ruins
            'grassland': 0.7,
            'plains': 0.6,
            'desert': 0.7,   # Good for oases, ruins
            'hills': 0.8,    # Good for watchtowers, mines
            'mountain': 0.4, # Some mountain passes, caves
            'snow': 0.2,     # Few snow POIs
            'tundra': 0.3
        }

        # Create weight grid
        weight_grid = np.zeros((rows, cols))
        for y in range(rows):
            for x in range(cols):
                biome = biome_grid[y, x]
                weight_grid[y, x] = biome_weights.get(biome, 0.5)

        # Normalize weights
        weight_grid = weight_grid / weight_grid.sum()

        # Sample positions
        positions = []
        for _ in range(target_pois):
            # Find random position based on weights
            flat_weights = weight_grid.flatten()
            idx = np.random.choice(len(flat_weights), p=flat_weights)

            y, x = np.unravel_index(idx, weight_grid.shape)
            biome = biome_grid[y, x]

            positions.append((x, y, biome))

        return positions

# Example usage
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from terrain.noise import PerlinNoise
    from terrain.biomes import BiomeClassifier

    # Generate terrain
    noise_gen = PerlinNoise(seed=42)
    heightmap = noise_gen.generate_island_heightmap(50, 50)

    # Classify biomes
    classifier = BiomeClassifier()
    biome_grid, _ = classifier.classify_heightmap(heightmap)

    # Generate mesh
    mesh_gen = TerrainMeshGenerator()
    mesh_data = mesh_gen.generate_biome_mesh_data(heightmap, biome_grid)

    print(f"Generated mesh with {len(mesh_data['vertices']) // 3} vertices and {len(mesh_data['indices'])} indices")

    # Generate POI positions
    poi_positions = mesh_gen.generate_poi_positions(biome_grid)
    print(f"Generated {len(poi_positions)} potential POI positions")

    # Visualize some POIs
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(biome_grid, cmap='terrain', alpha=0.7)

    for x, y, biome in poi_positions[:20]:  # Show first 20
        ax.scatter(x, y, c='red', s=20, alpha=0.7)

    plt.title("SPECTRE POI Placement")
    plt.axis('off')
    plt.show()