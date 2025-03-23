import cohere
import json
from .queue import Queue

# ==================== CONFIGURATION ====================
API_KEY = "V1WlqVxN5PtUEXsNbA5LgOliHoS6SysKT9a8wiO3"  # Replace with your Cohere API Key
TOPIC = "elementary math"
QUESTIONS_FILE = "questions.json"

# ==================== INITIALIZE COHERE ====================
co = cohere.Client(API_KEY)

# ==================== PYGAME SETUP ====================
# pygame.init()
# WIDTH, HEIGHT = 800, 600
# WHITE, BLACK, BLUE, GREEN, RED = (255, 255, 255), (0, 0, 255), (100, 100, 255), (0, 200, 0), (200, 0, 0)
#
# main_screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
# pygame.display.set_caption("AI Quiz Game")
#
# font = pygame.font.Font(None, 36)
# small_font = pygame.font.Font(None, 28)


# ==================== QUESTION GENERATION ====================
def generate_questions(topic, n=5):
    prompt = f"""
        Generate {n} different multiple-choice questions with 4 options about "{topic}".
        Format for each question:
        Question: <question>
        Correct: <correct>
        Incorrect: <incorrect_1>, <incorrect_2>, <incorrect_3>
        """
    print(prompt)
    response = co.generate(model="command-r-plus", prompt=prompt, max_tokens=50 * n, temperature=0.7)

    questions = Queue()
    raw_questions = response.generations[0].text.strip().split("\n\n")
    questions_list = []

    for raw_question in raw_questions:
        lines = raw_question.strip().split("\n")
        if len(lines) < 3:
            continue
        question = lines[0].replace("Question: ", "").strip()
        correct_answer = lines[1].replace("Correct: ", "").strip()
        incorrect_answers = [ans.strip() for ans in lines[2].replace("Incorrect: ", "").split(",")]
        questions.enqueue({"question": question, "correct": correct_answer, "incorrect": incorrect_answers})
        questions_list.append({"question": question, "correct": correct_answer, "incorrect": incorrect_answers})
    with open(QUESTIONS_FILE, "w") as f:
        json.dump(questions_list, f)
    print(questions_list)
    return questions


# def load_questions():
#     return generate_questions("elementary math")
#
# questions = load_questions()
# current_index = 0


def generate_similar_question(similar_to):
    prompt = f"""
    Generate a multiple-choice question of the same subtopic as "{similar_to}", but with other values/details, not a rewording!.
    Format:
    Question: <question>
    Correct: <correct>
    Incorrect: <incorrect_1>, <incorrect_2>, <incorrect_3>
    """
    response = co.generate(model="command-r-plus", prompt=prompt, max_tokens=150, temperature=0.7)
    lines = response.generations[0].text.strip().split("\n")
    if len(lines) < 3:
        return generate_similar_question(similar_to)
    question = lines[0].replace("Question: ", "").strip()
    correct_answer = lines[1].replace("Correct: ", "").strip()
    incorrect_answers = [ans.strip() for ans in lines[2].replace("Incorrect: ", "").split(",")]
    return {"question": question, "correct": correct_answer, "incorrect": incorrect_answers}


def explain_mistake(question, correct_answer, user_answer):
    prompt = f"""
    A child answered a multiple-choice question incorrectly.
    Question: {question}
    User's incorrect answer: {user_answer}
    Correct answer: {correct_answer}
    Explanation: Explain in simple, easy-to-understand language why the correct answer is right and why the child’s answer was not correct. Avoid complex terms and provide a straightforward reasoning that a child can grasp.
    Encouragement: Include an encouraging note that reinforces that making mistakes is a normal part of learning and that trying is important.
    """
    response = co.generate(model="command-r-plus", prompt=prompt, max_tokens=50, temperature=0.7)
    return response.generations[0].text.strip()
#
#
# def show_question():
#     global current_index, questions
#     if current_index >= len(questions):
#         questions = generate_questions("elementary math")
#         current_index = 0
#
#     current_question = questions[current_index]
#     question_window = pygame.display.set_mode((600, 400))
#     pygame.display.set_caption("Quiz Question")
#
#     question_text = current_question["question"]
#     correct_answer = current_question["correct"]
#     options = [correct_answer] + current_question["incorrect"]
#     random.shuffle(options)
#
#     explanation = None
#     answered = False
#
#     while True:
#         question_window.fill(WHITE)
#         draw_text(question_window, question_text, 50, 50, 500, BLACK, font)
#         buttons = []
#         for i, option in enumerate(options):
#             btn_rect = pygame.Rect(100, 150 + i * 50, 400, 40)
#             pygame.draw.rect(question_window, BLUE, btn_rect)
#             draw_text(question_window, option, btn_rect.x + 10, btn_rect.y + 10, btn_rect.width - 20, WHITE, small_font)
#             buttons.append((btn_rect, option))
#
#         if explanation:
#             draw_text(question_window, "Explanation:", 50, 300, 500, RED, small_font)
#             draw_text(question_window, explanation, 50, 330, 500, BLACK, small_font)
#             close_button = pygame.Rect(200, 370, 200, 40)
#             pygame.draw.rect(question_window, GREEN, close_button)
#             draw_text(question_window, "Close", close_button.x + 10, close_button.y + 10, close_button.width - 20, WHITE, font)
#
#         pygame.display.flip()
#
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 sys.exit()
#             if event.type == pygame.MOUSEBUTTONDOWN:
#                 if not answered:
#                     for btn_rect, selected_answer in buttons:
#                         if btn_rect.collidepoint(event.pos):
#                             if selected_answer == correct_answer:
#                                 current_index += 1
#                                 pygame.display.set_mode((WIDTH, HEIGHT))
#                                 return
#                             else:
#                                 explanation = explain_mistake(question_text, correct_answer, selected_answer)
#                                 questions[current_index] = generate_similar_question(question_text)
#                                 answered = True
#                 elif close_button and close_button.collidepoint(event.pos):
#                     pygame.display.set_mode((WIDTH, HEIGHT))
#                     return
#
#
# def draw_text(surface, text, x, y, max_width, color, font):
#     words = text.split()
#     lines = []
#     while words:
#         line = ''
#         while words and font.size(line + words[0])[0] <= max_width:
#             line += (words.pop(0) + ' ')
#         lines.append(line.strip())
#     for line in lines:
#         text_surface = font.render(line, True, color)
#         surface.blit(text_surface, (x, y))
#         y += text_surface.get_height() + 5


# if __name__ == '__main__':
    # while True:
    #     main_screen.fill(WHITE)
    #     button_rect = pygame.Rect(300, 250, 200, 50)
    #     pygame.draw.rect(main_screen, BLUE, button_rect)
    #     draw_text(main_screen, "Get Question", button_rect.x + 20, button_rect.y + 15, 160, WHITE, font)
    #     pygame.display.flip()
    #
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             pygame.quit()
    #             sys.exit()
    #         if event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
    #             show_question()
