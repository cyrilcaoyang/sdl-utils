"""
Preconfigured WebSocket implementation for SDLs
Author: Yang Cao, Acceleration Consortium
Version: 0.1

A list of functions:
 - connect_socket
 - send_file_size
 - receive_file_size
 - receive_file

"""


def connect_socket(sock, server_ip, server_port, logger=None):
    pass


def send_file_size(sock, value: int, logger=None):
    """
    Helper: Sends the INTEGER 'value' as ASCII digits followed by a newline.
    Application: Sends the file size before sending the file
    :param sock: an active socket
    :param value: an integer (4 bytes)
    :param logger: a logger
    :return: None
    """
    message = f"{value}\n"
    sock.sendall(message.encode("utf-8"))
    logger.info(f"Integer {value=} sent over")


def receive_file_size(conn, logger=None):
    """
    Helper: Receives the INTEGER 'value' as ASCII digits followed by a newline.
    Application: Receives the file size before sending the file
    :param conn: an active socket
    :param logger: a logger
    :return: the integer number
    """
    data_chunks = []
    while True:
        chunk = conn.recv(1)
        if not chunk:
            # Connection closed or error
            logger.debug("Did not receive file size from server (connection closed).")
            raise ConnectionError
        if chunk == b'\n':
            break
        data_chunks.append(chunk)

    num_in_str = b''.join(data_chunks).decode('utf-8')
    try:
        # Parse the string into an integer
        file_size = int(num_in_str)
        return file_size
    except ValueError:
        logger.debug(f"Could not parse file size as int: '{num_in_str}'")
        raise ValueError(f"Could not parse '{num_in_str}' into int")


def receive_file(sock, chunk_size, file_size, logger=None):
    """
    After getting the header of the file size,
    start to receive the file in chunks
    :param sock: open socket
    :param chunk_size: the size of each chunk to be sent as part of the file
    :param file_size: the exact size of the file
    :param logger: a logger
    :return: the received file
    """

    # Receive the actual file data in chunks
    received_file = b''
    bytes_received = 0
    logger.info(f"Receiving file of size {file_size} bytes...")
    while bytes_received < file_size:
        chunk = sock.recv(min(chunk_size, file_size - bytes_received))
        if not chunk:
            logger.debug(f"Connection lost while receiving file data.")
            raise ConnectionError
        received_file += chunk
        bytes_received += len(chunk)

    logger.info("Received the entire file from server.")
    return received_file


if __name__ == "__main__":
    """
    Example usage of the sdl_socket module.
    """