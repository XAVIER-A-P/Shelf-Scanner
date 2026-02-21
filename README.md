# Shelf-Scanner 📚

### Walk out of every bookstore with a treasure in hand!

Ever found yourself staring at endless shelves in a library, book sale, or even a friend’s collection—unsure which titles are worth your time? ShelfScanner makes the choice simple. With AI-powered recommendations, it helps you uncover books that match your taste and spark your curiosity.

https://shelf-scanner-8.onrender.com


## 🛠 Technology Stack
Frontend: FastAPI with Jinja2 Templates and HTMX  
Backend: FastAPI, PostgreSQL SQLModel, Redis (rate limiting and response caching)  
AI Services: OpenAI GPT-4o for recommendations and descriptions  
Deployment: Docker on Render  

## 📁 Project Architecture

shelf-scanner-py/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point & API Routes
│   ├── models.py            # Database Schema (SQLModel)
│   ├── config.py            # Environment variables settings
│   ├── dependencies.py      # DB sessions & User tracking
│   └── services/
│       ├── __init__.py
│       ├── vision.py        # GPT-4o & Google Vision Logic
│       ├── storage.py       # AWS S3 Logic
│       └── recommendations.py # Recommendation Logic
├── static/
│   ├── styles.css
│   └── js/                  # Optional frontend scripts
├── templates/
│   ├── base.html            # The shell (imports Tailwind/HTMX)
│   ├── index.html           # The camera scanner UI
│   └── components/
│       ├── book_list.html   # The results partial
│       └── loading.html     # The spinner
├── Dockerfile               # Production container definition
├── requirements.txt         # Python dependencies
└── .env                     # Secrets (Gitignored)          # Secrets (Gitignored)
