import tkinter as tk
import threading
import time

class IdleGame:
    def __init__(self, master):
        self.master = master
        self.resources = 0
        self.resource_rate = 1
        self.running = True

        self.master.title("Idle Game")
        self.master.geometry("400x300")

        self.resources_label = tk.Label(master, text=f"Resources: {self.resources}")
        self.resources_label.pack(pady=10)

        self.rate_label = tk.Label(master, text=f"Rate: {self.resource_rate}/s")
        self.rate_label.pack(pady=10)

        self.upgrade_button = tk.Button(master, text="Upgrade", command=self.upgrade)
        self.upgrade_button.pack(pady=20)

        self.update_display()
        threading.Thread(target=self.generate_resources, daemon=True).start()

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

    def update_display(self):
        self.resources_label.config(text=f"Resources: {self.resources}")
        self.rate_label.config(text=f"Rate: {self.resource_rate}/s")
        self.master.after(100, self.update_display)

    def run(self):
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.master.mainloop()

    def on_closing(self):
        self.running = False
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    game = IdleGame(root)
    game.run()