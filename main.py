import pygame
import threading
import time

class IdleGame:
    def __init__(self):
        self.resources = 0
        self.resource_rate = 1
        self.running = True
        self.screen = None
        self.font = None

    def generate_resources(self):
        while self.running:
            time.sleep(1)
            self.resources += self.resource_rate

    def upgrade(self):
        if self.resources >= 10:
            self.resources -= 10
            self.resource_rate += 1
        else:
            print("Not enough resources to upgrade!")

    def start(self):
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((400, 300))
        pygame.display.set_caption("Idle Game")
        self.font = pygame.font.Font(None, 36)

        # Start resource generation in a separate thread
        threading.Thread(target=self.generate_resources, daemon=True).start()

        # Main game loop
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if 150 <= event.pos[0] <= 250 and 200 <= event.pos[1] <= 250:
                        self.upgrade()

            # Draw the game screen
            self.screen.fill((30, 30, 30))
            resources_text = self.font.render(f"Resources: {self.resources}", True, (255, 255, 255))
            rate_text = self.font.render(f"Rate: {self.resource_rate}/s", True, (255, 255, 255))
            upgrade_text = self.font.render("Upgrade", True, (0, 0, 0))

            self.screen.blit(resources_text, (20, 20))
            self.screen.blit(rate_text, (20, 60))
            pygame.draw.rect(self.screen, (0, 255, 0), (150, 200, 100, 50))
            self.screen.blit(upgrade_text, (160, 210))

            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = IdleGame()
    game.start()