import pandas as pd
import logging

try:
    # Make sure the CSV file is located at 'data/imdb_cleaned.csv'
    MOVIE_DATA = pd.read_csv("data/imdb_cleaned.csv")
    logging.info("✅ IMDb data loaded successfully for data access.")
except Exception as e:
    logging.error(f"❌ Failed to load IMDb data: {e}")
    MOVIE_DATA = pd.DataFrame()


def search_movies_by_keywords(query: str, top_k: int = 5) -> list:
    """
    Keyword-based search across Title, Genre, Star Cast, and Director.
    """
    if MOVIE_DATA.empty:
        logging.warning("⚠️ No movie data available for search.")
        return []

    query_lower = query.lower()
    
    # --- FIX 1: Using column names from your dataset sample ---
    matches = MOVIE_DATA[
        MOVIE_DATA['Title'].str.strip().str.lower().str.contains(query_lower, na=False) |
        MOVIE_DATA['Genre'].str.strip().str.lower().str.contains(query_lower, na=False) |
        MOVIE_DATA['Star Cast'].str.strip().str.lower().str.contains(query_lower, na=False) |
        MOVIE_DATA['Director'].str.strip().str.lower().str.contains(query_lower, na=False)
    ]

    results = []
    for _, row in matches.head(top_k).iterrows():
        results.append({
            "title": row["Title"],
            # --- IMPORTANT CHANGE: Use the 'Generated_Plot' column ---
            "plot": row.get("Generated_Plot", "No plot available."), # <-- This line is changed
            "description": row.get("embedding_text", "No description available.") # Keep this if needed for other purposes
        })
    return results


def get_rating_by_title(title: str) -> dict:
    """
    Retrieve rating and votes for a movie title using a flexible search.
    """
    if MOVIE_DATA.empty:
        return None

    title_lower = title.lower()
    
    match = MOVIE_DATA[MOVIE_DATA['Title'].str.strip().str.lower().str.contains(title_lower, na=False)]

    if match.empty:
        return None

    row = match.iloc[0]

    rating = row.get("IMDb Rating", "N/A")
    votes = "N/A" # Your sample did not include a votes column

    return {
        "rating": rating,
        "votes": votes
    }