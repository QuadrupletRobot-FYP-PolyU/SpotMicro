import socket
import json

# Set up the UDP server
udp_ip = "172.20.10.10"  # The server's IP address
udp_port = 7777        # The port that the server will listen on

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the IP and port
sock.bind((udp_ip, udp_port))

print(f"UDP server up and listening at {udp_ip}:{udp_port}")

try:
    while True:
        # Wait for a message
        data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes

        # Decode the data
        message = data.decode('utf-8')
        input_states = json.loads(message)

        # Print the received message
        print(f"Received message from {addr}: {input_states}")

        # Here you can add the logic to do something with the received input_states
        # ...

except KeyboardInterrupt:
    print("\nServer is shutting down.")

finally:
    # Close the socket
    sock.close()
    print("Server has been closed.")
