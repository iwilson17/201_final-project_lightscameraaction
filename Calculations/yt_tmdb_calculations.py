import sqlite3
import re
import matplotlib.pyplot as plt

def compare_trailer_popularity_to_budget():
    conn = sqlite3.connect("movies.db")
    cur = conn.cursor()

    cur.execute("SELECT tmdb_id, title, budget FROM tmdb_movies")
    movies = cur.fetchall()

    cur.execute("SELECT title, view_count, like_count, comment_count FROM youtube_trailers")
    trailers = cur.fetchall()

    results = []

    for tmdb_id, movie_title, budget in movies: 
        movie_official = re.sub(r"[^\w\s]", "", movie_title.lower()).strip()
        matched = [
            t for t in trailers
            if movie_official in re.sub(r"[^\w\s]", "", t[0].lower()).strip()
        ]
        if matched: 
            total_views = sum(t[1] for t in matched)
            total_likes = sum(t[2] for t in matched)
            total_comments = sum(t[3] for t in matched)

            results.append ({
                "movie_title": movie_title, 
                "budget": budget,
                "total_views": total_views,
                "total_likes": total_likes,
                "total_comments": total_comments,
            })

    conn.close()
    return results

def plot_trailer_vs_budget(data, top_n_labels=5): 
    budgets = [d['budget']/1_000_000 for d in data]
    views = [d['total_views'] for d in data]
    titles = [d['movie_title'] for d in data]

    plt.figure(figsize=(12,6))
    plt.scatter(budgets, views, color='teal', alpha=0.7, edgecolors='k')
    plt.title("Youtube Trailer Views vs. Movie Budget")
    plt.xlabel("Movie Budget (Millions USD)")
    plt.ylabel("Total Trailer Views")
    plt.grid(True, linestyle='--', alpha=0.5)

    top_indices = sorted(range(len(views)), key=lambda i: views[i], reverse=True)[:top_n_labels]
    for i in top_indices: 
        plt.text(budgets[i], views[i], titles[i], fontsize=9, ha='right', va='bottom')

    plt.show()

if __name__ == "__main__":
    data = compare_trailer_popularity_to_budget()
    plot_trailer_vs_budget(data)
