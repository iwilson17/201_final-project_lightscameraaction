# SI 201 HW4
# Your names: Isa Wilson, Amani, Rahma
# Your emails: ifwilson@umich.edu, aaggour@umich.edu, rmusse@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT): ChatGPT
# If you worked with generative AI also add a statement for how you used it. We used ChatGPT for assistance debugging the code.
# e.g.: 
# Asked Chatgpt hints for debugging and suggesting the general sturcture of the code
import os
import json
import requests
from API_keys import nyt_key
from API_keys import tmdb_key
from API_keys import omdb_key 


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


def get_nyt_movie_articles(genres=None, pages=10, output_file="nyt_articles.json"):
    if genres is None: 
        genres = ["Action, Thriller, Adventure, Horror, Fantasy, Sci-Fi"]

    articles = []
    for genre in genres: 
       for page in range(0, pages): 
            url = "https://api.nytimes.com/svc/search/v2/articlesearch.json" 
            params = {
                "q": f"{genre} movies OR {genre} films", 
                "api-key": nyt_key.api_key,
                "page": page
            }

            response = requests.get(url, params=params)
            data = response.json()
            print(response)
            print(data)
            
            for d in data.get("response", {}).get("docs", []): 
                articles.append ({
                    "genre": genre,
                    "headline": d.get("headline", {}).get("main"), 
                    "summary": d.get("snippet") or d.get("lead_paragraph") or d.get("abstract"),
                    "section": d.get("section_name"), 
                    "byline": d.get("byline", {}).get("original"),
                    "date": d.get("pub_date"),
                    "url": d.get("web_url")
                })
    with open(output_file, "w") as f: 
        json.dump(articles, f, indent=4)

    return articles


def main():
    # # 1. Fetch TMDB movies
    # tmdb_movies = get_tmdb_movies(pages=6)
    # print("TMDB movies collected:", len(tmdb_movies))

    # # 2. Extract IMDb IDs from TMDB movies
    # imdb_ids = [m["imdb_id"] for m in tmdb_movies if m.get("imdb_id")]

    # # 3. Fetch OMDB ratings using the IMDb IDs
    # omdb_movies = get_omdb_ratings(imdb_ids)
    # print("OMDB movies collected:", len(omdb_movies))

    nyt_articles = get_nyt_movie_articles()
    print("NYT articles collected:", len(nyt_articles))


if __name__ == "__main__":
    main()