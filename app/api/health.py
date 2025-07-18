from fastapi import APIRouter
from datetime import datetime
from loopy.data.cgm import CGMDataAccess
from app.core.config import settings
import os

router = APIRouter()


@router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "service": "loopy-api",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/ping")
async def ping():
    """Simple ping endpoint for monitoring."""
    return {"message": "pong"}


@router.get("/debug")
async def debug_info():
    """Debug endpoint to check MongoDB connection and environment."""
    try:
        # Test MongoDB connection
        with CGMDataAccess() as cgm:
            # Try to get total count of documents
            from pymongo import MongoClient
            client = MongoClient(settings.mongodb_uri)
            db = client[settings.mongodb_database]
            collection = db['entries']  # Common CGM collection name
            doc_count = collection.count_documents({})
            
            # Get one recent document to check data structure
            recent_doc = collection.find_one(sort=[('date', -1)])
            
        return {
            "status": "connected",
            "mongodb_database": settings.mongodb_database,
            "mongodb_uri_template": settings.mongodb_uri_template,
            "total_documents": doc_count,
            "recent_document_sample": {
                "sgv": recent_doc.get('sgv') if recent_doc else None,
                "date": recent_doc.get('date') if recent_doc else None,
                "dateString": recent_doc.get('dateString') if recent_doc else None
            } if recent_doc else None,
            "env_mongodb_uri_set": bool(os.environ.get('MONGODB_URI')),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "mongodb_database": settings.mongodb_database,
            "mongodb_uri_template": settings.mongodb_uri_template,
            "env_mongodb_uri_set": bool(os.environ.get('MONGODB_URI')),
            "timestamp": datetime.now().isoformat()
        }