"""
SPECTRE Terrain Generation - Perlin Noise Module

Multi-octave Perlin noise implementation for procedural terrain generation.
"""

import random
import math
import numpy as np
from typing import List, Tuple, Dict, Any

class PerlinNoise:
    """
    Pure Python implementation of Perlin noise with multi-octave support.
    """

    def __init__(self, seed: int = None, octaves: int = 6, persistence: float = 0.5, lacunarity: float = 2.0):
        """
        Initialize Perlin noise generator.

        Args:
            seed: Random seed for reproducible noise
            octaves: Number of octaves for fractional Brownian motion
            persistence: Amplitude reduction per octave
            lacunarity: Frequency increase per octave
        """
        self.seed = seed or random.randint(0, 1000000)
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity

        # Initialize permutation table
        self.permutation = self._initialize_permutation()

    def _initialize_permutation(self) -> List[int]:
        """Initialize permutation table with seed."""
        random.seed(self.seed)
        permutation = list(range(256))
        random.shuffle(permutation)
        return permutation * 2

    def _fade(self, t: float) -> float:
        """Fade function for smooth interpolation."""
        return t * t * t * (t * (t * 6 - 15) + 10)

    def _lerp(self, a: float, b: float, t: float) -> float:
        """Linear interpolation."""
        return a + t * (b - a)

    def _grad(self, hash: int, x: float, y: float, z: float) -> float:
        """Gradient function."""
        h = hash & 15
        u = x if h < 8 else y
        v = y if h < 4 else (x if h == 12 or h == 14 else z)
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)

    def _noise2d(self, x: float, y: float) -> float:
        """Generate 2D Perlin noise at given coordinates."""
        # Find unit grid cell containing point
        X = int(x) & 255
        Y = int(y) & 255

        # Get relative xy coordinates of point within that cell
        x -= int(x)
        y -= int(y)

        # Compute fade curves for each of x, y
        u = self._fade(x)
        v = self._fade(y)

        # Hash coordinates of the 4 cube corners
        A = self.permutation[X] + Y
        AA = self.permutation[A]
        AB = self.permutation[A + 1]
        B = self.permutation[X + 1] + Y
        BA = self.permutation[B]
        BB = self.permutation[B + 1]

        # Blend results from 4 corners of cube
        return self._lerp(
            self._lerp(self._grad(self.permutation[AA], x, y, 0),
                      self._grad(self.permutation[BA], x - 1, y, 0), u),
            self._lerp(self._grad(self.permutation[AB], x, y - 1, 0),
                      self._grad(self.permutation[BB], x - 1, y - 1, 0), u),
            v
        )

    def noise(self, x: float, y: float) -> float:
        """
        Generate fractional Brownian motion noise at given coordinates.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Noise value in range [-1, 1]
        """
        total = 0.0
        frequency = 1.0
        amplitude = 1.0
        max_value = 0.0

        for _ in range(self.octaves):
            total += self._noise2d(x * frequency, y * frequency) * amplitude
            max_value += amplitude
            frequency *= self.lacunarity
            amplitude *= self.persistence

        # Normalize to [-1, 1] range
        return total / max_value

    def generate_heightmap(self, width: int, height: int, scale: float = 50.0) -> np.ndarray:
        """
        Generate a 2D heightmap using Perlin noise.

        Args:
            width: Width of heightmap
            height: Height of heightmap
            scale: Noise scale factor

        Returns:
            2D numpy array of height values
        """
        heightmap = np.zeros((height, width))

        for y in range(height):
            for x in range(width):
                # Scale coordinates to get more interesting features
                nx = x / width * scale
                ny = y / height * scale

                # Get noise value and normalize to [0, 1]
                noise_val = (self.noise(nx, ny) + 1) / 2
                heightmap[y, x] = noise_val

        return heightmap

    def generate_island_heightmap(self, width: int, height: int, island_factor: float = 2.0) -> np.ndarray:
        """
        Generate an island-shaped heightmap.

        Args:
            width: Width of heightmap
            height: Height of heightmap
            island_factor: Controls how "island-like" the terrain is

        Returns:
            2D numpy array of height values
        """
        heightmap = self.generate_heightmap(width, height)

        # Create island effect by reducing height based on distance from center
        center_x, center_y = width / 2, height / 2

        for y in range(height):
            for x in range(width):
                # Calculate distance from center (normalized)
                dx = (x - center_x) / width
                dy = (y - center_y) / height
                distance = math.sqrt(dx*dx + dy*dy)

                # Apply island falloff
                falloff = 1.0 - distance ** island_factor
                heightmap[y, x] = heightmap[y, x] * max(falloff, 0.1)

        return heightmap

# Utility functions
def normalize_heightmap(heightmap: np.ndarray) -> np.ndarray:
    """
    Normalize heightmap to 0-1 range.

    Args:
        heightmap: Input heightmap

    Returns:
        Normalized heightmap
    """
    min_val = heightmap.min()
    max_val = heightmap.max()

    if max_val - min_val > 0:
        return (heightmap - min_val) / (max_val - min_val)
    return heightmap

def apply_erosion(heightmap: np.ndarray, iterations: int = 3, radius: int = 1) -> np.ndarray:
    """
    Apply simple erosion simulation to heightmap.

    Args:
        heightmap: Input heightmap
        iterations: Number of erosion iterations
        radius: Erosion radius

    Returns:
        Eroded heightmap
    """
    eroded = heightmap.copy()

    for _ in range(iterations):
        for y in range(radius, heightmap.shape[0] - radius):
            for x in range(radius, heightmap.shape[1] - radius):
                # Simple average of neighboring cells
                total = 0
                count = 0

                for dy in range(-radius, radius + 1):
                    for dx in range(-radius, radius + 1):
                        if dx == 0 and dy == 0:
                            continue
                        total += heightmap[y + dy, x + dx]
                        count += 1

                if count > 0:
                    average = total / count
                    eroded[y, x] = (heightmap[y, x] + average) / 2

    return eroded

# Example usage
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # Create noise generator
    noise_gen = PerlinNoise(seed=42, octaves=6)

    # Generate heightmap
    heightmap = noise_gen.generate_island_heightmap(100, 100)

    # Display
    plt.imshow(heightmap, cmap='terrain')
    plt.colorbar()
    plt.title("SPECTRE Island Heightmap")
    plt.show()