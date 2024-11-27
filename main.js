document.addEventListener('DOMContentLoaded', () => {
    const questions = document.querySelectorAll('.question');
    const progressBar = document.querySelector('.progress');
    const result = document.querySelector('.result');
    const loading = document.querySelector('.loading');
    
    let currentQuestion = 0;
    const answers = [];

    // Initialize progress bar
    updateProgress();

    // Add navigation buttons to each question
    questions.forEach((question, index) => {
        const navButtons = document.createElement('div');
        navButtons.className = 'navigation-buttons';
        
        if (index > 0) {
            const prevButton = document.createElement('button');
            prevButton.className = 'button';
            prevButton.textContent = 'Previous';
            prevButton.onclick = () => navigateQuestion(-1);
            navButtons.appendChild(prevButton);
        }
        
        if (index < questions.length - 1) {
            const nextButton = document.createElement('button');
            nextButton.className = 'button';
            nextButton.textContent = 'Next';
            nextButton.onclick = () => {
                if (validateQuestion(index)) {
                    navigateQuestion(1);
                }
            };
            navButtons.appendChild(nextButton);
        } else {
            const submitButton = document.createElement('button');
            submitButton.className = 'button';
            submitButton.textContent = 'Get Recommendation';
            submitButton.onclick = () => {
                if (validateQuestion(index)) {
                    submitAnswers();
                }
            };
            navButtons.appendChild(submitButton);
        }
        
        question.appendChild(navButtons);
    });

    // Handle option selection
    document.querySelectorAll('.button[data-option]').forEach(button => {
        button.addEventListener('click', () => {
            const questionIndex = parseInt(button.closest('.question').dataset.question);
            const siblings = button.parentElement.querySelectorAll('.button[data-option]');
            
            siblings.forEach(sib => sib.classList.remove('selected'));
            button.classList.add('selected');
            
            answers[questionIndex] = button.dataset.option;
        });
    });

    function validateQuestion(index) {
        const question = questions[index];
        
        if (question.querySelector('.checkbox-group')) {
            const checked = question.querySelectorAll('input[type="checkbox"]:checked');
            if (checked.length === 0) {
                alert('Please select at least one option');
                return false;
            }
            if (index === 2 && checked.length > 3) {
                alert('Please select up to 3 genres only');
                return false;
            }
            answers[index] = Array.from(checked).map(cb => cb.value);
        } else {
            const selected = question.querySelector('.button.selected');
            if (!selected) {
                alert('Please select an option');
                return false;
            }
            answers[index] = selected.dataset.option;
        }
        
        return true;
    }

    function navigateQuestion(direction) {
        questions[currentQuestion].classList.remove('active');
        currentQuestion += direction;
        questions[currentQuestion].classList.add('active');
        updateProgress();
    }

    function updateProgress() {
        const progress = ((currentQuestion + 1) / questions.length) * 100;
        progressBar.style.width = `${progress}%`;
    }

    async function submitAnswers() {
        try {
            questions[currentQuestion].style.display = 'none';
            loading.style.display = 'block';

            const response = await fetch('/get-movie', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ answers }),
            });

            if (!response.ok) {
                throw new Error('Failed to get recommendation');
            }

            const data = await response.json();
            displayResult(data);
        } catch (error) {
            console.error('Error:', error);
            alert('Error getting movie recommendation. Please try again.');
            questions[currentQuestion].style.display = 'block';
        } finally {
            loading.style.display = 'none';
        }
    }

    function displayResult(movie) {
        const movieTitle = document.getElementById('movie-title');
        const moviePoster = document.getElementById('movie-poster');
        const movieOverview = document.getElementById('movie-overview');
        const movieRating = document.getElementById('movie-rating');
        const movieReleaseDate = document.getElementById('movie-release-date');
        const movieGenres = document.getElementById('movie-genres');
        const watchProviders = document.getElementById('watch-providers');

        movieTitle.textContent = movie.title;
        moviePoster.src = movie.poster_path || '/static/images/no-poster.png';
        movieOverview.textContent = movie.overview;
        movieRating.textContent = movie.vote_average ? `${movie.vote_average}/10` : 'N/A';
        movieReleaseDate.textContent = movie.release_date ? new Date(movie.release_date).getFullYear() : 'N/A';

        // Display genres
        movieGenres.innerHTML = movie.genres
            .map(genre => `<span class="genre-tag">${genre}</span>`)
            .join('');

        // Display watch providers
        if (movie.watch_providers && Object.keys(movie.watch_providers).length > 0) {
            const providers = [];
            if (movie.watch_providers.flatrate) {
                providers.push(...movie.watch_providers.flatrate.map(p => `<div class="provider-item">Stream on ${p.provider_name}</div>`));
            }
            if (movie.watch_providers.rent) {
                providers.push(...movie.watch_providers.rent.map(p => `<div class="provider-item">Rent on ${p.provider_name}</div>`));
            }
            if (movie.watch_providers.buy) {
                providers.push(...movie.watch_providers.buy.map(p => `<div class="provider-item">Buy on ${p.provider_name}</div>`));
            }
            watchProviders.innerHTML = providers.join('');
        } else {
            watchProviders.innerHTML = '<div class="provider-item">No streaming information available</div>';
        }

        result.style.display = 'block';
    }
});
