import json
import os
from groq import Groq
from dotenv import load_dotenv
import re
from typing import List, Dict

load_dotenv()

def clean_json_response(response_text):
    response_text = re.sub(r"```json\s*|\s*```", "", response_text.strip())
    return response_text

def evaluate(data):
    prompt = f"""
    Given the following personality trait scores, generate a structured JSON response strictly in the format below:

    **Output Format:**  
    A list of lists, where each element follows this structure:
    
    [
        "Trait Name",
        "Score in percentage (rounded, e.g., '75%')",
        "A very short description of the trait based on the score.",
        {{
            "Facet Name 1": "Very short explanation of the facet based on the score",
            "Facet Name 2": "Very short explanation of the facet based on the score",
            ...
        }}
    ]

    **Trait-Specific Facets:**  
    Each trait must include only its predefined facets. Do not add, rename, or omit facets.

    - **Extroversion vs Introversion**  
      - Facets: "Gregariousness", "Assertiveness", "Activity", "Excitement-Seeking", "Positive Emotions", "Warmth"

    - **Agreeableness vs Antagonism**
        - Facets: "Trust", "Straightforwardness", "Altruism", "Compliance", "Modesty", "Tender-Mindedness"
    
    - **Conscientiousness vs Lack Of Direction**
        - Facets: "Competence", "Order", "Dutifulness", "Achievement-Striving", "Self-Discipline", "Deliberation"

    - **Neuroticism vs Emotional Stability**
        - Facets: "Anxiety", "Angry Hostility", "Depression", "Self-Consciousness", "Impulsiveness", "Vulnerability"

    - **Openness vs Closeness**  
        - Facets: "Ideas", "Fantasy", "Aesthetic", "Actions", "Feelings", "Values", "Openness To Experience"

    **Instructions for the Model:**
    - **Each trait should contain only the facets listed above**. Do not mix facets from different traits or invent new ones.
    - Generate descriptions for each personality trait based on the given score. Higher scores indicate stronger presence of the trait.
    - Provide **concise but insightful** explanations of the facets related to each trait.
    - If a facet does not have enough information, return `"N/A"` instead of omitting it.
    - Strictly follow the JSON format with no extra explanations, markdown, or commentary.

    **Trait Scores for Evaluation:**  
    {json.dumps(data, indent=4)}

    **Output must be valid JSON with no extra text.**
    """

    client = Groq(
        api_key=os.getenv("GROQ_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[{
            "role": "user",
            "content": prompt,
        }],
        # model="llama-3.3-70b-specdec",
        model="llama-3.3-70b-versatile",
    )

    response_text = chat_completion.choices[0].message.content

    cleaned_response = clean_json_response(response_text)

    try:
        structured_data = json.loads(cleaned_response)
    except json.JSONDecodeError:
        raise ValueError("Groq response is not in valid JSON format.")

    return structured_data

def explain_code(code):
    prompt = f"""
    Explain the following Python code in detail. Describe its purpose, logic, and how it works in simple terms. Remember not to add your comments or explanation.
    This is the incoming code you have to explain: {code}.
    """
    try:
        client = Groq(
            api_key = os.getenv("GROQ_API_KEY"),
        )

        chat_completion = client.chat.completions.create(
            messages=[{
                "role":"user",
                "content":prompt,
            }],
            model="gemma2-9b-it",
        )
        return chat_completion.choices[0].message.content
    
    except Exception as e:
        return{
            "error":f"An error occurred: {str(e)}"
        }

def explain_engagement_metric(engagement_data):
    explanations = {}

    for metric_name, value in engagement_data.items():
        prompt = f"""
        Generate a structured and well-formatted analytical report of an interviewer based on the following engagement metric. The report should be **concise, professional, and formatted in sections** that clearly highlight key details. The response should be structured with the following sections:

        **Engagement Metric Analysis Report**  
        - **Metric Name**: {metric_name}  
        - **Metric Value**: {value}%  

        ### **1. Definition**  
        Clearly define what the metric represents in the context of interview analysis.  

        ### **2. Interpretation of {value}%**  
        Analyze what it means to have a value of {value}% for this metric. Provide insights into whether this is a strong, average, or weak score, and what actions could be taken for improvement.  

        ### **3. Contextual Insights & Recommendations**  
        Offer practical insights or suggestions based on this metric value. If applicable, compare it with industry benchmarks or ideal ranges.  

        ### **4. Summary**  
        Provide a brief summary highlighting the key takeaways from this report.  

        Ensure that the output is **strictly formatted**, follows a structured approach, and does not include unnecessary comments or additional explanations beyond the structured content. The language should be **clear, formal, and suitable for direct inclusion in a professional PDF report**.
        """
        try:
            client = Groq(
                api_key=os.getenv("GROQ_API_KEY"),
            )

            chat_completion = client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": prompt,
                }],
                model="llama-3.1-8b-instant",
            )

            explanations[metric_name] = chat_completion.choices[0].message.content.strip()

        except Exception as e:
            explanations[metric_name] = f"Error: {str(e)}"

    return explanations

def explain_diversity_metric(metric):
    explanation = {}

    prompt = f"""
    Generate a structured and well-formatted analytical report based on the diversity and distribution of interview questions. The report should be **concise, professional, and formatted in sections** that clearly highlight key details. The response should be structured with the following sections:

    **Interview Question Diversity Analysis Report**  
    - **Diversity Score**: {metric["diversity_score"]}  
    - **Cluster Counts**: {metric["cluster_counts"]}  

    ### **1. Definition**  
    The diversity score measures the range and variability of interview questions presented to candidates. A higher diversity score (closer to 100) indicates that the interview includes a well-balanced mix of question types, covering various competencies, skills, and experiences. A lower score (closer to 1 or negative) suggests that the questions are highly repetitive, focusing on a narrow range of topics.

    ### **2. Interpretation of Diversity Score: {metric["diversity_score"]}**  
    A diversity score of {metric["diversity_score"]} suggests that:  

    - If the score is **high**, the interview covers a broad range of topics, ensuring a comprehensive evaluation of the candidate's abilities.  
    - If the score is **low**, the questions may be too repetitive, focusing on a limited area and potentially overlooking key competencies.  
    - A **moderate score** suggests that while some variation exists, there may still be an imbalance in the type of questions asked.  

    ### **3. Cluster Distribution & Question Analysis**  
    The interview questions are distributed across the following categories:  

    |  Question Category (Cluster ID)  |  Number of Questions  |
    {chr(13).join([f"| {key} | {value} |" for key, value in metric["cluster_counts"].items()])}  

    {chr(13).join([f"- Cluster **{key}** contains {value} question(s), likely focusing on a specific area of evaluation." for key, value in metric["cluster_counts"].items()])}  

    **Key Observations:**  
    - If one cluster has significantly more questions than others, it suggests that the interview is **skewed toward a particular topic**.  
    - A balanced distribution across clusters implies that the interview **assesses candidates across multiple dimensions**.  

    ### **4. Contextual Insights & Recommendations**  
    - If the diversity score is low, **consider incorporating a wider range of questions**, including technical, behavioral, and situational prompts.  
    - If one category dominates, ensure that the interview includes **questions that assess soft skills, problem-solving abilities, and adaptability** rather than focusing solely on technical proficiency.  

    ### **5. Summary**  
    The diversity score of {metric["diversity_score"]} indicates the overall balance of question types in the interview. The cluster distribution provides insights into the dominant question categories, revealing potential areas for improvement. To create a more **holistic and fair interview**, incorporating a diverse mix of questions across different competencies is recommended.  

    Ensure that the output is **strictly formatted**, follows a structured approach, and does not include unnecessary comments or additional explanations beyond the structured content. The language should be **clear, formal, and suitable for direct inclusion in a professional PDF report**.
    """
    try:
        client = Groq(
            api_key=os.getenv("GROQ_API_KEY"),
        )

        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": prompt,
            }],
            model="llama-3.1-8b-instant",
        )

        explanation["report"] = chat_completion.choices[0].message.content.strip()

    except Exception as e:
        explanation["report"] = f"Error: {str(e)}"

    return explanation


def explain_tone(neutral_tone_percentage, friendly_tone_percentage, authoritative_tone_percentage):
    if any(p < 0 or p > 100 for p in [neutral_tone_percentage, friendly_tone_percentage, authoritative_tone_percentage]):
        return "Error: Tone percentages must be between 0 and 100."

    prompt = f"""
    Generate a structured and well-formatted analytical report based on the following interview engagement metric. 
    The report should be **concise, professional, and formatted in sections** that clearly highlight key details. 
    The response should be structured with the following sections:

    **Interview Tone Analysis Report**  
    - **Metric Name**: Interviewer's Tone Distribution  
    - **Metric Values**:  
      - Neutral Tone: {neutral_tone_percentage}%  
      - Friendly Tone: {friendly_tone_percentage}%  
      - Authoritative Tone: {authoritative_tone_percentage}%  

    ### **1. Definition**  
    This report evaluates the tone used by the interviewer when interacting with the interviewee. It categorizes the tone into three key dimensions:  
    - **Neutral Tone**: A balanced and impartial approach without strong emotional engagement.  
    - **Friendly Tone**: A warm, encouraging, and positive manner that may create a relaxed atmosphere.  
    - **Authoritative Tone**: A firm and assertive approach, which may indicate control or dominance in conversation.  

    ### **2. Interpretation of the Current Tone Distribution**  
    - **Neutral Tone ({neutral_tone_percentage}%)**: This indicates whether the interviewer maintained an unbiased stance throughout the interview. A **0% score** suggests that no neutral tone was observed, meaning the interviewer adopted either a friendly or authoritative tone at all times.  
    - **Friendly Tone ({friendly_tone_percentage}%)**: With a **{friendly_tone_percentage}% score**, the interviewer used a friendly tone extensively, which could imply a welcoming and positive attitude but may also raise concerns about a potential lack of formality or structured control.  
    - **Authoritative Tone ({authoritative_tone_percentage}%)**: A **{authoritative_tone_percentage}% score** indicates the extent to which the interviewer exhibited a strong authoritative presence, affecting the level of control and professionalism in the conversation.  

    ### **3. Contextual Insights & Recommendations**  
    - The absence of a **neutral tone** suggests that the interviewer did not maintain an impartial or balanced demeanor, which might indicate a tendency to engage with interviewees in a more personal or informal manner rather than a strictly professional way.  
    - A **high friendly tone** can contribute to a positive candidate experience, but if not balanced, it may create inconsistencies in how different interviewees are treated.  
    - The lack of an authoritative tone suggests that the interviewer avoids a strict or commanding approach, which can foster open communication but might reduce perceived professionalism in formal settings.  
    - To enhance fairness and consistency, the interviewer should aim for a more **balanced tone distribution**, incorporating neutral engagement where necessary to ensure objective evaluation and avoid unintended bias.  

    ### **4. Summary**  
    This analysis highlights that the interviewer exhibited a **{friendly_tone_percentage}% friendly tone**, with **{neutral_tone_percentage}% neutrality** and **{authoritative_tone_percentage}% authority**. While this can contribute to a positive candidate experience, it is essential to ensure that **all interviewees are treated with equal levels of friendliness** to avoid unintended favoritism or bias. A more **balanced tone incorporating neutrality and structured authority** where appropriate can improve the overall fairness and consistency of the interview process.  

    Ensure that this analysis remains strictly structured and formatted for inclusion in a professional report. Avoid any extraneous commentary beyond the specified sections. Do not add any additional explanation or comments.
    """
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
        )
        return chat_completion.choices[0].message.content.strip()

    except Exception as e:
        return f"Error: {str(e)}"

def explain_bias(bias_result: dict) -> str:
    try:
        candidate_name = list(bias_result.keys())[0]
        result = bias_result[candidate_name]

        total_questions = result.get("total_questions", 0)
        avg_sentiment = result.get("avg_sentiment", 0.0)
        gender_bias_count = result.get("gender_bias_count", 0)
        race_bias_count = result.get("race_bias_count", 0)
        age_bias_count = result.get("age_bias_count", 0)
        topic_diversity = result.get("topic_diversity", 0)

        prompt = f"""
        Generate a structured and well-formatted analytical report of the interviewer who is taking the interview based on the following interview bias metrics. The report should be **concise, professional, and formatted in sections** that clearly highlight key details. The response should be structured with the following sections:

        **Interview Bias Analysis Report**  
        - **Candidate Name**: {candidate_name}  
        - **Total Questions Asked**: {total_questions}  
        - **Average Sentiment Score**: {avg_sentiment}  
        - **Gender Bias Count**: {gender_bias_count}  
        - **Race Bias Count**: {race_bias_count}  
        - **Age Bias Count**: {age_bias_count}  
        - **Topic Diversity Score**: {topic_diversity}  

        ### **1. Definition of Metrics**  
        Provide a clear definition of each metric and its significance in assessing bias in an interview.  

        ### **2. Interpretation of the Metrics**  
        Analyze what each metric value suggests about the interview process. Indicate whether these values reflect fairness, neutrality, or potential bias.  

        ### **3. Contextual Insights & Recommendations**  
        Offer practical insights and recommendations to mitigate bias if detected. If applicable, compare these metrics with best practices or industry standards.  

        ### **4. Summary & Final Assessment**  
        Provide a well-structured summary highlighting the key takeaways from this report, ensuring clarity in evaluating interview fairness.  

        Ensure that the output is **strictly formatted**, follows a structured approach, and is **suitable for direct inclusion in a professional PDF report without adding any additional comments or additional explanation**.
        """

        client = Groq(
            api_key=os.getenv("GROQ_API_KEY"),
        )

        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": prompt,
            }],
            model="llama-3.1-8b-instant",
        )

        return chat_completion.choices[0].message.content

    except Exception as e:
        return f"Error generating content for analyze bias api: {str(e)}"


def classified_question_explanation(questions_data: list) -> Dict[str, List[Dict[str, str]]]:
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        prompt = """
        Given the following questions and their assigned categories, explain why each question falls under its respective category.
        Ensure your response follows a strict JSON format:
        
        {
            "explanations": [
                {"question": "question_text", "category": "category_name", "explanation": "brief_reasoning"}
            ]
        }
        
        Do NOT change the assigned category. Only provide the explanation. Keep the response concise.
        
        Questions and Categories:
        """
        for item in questions_data:
            prompt += f'\n- Question: "{item["question"]}"\n  Category: {item["category"]}'

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt.strip()}],
            model="llama-3.1-8b-instant",
        )
        
        response_text = chat_completion.choices[0].message.content.strip()

        try:
            response_data = json.loads(response_text)
        except json.JSONDecodeError:
            return {"error": "Failed to parse Groq response as JSON."}

        explanation_map = {item["question"]: item["explanation"] for item in response_data.get("explanations", [])}

        for item in questions_data:
            item["explanation"] = explanation_map.get(item["question"], "No explanation available")

        return {"questions": questions_data}

    except Exception as e:
        return {"error": f"Error generating content for classify questions API: {str(e)}"}
    

def explain_clarity(analysis: dict) -> str:
    try:
        prompt = """You are an expert in text clarity analysis. Your task is to **ONLY format, structure and explain a little bit** for the given interview clarity report.  
Do **NOT** add explanations, insights, recommendations, or any additional content beyond the provided data.  
Format the output aesthetically using sections, bold headers, and bullet points to make it visually appealing for a PDF.

**📌 Interview Clarity Report Summary**  

🔹 **Total Questions:** {Total Questions}  
🔹 **Total Sentences:** {Total Sentences}  
🔹 **Total Words:** {Total Words}  
🔹 **Average Readability Score:** {Average Readability Score}  
🔹 **Readability Assessment:** {Readability}  
🔹 **Total Grammar Issues:** {Total Grammar Issues}  
🔹 **Grammar Clarity:** {Grammar Clarity}  
🔹 **Complex Sentences:** {Complex Sentences}  
🔹 **Syntactic Complexity:** {Syntactic Complexity}  
🔹 **Vague Words Detected:** {Vagueness Detected}  

---

### **📖 Detailed Question Analysis**  

""".format(**analysis)

        for q_key, q_analysis in analysis.get("Question Analysis", {}).items():
            prompt += f"""🔹 **{q_key}**  
- 📏 **Word Count:** {q_analysis.get('Word Count', 0)} ({q_analysis.get('Conciseness', 'Unknown')})  
- 📖 **Readability Score:** {q_analysis.get('Readability Score', 0)} ({q_analysis.get('Readability', 'Unknown')})  
- ✍️ **Grammar Issues:** {q_analysis.get('Grammar Issues', 0)} ({q_analysis.get('Grammar Clarity', 'Unknown')})  
- 🏗️ **Syntactic Complexity:** {q_analysis.get('Syntactic Complexity', 'Unknown')}  
- ❓ **Vague Words:** {q_analysis.get('Vagueness Detected', 'None')}  

"""

        prompt += """  
---
🎯 **Conclusion**  
This section should **only summarize the provided clarity metrics** without any additional explanation.  
Do not add new recommendations, suggestions, or commentary. Keep it strictly factual.  
"""

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": prompt,
            }],
            model="llama-3.1-8b-instant",
        )

        return chat_completion.choices[0].message.content

    except Exception as e:
        return f"Error generating content for clarity analysis: {str(e)}"
