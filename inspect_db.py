import os
import chromadb

# Path to the local database
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db_persist")

def inspect_database():
    print("=" * 60)
    print(f"Inspecting local ChromaDB at: {DB_PATH}")
    print("=" * 60)
    
    if not os.path.exists(DB_PATH):
        print(f"Error: Database directory '{DB_PATH}' does not exist yet. Start the server and ingest slides first.")
        return

    try:
        # Initialize client
        client = chromadb.PersistentClient(path=DB_PATH)
        collections = client.list_collections()
        
        if not collections:
            print("No collections found in database.")
            return
            
        print(f"Found {len(collections)} collections:")
        for col in collections:
            print(f"\n- Collection Name: {col.name}")
            
            # Get count of items
            count = col.count()
            print(f"  Item count: {count}")
            
            if count > 0:
                print("  Sample Data:")
                # Fetch all data
                data = col.get()
                for i in range(min(count, 10)):  # print up to 10 items
                    doc_id = data["ids"][i]
                    doc = data["documents"][i]
                    meta = data["metadatas"][i]
                    
                    print(f"    [{i+1}] ID: {doc_id}")
                    print(f"        Metadata: {meta}")
                    print(f"        Content: {doc[:150]}...")
                    print("-" * 40)
                    
    except Exception as e:
        print(f"Error reading database: {e}")
        print("Note: If the FastAPI server is running and locking the ChromaDB database files, you might need to stop the server to run this inspection script.")
    print("=" * 60)

if __name__ == "__main__":
    inspect_database()
