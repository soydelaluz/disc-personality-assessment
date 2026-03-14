import numpy as np
import math
import json

def load_questions(filepath="questions.json"):
    with open(filepath, "r") as f:
        return json.load(f)

def load_descriptions(filepath="disc_descriptions.json"):
    with open(filepath, "r") as f:
        return json.load(f)

def calculate_raw_scores(answers, questions):
    """
    answers: dict of {question_index: score (1-5)}
    questions: list of question objects
    """
    raw_score = {"D": 0, "I": 0, "S": 0, "C": 0}
    for i, answer in answers.items():
        q = questions[i]
        for style in ["D", "I", "S", "C"]:
            raw_score[style] += q["mapping"][style] * (answer - 3)
    return raw_score

def normalize_scores(scores, questions):
    max_possible_scores = {style: 0.0 for style in ["D", "I", "S", "C"]}
    min_possible_scores = {style: 0.0 for style in ["D", "I", "S", "C"]}

    for q in questions:
        for style in ["D", "I", "S", "C"]:
            mapping = q["mapping"][style]
            if mapping >= 0:
                max_contribution = mapping * 2  # Max when (answer - 3) = +2
                min_contribution = mapping * (-2)  # Min when (answer - 3) = -2
            else:
                max_contribution = mapping * (-2)  # Max when (answer - 3) = -2
                min_contribution = mapping * 2  # Min when (answer - 3) = +2

            max_possible_scores[style] += max_contribution
            min_possible_scores[style] += min_contribution

    normalized_scores = {}
    for style in ["D", "I", "S", "C"]:
        score = max(min(scores[style], max_possible_scores[style]), min_possible_scores[style])
        score_range = max_possible_scores[style] - min_possible_scores[style]
        if score_range == 0:
            normalized_scores[style] = 50.0
        else:
            normalized_scores[style] = ((score - min_possible_scores[style]) / score_range) * 100
            normalized_scores[style] = max(0, min(normalized_scores[style], 100))
    return normalized_scores

def calculate_resultant_vector(normalized_score):
    categories = ["D", "I", "S", "C"]
    angles = [7 * np.pi / 4, np.pi / 4, 3 * np.pi / 4, 5 * np.pi / 4]

    scaled_scores = {style: score / 100 for style, score in normalized_score.items()}

    x_components = []
    y_components = []
    for i, style in enumerate(categories):
        angle = angles[i]
        magnitude = scaled_scores[style]
        x_components.append(magnitude * np.cos(angle))
        y_components.append(magnitude * np.sin(angle))

    total_x = sum(x_components)
    total_y = sum(y_components)

    resultant_magnitude = np.sqrt(total_x**2 + total_y**2)
    resultant_angle = np.arctan2(total_y, total_x)

    return resultant_angle, resultant_magnitude

def get_style_description(normalized_score, resultant_angle, disc_descriptions):
    resultant_degrees = math.degrees(resultant_angle)
    if resultant_degrees < 0:
        resultant_degrees += 360

    style_ranges = {
        "D": (315, 337.5),
        "DC": (270, 315),
        "DI": (337.5, 360),
        "I": (45, 67.5),
        "ID": (0, 45),
        "IS": (67.5, 90),
        "S": (135, 157.5),
        "SI": (90, 135),
        "SC": (157.5, 180),
        "C": (225, 247.5),
        "CS": (180, 225),
        "CD": (247.5, 270)
    }

    if all(score == list(normalized_score.values())[0] for score in normalized_score.values()):
        return {
            "title": "Estilo Equilibrado",
            "description": "Tus respuestas indican una personalidad equilibrada, en la que no muestras una preferencia clara por ningún estilo DISC específico.",
            "strengths": "N/A",
            "challenges": "N/A"
        }

    for style, (start_angle, end_angle) in style_ranges.items():
        if start_angle <= resultant_degrees < end_angle or (start_angle == 337.5 and resultant_degrees == 0):
            return disc_descriptions["single"][style]

    return {
        "title": "Estilo Equilibrado",
        "description": "Tus respuestas indican una personalidad equilibrada sin una preferencia clara por ningún estilo DISC específico.",
        "strengths": "N/A",
        "challenges": "N/A"
    }

def get_relative_percentages(normalized_score):
    total_normalized = sum(normalized_score.values())
    relative_percentages = {}
    for style, score in normalized_score.items():
        if total_normalized == 0:
            relative_percentages[style] = 0
        else:
            relative_percentages[style] = (score / total_normalized) * 100
    return relative_percentages
