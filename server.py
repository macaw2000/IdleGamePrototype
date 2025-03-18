import socket
import threading
import json
import time
from file_manager import FileManager  # Import the new FileManager class

class GameServer:
    def __init__(self, host="127.0.0.1", port=12345):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)
        self.clients = []
        self.resources = 0
        self.resource_rate = 1
        self.running = True

        # Character stats
        self.character = {
            "health": 100,
            "strength": 10,
            "level": 1
        }
        self.file_manager = FileManager("saves")  # Initialize FileManager with save directory
        saved_character = self.file_manager.load_character_progress()
        if saved_character:
            self.character = saved_character  # Load saved character data
            print("Character progress loaded successfully.")
        else:
            print("No saved character progress found.")

    def start(self):
        print("Server started...")
        self.server.settimeout(1.0)  # Set a timeout for the accept call
        threading.Thread(target=self.generate_resources, daemon=True).start()
        while self.running:
            try:
                client, addr = self.server.accept()
                print(f"Client connected: {addr}")
                self.clients.append(client)
                threading.Thread(target=self.handle_client, args=(client,), daemon=True).start()
            except socket.timeout:
                continue  # Continue the loop if no connection is made within the timeout

    def generate_resources(self):
        while self.running:
            time.sleep(1)
            self.resources += self.resource_rate
            self.broadcast_game_state()

    def handle_client(self, client):
        try:
            while True:
                data = client.recv(1024).decode()
                if not data:
                    break
                message = json.loads(data)
                if message["action"] == "upgrade":
                    self.handle_upgrade(client)
                elif message["action"] == "save":
                    self.file_manager.save_character_progress(message.get("character"))
                    client.send(json.dumps({"status": "success", "message": "Progress saved successfully."}).encode())
        except ConnectionResetError:
            pass
        finally:
            self.clients.remove(client)
            client.close()
            print("Client disconnected")  # Log when a client disconnects

    def handle_upgrade(self, client):
        if self.resources >= 10:
            self.resources -= 10
            self.resource_rate += 1
            self.character["level"] += 1
            self.broadcast_game_state()
        else:
            client.send(json.dumps({"error": "Not enough resources to upgrade!"}).encode())

    def broadcast_game_state(self):
        state = {
            "resources": self.resources,
            "resource_rate": self.resource_rate,
            "character": self.character
        }
        for client in self.clients:
            client.send(json.dumps(state).encode())

    def stop(self):
        self.running = False
        print("Closing all client connections...")
        for client in self.clients:
            try:
                client.close()  # Close each client connection
            except Exception as e:
                print(f"Error closing client connection: {e}")
        self.server.close()
        print("Server stopped.")

if __name__ == "__main__":
    server = GameServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.stop()  # Gracefully stop the server
