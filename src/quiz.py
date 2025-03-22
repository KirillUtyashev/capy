# src/quiz.py
import pygame
import sys

from .settings import WIDTH, HEIGHT, FPS, BLACK, WHITE


def show_quiz(surface, clock, font, question):
    """
    Displays a quiz with multiple choice answers on 'surface'.
    Returns True if the correct answer is chosen, otherwise False.
    Pauses the main loop until user clicks on an answer.
    """
    question_ = question["question"]
    incorrect_answers = question["incorrect"]
    answers = incorrect_answers
    answers.append(question["correct"])
    correct_answer = question["correct"]

    quiz_width, quiz_height = 400, 300
    quiz_x = (WIDTH - quiz_width) // 2
    quiz_y = (HEIGHT - quiz_height) // 2
    quiz_rect = pygame.Rect(quiz_x, quiz_y, quiz_width, quiz_height)

    question_surf = font.render(question_, True, WHITE)
    question_rect = question_surf.get_rect(center=(quiz_rect.centerx, quiz_rect.top + 40))

    # Create 4 buttons in a 2x2 grid
    button_width, button_height = 100, 40
    buttons = []
    for i, ans in enumerate(answers):
        row = i // 2
        col = i % 2
        btn_x = quiz_rect.left + 50 + col * (button_width + 20)
        btn_y = quiz_rect.top + 100 + row * (button_height + 20)
        rect = pygame.Rect(btn_x, btn_y, button_width, button_height)
        buttons.append((ans, rect))

    quiz_running = True
    user_answer_correct = False

    while quiz_running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for ans, rect in buttons:
                    if rect.collidepoint(mouse_pos):
                        user_answer_correct = (ans == correct_answer)
                        quiz_running = False
                        break

        # Dim the background
        surface.fill(BLACK)
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(120)
        overlay.fill((50, 50, 50))
        surface.blit(overlay, (0, 0))

        # Draw quiz box
        pygame.draw.rect(surface, BLACK, quiz_rect)
        pygame.draw.rect(surface, WHITE, quiz_rect, 2)

        # Draw question
        surface.blit(question_surf, question_rect)

        # Draw answer buttons
        for ans, rect in buttons:
            pygame.draw.rect(surface, (100, 100, 100), rect)
            pygame.draw.rect(surface, WHITE, rect, 2)
            ans_surf = font.render(ans, True, WHITE)
            ans_rect = ans_surf.get_rect(center=rect.center)
            surface.blit(ans_surf, ans_rect)

        scaled_surface = pygame.transform.scale(surface, (WIDTH, HEIGHT))
        pygame.display.get_surface().blit(scaled_surface, (0, 0))
        pygame.display.flip()

    return user_answer_correct
