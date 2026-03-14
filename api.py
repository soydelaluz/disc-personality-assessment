from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
from disc_core import (
    load_questions,
    load_descriptions,
    calculate_raw_scores,
    normalize_scores,
    calculate_resultant_vector,
    get_style_description,
    get_relative_percentages
)

app = FastAPI(title="DISC Assessment API")

# Load data at startup
questions = load_questions()
descriptions = load_descriptions()

class AssessmentAnswers(BaseModel):
    # Dictionary where key is question index (as string for JSON) and value is 1-5
    answers: Dict[str, int]

@app.get("/questions")
def get_questions():
    """Returns the list of DISC assessment questions."""
    return questions

@app.post("/evaluate")
def evaluate_assessment(data: AssessmentAnswers):
    """
    Evaluates the assessment answers and returns the DISC profile.
    """
    # Convert string keys back to integers for the core logic
    try:
        answers_int = {int(k): v for k, v in data.answers.items()}
    except ValueError:
        raise HTTPException(status_code=400, detail="Question indices must be integers")

    # Calculate scores
    raw_scores = calculate_raw_scores(answers_int, questions)
    normalized_scores = normalize_scores(raw_scores, questions)

    # Calculate vector and style
    resultant_angle, resultant_magnitude = calculate_resultant_vector(normalized_scores)
    style_info = get_style_description(normalized_scores, resultant_angle, descriptions)
    relative_percentages = get_relative_percentages(normalized_scores)

    return {
        "raw_scores": raw_scores,
        "normalized_scores": normalized_scores,
        "relative_percentages": relative_percentages,
        "resultant_vector": {
            "angle": resultant_angle,
            "magnitude": resultant_magnitude
        },
        "style": style_info
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
