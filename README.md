# MovieMatch

MovieMatch is an intelligent movie recommendation system that suggests movies based on your mood, preferences, and viewing context. It uses OpenAI's GPT model for personalized recommendations and TMDB API for detailed movie information.

## Features

- Personalized movie recommendations based on:
  - Current mood
  - Viewing occasion
  - Genre preferences
  - Movie age preferences
  - Age rating preferences
- Detailed movie information including:
  - Movie poster
  - Release date
  - Rating
  - Overview
  - Genres
  - Watch providers (where to stream/rent/buy)
- Modern, responsive UI
- Progress tracking
- Previous/Next navigation
- Input validation
- Loading states
- Error handling

## Prerequisites

- Python 3.8+
- OpenAI API key
- TMDB API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/MovieMatch.git
cd MovieMatch
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory and add your API keys:
```
OPENAI_API_KEY=your_openai_api_key_here
TMDB_API_KEY=your_tmdb_api_key_here
SECRET_KEY=your_secret_key_here
```

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn backend:app --reload
```

2. Open your browser and navigate to:
```
http://127.0.0.1:8000
```

## Project Structure

```
MovieMatch/
├── backend.py          # FastAPI backend
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
├── README.md          # Documentation
├── static/            # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
└── templates/         # HTML templates
    └── index.html
```

## Technologies Used

- Backend:
  - FastAPI
  - OpenAI API
  - TMDB API
  - Python-dotenv
  - Jinja2

- Frontend:
  - HTML5
  - CSS3
  - JavaScript (ES6+)
  - Google Fonts (Poppins)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
