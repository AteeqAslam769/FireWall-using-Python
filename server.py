import socket
import threading
import tkinter as tk
import os
from PIL import Image
import io


variable_to_clear = 0
def is_text_data(data):
    try:
        data.decode('utf-8')
        return True
    except (UnicodeDecodeError, AttributeError):
        return False

def is_image_data(data):
    try:
        image = Image.open(io.BytesIO(data))
        image.verify()  # This will raise an exception if the data is not a valid image
        return True
    except (IOError, SyntaxError, AttributeError):
        return False

def reset_value():
    global variable_to_clear
    variable_to_clear = 0
    
    
def start_clear_timer():
    # Create a timer that will call `clear_variable` after 60 seconds (1 minute)
    timer = threading.Timer(15, reset_value)
    timer.start()
    
def is_video_data(data):
    video_signatures = {
        b'\x00\x00\x00\x18ftypmp42': 'mp4',
        b'\x00\x00\x00\x20ftypisom': 'mp4',
        b'\x1A\x45\xDF\xA3': 'mkv',
        b'\x52\x49\x46\x46': 'avi',
    }
    for signature in video_signatures:
        if data.startswith(signature):
            return True
    return False

def detect_ip_type(ip_address):
    private_ranges = [
        ('10.0.0.0', '10.255.255.255'),
        ('172.16.0.0', '172.31.255.255'),
        ('192.168.0.0', '192.168.255.255')
    ]
    ip_parts = list(map(int, ip_address.split('.')))
    for start, end in private_ranges:
        start_parts = list(map(int, start.split('.')))
        end_parts = list(map(int, end.split('.')))
        if all(start_parts[i] <= ip_parts[i] <= end_parts[i] for i in range(4)):
            return 'Private'
    return 'Public'

def identify_data_type(data):
    if is_text_data(data):
        return "Text Data"
    elif is_image_data(data):
        return "Image Data"
    elif is_video_data(data):
        return "Video Data"
    else:
        return "Unknown Data"
    
    

def handle_client(client_socket):
    global variable_to_clear
    try:
        connection_Ip = client_socket.recv(1024).decode('utf-8')
        if (block_public.get()):
            if(detect_ip_type(connection_Ip) == "Public"):
                update_label(client_result_label,f"Client with IP Address {connection_Ip}({detect_ip_type(connection_Ip)} IP Address) Blocked!!!")
                client_socket.send("You Are Blocked By Server".encode('utf-8'))
                return
        if(block_specific_ip.get()==connection_Ip):
            update_label(client_result_label,f"Client with IP Address {connection_Ip}({detect_ip_type(connection_Ip)} IP Address) Blocked!!!")
            client_socket.send("You Are Blocked By Server".encode('utf-8'))
            
            return
        update_label(client_result_label,f"Client with IP Address {connection_Ip}({detect_ip_type(connection_Ip)} IP Address) Connected")
        client_socket.send("You Are Connected to Server.".encode('utf-8'))
        while True:
            
            # Read the initial message to determine the type of request
            initial_message = client_socket.recv(1024).decode('utf-8')
            if not initial_message:
                break
            
            
            
            if(variable_to_clear==2):
                update_label(client_result_label,f"Request Limit Reached of {connection_Ip} Wait For a While!")
                continue
            
            
            variable_to_clear=variable_to_clear+1
            start_clear_timer()
            
            
            if initial_message == "FILE_TRANSFER":
                # Handle file transfer
                file_name = client_socket.recv(1024).decode('utf-8')
                client_socket.sendall("READY".encode('utf-8'))

                file_data = b""
                packet = client_socket.recv(10240)
                while True:
                    if not packet:
                        break
                    file_data += packet
                    packet=0

                data_type = identify_data_type(file_data)
                
                if(data_type == "Text Data"):
                    with open(file_name, 'wb') as file:
                        file.write(file_data)
                    update_label(client_result_label, f"Received file '{file_name}' from client with Ip {connection_Ip}.")
                elif(data_type=="Image Data"):
                    update_label(client_result_label,f"Blocked data containing pixels send by client {connection_Ip}")
                elif("Video Data"):
                    update_label(client_result_label,f"Blocked data containing pixels send by client {connection_Ip}")
                else:
                    update_label(client_result_label,"Blocked Anonymus data")
                    
            
            else:
                
                update_label(client_result_label, f"Received message from client with IP {connection_Ip}:   {initial_message}")
                continue
    
    except Exception as e:
        update_label(client_result_label, f"Error handling client: {e}")
    finally:
        client_socket.close()

def update_label(label, text):
    label.config(text=text)
    root.update_idletasks()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 5050))
    server_socket.listen(5)

    start_button.config(state=tk.DISABLED)  # Disable the button
    status_label.config(text="Server Status: Running", fg="green")
    result_label.config(text="Server is Listening")
    root.update()  # Update the GUI to reflect the changed status

    def accept_clients():
        while True:
            client_socket, client_address = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket,)).start()

    threading.Thread(target=accept_clients, daemon=True).start()

def main():
    global root, status_label, start_button, result_label, client_result_label,block_public,block_specific_ip
    
    # Create Tkinter window
    root = tk.Tk()
    root.title("Server GUI")
    root.geometry("800x400")
    
    
    # Styling
    root.configure(bg="GREY")

    # Create a label for server status
    status_label = tk.Label(root, text="Server Status: Not Running", fg="red", bg="GREY", font=("Arial", 20,"bold"))
    status_label.pack(pady=5)

    # Create a button to start the server
    start_button = tk.Button(root, text="Start Server", command=start_server, bg="#4CAF50", fg="white", font=("Arial", 12,"bold"), padx=20, pady=8)
    start_button.pack(pady=5)
    
    # Create result label for server status
    result_label = tk.Label(root, text="", fg="white", bg="GREY", font=("Arial", 15,"bold"))
    result_label.pack(pady=5)
    
    # Create result label for client messages and IP type
    client_result_label = tk.Label(root, text="", fg="white", bg="GREY", font=("Arial", 10,"bold"))
    client_result_label.pack(pady=5)

    # Checkbox to block public IP addresses
    block_public = tk.BooleanVar()
    block_public_checkbox = tk.Checkbutton(root, text="Block Public IP Addresses", variable=block_public, bg="GREY" ,font=("Arial",12, "bold"))
    block_public_checkbox.pack(pady=5)
    
    # Entry field for specific IP addresses to block
    block_specific_ip = tk.StringVar()
    
    block_specific_ip_label = tk.Label(root, text="Enter specific IP addresses to block:", bg="GREY", font=("Arial",12, "bold"))
    block_specific_ip_label.pack(pady=5)
    block_specific_ip_entry = tk.Entry(root, textvariable=block_specific_ip, bg="white", font=("Arial", 10,"bold"),width=30)
    block_specific_ip_entry.pack(pady=15)

    # Run the Tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    main()