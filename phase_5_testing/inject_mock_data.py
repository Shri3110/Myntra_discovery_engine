import os
import chromadb

def inject_mock_data():
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'phase_2_processing', 'chroma_db'))
    client = chromadb.PersistentClient(path=db_path)
    
    # Create or get collection
    collection = client.get_or_create_collection(name="myntra_feedback")
    
    mock_reviews = [
        {"id": "mock_1", "text": "I really love the style of this jacket, but I'm just not sure if a Medium will be too tight on the shoulders. Waiting for more photo reviews.", "source": "Reddit", "category": "Sizing/Fit Uncertainty", "intent_level": "High Intent"},
        {"id": "mock_2", "text": "Added to wishlist. It's between this and a similar dress on Ajio. I need to check the return policy first.", "source": "YouTube", "category": "Comparison Paralysis", "intent_level": "Medium Intent"},
        {"id": "mock_3", "text": "I want to buy this so bad but my size is out of stock! Pls restock size L.", "source": "App Store", "category": "High Friction", "intent_level": "High Intent"},
        {"id": "mock_4", "text": "Looks okay but I'm waiting to see if my sister approves of the color before I checkout.", "source": "Reddit", "category": "Waiting for Validation", "intent_level": "Low Intent"},
        {"id": "mock_5", "text": "The jeans look great on the model but I'm 5'2 and worried they will be way too long. Wish they had petite sizing.", "source": "Reddit", "category": "Sizing/Fit Uncertainty", "intent_level": "High Intent"},
        {"id": "mock_6", "text": "Saved it for later. Honestly just using the wishlist as a mood board at this point lol.", "source": "YouTube", "category": "Low Intent/Browsing", "intent_level": "Low Intent"},
        {"id": "mock_7", "text": "Is this fabric breathable? I wishlisted it but I can't tell from the photos if it will be too hot for summer.", "source": "Reddit", "category": "Product Info Missing", "intent_level": "Medium Intent"},
        {"id": "mock_8", "text": "Love the shoes! But I don't know if UK 7 or UK 8 is better since the reviews say it runs small.", "source": "App Store", "category": "Sizing/Fit Uncertainty", "intent_level": "High Intent"},
        {"id": "mock_9", "text": "Putting this in the wishlist until I figure out if I can find a cheaper dupe somewhere else.", "source": "Reddit", "category": "Comparison Paralysis", "intent_level": "Medium Intent"},
        {"id": "mock_10", "text": "The checkout process was glitching so I just wishlisted it and closed the app. Will try again tomorrow.", "source": "App Store", "category": "High Friction", "intent_level": "High Intent"}
    ]
    
    texts = []
    metadatas = []
    ids = []
    
    for item in mock_reviews:
        texts.append(item["text"])
        metadatas.append({
            "source": item["source"],
            "category": item["category"],
            "intent_level": item["intent_level"]
        })
        ids.append(item["id"])
        
    collection.add(
        documents=texts,
        metadatas=metadatas,
        ids=ids
    )
    print(f"Successfully injected {len(mock_reviews)} categorized mock reviews into ChromaDB.")

if __name__ == "__main__":
    inject_mock_data()
