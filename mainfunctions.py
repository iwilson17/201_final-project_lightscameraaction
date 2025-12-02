# SI 201 HW4
# Your names: Isa Wilson, Amani, Rahma
# Your emails: ifwilson@umich.edu, aaggour@umich.edu, rmusse@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT): ChatGPT
# If you worked with generative AI also add a statement for how you used it. We used ChatGPT for assistance debugging the code.
# e.g.: 
# Asked Chatgpt hints for debugging and suggesting the general sturcture of the code
import requests
import json
import nyt_key

def get_tmdb_movies(pages=5, output_file="movie.json"):
    """
    Fetches popular movies from TMDB, gets detailed info for each movie,
    and saves the results to a JSON file.

    Returns: list of movie dictionaries
    """

    movies = []

    for page in range(1, pages + 1):

        # Endpoint for popular movies
        url = "https://api.themoviedb.org/3/movie/popular"
        params = {
            "api_key": api_key.api_key,
            "language": "en-US",
            "page": page
        }

        response = requests.get(url, params=params)
        data = response.json()

        # Loop through movies on the page
        for movie in data.get("results", []):
            tmdb_id = movie["id"]

            # Fetch detailed info
            detail_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
            detail_params = {
                "api_key": api_key.api_key,
                "language": "en-US"
            }

            detail_res = requests.get(detail_url, params=detail_params)
            detail_data = detail_res.json()

            # Save relevant fields
            movies.append({
                "title": detail_data.get("title"),
                "tmdb_id": tmdb_id,
                "imdb_id": detail_data.get("imdb_id"),
                "budget": detail_data.get("budget")
            })

    # Save to file
    with open(output_file, "w") as f:
        json.dump(movies, f, indent=4)

    print(f"Saved {len(movies)} movies to {output_file}")
    return movies


def get_nyt_movie_articles(movie_title):
    url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
    
    params = {
        "q": movie_title, 
        "api-key": my_key.API_KEY,

    }

    headers = {
        "User-Agent": "SI201-finalproject", 
        "Accept": "application/json"
    }

    response = requests.get(url, params=params, headers=headers)
    print("STATUS", response.status_code)

    if response.status_code != 200: 
        print("Request failed")
        return []
    
    data = response.json()
    docs = data.get("response", {}).get("docs", [])

    if not docs:
        print("No articles found for:", movie_title)
        return []

    results = []

    for d in docs[:1]: 
        article = {
            "movie_title": movie_title, 
            "headline": d.get("headline", {}).get("main", "No headline"),
            "summary": d.get("abstract", "No summary"), 
            "section": d.get("section_name"), 
            "byline": d.get("byline", {}).get("original"),
            "date": d.get("pub_date")
        }

        results.append(article)


    with open("articles.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
    print(f"Saved {len(article)} articles to articles.json")

    return results 


# if __name__ == "__main__":
#     print(get_nyt_movie_articles("Shrek"))
#     print(get_nyt_movie_articles("Barbie"))




import sqlite3
import matplotlib.pyplot as plt

def plot_mentions_vs_budget(db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    rows = cur.execute("""
        SELECT tmdb.budget 
        FROM tmdb 
        JOIN nyt
            ON LOWER(tmdb.title) = LOWER(nyt.movie_title); 
    """).fetchall()

    conn.close()

    low = 0 
    medium = 0 
    high = 0 

    for (budget,) in rows: 
        if budget is None: 
            continue 
        if budget < 20_000_000: 
            low += 1 
        elif 20_000_000 <= budget <= 80_000_000: 
            medium += 1
        else: 
            high += 1 

    categories = ["Low", "Medium", "High"]
    counts = [low, medium, high]

    plt.figure(figsize=(8, 5))
    plt.bar(categories, counts)
    plt.title("NYT Article Mentions by Movie Budget Category")
    plt.xlabel("Budget Category")
    plt.ylabel("Number of NYT Mentions")
    plt.tight_layout()
    plt.savefig("NYT_Mention_vs_Budget.png")
    plt.show()

if __name__ == "__main__":
    plot_mentions_vs_budget(".db")