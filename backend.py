git acd c:/Users/user6549/Desktop/MovieMatch
git add .
git commit -m "Fix logging configuration for Vercel"
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import openai
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

# Initialize API keys
openai.api_key = os.getenv("OPENAI_API_KEY")
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
        # Create cache key from user answers
        cache_key = json.dumps(request.answers, sort_keys=True)
        
        # Check cache
        if cache_key in movie_cache:
            logger.info("Returning cached recommendation")
            return movie_cache[cache_key]

        # Format prompt for ChatGPT
        prompt = (
            "You are a professional movie critic and recommendation expert. "
            "Based on the following preferences, recommend ONE specific movie title (no explanations needed):\n"
            f"1. Mood: {request.answers[0]}\n"
            f"2. Occasion: {request.answers[1]}\n"
            f"3. Preferred genres: {', '.join(request.answers[2])}\n"
            f"4. Movie age preference: {request.answers[3]}\n"
            f"5. Ratings importance: {request.answers[4]}\n"
            f"6. Acceptable MPAA ratings: {', '.join(request.answers[5])}\n\n"
            "Return only the movie title, nothing else."
        )

        # Get recommendation from OpenAI
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a movie recommendation expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.7
        )

        movie_title = response.choices[0].message.content.strip()
        
        # Get detailed movie information
        movie_details = await get_movie_details(movie_title)
        
        # Cache the result
        movie_cache[cache_key] = movie_details
        
        # Log successful recommendation
        logger.info(f"Successfully recommended movie: {movie_title}")
        
        return movie_details

    except Exception as e:
        logger.error(f"Error generating recommendation: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating movie recommendation")from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import openai
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

# Initialize API keys
openai.api_key = os.getenv("OPENAI_API_KEY")
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
        # Create cache key from user answers
        cache_key = json.dumps(request.answers, sort_keys=True)
        
        # Check cache
        if cache_key in movie_cache:
            logger.info("Returning cached recommendation")
            return movie_cache[cache_key]

        # Format prompt for ChatGPT
        prompt = (
            "You are a professional movie critic and recommendation expert. "
            "Based on the following preferences, recommend ONE specific movie title (no explanations needed):\n"
            f"1. Mood: {request.answers[0]}\n"
            f"2. Occasion: {request.answers[1]}\n"
            f"3. Preferred genres: {', '.join(request.answers[2])}\n"
            f"4. Movie age preference: {request.answers[3]}\n"
            f"5. Ratings importance: {request.answers[4]}\n"
            f"6. Acceptable MPAA ratings: {', '.join(request.answers[5])}\n\n"
            "Return only the movie title, nothing else."
        )

        # Get recommendation from OpenAI
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a movie recommendation expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.7
        )

        movie_title = response.choices[0].message.content.strip()
        
        # Get detailed movie information
        movie_details = await get_movie_details(movie_title)
        
        # Cache the result
        movie_cache[cache_key] = movie_details
        
        # Log successful recommendation
        logger.info(f"Successfully recommended movie: {movie_title}")
        
        return movie_details

    except Exception as e:
        logger.error(f"Error generating recommendation: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating movie recommendation")
