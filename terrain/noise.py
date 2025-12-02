"""
Perlin Noise Generator

Pure Python implementation of Perlin noise for terrain generation.
"""

import random
import math
from typing import List, Tuple

class PerlinNoise:
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.permutation = self._generate_permutation_table()

    def _generate_permutation_table(self) -> List[int]:
        """Generate permutation table for noise"""
        random.seed(self.seed)
        p = list(range(256))
        random.shuffle(p)
        return p * 2

    def _fade(self, t: float) -> float:
        """Fade function for smooth interpolation"""
        return t * t * t * (t * (t * 6 - 15) + 10)

    def _lerp(self, t: float, a: float, b: float) -> float:
        """Linear interpolation"""
        return a + t * (b - a)

    def _grad(self, hash: int, x: float, y: float, z: float) -> float:
        """Gradient function"""
        h = hash & 15
        u = x if h < 8 else y
        v = y if h < 4 else (x if h == 12 or h == 14 else z)
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)

    def noise(self, x: float, y: float, z: float = 0) -> float:
        """Generate 3D Perlin noise"""
        # Find unit cube containing point
        xi = int(x) & 255
        yi = int(y) & 255
        zi = int(z) & 255

        # Find relative x, y, z of point in cube
        xf = x - int(x)
        yf = y - int(y)
        zf = z - int(z)

        # Compute fade curves for each of x, y, z
        u = self._fade(xf)
        v = self._fade(yf)
        w = self._fade(zf)

        # Hash coordinates of the 8 cube corners
        aaa = self.permutation[self.permutation[xi] + yi] + zi
        aba = self.permutation[self.permutation[xi] + yi + 1] + zi
        aab = self.permutation[self.permutation[xi] + yi] + zi + 1
        abb = self.permutation[self.permutation[xi] + yi + 1] + zi + 1
        baa = self.permutation[self.permutation[xi + 1] + yi] + zi
        bba = self.permutation[self.permutation[xi + 1] + yi + 1] + zi
        bab = self.permutation[self.permutation[xi + 1] + yi] + zi + 1
        bbb = self.permutation[self.permutation[xi + 1] + yi + 1] + zi + 1

        # Calculate gradients
        grad_aaa = self._grad(self.permutation[aaa], xf, yf, zf)
        grad_aba = self._grad(self.permutation[aba], xf - 1, yf, zf)
        grad_aab = self._grad(self.permutation[aab], xf, yf - 1, zf)
        grad_abb = self._grad(self.permutation[abb], xf - 1, yf - 1, zf)
        grad_baa = self._grad(self.permutation[baa], xf, yf, zf - 1)
        grad_bba = self._grad(self.permutation[bba], xf - 1, yf, zf - 1)
        grad_bab = self._grad(self.permutation[bab], xf, yf - 1, zf - 1)
        grad_bbb = self._grad(self.permutation[bbb], xf - 1, yf - 1, zf - 1)

        # Interpolate along x
        x1 = self._lerp(u, grad_aaa, grad_aba)
        x2 = self._lerp(u, grad_aab, grad_abb)
        x3 = self._lerp(u, grad_baa, grad_bba)
        x4 = self._lerp(u, grad_bab, grad_bbb)

        # Interpolate along y
        y1 = self._lerp(v, x1, x2)
        y2 = self._lerp(v, x3, x4)

        # Interpolate along z
        return self._lerp(w, y1, y2)

    def octave_noise(self, x: float, y: float, octaves: int = 4, persistence: float = 0.5, lacunarity: float = 2.0) -> float:
        """Generate multi-octave Perlin noise"""
        total = 0
        frequency = 1
        amplitude = 1
        max_value = 0

        for _ in range(octaves):
            total += self.noise(x * frequency, y * frequency) * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= lacunarity

        return total / max_value

    def generate_heightmap(self, width: int, height: int, scale: float = 0.1, octaves: int = 4) -> List[List[float]]:
        """Generate a 2D heightmap"""
        heightmap = []
        for y in range(height):
            row = []
            for x in range(width):
                nx = x / width - 0.5
                ny = y / height - 0.5
                elevation = self.octave_noise(nx * scale, ny * scale, octaves)
                row.append((elevation + 1) / 2)  # Normalize to 0-1 range
            heightmap.append(row)
        return heightmap