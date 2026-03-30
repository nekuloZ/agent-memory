---
name: playnite
description: Browse, search, and launch games in your Playnite library. Search games by name, launch games via command line, view database structure, and export games via plugins. Use when asking about Playnite games, game discovery, or launching games across Steam, GOG, Epic, and more.
---

# Playnite Games Library

CLI for browsing, searching, and launching games in your Playnite library across Steam, GOG, Epic, and more.

## Quick Start

**Search a game:** Use Playnite's built-in search (Ctrl+F) or filter panel
**Launch a game:** `playnite://start/{gameId}` URL scheme or command line

## Launching Games

### URL Scheme (Recommended)

Playnite supports a custom URL protocol for launching games:

```
playnite://start/{gameId}
```

**Example:**
```
playnite://start/12345
```

You can use this from:
- Run dialog (Win+R)
- Browser/shortcuts
- Command line: `start playnite://start/12345`

### Command Line

```cmd
Playnite.exe --start <gameId>
Playnite.exe --uri "playnite://game/1234"
```

### Finding Game IDs

In Playnite Desktop Mode:
1. Right-click column header → Select columns → Check "Id"
2. The Id column shows each game's numeric ID
3. Use this ID with the URL scheme or --start parameter

**Alternative**: Export library with "Json Library Import Export" addon to get all IDs

## Searching & Launching Games

### Using Python Script (Recommended)

If you have exported your Playnite library to JSON:

```bash
# Search games
python search.py "query"

# Launch a game (exact match or first result)
python search.py "launch query"

# List all games
python search.py "list"
```

**Examples:**
```bash
python E:\AI_program\Jarvis\jarvis-memory\data\playnite\search.py "elden"
python E:\AI_program\Jarvis\jarvis-memory\data\playnite\search.py "launch wukong"
python E:\AI_program\Jarvis\jarvis-memory\data\playnite\search.py "list"
```

### In Playnite UI

**Quick Search (Ctrl+F):**
- Searches across game names
- Real-time filtering as you type

**Filter Panel:**
- Platform (Steam, GOG, Epic, etc.)
- Genre, Tags, Categories
- Installation status
- Completion status
- Favorites/Hidden

### External Search (via Export)

To search from command line or external tools:

1. Install "Json Library Import Export" addon
2. Export library to JSON
3. Use jq or similar tools:

```bash
# Find game by name
jq '.[] | select(.Name | contains("Elden"))' exported_games.json

# Get game ID for launching
jq '.[] | select(.Name == "Elden Ring") | .Id' exported_games.json
```

## Database Location

Playnite uses **LiteDB** (NoSQL document database), not SQLite.

**Default Path:** `%AppData%\Playnite\library`
**Full Path:** `C:\Users\[Username]\AppData\Roaming\Playnite\library`

**Main Database Files:**
- `games.db` - Game library (main database)
- `tags.db` - Tags
- `genres.db` - Genres
- `platforms.db` - Platforms
- `categories.db` - Categories
- `companies.db` - Developers/Publishers

## Configuration

**Config File:** `%AppData%\Playnite\config.json`
**Database Path:** Check `"DatabasePath"` field in config

## Exporting Library Data

### Export Extensions

**Json Library Import Export**
- Author: sokolinthesky
- Install: Playnite → Addons → Search "Json Library Import Export"
- Export entire library to JSON format

**Library Exporter Advanced**
- Author: Lacro59
- Export to CSV, JSON, and other formats
- Source: https://playnite.link/addons.html

### Individual Game Export

1. Right-click game in Playnite
2. Select "Edit Game"
3. Click "Export" button
4. Choose JSON or XML format

## Game Fields

| Field | Description |
|-------|-------------|
| Id | Game ID (for launching) |
| Name | Game title |
| Platform | Platform (Steam, GOG, Epic, etc.) |
| Playtime | Hours played |
| LastPlayed | Last play date |
| ReleaseDate | Release date |
| Genres | Game genres |
| Tags | Custom tags |
| Categories | Categories |
| Developers | Developers |
| Publishers | Publishers |
| CompletionStatus | Playing, Completed, Abandoned, etc. |
| Installed | Is game installed |
| Favorite | Is marked as favorite |
| UserScore | User rating |

## Usage Examples

**"Search for game X in Playnite"**
→ Open Playnite → Ctrl+F → Type game name

**"Launch [game name] via Playnite"**
→ Get game ID → Use `playnite://start/{gameId}` URL

**"What games do I have from Epic?"**
→ Filter panel → Platform → Epic

**"Show uninstalled favorites"**
→ Filter panel → Favorite + Uninstalled

**"Export my library"**
→ Install "Json Library Import Export" addon

**"How many games total?"**
→ Check bottom status bar in Playnite

## Filtering in Playnite

**By Status:**
- Installed / Uninstalled
- Favorites
- Hidden
- Completion Status

**By Time:**
- Last Played
- Playtime hours
- Recently Added

**By Metadata:**
- Platform (Steam, GOG, Epic, etc.)
- Genre
- Tags
- Categories

**By Installation:**
- Install Size
- Install Directory

## Tips

1. **Enable Id Column**: Right-click headers → Select "Id" to see game IDs for launching
2. **Create Shortcuts**: Use URL scheme to create desktop shortcuts for games
3. **Export for Search**: Export to JSON for advanced searching from command line
4. **Filter Combinations**: Combine multiple filters in the filter panel

## Database Structure Details

Playnite 10+ database structure:
- Engine: LiteDB 5.x (NoSQL document database)
- Format: Binary (not human-readable)
- Relationships: Games reference IDs for tags, genres, platforms, etc.
- Collections: Each `.db` file is a separate collection

**Note**: Unlike SQLite, LiteDB cannot be opened with standard database tools. You need:
1. .NET SDK + LiteDB package, OR
2. Playnite extension with export functionality, OR
3. Third-party LiteDB viewer

## Sources

- [Playnite Command-line Arguments](https://api.playnite.link/docs/manual/advanced/cmdlineArguments.html)
- [Playnite URL Browser Protocol](https://github.com/JosefNemec/Playnite/issues/1133)
- [Playnite Addons](https://playnite.link/addons.html)
- [Playnite API Documentation](https://api.playnite.link/docs/)
- [LiteDB Documentation](https://www.litedb.org/docs/)
