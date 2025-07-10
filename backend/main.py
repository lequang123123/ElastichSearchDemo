import uvicorn
import os
from app.database import init_db
from app.api import app

if __name__ == "__main__":
    # Initialize database tables
    init_db()
    
    # Get port from environment or default to 8000
    port = int(os.getenv("PORT", 8000))
    
    # Run the application
    uvicorn.run(
        "app.api:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    ) 