import socket


def udp_client(server_address, server_port, message):
    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Send the message to the server
        client_socket.sendto(message.encode(), (server_address, server_port))

        # Receive the response from the server
        response, server_address = client_socket.recvfrom(1024)

        # Print the received response
        print("Response from server:", response.decode())

    except socket.error as e:
        print("Socket error:", e)

    finally:
        # Close the socket
        client_socket.close()


# Example usage
server_address = '127.0.0.1'  # Replace with the server IP address
server_port = 55555  # Replace with the server port number
message = 'LOGIN'  # Replace with the message to send

udp_client(server_address, server_port, message)
