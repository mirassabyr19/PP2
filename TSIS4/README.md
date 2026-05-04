# TSIS4 Snake Game — Database Integration & Advanced Gameplay

## How to run

1. Install packages:
```bash
pip install pygame psycopg2-binary
```

2. Create PostgreSQL database:
```sql
CREATE DATABASE tsis4;
```

3. Edit `config.py` if your PostgreSQL password is not `1234`.

4. Run:
```bash
python main.py
```

## Implemented requirements

- PostgreSQL schema: `players` and `game_sessions`
- Username entry in Pygame
- Auto-save result after game over
- Leaderboard Top 10 from database
- Personal best displayed during gameplay
- Poison food shortens snake by 2 segments
- Power-ups: speed boost, slow motion, shield
- Timed effects with `pygame.time.get_ticks()`
- Obstacles from Level 3
- Food and power-ups do not spawn on snake or obstacles
- `settings.json` for snake color, grid, and sound
- Screens: Main Menu, Game, Game Over, Leaderboard, Settings

## Controls

- Arrow keys: move snake
- Mouse: use menu buttons
