import sqlite3


def create_tmdb_tables():
    conn = sqlite3.connect("movies.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tmdb_movies (
            tmdb_id INTEGER PRIMARY KEY,
            title TEXT,
            imdb_id TEXT,
            budget INTEGER
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tmdb_links (
            imdb_id TEXT PRIMARY KEY
        );
    """)

    conn.commit()
    conn.close()



def save_tmdb_to_db(movies):
    conn = sqlite3.connect("movies.db")
    cur = conn.cursor()

    count_added = 0

    for movie in movies:
        try:
            imdb_id = movie.get("imdb_id")
            if not imdb_id:
                imdb_id = "N/A"   # beginner style fix

            before = conn.total_changes
            cur.execute("""
                INSERT OR IGNORE INTO tmdb_movies (tmdb_id, title, imdb_id, budget)
                VALUES (?, ?, ?, ?)
            """, (movie.get("tmdb_id"), movie.get("title"), imdb_id, movie.get("budget")))
            after = conn.total_changes

            if after > before:
                count_added += 1

            if count_added >= 25:
                break

        except Exception as e:
            print("Error saving TMDB movie:", e)

    conn.commit()
    conn.close()
    print("TMDB: Added", count_added, "movies.")



def create_omdb_tables():
    conn = sqlite3.connect("movies.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS omdb_movies (
            imdb_id TEXT PRIMARY KEY,
            title TEXT,
            genre TEXT,
            imdb_rating REAL
        );
    """)

    conn.commit()
    conn.close()


# --------------------------------------------------------
# Save OMDB ratings (limit 25)
# --------------------------------------------------------
def save_omdb_to_db(movies):
    conn = sqlite3.connect("movies.db")
    cur = conn.cursor()

    count_added = 0

    for movie in movies:
        try:
            imdb_id = movie.get("imdb_id")
            title = movie.get("title")
            genre = movie.get("genre")
            rating = movie.get("imdb_rating")

            if not imdb_id or not title:
                continue   # skip bad records

            before = conn.total_changes
            cur.execute("""
                INSERT OR IGNORE INTO omdb_movies (imdb_id, title, genre, imdb_rating)
                VALUES (?, ?, ?, ?)
            """, (imdb_id, title, genre, rating))
            after = conn.total_changes

            if after > before:
                count_added += 1

            if count_added >= 25:
                break

        except Exception as e:
            print("Error saving OMDB movie:", e)

    conn.commit()
    conn.close()
    print("OMDB: Added", count_added, "movies.")



def main():
    from mainfunctions import get_tmdb_movies, get_omdb_ratings  

    create_tmdb_tables()
    create_omdb_tables()

    tmdb_movies = get_tmdb_movies()
    save_tmdb_to_db(tmdb_movies)

    imdb_ids = [m.get("imdb_id") for m in tmdb_movies if m.get("imdb_id")]
    omdb_movies = get_omdb_ratings(imdb_ids)
    save_omdb_to_db(omdb_movies)

    print("DONE.")


if __name__ == "__main__":
    main()
