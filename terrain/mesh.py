"""
Terrain Mesh Generator

Converts heightmaps to 3D mesh data for visualization.
"""

from typing import List, Dict, Tuple
import math

class TerrainMesh:
    def __init__(self):
        pass

    def generate_mesh(self, heightmap: List[List[float]], scale: float = 1.0, height_scale: float = 10.0) -> Dict[str, any]:
        """
        Generate 3D mesh data from heightmap

        Returns:
            {
                "vertices": [...],
                "normals": [...],
                "colors": [...],
                "indices": [...],
                "size": (width, height)
            }
        """
        height = len(heightmap)
        width = len(heightmap[0]) if height > 0 else 0

        vertices = []
        normals = []
        colors = []
        indices = []

        # Generate vertices and colors
        for y in range(height):
            for x in range(width):
                # Position
                vertices.append(x * scale)
                vertices.append(y * scale)
                vertices.append(heightmap[y][x] * height_scale)

                # Color (based on height for now)
                height_value = heightmap[y][x]
                if height_value < 0.2:
                    # Water
                    vertices.append(0.1)  # r
                    vertices.append(0.3)  # g
                    vertices.append(0.8)  # b
                elif height_value < 0.4:
                    # Sand/beach
                    vertices.append(0.9)
                    vertices.append(0.8)
                    vertices.append(0.4)
                elif height_value < 0.6:
                    # Grassland
                    vertices.append(0.2)
                    vertices.append(0.8)
                    vertices.append(0.2)
                else:
                    # Mountain
                    vertices.append(0.5)
                    vertices.append(0.3)
                    vertices.append(0.1)

        # Generate indices (triangle strip)
        for y in range(height - 1):
            for x in range(width - 1):
                # First triangle
                indices.append(y * width + x)
                indices.append((y + 1) * width + x)
                indices.append(y * width + x + 1)

                # Second triangle
                indices.append((y + 1) * width + x)
                indices.append((y + 1) * width + x + 1)
                indices.append(y * width + x + 1)

        # Calculate normals (simplified)
        normals = [0, 1, 0] * len(vertices) // 3

        return {
            "vertices": vertices,
            "normals": normals,
            "colors": vertices[3:],  # Colors are stored after position
            "indices": indices,
            "size": (width, height)
        }

    def generate_poi_mesh(self, poi_data: Dict[str, any]) -> Dict[str, any]:
        """Generate mesh for a point of interest marker"""
        # Simple cube mesh for POI markers
        size = 2.0

        vertices = [
            # Front face
            -size, -size,  size,  1.0, 0.0, 0.0,
             size, -size,  size,  1.0, 0.0, 0.0,
             size,  size,  size,  1.0, 0.0, 0.0,
            -size,  size,  size,  1.0, 0.0, 0.0,

            # Back face
            -size, -size, -size,  0.0, 1.0, 0.0,
             size, -size, -size,  0.0, 1.0, 0.0,
             size,  size, -size,  0.0, 1.0, 0.0,
            -size,  size, -size,  0.0, 1.0, 0.0,

            # Top face
            -size,  size,  size,  0.0, 0.0, 1.0,
             size,  size,  size,  0.0, 0.0, 1.0,
             size,  size, -size,  0.0, 0.0, 1.0,
            -size,  size, -size,  0.0, 0.0, 1.0,

            # Bottom face
            -size, -size,  size,  1.0, 1.0, 0.0,
             size, -size,  size,  1.0, 1.0, 0.0,
             size, -size, -size,  1.0, 1.0, 0.0,
            -size, -size, -size,  1.0, 1.0, 0.0,

            # Right face
             size, -size,  size,  0.0, 1.0, 1.0,
             size,  size,  size,  0.0, 1.0, 1.0,
             size,  size, -size,  0.0, 1.0, 1.0,
             size, -size, -size,  0.0, 1.0, 1.0,

            # Left face
            -size, -size,  size,  1.0, 0.0, 1.0,
            -size,  size,  size,  1.0, 0.0, 1.0,
            -size,  size, -size,  1.0, 0.0, 1.0,
            -size, -size, -size,  1.0, 0.0, 1.0
        ]

        indices = [
            0, 1, 2,  0, 2, 3,    # front
            4, 5, 6,  4, 6, 7,    # back
            8, 9, 10, 8, 10, 11,  # top
            12, 13, 14, 12, 14, 15, # bottom
            16, 17, 18, 16, 18, 19, # right
            20, 21, 22, 20, 22, 23  # left
        ]

        return {
            "vertices": vertices,
            "indices": indices,
            "position": [poi_data["x"] * scale, poi_data["y"] * scale, 10.0],  # Position above terrain
            "type": poi_data["type"]
        }