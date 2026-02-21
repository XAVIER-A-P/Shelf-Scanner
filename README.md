# Shelf-Scanner 📚

### Walk out of every bookstore with a treasure in hand!

Ever found yourself staring at endless shelves in a library, book sale, or even a friend’s collection—unsure which titles are worth your time? ShelfScanner makes the choice simple. With AI-powered recommendations, it helps you uncover books that match your taste and spark your curiosity.

https://shelf-scanner-8.onrender.com


## The Production Stack
I will use FastAPI because it is asynchronous (fast), automatically generates documentation  and uses Pydantic for data validation, which prevents many runtime errors.

Component,Choice,Rationale
Backend Framework,FastAPI,The industry standard for high-performance Python AI microservices.
Database ORM,SQLModel,A modern wrapper around SQLAlchemy that combines DB definition with Pydantic validation.
Database,PostgreSQL,"Stays the same (Neon, Supabase, or RDS)."
File Storage,AWS S3 (via boto3),Standard object storage for Python apps (replaces Vercel Blob).
Caching/Queue,Redis,Used for rate limiting and response caching.
AI Clients,"openai, google-cloud-vision",Official Python SDKs.
Deployment,Docker on Render/Railway,Python apps run best in containers.
