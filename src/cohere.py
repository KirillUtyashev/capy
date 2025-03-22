import cohere
import json
import random

# Replace with your actual API key
API_KEY = "iAs2cuHYp8H7mbFQDFT9jrNrqeKezoJWrF8h0IjL"
TOPIC= "ancient greece"

co = cohere.Client(API_KEY)


def generate_quiz_question(num_incorrect=3, existing_questions=set()):
    """Generates a unique multiple-choice question for the defined topic."""

    while True:
        prompt = f"""
        Generate a multiple-choice question based on the topic "{TOPIC}".
        Provide a correct answer and {num_incorrect} incorrect answers.
        Format: 
        Question: <question>
        Correct: <correct_answer>
        Incorrect: <incorrect_answer_1>, <incorrect_answer_2>, <incorrect_answer_3>
        """

        response = co.generate(
            model="command-r-plus",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7
        )

        # Parse the response
        lines = response.generations[0].text.strip().split("\n")
        if len(lines) < 3:
            continue  # Ignore incomplete responses

        question = lines[0].replace("Question: ", "").strip()
        correct_answer = lines[1].replace("Correct: ", "").strip()
        incorrect_answers = [ans.strip() for ans in lines[2].replace("Incorrect: ", "").split(",")]

        # Ensure uniqueness
        if question not in existing_questions:
            existing_questions.add(question)
            return {
                "question": question,
                "correct": correct_answer,
                "incorrect": incorrect_answers
            }


def generate_quiz(num_questions=5):
    """Generates a unique quiz with the specified number of questions."""

    quiz_data = []
    existing_questions = set()

    while len(quiz_data) < num_questions:
        question_data = generate_quiz_question(existing_questions=existing_questions)
        if question_data:  # Add only if a valid question was generated
            quiz_data.append(question_data)

    # Save as JSON
    filename = f"{TOPIC.replace(' ', '_')}_quiz.json"
    with open(filename, "w") as f:
        json.dump(quiz_data, f, indent=4)

    print(f"Quiz saved as {filename}")


generate_quiz(num_questions=5)


