# SI 201 HW4
# Your names: Isa Wilson, Amani, Rahma
# Your emails: ifwilson@umich.edu, aaggour@umich.edu, rmusse@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT): ChatGPT
# If you worked with generative AI also add a statement for how you used it. We used ChatGPT for assistance debugging the code.
# e.g.: 
# Asked Chatgpt hints for debugging and suggesting the general sturcture of the code
import os
import sqlite3
import json
import requests
from API_keys import nyt_key
from API_keys import tmdb_key
from API_keys import omdb_key 

DB = "functions.db"

def set_up_database(db=DB): 
    path = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(path, db)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    return cur, conn


def nyt_table(cur, conn): 
    cur.execute("""
        CREATE TABLE IF NOT EXISTS nyt_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            movie_title TEXT, 
            headline TEXT, 
            summary TEXT,
            section TEXT, 
            byline TEXT, 
            date TEXT,
            UNIQUE(headline, date)
        )     
    """)
    conn.commit()


def get_tmdb_movies(pages=5, output_file="movie.json"):
    movies = []

    for page in range(1, pages + 1):

        # Endpoint for popular movies
        url = "https://api.themoviedb.org/3/movie/popular"
        params = {
            "api_key": tmdb_key.api_key,
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
                "api_key": tmdb_key.api_key,
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

    return movies



def get_omdb_ratings(imdb_ids, output_file="omdb_movies.json"):

    movies = []
    base_url = "http://www.omdbapi.com/"

    for imdb_id in imdb_ids:

        params = {
            "apikey": omdb_key.api_key,
            "i": imdb_id
        }

        detail = requests.get(base_url, params=params).json()

        # Store only fields we need
        movies.append({
            "title": detail.get("Title"),
            "imdb_id": imdb_id,
            "genre": detail.get("Genre"),
            "imdb_rating": detail.get("imdbRating")
        })

    # Save to file
    with open(output_file, "w") as f:
        json.dump(movies, f, indent=4)
    
    return movies



def get_nyt_movie_articles(max_results):
    url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
    results = [] 
    page = 0

    while len(results) < max_results and page < 10:  
        params = {
            "q": "movie",
            "api-key": nyt_key.api_key,
            "page": page
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            print("NYT request failed:", response.text[:250]) 
            break 

        data = response.json()
        if "fault" in data: 
            break

        docs = data.get("response", {}).get("docs") or []
        print(f"Page {page} returned {len(docs)} docs")
        if not docs:
            break

        for d in docs: 
            headline = d.get("headline", {}).get("main", "No headline")
            summary = (
                d.get("abstract")
                or d.get("snippet")
                or d.get("lead_paragraph")
                or "No summary avaliable"
            )
            movie_title = None
            keywords = d.get("keywords", [])
            for kw in keywords: 
                if kw.get("name") == "subject": 
                    movie_title = kw.get("value")
                    break
            if not movie_title: 
                movie_title = headline.split(":")[0]

            article = {
                "movie_title": movie_title,
                "headline": headline,
                "summary": summary,
                "section": d.get("section_name"), 
                "byline": d.get("byline", {}).get("original"),
                "date": d.get("pub_date")
            }
            results.append(article)
            if len(results) >= max_results: 
                break 
        
        page += 1
        
    return results[:max_results]

def insert_nyt(cur, conn, articles, max_insert=25): 
    inserted = 0 
    for a in articles: 
        if inserted >= max_insert: 
            break 

        cur.execute("""
            INSERT OR IGNORE INTO nyt_articles
            (movie_title, headline, summary, section, byline, date) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            a.get("movie_title"),
            a.get("headline"),  
            a.get("summary"), 
            a.get("section"), 
            a.get("byline"), 
            a.get("date") 
        )) 

        inserted += 1
    conn.commit()


def main():
    cur, conn = set_up_database()
    nyt_table(cur, conn)

    cur.execute("SELECT COUNT(*) FROM nyt_articles")
    current = cur.fetchone()[0]
    target = 100
    print(f"[NYT] Currently {current} rows in nyt_articles.")
    # tmdb_movies = get_tmdb_movies()
    # print("TMDB movies collected:", len(tmdb_movies))

    if current >= target: 
        conn.close()
        return 
    
    needed = target - current 
    max_ran = min(25, needed)

    articles = get_nyt_movie_articles(max_ran)
    
    if articles: 
        insert_nyt(cur, conn, articles, max_insert=max_ran)
        cur.execute("SELECT COUNT(*) FROM nyt_articles")
        new_count = cur.fetchone()[0]
        print(f"[NYT] Now {new_count} rows in nyt_articles.")
    else: 
        print("Nothing left to insert into NYT")
    conn.close()


    # imdb_ids = [m["imdb_id"] for m in tmdb_movies if m.get("imdb_id")]
    # omdb_movies = get_omdb_ratings(imdb_ids)
    # nyt_articles = get_nyt_movie_articles()

    # print("TMDB movies collected:", len(tmdb_movies))
    # print("OMDb movies collected:", len(omdb_movies))
    # print("NYT articles collected:", len(nyt_articles))


if __name__ == "__main__":
    main()