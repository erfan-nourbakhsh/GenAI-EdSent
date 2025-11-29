import os                     # Imports the OS module to access environment variables
import openai                # Imports the OpenAI Python library

openai.api_key = os.getenv("OPENAI_API_KEY")   # Retrieves your OpenAI API key from environment variables

# Your prompt
prompt = """
You are a professional data analyst extracting explicit pros and cons from user reviews.

TASK:
1. Read ALL user reviews completely before beginning analysis
2. Extract only genuine positive and negative points that users explicitly mention
3. Focus on functional aspects, features, usability, and user experience
4. Ignore generic praise/criticism without specific details

EXTRACTION RULES:
- ONLY extract points that describe specific app features, functionality, or user experience
- EXCLUDE vague comments like "good," "awesome," "bad" unless they include specific reasons
- EXCLUDE duplicate or nearly identical points
- INCLUDE user complaints about limitations, bugs, pricing, or missing features
- INCLUDE user praise for specific features, ease of use, or helpful functionality

KEYWORD STRUCTURE REQUIREMENTS:
- Each point must be a concise keyword phrase (2-6 words)
- Use clear, descriptive terms that capture specific features or issues
- No complete sentences, articles (a, an, the), or conjunctions
- Use present tense verbs when needed
- Be specific and actionable, not vague
- Use consistent formatting and terminology

COMMENTS TO ANALYZE:
{comments}

OUTPUT FORMAT:
Return only a valid JSON object with this exact structure:
{{
    "positive_points": [
        "Keyword phrases about positive aspects"
    ],
    "negative_points": [
        "Keyword phrases about negative aspects"
    ]
}}
"""
# Defines a multi-line prompt explaining tasks, rules, and output format for the model

# Call GPT-4o
response = openai.chat.completions.create(      # Sends a chat completion request to OpenAI API
    model="gpt-4o",                             # Specifies the GPT-4o model
    messages=[
        {"role": "user", "content": prompt},    # Provides the prompt as a user message
    ],
    temperature=0.0,                            # Ensures deterministic, consistent output
)

# Print the model's response
print(response.choices[0].message.content)      # Prints the generated JSON result from the model
