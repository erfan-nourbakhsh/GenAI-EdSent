import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os
import json
import glob

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment-latest")
model = AutoModelForSequenceClassification.from_pretrained(
    "cardiffnlp/twitter-roberta-base-sentiment-latest",
    torch_dtype=torch.float16
)

# Enable multi-GPU inference
model = torch.nn.DataParallel(model).cuda().eval()

def sentiment(text):
    """Return only positive and negative sentiment percentages."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    inputs = {k: v.cuda() for k, v in inputs.items()}

    with torch.no_grad():
        probs = torch.nn.functional.softmax(model(**inputs).logits, dim=-1)[0]

    return {
        "negative": round(probs[0].item() * 100, 1),
        "positive": round(probs[2].item() * 100, 1)
    }

def sentiment_batch(texts, batch_size=32):
    """Batch sentiment analysis returning only positive + negative."""
    results = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        # Clean missing or non-string inputs
        cleaned_batch = [
            "[empty]" if text in ["", None] else str(text)
            for text in batch
        ]

        inputs = tokenizer(
            cleaned_batch,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )
        inputs = {k: v.cuda() for k, v in inputs.items()}

        with torch.no_grad():
            probs = torch.nn.functional.softmax(model(**inputs).logits, dim=-1)

        for j in range(len(batch)):
            results.append({
                "negative": round(probs[j][0].item() * 100, 1),
                "positive": round(probs[j][2].item() * 100, 1),
            })

    return results

def process_reviews():
    """Process all review JSON files and save sentiment results."""
    json_files = glob.glob("Data/*/*.json")
    print(f"Found {len(json_files)} JSON files")

    for json_file in json_files:
        print(f"Processing: {json_file}")

        try:
            # Load file
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Ensure 'reviews' exists
            if "reviews" not in data:
                print(f"No 'reviews' key in {json_file}")
                continue

            reviews = data["reviews"]
            print(f"Found {len(reviews)} reviews")

            batch_size = 32

            # Process in batches
            for i in range(0, len(reviews), batch_size):
                batch_reviews = reviews[i:i + batch_size]
                contents = [review.get("content", "") for review in batch_reviews]

                sentiments = sentiment_batch(contents, batch_size)

                # Attach sentiment
                for j, review in enumerate(batch_reviews):
                    review["sentiment"] = sentiments[j]

                print(f"Processed {min(i + batch_size, len(reviews))}/{len(reviews)}")

            # Write results
            folder_path = os.path.dirname(json_file)
            output_file = os.path.join(folder_path, "data_sentiment.json")

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"Saved: {output_file}")

        except Exception as e:
            print(f"Error processing {json_file}: {e}")

if __name__ == "__main__":
    print("Starting sentiment analysis on review data...")
    process_reviews()
    print("Done!")
