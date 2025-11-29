import os
import json
import openai
import json_repair

# Load API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_top_5_points_positive(positive_points):
    # Prompt for extracting positive points
    positive_prompt = f"""
    Analyze the following app reviews and extract positive points mentioned by users. 

    Instructions:
    1. Identify all positive aspects, features, or experiences mentioned in the reviews
    2. Group similar positive points together (e.g., "fast loading" and "quick performance" should be grouped)
    3. Count how frequently each positive point is mentioned across all reviews
    4. Return the top 5 most frequently mentioned positive points
    5. Present each point as a complete, clear sentence
    6. Focus on specific features, benefits, or user experiences rather than generic praise

    Reviews to analyze:
    {positive_points}

    Please provide your response ONLY as a valid JSON object in the following format:
    {{
        "top_5_positive_points": [
            "Most frequent positive point as a complete sentence",
            "Second most frequent positive point as a complete sentence",
            "Third most frequent positive point as a complete sentence",
            "Fourth most frequent positive point as a complete sentence",
            "Fifth most frequent positive point as a complete sentence"
        ]
    }}

    Make sure each sentence is actionable and specific, avoiding generic statements like "the app is good" or "users love it".
    Return ONLY the JSON object, no additional text or explanation.
    """
    # Send request to OpenAI API
    response = openai.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": positive_prompt}],
    )
    # Parse repaired JSON and return extracted list
    return json_repair.loads(response.choices[0].message.content)['top_5_positive_points']


def get_top_5_points_negative(negative_points):
    # Prompt for extracting negative points
    negative_prompt = f"""
    Analyze the following app reviews and extract negative points mentioned by users. 

    Instructions:
    1. Identify all negative aspects, issues, or problems mentioned in the reviews
    2. Group similar negative points together (e.g., "slow loading" and "poor performance" should be grouped)
    3. Count how frequently each negative point is mentioned across all reviews
    4. Return the top 5 most frequently mentioned negative points
    5. Present each point as a complete, clear sentence
    6. Focus on specific issues, bugs, or user pain points rather than generic complaints

    Reviews to analyze:
    {negative_points}

    Please provide your response ONLY as a valid JSON object in the following format:
    {{
        "top_5_negative_points": [
            "Most frequent negative point as a complete sentence",
            "Second most frequent negative point as a complete sentence",
            "Third most frequent negative point as a complete sentence",
            "Fourth most frequent negative point as a complete sentence",
            "Fifth most frequent negative point as a complete sentence"
        ]
    }}

    Make sure each sentence is actionable and specific, avoiding generic statements like "the app is bad" or "users hate it".
    Return ONLY the JSON object, no additional text or explanation.
    """
    # Send request to OpenAI API
    response = openai.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": negative_prompt}],
    )
    # Parse repaired JSON and return extracted list
    return json_repair.loads(response.choices[0].message.content)['top_5_negative_points']


# Root directory containing app review folders
root_dir = "Data"
all_data = []

# Iterate through folders and process summaries
for idx, folder_name in enumerate(os.listdir(root_dir)):
    print('idx:', idx, 'len:', len(os.listdir(root_dir)), 'folder_name:', folder_name)
    folder_path = os.path.join(root_dir, folder_name)

    if os.path.isdir(folder_path):
        json_file_path = os.path.join(folder_path, "summerization.json")

        # Read existing summarization file
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Generate top 5 lists
        all_data.append({
            'positive_points': get_top_5_points_positive(data['positive_points']),
            'negative_points': get_top_5_points_negative(data['negative_points'])
        })

        # Write output file
        with open(os.path.join(folder_path, "top_5_points.json"), "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=4, ensure_ascii=False)

print('All data saved to all_data.json')
