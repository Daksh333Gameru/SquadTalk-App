# src/config.py

# Appwrite Engine Configuration
ENDPOINT = "https://cloud.appwrite.io/v1"
PROJECT_ID = "69f49fc8003b3704da14"      # Replace with your actual Project ID
DATABASE_ID = "6a1acb7e0018388f3a07"             # Your Database ID
COLLECTION_ID = "messages"               # Your Table/Collection ID

# Base Headers required for Appwrite REST Client requests
HEADERS = {
    "X-Appwrite-Project": PROJECT_ID,
    "Content-Type": "application/json"
}
