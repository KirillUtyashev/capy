import pygame
import cohere
import random
import sys

# ==================== CONFIGURATION ====================
API_KEY = "iAs2cuHYp8H7mbFQDFT9jrNrqeKezoJWrF8h0IjL"  # Replace with your Cohere API Key
TOPIC = "Highschool math"

# ==================== INITIALIZE COHERE ====================
co = cohere.Client(API_KEY)

# ==================== PYGAME SETUP ====================
pygame.init()
WIDTH, HEIGHT = 800, 600
WHITE, BLACK, BLUE, GREEN, RED = (255, 255, 255), (0, 0, 0), (100, 100, 255), (0, 200, 0), (200, 0, 0)

main_screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("AI Quiz Game")

font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)


# ==================== QUESTION GENERATION ====================
def generate_question(similar_to=None):
    topic_prompt = f"A multiple-choice question about '{TOPIC}'" if not similar_to else f"A multiple-choice question related to '{similar_to}', but with other values/details."
    prompt = f"""
    Generate a multiple-choice question about "{topic_prompt}".
    Format:
    Question: <question>
    Correct: <correct>
    Incorrect: <incorrect_1>, <incorrect_2>, <incorrect_3>
    """
    response = co.generate(model="command-r-plus", prompt=prompt, max_tokens=150, temperature=0.7)
    lines = response.generations[0].text.strip().split("\n")
    if len(lines) < 3:
        return generate_question(similar_to)
    question = lines[0].replace("Question: ", "").strip()
    correct_answer = lines[1].replace("Correct: ", "").strip()
    incorrect_answers = [ans.strip() for ans in lines[2].replace("Incorrect: ", "").split(",")]
    return {"question": question, "correct": correct_answer, "incorrect": incorrect_answers}


def explain_mistake(question, correct_answer, user_answer):
    prompt = f"""
    The user answered a multiple-choice question incorrectly.
    Question: {question}
    User's incorrect answer: {user_answer}
    Correct answer: {correct_answer}
    Explain why the user was wrong.
    """
    response = co.generate(model="command-r-plus", prompt=prompt, max_tokens=100, temperature=0.7)
    return response.generations[0].text.strip()


# ==================== QUIZ LOGIC ====================
current_question = None
previous_wrong_question = None


def show_question():
    global current_question, previous_wrong_question

    if previous_wrong_question:
        current_question = generate_question(previous_wrong_question)
    else:
        current_question = generate_question()

    question_window = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("Quiz Question")

    question_text = current_question["question"]
    correct_answer = current_question["correct"]
    options = [correct_answer] + current_question["incorrect"]
    random.shuffle(options)

    explanation = None
    answered = False

    while True:
        question_window.fill(WHITE)
        draw_text(question_window, question_text, 50, 50, 500, BLACK, font)
        buttons = []
        for i, option in enumerate(options):
            btn_rect = pygame.Rect(100, 150 + i * 50, 400, 40)
            pygame.draw.rect(question_window, BLUE, btn_rect)
            draw_text(question_window, option, btn_rect.x + 10, btn_rect.y + 10, btn_rect.width - 20, WHITE, small_font)
            buttons.append((btn_rect, option))

        if explanation:
            draw_text(question_window, "Explanation:", 50, 300, 500, RED, small_font)
            draw_text(question_window, explanation, 50, 330, 500, BLACK, small_font)
            close_button = pygame.Rect(200, 370, 200, 40)
            pygame.draw.rect(question_window, GREEN, close_button)
            draw_text(question_window, "Close", close_button.x + 10, close_button.y + 10, close_button.width - 20,
                      WHITE, font)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not answered:
                    for btn_rect, selected_answer in buttons:
                        if btn_rect.collidepoint(event.pos):
                            if selected_answer == correct_answer:
                                previous_wrong_question = None
                                pygame.display.set_mode((WIDTH, HEIGHT))
                                return
                            else:
                                explanation = explain_mistake(question_text, correct_answer, selected_answer)
                                previous_wrong_question = question_text
                                answered = True
                elif close_button and close_button.collidepoint(event.pos):
                    pygame.display.set_mode((WIDTH, HEIGHT))
                    return


def draw_text(surface, text, x, y, max_width, color, font):
    words = text.split()
    lines = []
    while words:
        line = ''
        while words and font.size(line + words[0])[0] <= max_width:
            line += (words.pop(0) + ' ')
        lines.append(line.strip())

    for line in lines:
        text_surface = font.render(line, True, color)
        surface.blit(text_surface, (x, y))
        y += text_surface.get_height() + 5


# ==================== MAIN LOOP ====================
while True:
    main_screen.fill(WHITE)
    button_rect = pygame.Rect(300, 250, 200, 50)
    pygame.draw.rect(main_screen, BLUE, button_rect)
    draw_text(main_screen, "Get Question", button_rect.x + 20, button_rect.y + 15, 160, WHITE, font)
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
            show_question()
