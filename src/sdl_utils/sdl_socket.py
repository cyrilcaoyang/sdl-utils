"""
Preconfigured WebSocket implementation for SDLs

Use Socket for file transfers and time-sensitive communications

Author: Yang Cao, Acceleration Consortium
Version: 0.1

A list of functions:
 - connect_socket
 - send_file_name
 - send_file_size
 - receive_file_size
 - receive_file
"""


def connect_socket(sock, server_ip, server_port, logger=None):
    """
    Helper: Useful in early returns
    Return False when connection cannot be established.
    """
    try:
        # Set a 10-second timeout BEFORE connecting, and attempt to connect to server
        sock.settimeout(10.0)
        sock.connect((server_ip, server_port))
        # If successful, reset the timeout if desired to avoid timeout following actions
        sock.settimeout(None)
        logger.info("Connected to server")
        return True
    # Catch exceptions
    except ConnectionError:
        logger.info("Connection timed out after 10 seconds.")
        return False


def _recv_until_newline(sock):
    """
    Helper: Read bytes from 'conn' until we encounter a newline (b'\\n').
    Returns the line as a string (minus the newline).
    """
    data_chunks = []
    while True:
        chunk = sock.recv(1)
        if not chunk:
            # Connection closed or error
            return ""
        if chunk == b'\n':
            break
        data_chunks.append(chunk)
    return b''.join(data_chunks).decode('utf-8')


def send_file_name(sock, name: str, logger=None):
    """
    Helper: Sends the INTEGER 'value' as ASCII digits followed by a newline.
    :param sock: an active socket
    :param name: a string of the file name (path.basename)
    :param logger: a logger
    :return: None
    """
    message = name + "\n"
    sock.sendall(message.encode("utf-8"))
    logger.info(f"File name {name} sent over")


def receive_file_name(sock, logger=None):
    """
    Helper: Receives the file name 'value' as string followed by a newline.
    """
    return _recv_until_newline(sock)


def send_file_size(sock, size: int, logger=None):
    """
    Helper: Sends the INTEGER 'value' as ASCII digits followed by a newline.
    :param sock: an active socket
    :param size: an integer (4 bytes)
    :param logger: a logger
    :return: None
    """
    message = f"{size}\n"
    sock.sendall(message.encode("utf-8"))
    logger.info(f"File {size=} sent over")


def receive_file_size(sock, logger=None):
    """
    Helper: Receives the INTEGER 'value' as ASCII digits followed by a newline.
    Receives the file size before sending the file
    :param sock: an active socket
    :param logger: a logger
    :return: the integer number
    """
    num_in_str = _recv_until_newline(sock)
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