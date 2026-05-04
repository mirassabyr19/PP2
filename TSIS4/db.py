import psycopg2
from config import DB_CONFIG


def get_connection():
    """Create and return a PostgreSQL connection."""
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    """Create required tables if they do not exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS game_sessions (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES players(id) ON DELETE CASCADE,
            score INTEGER NOT NULL,
            level_reached INTEGER NOT NULL,
            played_at TIMESTAMP DEFAULT NOW()
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


def get_or_create_player(username):
    """Insert a player if missing and return player id."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO players(username)
        VALUES (%s)
        ON CONFLICT (username) DO NOTHING;
    """, (username,))

    cur.execute("SELECT id FROM players WHERE username = %s;", (username,))
    player_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()
    return player_id


def save_result(username, score, level_reached):
    """Save game result after game over."""
    player_id = get_or_create_player(username)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO game_sessions(player_id, score, level_reached)
        VALUES (%s, %s, %s);
    """, (player_id, score, level_reached))

    conn.commit()
    cur.close()
    conn.close()


def get_personal_best(username):
    """Return player's best score."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COALESCE(MAX(score), 0)
        FROM game_sessions
        JOIN players ON players.id = game_sessions.player_id
        WHERE username = %s;
    """, (username,))

    best = cur.fetchone()[0]
    cur.close()
    conn.close()
    return best


def get_top_scores(limit=10):
    """Return top scores for leaderboard screen."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT players.username, game_sessions.score, game_sessions.level_reached,
               TO_CHAR(game_sessions.played_at, 'YYYY-MM-DD HH24:MI')
        FROM game_sessions
        JOIN players ON players.id = game_sessions.player_id
        ORDER BY game_sessions.score DESC, game_sessions.level_reached DESC, game_sessions.played_at ASC
        LIMIT %s;
    """, (limit,))

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
