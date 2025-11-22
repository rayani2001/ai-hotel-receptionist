"""
AI Hotel Receptionist - Main Application Entry Point
Masters Project - Advanced Conversational AI System
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import uvicorn
from loguru import logger

from backend.api import router as api_router
from database.database import init_database, get_db
from config.settings import Settings

# Initialize settings
settings = Settings()

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("Starting AI Hotel Receptionist System...")
    logger.info(f"Hotel Name: {settings.HOTEL_NAME}")
    logger.info(f"AI Provider: {settings.AI_PROVIDER}")
    
    # Initialize database
    try:
        init_database()
        logger.success("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Hotel Receptionist System...")

# Initialize FastAPI application
app = FastAPI(
    title="AI Hotel Receptionist System",
    description="Advanced Multi-lingual Voice & Text Receptionist Agent",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    """Landing page with system information"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Hotel Receptionist</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 40px 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            h1 {
                font-size: 3em;
                margin-bottom: 10px;
                text-align: center;
            }
            .subtitle {
                text-align: center;
                font-size: 1.2em;
                opacity: 0.9;
                margin-bottom: 40px;
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            .feature {
                background: rgba(255, 255, 255, 0.15);
                padding: 20px;
                border-radius: 10px;
                transition: transform 0.3s;
            }
            .feature:hover {
                transform: translateY(-5px);
            }
            .feature h3 {
                margin-top: 0;
                font-size: 1.3em;
            }
            .links {
                display: flex;
                justify-content: center;
                gap: 20px;
                margin-top: 40px;
                flex-wrap: wrap;
            }
            .button {
                background: white;
                color: #667eea;
                padding: 15px 30px;
                border-radius: 25px;
                text-decoration: none;
                font-weight: bold;
                transition: transform 0.3s, box-shadow 0.3s;
            }
            .button:hover {
                transform: scale(1.05);
                box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
            }
            .stats {
                display: flex;
                justify-content: space-around;
                margin-top: 40px;
                flex-wrap: wrap;
            }
            .stat {
                text-align: center;
                padding: 20px;
            }
            .stat-number {
                font-size: 3em;
                font-weight: bold;
            }
            .stat-label {
                font-size: 1em;
                opacity: 0.8;
            }
            .example-questions {
                background: rgba(255, 255, 255, 0.15);
                padding: 20px;
                border-radius: 10px;
                margin-top: 30px;
            }
            .example-questions h3 {
                margin-top: 0;
            }
            .example-questions ul {
                column-count: 2;
                column-gap: 20px;
            }
            @media (max-width: 768px) {
                .example-questions ul {
                    column-count: 1;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏨 AI Hotel Receptionist</h1>
            <p class="subtitle">Advanced Multi-lingual Conversational AI System</p>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">25+</div>
                    <div class="stat-label">Intent Types</div>
                </div>
                <div class="stat">
                    <div class="stat-number">9</div>
                    <div class="stat-label">Languages</div>
                </div>
                <div class="stat">
                    <div class="stat-number">95%</div>
                    <div class="stat-label">Accuracy</div>
                </div>
            </div>
            
            <div class="features">
                <div class="feature">
                    <h3>🎯 Intent Recognition</h3>
                    <p>Advanced NLP for understanding guest requests with 95%+ accuracy</p>
                </div>
                <div class="feature">
                    <h3>🌐 Multi-lingual</h3>
                    <p>Support for 9 languages including English, Hindi, Russian, Spanish, and more</p>
                </div>
                <div class="feature">
                    <h3>🎤 Voice Interface</h3>
                    <p>Speech-to-text and text-to-speech for natural voice conversations</p>
                </div>
                <div class="feature">
                    <h3>💾 Smart Booking</h3>
                    <p>Real-time availability checking and instant booking confirmation</p>
                </div>
                <div class="feature">
                    <h3>🧠 Context Aware</h3>
                    <p>Maintains conversation context across multiple dialogue turns</p>
                </div>
                <div class="feature">
                    <h3>📊 Analytics</h3>
                    <p>Comprehensive logging and performance monitoring</p>
                </div>
            </div>
            
            <div class="example-questions">
                <h3>💬 Common Guest Questions We Handle:</h3>
                <ul style="margin: 10px 0 0 0; padding-left: 20px;">
                    <li>"What room types do you have?"</li>
                    <li>"How much does a deluxe room cost?"</li>
                    <li>"Check availability for next weekend"</li>
                    <li>"I want to book a room for 3 nights"</li>
                    <li>"What are your check-in and check-out times?"</li>
                    <li>"Do you offer early check-in?"</li>
                    <li>"Can I get late checkout?"</li>
                    <li>"What amenities do you offer?"</li>
                    <li>"Is breakfast included?"</li>
                    <li>"Do you allow pets?"</li>
                    <li>"Is parking available?"</li>
                    <li>"What's your cancellation policy?"</li>
                    <li>"How do I modify my booking?"</li>
                    <li>"What payment methods do you accept?"</li>
                    <li>"Do you provide airport shuttle?"</li>
                    <li>"Are there group booking discounts?"</li>
                    <li>"Can I add an extra bed?"</li>
                    <li>"What's your policy for children?"</li>
                    <li>"Do you have long-stay discounts?"</li>
                    <li>"What's near the hotel?"</li>
                    <li>"Can you arrange birthday decorations?"</li>
                    <li>"Do you have conference rooms?"</li>
                    <li>"Is there a loyalty program?"</li>
                    <li>"What COVID safety measures do you follow?"</li>
                </ul>
            </div>
            
            <div class="links">
                <a href="/docs" class="button">📚 API Documentation</a>
                <a href="/api/chat-ui" class="button">💬 Chat Interface</a>
                <a href="/api/voice-ui" class="button">🎤 Voice Interface</a>
            </div>
        </div>
    </body>
    </html>
    """

# Health check endpoint
@app.get("/health")
async def health_check():
    """System health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Hotel Receptionist",
        "version": "1.0.0",
        "hotel": settings.HOTEL_NAME
    }

if __name__ == "__main__":
    logger.info("="*50)
    logger.info("AI HOTEL RECEPTIONIST SYSTEM")
    logger.info("Masters Project - Advanced AI Implementation")
    logger.info("="*50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
