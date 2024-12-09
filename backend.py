from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import tmdbsimple as tmdb
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
import random

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI()

# Get the absolute path to the project root directory
BASE_DIR = Path(__file__).resolve().parent

# Configure static files and templates
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize TMDB
tmdb.API_KEY = os.getenv("TMDB_API_KEY")

class UserAnswers(BaseModel):
    answers: List[str]

class SearchQuery(BaseModel):
    query: str

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/recommend")
async def get_movie(request: UserAnswers):
    try:
        # Map moods to genres
        mood_to_genre = {
            "happy": ["comedy", "family", "adventure"],
            "sad": ["drama", "romance"],
            "excited": ["action", "adventure", "science fiction"],
            "relaxed": ["animation", "family", "fantasy"],
            "thoughtful": ["documentary", "drama", "history"]
        }

        # Get genre IDs from TMDB
        genre = tmdb.Genres()
        genre_list = genre.movie_list()['genres']
        genre_map = {g['name'].lower(): g['id'] for g in genre_list}
        
        # Get user's mood from answers
        user_mood = request.answers[0].lower()
        selected_genres = mood_to_genre.get(user_mood, ["action"])
        
        # Convert genre names to IDs
        genre_ids = [genre_map[g] for g in selected_genres if g in genre_map]
        
        # Get movies for these genres
        discover = tmdb.Discover()
        response = discover.movie(with_genres=','.join(map(str, genre_ids)))
        
        if not response['results']:
            return {"error": "No movies found"}
            
        # Select a random movie from results
        movie = random.choice(response['results'])
        
        return {
            "title": movie.get('title'),
            "year": movie.get('release_date', '')[:4],
            "poster_path": f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}",
            "overview": movie.get('overview'),
            "vote_average": movie.get('vote_average'),
            "original_language": movie.get('original_language')
        }
        
    except Exception as e:
        logger.error(f"Error recommending movie: {str(e)}")
        return {"error": str(e)}

@app.post("/api/search")
async def search_movies(search_query: SearchQuery):
    try:
        search = tmdb.Search()
        response = search.movie(query=search_query.query)
        
        movies = []
        for movie in response['results'][:5]:  # Limit to 5 results
            movies.append({
                "title": movie.get('title'),
                "year": movie.get('release_date', '')[:4],
                "poster_path": f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}",
                "overview": movie.get('overview'),
                "vote_average": movie.get('vote_average')
            })
            
        return {"movies": movies}
        
    except Exception as e:
        logger.error(f"Error searching movies: {str(e)}")
        return {"error": str(e)}
