comparator_prompt = """
You are a professional website analyzer. Your task is to compare the following two websites and extract meaningful insights in a structured manner.

### Guidelines:
- Focus on the **Key Information**, **Unique Features**, **Strengths**, and **Limitations**.
- Extract relevant details concisely while maintaining accuracy.
- Format the output **strictly** as valid JSON.

### Websites:

**Website 1:**
{doc1}

**Website 2:**
{doc2}

### **Provide the analysis in the following JSON format exactly and strictly:**

{{
    "key_information": {{
        "web1": ["Summarized key point 1", "Summarized key point 2",....],
        "web2": ["Summarized key point 1", "Summarized key point 2",....]
    }},
    "unique_features": {{
        "web1": ["Unique feature 1", "Unique feature 2",....],
        "web2": ["Unique feature 1", "Unique feature 2",....]
    }},
    "content_structure": {{
        "web1": {{
            "introduction": "Brief summary of introduction",
            "mainContent": "Brief summary of main content",
            "conclusion": "Brief summary of conclusion"
        }},
        "web2": {{
            "introduction": "Brief summary of introduction",
            "mainContent": "Brief summary of main content",
            "conclusion": "Brief summary of conclusion"
        }}
    }},
    "strengths": {{
        "web1": ["Notable strength 1", "Notable strength 2",....],
        "web2": ["Notable strength 1", "Notable strength 2",....]
    }},
    "limitations": {{
        "web1": ["Limitation 1", "Limitation 2",....],
        "web2": ["Limitation 1", "Limitation 2",....]
    }}
}}

### Important Notes:
- Ensure **factual accuracy** based on the given documents.
- Use **concise yet informative** statements.
- Return only valid JSON without any extra explanations or formatting errors.

"""

cleaning_prompt = """
You are a web content processor and summarizer. Extract and rewrite the main content from this webpage while:

1. CLEANING INSTRUCTIONS:
- Remove all HTML tags, scripts, and styling
- Remove navigation elements, headers, footers, and sidebars
- Remove advertisements and promotional content
- Clean up any encoding issues or special characters
- Remove duplicate content

2. CONTENT ORGANIZATION:
- Focus on the main article or content body
- Maintain the logical flow of information
- Preserve key code snippets or technical content if present
- Keep important lists, examples, or demonstrations
- Retain any crucial data or statistics

3. OUTPUT REQUIREMENTS:
- Keep the length under 1000 words
- Preserve technical accuracy
- Maintain code examples in their original form
- Write in clear, professional language
- Keep all relevant technical terms and concepts

Content:
{content}

Clean, Organized Content:
"""

summary_template = """Summarize the content below in exactly 5 lines or fewer. Focus only on the most essential information and main points. 
Eliminate all unnecessary details, introductions, conclusions, and filler language. 
Provide your summary as plain text with no formatting, special characters, or additional commentary.

**MUST BE LESS THAN 5 LINES**

Content: {content}
"""

summarized_template="""Read the given paragraph and summarize it into exactly 5 or less key points. Follow these rules:

Extract only the most relevant and verified information.
***Keep each point clear and concise (1-2 sentences maximum).***
Focus on essential facts, avoiding opinions or unnecessary details.
Present information in order of importance.
Return the summary strictly as a list of 5 sentences pipe(|) separated without any additional information.
Format:

[Sentence 1|
Sentence 2|
Sentence 3|
Sentence 4|
Sentence 5 ]

**MUST BE 5 OR LESS THAN 5 KEY POINTS**

✅ Example 1: History
Paragraph: The Industrial Revolution, which began in the late 18th century, drastically changed the way goods were produced. It introduced mechanization, leading to mass production and urbanization. The steam engine played a crucial role in this transformation, enabling efficient transportation and manufacturing. As a result, economic growth accelerated, but poor working conditions and child labor also became widespread. Governments later introduced labor laws to improve working conditions.

Output:
[ The Industrial Revolution introduced mechanization, transforming production and urbanization.|
The steam engine significantly improved transportation and manufacturing efficiency.|
Mass production led to rapid economic growth.|
Harsh working conditions and child labor were common during this period.|
Labor laws were eventually implemented to protect workers. ]

✅ Example 2: Science
Paragraph: Photosynthesis is a process in which plants convert sunlight into energy. It takes place in chloroplasts, where chlorophyll absorbs light to trigger chemical reactions. Carbon dioxide and water are used to produce glucose and oxygen. This process is essential for sustaining life on Earth by providing oxygen and forming the base of the food chain. Without photosynthesis, most ecosystems would collapse.

Output:
[ Photosynthesis allows plants to convert sunlight into energy.|
Chlorophyll in chloroplasts absorbs light to initiate the process.|
Carbon dioxide and water are converted into glucose and oxygen.|
Photosynthesis is vital for oxygen production and supports the food chain.|
The absence of photosynthesis would lead to the collapse of ecosystems. ]

Paragraph: {paragraph}"""

