import socket
import json
import csv
import sys
import logging

BUF_SIZE = 4096  # Buffer size for server response.
TIMEOUT_SEC = 0.2  # Timeout in seconds when sending/receiving data.
MAX_ATTEMPTS = 8  # Max retransmission attempts when no data is received.

# Function to send an HTTP request and receive the response
def send_request(sock, request):
    attempts: int = MAX_ATTEMPTS
    sock.settimeout(TIMEOUT_SEC)
    while attempts:
        res: bytes = bytes()

        try:
            sock.sendall(request.encode())  # Send the request to the server

            # Try to receive as much data as possible until a timeout occurs
            while True:
                chunk: bytes = sock.recv(BUF_SIZE)
                res += chunk

        except socket.timeout:
            logging.debug(
                f"Socket connected to {sock.getsockname()}, received {len(res)} bytes in total"
            )

            if len(res) > 0:
                logging.debug(res.decode("utf-8"))
                return res.decode()

        except OSError as msg:
            logging.error(
                f"Socket connected to {sock.getsockname()}, could not send and/or receive data. {msg}"
            )

# Function to get paginated data from the server
def get_paginated_data(sock, endpoint, max=50):
    start = 0
    all_data = []
    limit = 50  # Setting the initial limit to 50, as required
    while limit <= max:
        # Constructing the HTTP GET request
        request = f"GET {endpoint}?limit={limit}&start={start} HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n"
        
        # Sending the request and receiving the response
        response = send_request(sock, request)
        
        # Splitting the response to separate headers from the body
        body = response.split('\r\n\r\n')

        # Parsing the body as JSON and extracting the "games" data
        data = json.loads(body[1]).get("games", [])
        
        # If no more data is received, exit the loop
        if not data:
            break
        
        # Adding the received data to the cumulative list
        all_data.extend(data)
        
        # Updating the start index for the next request
        start += limit
        
        # Incrementing the limit to stay within the maximum allowed items
        limit += 50
    return all_data


# Function to get game information by game ID
def get_game_info(sock, game_id):
    request = f"GET /api/game/{game_id} HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n"
    response = send_request(sock, request)
    print("response:", response)
    body = response.split('\r\n\r\n')[1]
    return json.loads(body)

# Function to analyze GAS with the best performance and generate a CSV file
def analyze_gas_best_performance(sock, output_file):
    top100_games = get_paginated_data(sock, "/api/rank/sunk")
    gas_performance = {}

    for game_id in top100_games:
        game_info = get_game_info(sock, game_id)
        if game_info:
            gas = game_info["game_stats"].get("gas")
            sunk_ships = game_info["game_stats"].get("sunk_ships", 0)

            if gas not in gas_performance:
                gas_performance[gas] = {"count": 0, "total_sunk": 0}

            gas_performance[gas]["count"] += 1
            gas_performance[gas]["total_sunk"] += sunk_ships

    # Create a CSV file for GAS performance without headers
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        sorted_gas = sorted(gas_performance.items(), key=lambda x: x[1]["count"], reverse=True)
        for gas, stats in sorted_gas:
            average_sunk = stats["total_sunk"] / stats["count"]
            writer.writerow([gas, stats["count"], average_sunk])

# Function to normalize cannon placement into an 8-digit string
def normalize_cannon_placement(cannon_placement):
    normalized = [0] * 8
    for placement in cannon_placement:
        if 0 <= placement < 8:
            normalized[placement] += 1
    return "".join(map(str, normalized))

# Function to analyze the best cannon placements and generate a CSV file
def analyze_best_cannon_placements(sock, output_file):
    top100_games = get_paginated_data(sock, "/api/rank/escaped")
    cannon_placements = {}

    for game_id in top100_games:
        game_info = get_game_info(sock, game_id)
        if game_info:
            cannon_placement = game_info["game_stats"].get("cannon_placement", [])
            escaped_ships = game_info["game_stats"].get("escaped_ships", 0)
            normalized_placement = normalize_cannon_placement(cannon_placement)

            if normalized_placement not in cannon_placements:
                cannon_placements[normalized_placement] = {"count": 0, "total_escaped": 0}

            cannon_placements[normalized_placement]["count"] += 1
            cannon_placements[normalized_placement]["total_escaped"] += escaped_ships

    # Create a CSV file for cannon placements without headers
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        sorted_placements = sorted(cannon_placements.items(), key=lambda x: x[1]["total_escaped"] / x[1]["count"])
        for placement, stats in sorted_placements:
            average_escaped = stats["total_escaped"] / stats["count"]
            writer.writerow([placement, average_escaped])

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: ./client <IP> <port> <analysis> <output>")
        sys.exit(1)

    IP = sys.argv[1]
    PORT = int(sys.argv[2])
    ANALYSIS = int(sys.argv[3])
    OUTPUT_FILE = sys.argv[4]

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((IP, PORT))
        
        if ANALYSIS == 1:
            analyze_gas_best_performance(sock, OUTPUT_FILE)
        elif ANALYSIS == 2:
            analyze_best_cannon_placements(sock, OUTPUT_FILE)
        else:
            print("Invalid analysis option. Use 1 or 2.")
            sys.exit(1)
