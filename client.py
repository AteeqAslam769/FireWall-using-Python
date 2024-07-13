import tkinter as tk
from tkinter import filedialog
import socket
import os
import ipaddress

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.client_socket = None
        self.connected = False

        self.root.title("Client GUI")
        self.root.geometry("800x400")
        self.root.resizable(False, False)

        self.create_widgets()

    @staticmethod    
    def is_valid_ip(ip_str):
        try:
            # Attempt to create an IPv4 or IPv6 address object
            ipaddress.ip_address(ip_str)
            return True
        except ValueError:
            return False
        
    def create_widgets(self):
        # Create IP Entry field
        ip_label = tk.Label(self.root, text="Enter Your IP Address:", font=("Arial", 12, "bold"), fg="#2980b9")  # Blue text
        ip_label.pack(pady=5)
        self.ip_entry = tk.Entry(self.root, width=30, font=("Arial", 10), bg="#ecf0f1")  # Light grey background
        self.ip_entry.pack()

        # Create button to connect to server
        self.connect_button = tk.Button(self.root, text="Connect to Server", command=self.connect_to_server, font=("Arial", 12, "bold"), bg="#27ae60", fg="white")  # Green button
        self.connect_button.pack(pady=10)

        # Create Text Entry field
        text_label = tk.Label(self.root, text="Enter Text to Send to Server:", font=("Arial", 12, "bold"), fg="#2980b9")  # Blue text
        text_label.pack(pady=5)
        self.text_entry = tk.Entry(self.root, width=30, font=("Arial", 10), bg="#ecf0f1")  # Light grey background
        self.text_entry.pack()

        # Create button to send text to server
        self.send_text_button = tk.Button(self.root, text="Send Text", command=self.send_text_to_server, font=("Arial", 12, "bold"), bg="#2980b9", fg="white", state=tk.DISABLED)  # Blue button
        self.send_text_button.pack(pady=10)

        # Create button to send file to server
        self.send_file_button = tk.Button(self.root, text="Send File", command=self.send_file_to_server, font=("Arial", 12, "bold"), bg="#2980b9", fg="white", state=tk.DISABLED)  # Blue button
        self.send_file_button.pack(pady=10)

        # Create result label
        self.result_label = tk.Label(self.root, text="", font=("Arial", 12), fg="#e74c3c")  # Red text
        self.result_label.pack(pady=20)

    def connect_to_server(self):
        server_ip = '127.0.0.1'
        client_ip = self.ip_entry.get()
        valid_client_ip = self.is_valid_ip(client_ip)
        if(valid_client_ip):
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((server_ip, 5050))
                self.connected = True
                self.client_socket.send(client_ip.encode('utf-8'))
                msg =self.client_socket.recv(1024).decode('utf-8')
                if(msg =="You Are Connected to Server."):
                    self.result_label.config(text="Connected to the server.", fg="#27ae60")  # Green text
                else:
                    self.result_label.config(text="Blocked to the server.", fg="#e74c3c")  # Red text
                self.send_text_button.config(state=tk.NORMAL)
                self.send_file_button.config(state=tk.NORMAL)
                self.connect_button.config(state=tk.DISABLED)
            except ConnectionRefusedError:
                self.result_label.config(text="Failed to connect to the server. Ensure the server is running and the IP address is correct.", fg="#e74c3c")  # Red text
            except Exception as e:
                self.result_label.config(text=f"An error occurred: {e}", fg="#e74c3c")  # Red text
        elif(client_ip==""):
            self.result_label.config(text="Enter Ip Address", fg="#e74c3c")  # Red text
        else:
            self.result_label.config(text="Enter Valid Ip Address", fg="#e74c3c")  # Red text
            
    def send_text_to_server(self):
        if self.connected:
            try:
                # Send custom text
                self.client_socket.send(self.text_entry.get().encode('utf-8'))
                
                # Receive and display server response
                
            except Exception as e:
                self.result_label.config(text=f"An error occurred: {e}", fg="#e74c3c")  # Red text

    def send_file_to_server(self):
        if self.connected:
            file_path = filedialog.askopenfilename()
            if file_path:
                try:
                    # Determine file type
                    file_extension = os.path.splitext(file_path)[1].lower()
                    if file_extension in ['.jpg', '.jpeg', '.png', '.gif']:
                        file_type = "FILE"
                    elif file_extension in ['.mp4', '.avi', '.mov']:
                        file_type = "FILE"
                    else:
                        file_type = "FILE"

                    # Send a signal to indicate a file transfer with its type
                    self.client_socket.send(f"{file_type}_TRANSFER".encode('utf-8'))
                    
                    # Send the file name
                    file_name = os.path.basename(file_path)
                    self.client_socket.send(file_name.encode('utf-8'))
                    
                    # Wait for server acknowledgment
                    ack = self.client_socket.recv(1024).decode('utf-8')
                    if ack == "READY":
                        # Send the file data
                        with open(file_path, 'rb') as file:
                            
                                data = file.read(10240)
                                self.client_socket.sendall(data)
                        
                        self.result_label.config(text=f"{file_type} '{file_name}' sent to server.", fg="#27ae60")  # Green text
                    else:
                        self.result_label.config(text="Server failed to acknowledge file transfer request.", fg="#e74c3c")  # Red text
                except Exception as e:
                    self.result_label.config(text=f"An error occurred: {e}", fg="#e74c3c")  # Red text

    def on_closing(self):
        if self.client_socket:
            self.client_socket.close()
        self.root.destroy()

# Create Tkinter window
root = tk.Tk()
app = ClientApp(root)

# Handle the window close event to ensure the socket is closed
root.protocol("WM_DELETE_WINDOW", app.on_closing)

# Run the Tkinter event loop
root.mainloop()
