from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from openai import AsyncOpenAI
import tmdbsimple as tmdb
from dotenv import load_dotenv
import os
import json
import logging
from datetime import datetime
from pathlib import Path

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Only log to console for Vercel
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="MovieMatch API", version="2.0.0")

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

# Initialize API clients
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
tmdb.API_KEY = os.getenv("TMDB_API_KEY")

# Pydantic models
class UserAnswers(BaseModel):
    answers: List[any]

class MovieRecommendation(BaseModel):
    title: str
    overview: str
    poster_path: Optional[str]
    release_date: Optional[str]
    vote_average: Optional[float]
    genres: List[str]
    watch_providers: Optional[dict]

# Cache for movie recommendations
movie_cache = {}

async def get_movie_details(movie_title: str) -> MovieRecommendation:
    """Get detailed movie information from TMDB API"""
    try:
        search = tmdb.Search()
        response = search.movie(query=movie_title)
        
        if not response['results']:
            raise HTTPException(status_code=404, detail="Movie not found")
            
        movie = response['results'][0]
        
        # Get watch providers
        movie_id = movie['id']
        movie_info = tmdb.Movies(movie_id)
        providers = movie_info.watch_providers()
        
        return MovieRecommendation(
            title=movie['title'],
            overview=movie['overview'],
            poster_path=f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie['poster_path'] else None,
            release_date=movie['release_date'],
            vote_average=movie['vote_average'],
            genres=[genre['name'] for genre in movie_info.info()['genres']],
            watch_providers=providers.get('results', {}).get('US', {})
        )
    except Exception as e:
        logger.error(f"Error fetching movie details: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching movie details")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/get-movie", response_model=MovieRecommendation)
async def get_movie(request: UserAnswers):
    """Generate movie recommendation based on user answers"""
    try:
        # Verify API keys are set
        if not os.getenv("OPENAI_API_KEY"):
            logger.error("OpenAI API key is not set")
            raise HTTPException(status_code=500, detail="OpenAI API key is not configured")
        
        if not tmdb.API_KEY:
            logger.error("TMDB API key is not set")
            raise HTTPException(status_code=500, detail="TMDB API key is not configured")

        # Create cache key from user answers
        cache_key = json.dumps(request.answers, sort_keys=True)
        
        # Check cache
        if cache_key in movie_cache:
            logger.info("Returning cached recommendation")
            return movie_cache[cache_key]

        # Format prompt for ChatGPT
        mood = request.answers[0]
        occasion = request.answers[1]
        genres = request.answers[2]
        movie_age = request.answers[3]
        rating_importance = request.answers[4]
        acceptable_ratings = request.answers[5]

        prompt = (
            "Hi! I need a movie recommendation for tonight. Here are my preferences:\n\n"
            f"1. My current mood: {mood}\n"
            f"2. Viewing occasion: {occasion}\n"
            f"3. Preferred genres: {', '.join(genres)}\n"
            f"4. Movie age preference: {movie_age}\n"
            f"5. Rating importance: {rating_importance}\n"
            f"6. Acceptable MPAA ratings: {', '.join(acceptable_ratings)}\n\n"
            "Please recommend one specific movie. "
            "Reply ONLY with the movie title and year in the format: 'Movie Title (year)'. "
            "For example: 'The Shawshank Redemption (1994)'. No additional explanations."
        )

        try:
            # Get recommendation from OpenAI
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a movie expert. Respond only with the movie title and year in the format 'Title (year)'."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.7
            )
            
            if not response.choices:
                logger.error("OpenAI API returned no choices")
                raise HTTPException(status_code=500, detail="Failed to get movie recommendation")
            
            # Extract movie title and year
            movie_response = response.choices[0].message.content.strip()
            logger.info(f"OpenAI suggested movie: {movie_response}")
            
            # Extract year from response (assuming format "Movie Title (YEAR)")
            import re
            year_match = re.search(r'\((\d{4})\)$', movie_response)
            if year_match:
                year = year_match.group(1)
                title = movie_response[:movie_response.rfind('(')].strip()
            else:
                title = movie_response
                year = None
            
            logger.info(f"Parsed title: {title}, year: {year}")
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error communicating with OpenAI API: {str(e)}")

        try:
            # Search for movie in TMDB
            search = tmdb.Search()
            search_params = {"query": title}
            if year:
                search_params["year"] = year
            
            response = search.movie(**search_params)
            
            if not response.get('results'):
                # Try searching without year if no results found
                if year:
                    response = search.movie(query=title)
            
            if not response.get('results'):
                raise Exception(f"No movie found for title: {title}")
            
            # Get the first result
            movie = response['results'][0]
            
            # Create movie details response
            movie_details = {
                "title": movie['title'],
                "year": movie['release_date'][:4] if movie.get('release_date') else year or "N/A",
                "poster_path": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get('poster_path') else None,
                "overview": movie.get('overview', ""),
                "vote_average": movie.get('vote_average', 0),
                "original_language": movie.get('original_language', "en")
            }
            
            # Cache the result
            movie_cache[cache_key] = movie_details
            
            # Log successful recommendation
            logger.info(f"Successfully recommended movie: {movie_details['title']} ({movie_details['year']})")
            
            return movie_details
            
        except Exception as e:
            logger.error(f"TMDB API error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching movie details from TMDB: {str(e)}")

    except Exception as e:
        logger.error(f"Unexpected error in get_movie: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
