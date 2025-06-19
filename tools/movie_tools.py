import logging
from typing import Optional, List
from google.adk.tools.tool_context import ToolContext
from storage.movie_data_access import get_rating_by_title, search_movies_by_keywords
from storage.vector_db import movie_retriever_instance

logging.basicConfig(level=logging.INFO, format='%(asctime)s - LOG - %(message)s')

def get_movie_rating(title: str) -> dict:
    """Gets the rating for a specific movie title."""
    logging.info(f"TOOL EXECUTED: get_movie_rating(title='{title}')")
    rating_info = get_rating_by_title(title)
    if rating_info:
        return {"title": title, "rating": rating_info.get("rating"), "votes": rating_info.get("votes")}
    return {"title": title, "rating": "Not Found", "votes": "N/A"}

def search_movies(query: str) -> dict:
    """Finds information about a movie using keyword search."""
    logging.info(f"TOOL EXECUTED: search_movies(query='{query}')")
    return {"results": search_movies_by_keywords(query, top_k=5)}

# --- UPGRADED RECOMMENDATION TOOL ---
def recommend_movies(
    base_query: str,
    liked_movies: Optional[List[str]] = None,
    disliked_movies: Optional[List[str]] = None
) -> dict:
    """
    Recommends movies based on a query, using the user's liked and
    disliked movies to create a more personalized recommendation.
    """
    logging.info(f"TOOL EXECUTED: recommend_movies(base_query='{base_query}')")
    
    # Create a more sophisticated search query for the vector store.
    # This combines the user's explicit request with their implicit preferences.
    search_text = base_query
    if liked_movies:
        # Add liked movies to the search query to find similar items.
        search_text += " " + " ".join(liked_movies)
        logging.info(f"Personalizing search with liked movies: {liked_movies}")

    # In a more advanced system, you would also use the disliked_movies
    # to filter out or penalize certain results. For now, we'll keep it simple.
    
    recommendations = movie_retriever_instance.search(search_text, top_k=10) # Get more results to filter
    
    # Filter out movies the user has already liked or disliked to avoid re-recommending.
    final_recommendations = []
    if recommendations:
        for rec in recommendations:
            title = rec.get('Title')
            if title:
                # Keep the recommendation if it's not in the user's liked or disliked lists.
                if (not liked_movies or title not in liked_movies) and \
                   (not disliked_movies or title not in disliked_movies):
                    final_recommendations.append(rec)
    
    # Return the top 5 of the filtered list.
    return {"recommendations": final_recommendations[:5]}


def update_user_preferences(
    tool_context: ToolContext,
    user_id: str,
    liked_movie: Optional[str] = None,
    disliked_movie: Optional[str] = None
) -> dict:
    """Saves a user's movie preference directly into the session state."""
    logging.info(f"TOOL EXECUTED: update_user_preferences for user '{user_id}'")
    user_profile = tool_context.state.get("user_profile")

    if liked_movie and user_profile:
        if liked_movie not in user_profile.liked_movies:
            user_profile.liked_movies.append(liked_movie)
            logging.info(f"STATE UPDATED: Added '{liked_movie}' to liked movies for user '{user_id}'.")

    if disliked_movie and user_profile:
        if disliked_movie not in user_profile.disliked_movies:
            user_profile.disliked_movies.append(disliked_movie)
            logging.info(f"STATE UPDATED: Added '{disliked_movie}' to disliked movies for user '{user_id}'.")

    tool_context.state["user_profile"] = user_profile
    return {"status": "success", "user_id": user_id}