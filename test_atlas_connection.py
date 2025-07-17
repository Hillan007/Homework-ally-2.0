# MongoDB Atlas Connection Test
# Run this script to test your MongoDB Atlas connection

from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def test_mongodb_connection():
    """Test MongoDB Atlas connection"""
    try:
        # Get connection string from environment
        mongodb_url = os.getenv("MONGODB_URL")
        database_name = os.getenv("DATABASE_NAME", "homeally")
        
        print(f"🔗 Attempting to connect to: {mongodb_url[:20]}...")
        
        # Create MongoDB client
        client = MongoClient(mongodb_url, serverSelectionTimeoutMS=5000)
        
        # Test the connection
        client.admin.command('ping')
        print("✅ MongoDB Atlas connection successful!")
        
        # Get database
        db = client[database_name]
        print(f"📁 Connected to database: {database_name}")
        
        # List collections
        collections = db.list_collection_names()
        print(f"📝 Collections found: {collections}")
        
        # Test a simple operation
        users_collection = db.users
        user_count = users_collection.count_documents({})
        print(f"👥 Total users in collection: {user_count}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB Atlas connection failed: {e}")
        return False

if __name__ == "__main__":
    test_mongodb_connection()
