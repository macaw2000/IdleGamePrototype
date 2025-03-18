import tkinter as tk
import socket
import threading
import json

class IdleGameClient:
    def __init__(self, master, host="127.0.0.1", port=12345):
        self.master = master
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))

        self.resources = 0
        self.resource_rate = 1
        self.character = {"health": 100, "strength": 10, "level": 1}

        self.master.title("Idle Game Client")
        self.master.geometry("400x400")

        # Resources section
        self.resources_label = tk.Label(master, text=f"Resources: {self.resources}")
        self.resources_label.pack(pady=10)

        self.rate_label = tk.Label(master, text=f"Rate: {self.resource_rate}/s")
        self.rate_label.pack(pady=10)

        self.upgrade_button = tk.Button(master, text="Upgrade", command=self.upgrade)
        self.upgrade_button.pack(pady=20)

        # Save progress button
        self.save_button = tk.Button(master, text="Save Progress", command=self.save_progress)
        self.save_button.pack(pady=20)

        # Character stats section
        self.stats_label = tk.Label(master, text="Character Stats", font=("Arial", 14, "bold"))
        self.stats_label.pack(pady=10)

        self.health_label = tk.Label(master, text=f"Health: {self.character['health']}")
        self.health_label.pack(pady=5)

        self.strength_label = tk.Label(master, text=f"Strength: {self.character['strength']}")
        self.strength_label.pack(pady=5)

        self.level_label = tk.Label(master, text=f"Level: {self.character['level']}")
        self.level_label.pack(pady=5)

        threading.Thread(target=self.listen_to_server, daemon=True).start()

    def upgrade(self):
        message = {"action": "upgrade"}
        self.client.send(json.dumps(message).encode())

    def save_progress(self):
        """Send a save request to the server."""
        message = {"action": "save", "character": self.character}
        self.client.send(json.dumps(message).encode())

    def listen_to_server(self):
        while True:
            data = self.client.recv(1024).decode()
            if not data:
                break
            state = json.loads(data)
            if "error" in state:
                print(state["error"])
            else:
                self.resources = state["resources"]
                self.resource_rate = state["resource_rate"]
                self.character = state["character"]
                self.update_display()

    def update_display(self):
        self.resources_label.config(text=f"Resources: {self.resources}")
        self.rate_label.config(text=f"Rate: {self.resource_rate}/s")
        self.health_label.config(text=f"Health: {self.character['health']}")
        self.strength_label.config(text=f"Strength: {self.character['strength']}")
        self.level_label.config(text=f"Level: {self.character['level']}")

    def run(self):
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.master.mainloop()

    def on_closing(self):
        self.client.close()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    game = IdleGameClient(root)
    game.run()
