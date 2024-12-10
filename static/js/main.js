// TMDB API configuration
const TMDB_API_KEY = 'your_api_key_here'; // Replace with your TMDB API key
const TMDB_BASE_URL = 'https://api.themoviedb.org/3';
const TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500';

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const searchInput = document.getElementById('movie-search');
    const searchBtn = document.getElementById('search-btn');
    const googleSearchBtn = document.getElementById('google-search-btn');
    const searchResults = document.getElementById('search-results');
    const getRecommendationBtn = document.getElementById('get-recommendation');
    const recommendationResults = document.getElementById('recommendation-results');
    
    // Questions
    const moodQuestion = document.getElementById('mood-question');
    const occasionQuestion = document.getElementById('occasion-question');
    const genreQuestion = document.getElementById('genre-question');
    
    let selectedMood = '';
    let selectedOccasion = '';
    let selectedGenre = '';

    // Search functionality
    searchBtn.addEventListener('click', () => {
        const query = searchInput.value.trim();
        if (query) {
            searchMovies(query);
        }
    });

    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const query = searchInput.value.trim();
            if (query) {
                searchMovies(query);
            }
        }
    });

    googleSearchBtn.addEventListener('click', () => {
        const query = searchInput.value.trim();
        if (query) {
            window.open(`https://www.google.com/search?q=${encodeURIComponent(query + ' movie')}`, '_blank');
        }
    });

    // Question navigation
    document.querySelectorAll('.option-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            const question = e.target.closest('.question');
            const options = question.querySelectorAll('.option-btn');
            
            options.forEach(opt => opt.classList.remove('selected'));
            e.target.classList.add('selected');

            if (question.id === 'mood-question') {
                selectedMood = e.target.dataset.value;
                moodQuestion.style.display = 'none';
                occasionQuestion.style.display = 'block';
            } else if (question.id === 'occasion-question') {
                selectedOccasion = e.target.dataset.value;
                occasionQuestion.style.display = 'none';
                genreQuestion.style.display = 'block';
            } else if (question.id === 'genre-question') {
                selectedGenre = e.target.dataset.value;
                getRecommendationBtn.style.display = 'block';
            }
        });
    });

    // Get recommendation
    getRecommendationBtn.addEventListener('click', () => {
        getMovieRecommendation(selectedMood, selectedOccasion, selectedGenre);
    });

    async function searchMovies(query) {
        try {
            const response = await fetch(`/search?query=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            if (data.error) {
                displayError(searchResults, data.error);
                return;
            }
            
            displayMovies(searchResults, data.results);
        } catch (error) {
            displayError(searchResults, 'Failed to search movies. Please try again.');
        }
    }

    async function getMovieRecommendation(mood, occasion, genre) {
        try {
            const response = await fetch('/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ mood, occasion, genre })
            });
            
            const data = await response.json();
            
            if (data.error) {
                displayError(recommendationResults, data.error);
                return;
            }
            
            displayMovies(recommendationResults, [data.recommendation]);
        } catch (error) {
            displayError(recommendationResults, 'Failed to get recommendation. Please try again.');
        }
    }

    function displayMovies(container, movies) {
        container.innerHTML = '';
        
        movies.forEach(movie => {
            const movieCard = document.createElement('div');
            movieCard.className = 'movie-card';
            
            const posterPath = movie.poster_path
                ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
                : null;
            
            movieCard.innerHTML = `
                ${posterPath 
                    ? `<img src="${posterPath}" alt="${movie.title}" class="movie-poster">`
                    : `<div class="no-poster">No poster available</div>`
                }
                <div class="movie-info">
                    <h3 class="movie-title">${movie.title}</h3>
                    <p class="movie-year">${movie.release_date ? movie.release_date.split('-')[0] : 'N/A'}</p>
                    <span class="movie-rating">${movie.vote_average ? movie.vote_average.toFixed(1) : 'N/A'}</span>
                    <p class="movie-overview">${movie.overview || 'No overview available'}</p>
                </div>
            `;
            
            container.appendChild(movieCard);
        });
    }

    function displayError(container, message) {
        container.innerHTML = `<div class="error">${message}</div>`;
    }
});
