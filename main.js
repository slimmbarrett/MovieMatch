// TMDB API configuration
const TMDB_API_KEY = 'your_api_key_here'; // Replace with your TMDB API key
const TMDB_BASE_URL = 'https://api.themoviedb.org/3';
const TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500';

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    const googleSearchButton = document.getElementById('googleSearchButton');
    const getRecommendationBtn = document.getElementById('getRecommendationBtn');
    const resultsSection = document.getElementById('results');
    const optionButtons = document.querySelectorAll('.option-btn');

    // Handle regular movie search
    searchButton.addEventListener('click', () => {
        const query = searchInput.value.trim();
        if (query) {
            searchMovies(query);
        }
    });

    // Handle Google search
    googleSearchButton.addEventListener('click', () => {
        const query = searchInput.value.trim();
        if (query) {
            const searchQuery = `${query} фильм смотреть`;
            window.open(`https://www.google.com/search?q=${encodeURIComponent(searchQuery)}`, '_blank');
        }
    });

    // Handle option selection
    optionButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Find all buttons in the same question group
            const questionDiv = button.closest('.question');
            const buttonsInGroup = questionDiv.querySelectorAll('.option-btn');
            
            // Remove selected class from all buttons in group
            buttonsInGroup.forEach(btn => btn.classList.remove('selected'));
            
            // Add selected class to clicked button
            button.classList.add('selected');
        });
    });

    // Handle get recommendation button
    getRecommendationBtn.addEventListener('click', () => {
        const selectedOptions = {
            mood: getSelectedValue('moodQuestion'),
            occasion: getSelectedValue('occasionQuestion'),
            genre: getSelectedValue('genreQuestion')
        };

        if (selectedOptions.mood && selectedOptions.occasion && selectedOptions.genre) {
            getMovieRecommendation(selectedOptions);
        } else {
            alert('Пожалуйста, выберите все критерии для получения рекомендации');
        }
    });

    // Search for movies using the API
    async function searchMovies(query) {
        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query })
            });

            const data = await response.json();
            displayResults(data.movies);
        } catch (error) {
            console.error('Error searching movies:', error);
            resultsSection.innerHTML = '<p class="error">Произошла ошибка при поиске фильмов. Попробуйте позже.</p>';
        }
    }

    // Get movie recommendation based on selected options
    async function getMovieRecommendation(options) {
        try {
            const response = await fetch('/api/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    answers: [options.mood, options.occasion, options.genre]
                })
            });

            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }
            
            displayResults([data]); // Display as single movie in results
        } catch (error) {
            console.error('Error getting recommendation:', error);
            resultsSection.innerHTML = '<p class="error">Произошла ошибка при получении рекомендации. Попробуйте позже.</p>';
        }
    }

    // Helper function to get selected value from a question group
    function getSelectedValue(questionId) {
        const selectedButton = document.querySelector(`#${questionId} .option-btn.selected`);
        return selectedButton ? selectedButton.dataset.value : null;
    }

    // Display movie results
    function displayResults(movies) {
        if (!movies || movies.length === 0) {
            resultsSection.innerHTML = '<p>Фильмы не найдены. Попробуйте другой запрос.</p>';
            return;
        }

        resultsSection.innerHTML = movies.map(movie => `
            <div class="movie-card">
                ${movie.poster_path 
                    ? `<img src="${TMDB_IMAGE_BASE_URL}${movie.poster_path}" alt="${movie.title}" class="movie-poster">`
                    : '<div class="no-poster">Постер недоступен</div>'
                }
                <div class="movie-info">
                    <h3 class="movie-title">${movie.title}</h3>
                    <p class="movie-year">${movie.release_date ? movie.release_date.substring(0, 4) : 'N/A'}</p>
                    ${movie.vote_average 
                        ? `<span class="movie-rating">★ ${movie.vote_average.toFixed(1)}</span>`
                        : ''
                    }
                    ${movie.overview 
                        ? `<p class="movie-overview">${movie.overview}</p>`
                        : ''
                    }
                </div>
            </div>
        `).join('');
    }

    // Handle enter key in search input
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchButton.click();
        }
    });
});
