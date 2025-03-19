import socket
import threading
import json
import time
from file_manager import FileManager  # Import the new FileManager class
from character import Character  # Import the new Character class

class GameServer:
    def __init__(self, host="127.0.0.1", port=12345, max_clients=10):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow address reuse
        self.server.bind((host, port))
        self.server.listen(max_clients)
        self.clients = []
        self.resources = 0
        self.resource_rate = 1
        self.running = True
        self.lock = threading.Lock()  # Add a lock for thread safety

        # Create file manager and character instance
        self.file_manager = FileManager("saves", verbose=False)
        self.character = Character(self.file_manager)

    def start(self):
        print("Server started...")
        self.server.settimeout(1.0)  # Set a timeout for the accept call
        self.resource_thread = threading.Thread(target=self.generate_resources, daemon=True)
        self.resource_thread.start()
        try:
            while self.running:
                try:
                    client, addr = self.server.accept()
                    print(f"Client connected: {addr}")
                    with self.lock:
                        self.clients.append(client)
                    threading.Thread(target=self.handle_client, args=(client,), daemon=True).start()
                except socket.timeout:
                    continue  # Continue the loop if no connection is made within the timeout
                except OSError:
                    # This will be raised when socket is closed during accept
                    if not self.running:
                        break
                    raise
        finally:
            # Make sure to close the socket even if an exception occurs
            if not self.server._closed:
                self.server.close()

    def generate_resources(self):
        while self.running:
            time.sleep(1)
            with self.lock:
                self.resources += self.resource_rate
            self.broadcast_game_state()

    def handle_client(self, client):
        try:
            while True:
                try:
                    data = client.recv(1024).decode()
                    if not data:
                        break
                    message = json.loads(data)
                    if "action" not in message:
                        client.send(json.dumps({"error": "Invalid message format"}).encode())
                        continue
                    if message["action"] == "upgrade":
                        self.handle_upgrade(client)
                except json.JSONDecodeError:
                    client.send(json.dumps({"error": "Invalid JSON format"}).encode())
                except Exception as e:
                    print(f"Error handling client message: {e}")
                    break
        except ConnectionResetError:
            print("Client connection reset")
        finally:
            with self.lock:
                if client in self.clients:
                    self.clients.remove(client)
            client.close()
            print("Client disconnected")  # Log when a client disconnects

    def handle_upgrade(self, client):
        with self.lock:
            if self.resources >= 10:
                self.resources -= 10
                self.resource_rate += 1
                self.character.level_up()  # Use Character class method
                upgrade_success = True
            else:
                upgrade_success = False

        if upgrade_success:
            self.broadcast_game_state()
        else:
            client.send(json.dumps({"error": "Not enough resources to upgrade!"}).encode())

    def broadcast_game_state(self):
        with self.lock:
            state = {
                "resources": self.resources,
                "resource_rate": self.resource_rate,
                "character": self.character.get_stats()  # Get character stats from Character class
            }
        # Remove automatic save on every state broadcast
        # Only save when meaningful changes happen (like in handle_upgrade)
        with self.lock:
            clients_copy = self.clients.copy()
        message = json.dumps(state).encode()
        for client in clients_copy:
            try:
                client.send(message)
            except Exception as e:
                print(f"Error sending to client: {e}")

    def stop(self):
        print("\nStopping server...")
        self.running = False
        
        # Unblock the accept() call by connecting to the server
        try:
            temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_socket.settimeout(1.0)
            temp_socket.connect(("127.0.0.1", self.server.getsockname()[1]))
            temp_socket.close()
        except (ConnectionRefusedError, OSError) as e:
            print(f"Note: Could not connect to self to unblock: {e}")
        
        # Close all client connections
        print("Closing all client connections...")
        with self.lock:
            clients_copy = self.clients.copy()
            self.clients.clear()  # Clear the list to prevent any further access
        
        for client in clients_copy:
            try:
                client.close()
            except Exception as e:
                print(f"Error closing client connection: {e}")
        
        # Make sure server socket is closed
        try:
            if hasattr(self.server, '_closed') and not self.server._closed:
                self.server.close()
        except Exception as e:
            print(f"Error closing server socket: {e}")
        
        print("Server stopped.")

if __name__ == "__main__":
    server = GameServer()
    try:
        server.start()
    except KeyboardInterrupt:
        # Don't print here since stop() will print the message
        server.stop()  # Gracefully stop the server
