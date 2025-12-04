# Pi-table-games

## Usage

To start the game, cd into Pi-table-games and run the following commands to sync
dependencies and run the game. It will auto-detect your camera if one is
connected.

```bash
# Install uv if you haven't already
# curl -LsSf https://astral.sh/uv/install.sh | sh

uv sync
uv run hand-game
```

For demonstrating hand-tracking on its own, instead run the following

```bash
uv run hand-tracker
```

You can also control the game with your mouse by running the following

```bash
uv run mouse-game
```
