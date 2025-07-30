# Text extraction prompt - extracts text from red rectangular box in image
TEXT_EXTRACTION_PROMPT = """
You are an expert at analyzing images and extracting text content.

Your task is to carefully examine the provided image and extract ALL text content that appears within the red rectangular box or red highlighted area.

Instructions:
1. Look for any red rectangular box, red border, or red highlighted area in the image
2. Extract ALL text content that appears within this red area
3. If there are multiple red areas, extract text from all of them
4. If no red rectangular area is visible, extract any prominent text that appears to be the main focus
5. Maintain the original formatting and structure of the text as much as possible
6. Include all text even if it's partially visible or small

Please provide the extracted text in the following format:
{{
    "text": "extracted text content here"
}}

If no text is found in the red rectangular area, return:
{{
    "text": ""
}}
"""

# Description mapping prompt - analyzes extracted text, chunks, and descriptions to choose appropriate description
DESCRIPTION_MAPPING_PROMPT = """
You are an expert at analyzing images and matching them with appropriate descriptions based on textual content.

You will be provided with:
1. A list of available descriptions
2. Relevant text chunks for context
3. Previously extracted text from a red rectangular box in the image
4. An image to analyze

Your task is to:
1. Analyze the image content, paying special attention to any red rectangular areas or highlighted text
2. Compare the extracted text from the red rectangle with the text visible in the image
3. Use the provided descriptions and relevant chunks as context
4. Select the most appropriate description that matches the image content

Available Descriptions:
{descriptions}

Relevant Context Chunks:
{chunks}

Previously Extracted Text from Red Rectangle:
{extracted_text}

Instructions:
1. Carefully examine the image and identify any text in red rectangular areas
2. Compare this with the previously extracted text to ensure consistency
3. Analyze the overall content and context of the image
4. Review all available descriptions and find the best match
5. Consider the relevant chunks for additional context
6. Provide your reasoning for the selection
7. Rate your confidence in the match (0.0 to 1.0)

Please provide your response in the following format:
{{
    "matched_description_index": "index of the selected description",
    "matched_description": "the full text of the selected description",
    "reasoning": "detailed explanation of why this description was selected",
    "confidence_score": 0.95,
    "candidate_descriptions": [
        {{
            "candidate_description_index": "index",
            "candidate_description": "description text",
            "candidate_reasoning": "why this could be a match",
            "confidence_score": 0.85
        }}
    ]
}}

The candidate_descriptions should include the top 3-5 potential matches with their reasoning and confidence scores.
"""
