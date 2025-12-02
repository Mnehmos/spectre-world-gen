"""
SPECTRE World Generation - Database Module

Handles SQLite database persistence for world data.
"""

import aiosqlite
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

class DatabaseManager:
    """
    Manages SQLite database for world persistence.
    """

    def __init__(self, db_path: str = "spectre_world.db"):
        self.db_path = db_path
        self.connection = None

    async def initialize(self):
        """
        Initialize database connection and create tables.
        """
        self.connection = await aiosqlite.connect(self.db_path)

        # Create tables
        await self._create_tables()

    async def _create_tables(self):
        """
        Create database tables if they don't exist.
        """
        cursor = await self.connection.cursor()

        # Worlds table
        await cursor.execute("""
        CREATE TABLE IF NOT EXISTS worlds (
            id TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)

        # Events table
        await cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            world_id TEXT,
            type TEXT NOT NULL,
            data TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (world_id) REFERENCES worlds(id)
        )
        """)

        # POIs table
        await cursor.execute("""
        CREATE TABLE IF NOT EXISTS pois (
            id TEXT PRIMARY KEY,
            world_id TEXT NOT NULL,
            data TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (world_id) REFERENCES worlds(id)
        )
        """)

        # Lore table
        await cursor.execute("""
        CREATE TABLE IF NOT EXISTS lore (
            id TEXT PRIMARY KEY,
            world_id TEXT NOT NULL,
            type TEXT NOT NULL,
            title TEXT,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (world_id) REFERENCES worlds(id)
        )
        """)

        # Timeline table
        await cursor.execute("""
        CREATE TABLE IF NOT EXISTS timeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            world_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            description TEXT NOT NULL,
            date TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (world_id) REFERENCES worlds(id)
        )
        """)

        await self.connection.commit()

    async def save_world(self, world_id: str, world_data: Dict[str, Any]):
        """
        Save world data to database.

        Args:
            world_id: World identifier
            world_data: World data dictionary
        """
        timestamp = datetime.now().isoformat()
        data_json = json.dumps(world_data)

        cursor = await self.connection.cursor()

        await cursor.execute("""
        INSERT OR REPLACE INTO worlds (id, data, created_at, updated_at)
        VALUES (?, ?, ?, ?)
        """, (world_id, data_json, timestamp, timestamp))

        await self.connection.commit()

    async def load_world(self, world_id: str) -> Optional[Dict[str, Any]]:
        """
        Load world data from database.

        Args:
            world_id: World identifier

        Returns:
            World data dictionary or None if not found
        """
        cursor = await self.connection.cursor()

        await cursor.execute("SELECT data FROM worlds WHERE id = ?", (world_id,))
        result = await cursor.fetchone()

        if result:
            return json.loads(result[0])
        return None

    async def list_worlds(self) -> List[str]:
        """
        List all available world IDs.

        Returns:
            List of world IDs
        """
        cursor = await self.connection.cursor()

        await cursor.execute("SELECT id FROM worlds")
        results = await cursor.fetchall()

        return [row[0] for row in results]

    async def delete_world(self, world_id: str):
        """
        Delete a world and all associated data.

        Args:
            world_id: World identifier
        """
        cursor = await self.connection.cursor()

        # Delete from all related tables
        await cursor.execute("DELETE FROM events WHERE world_id = ?", (world_id,))
        await cursor.execute("DELETE FROM pois WHERE world_id = ?", (world_id,))
        await cursor.execute("DELETE FROM lore WHERE world_id = ?", (world_id,))
        await cursor.execute("DELETE FROM timeline WHERE world_id = ?", (world_id,))
        await cursor.execute("DELETE FROM worlds WHERE id = ?", (world_id,))

        await self.connection.commit()

    async def log_event(self, world_id: str, event_type: str, data: Dict[str, Any]):
        """
        Log an event for a world.

        Args:
            world_id: World identifier
            event_type: Event type
            data: Event data
        """
        timestamp = datetime.now().isoformat()
        data_json = json.dumps(data)

        cursor = await self.connection.cursor()

        await cursor.execute("""
        INSERT INTO events (world_id, type, data, timestamp)
        VALUES (?, ?, ?, ?)
        """, (world_id, event_type, data_json, timestamp))

        await self.connection.commit()

    async def get_events(self, world_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get events for a world.

        Args:
            world_id: World identifier
            limit: Maximum number of events to return

        Returns:
            List of event dictionaries
        """
        cursor = await self.connection.cursor()

        await cursor.execute("""
        SELECT id, type, data, timestamp FROM events
        WHERE world_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """, (world_id, limit))

        results = await cursor.fetchall()

        return [{
            "id": row[0],
            "type": row[1],
            "data": json.loads(row[2]),
            "timestamp": row[3]
        } for row in results]

    async def save_poi(self, poi_id: str, world_id: str, poi_data: Dict[str, Any]):
        """
        Save POI data to database.

        Args:
            poi_id: POI identifier
            world_id: World identifier
            poi_data: POI data dictionary
        """
        timestamp = datetime.now().isoformat()
        data_json = json.dumps(poi_data)

        cursor = await self.connection.cursor()

        await cursor.execute("""
        INSERT OR REPLACE INTO pois (id, world_id, data, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """, (poi_id, world_id, data_json, timestamp, timestamp))

        await self.connection.commit()

    async def load_poi(self, poi_id: str) -> Optional[Dict[str, Any]]:
        """
        Load POI data from database.

        Args:
            poi_id: POI identifier

        Returns:
            POI data dictionary or None if not found
        """
        cursor = await self.connection.cursor()

        await cursor.execute("SELECT data FROM pois WHERE id = ?", (poi_id,))
        result = await cursor.fetchone()

        if result:
            return json.loads(result[0])
        return None

    async def save_lore(self, lore_id: str, world_id: str, lore_type: str, title: str, content: str):
        """
        Save lore entry to database.

        Args:
            lore_id: Lore identifier
            world_id: World identifier
            lore_type: Type of lore
            title: Lore title
            content: Lore content
        """
        timestamp = datetime.now().isoformat()

        cursor = await self.connection.cursor()

        await cursor.execute("""
        INSERT OR REPLACE INTO lore (id, world_id, type, title, content, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (lore_id, world_id, lore_type, title, content, timestamp))

        await self.connection.commit()

    async def get_lore(self, world_id: str, lore_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get lore entries for a world.

        Args:
            world_id: World identifier
            lore_type: Optional filter by lore type

        Returns:
            List of lore dictionaries
        """
        cursor = await self.connection.cursor()

        if lore_type:
            await cursor.execute("""
            SELECT id, type, title, content, created_at FROM lore
            WHERE world_id = ? AND type = ?
            ORDER BY created_at
            """, (world_id, lore_type))
        else:
            await cursor.execute("""
            SELECT id, type, title, content, created_at FROM lore
            WHERE world_id = ?
            ORDER BY created_at
            """, (world_id,))

        results = await cursor.fetchall()

        return [{
            "id": row[0],
            "type": row[1],
            "title": row[2],
            "content": row[3],
            "created_at": row[4]
        } for row in results]

    async def add_timeline_event(self, world_id: str, event_type: str, description: str, date: Optional[str] = None):
        """
        Add an event to world timeline.

        Args:
            world_id: World identifier
            event_type: Event type
            description: Event description
            date: Optional event date

        Returns:
            Created event ID
        """
        timestamp = datetime.now().isoformat()
        event_date = date or f"Year {random.randint(-5000, 2023)}"

        cursor = await self.connection.cursor()

        await cursor.execute("""
        INSERT INTO timeline (world_id, event_type, description, date, created_at)
        VALUES (?, ?, ?, ?, ?)
        """, (world_id, event_type, description, event_date, timestamp))

        await self.connection.commit()

        return cursor.lastrowid

    async def get_timeline(self, world_id: str) -> List[Dict[str, Any]]:
        """
        Get timeline events for a world.

        Args:
            world_id: World identifier

        Returns:
            List of timeline event dictionaries
        """
        cursor = await self.connection.cursor()

        await cursor.execute("""
        SELECT id, event_type, description, date, created_at FROM timeline
        WHERE world_id = ?
        ORDER BY date
        """, (world_id,))

        results = await cursor.fetchall()

        return [{
            "id": row[0],
            "type": row[1],
            "description": row[2],
            "date": row[3],
            "created_at": row[4]
        } for row in results]

    async def close(self):
        """
        Close database connection.
        """
        if self.connection:
            await self.connection.close()
            self.connection = None

    async def backup_database(self, backup_path: str):
        """
        Create a backup of the database.

        Args:
            backup_path: Path for backup file
        """
        import shutil
        shutil.copyfile(self.db_path, backup_path)

    async def restore_database(self, backup_path: str):
        """
        Restore database from backup.

        Args:
            backup_path: Path to backup file
        """
        if self.connection:
            await self.close()

        import shutil
        shutil.copyfile(backup_path, self.db_path)

        # Reconnect
        await self.initialize()

# Utility functions
def import_json_backup(backup_path: str) -> Dict[str, Any]:
    """
    Import world data from JSON backup.

    Args:
        backup_path: Path to JSON backup file

    Returns:
        World data dictionary
    """
    with open(backup_path, 'r') as f:
        return json.load(f)

def export_json_backup(world_data: Dict[str, Any], backup_path: str):
    """
    Export world data to JSON backup.

    Args:
        world_data: World data dictionary
        backup_path: Path for backup file
    """
    with open(backup_path, 'w') as f:
        json.dump(world_data, f, indent=2)