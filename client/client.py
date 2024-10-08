import os
import socket
import json
import csv
import sys
import logging

BUF_SIZE = 4096  # Buffer size for server response.
TIMEOUT_SEC = 0.2  # Timeout in seconds when sending/receiving data.
MAX_ATTEMPTS = 8  # Max retransmission attempts when no data is received.
RANKING_RANGE = 100  # Number of games to analyze for ranking.

def extract_html_headers_and_body(response: bytes) -> dict[str, str] | None:
    # Get raw content length from remaining bytes
    content_length_bytes = len(response.split(b"\r\n\r\n", 1)[1])

    # Decode and split the response into headers and body
    headers, body = response.decode().split("\r\n\r\n", 1)

    # Initialize the result dict
    result = dict()

    # Get header lines and build a dict with key: value pairs
    header_lines = headers.split("\r\n")

    # First line is the status line
    result["status"] = header_lines[0]

    # Remaining lines are headers
    for line in header_lines[1:]:
        key, value = line.split(": ", 1)
        result[key] = value

    # Check content length and body length match
    if "content-length".casefold() in result:
        if int(result["content-length"]) != content_length_bytes:
            logging.warning("Content length mismatch")

            return None

    # Valid response, add the body to the result dict
    result["body"] = body

    return result

# Function to send an HTTP request and receive the response
def send_request(sock, request) -> dict[str, str]:
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

                # If response is mismatched (e.g.: wrong content-length), retry the request
                resDict = extract_html_headers_and_body(res)

                if resDict is None:
                    logging.warning("Retrying request due to content length mismatch")
                    attempts -= 1
                    continue

                # Return the response as a dictionary
                return resDict

        except OSError as msg:
            logging.error(
                f"Socket connected to {sock.getsockname()}, could not send and/or receive data. {msg}"
            )

    # Empty response if no data is received
    return dict()

# Function to get paginated data from the server
def get_paginated_data(sock, endpoint, max=RANKING_RANGE):
    start = 0
    all_data = []
    limit = 50  # Setting the initial limit to 50
    end = limit
    while end <= max:
        # Constructing the HTTP GET request
        request = f"GET {endpoint}?limit={limit}&start={start} HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n"
        
        # Sending the request and receiving the response
        response = send_request(sock, request)
        
        # Parsing the body as JSON and extracting the "games" data
        data = json.loads(response["body"]).get("games", [])
        
        # If no more data is received, exit the loop
        if not data:
            break
        
        # Adding the received data to the cumulative list
        all_data.extend(data)
        
        # Updating the start index for the next request
        start += limit
        end += limit

    return all_data

# Function to get game information by game ID
def get_game_info(sock, game_id):
    request = f"GET /api/game/{game_id} HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n"
    response = send_request(sock, request)

    return json.loads(response["body"])

# Function to analyze GAS with the best performance and generate a CSV file
def analyze_gas_best_performance(sock, output_file):
    top100_games = get_paginated_data(sock, "/api/rank/sunk")
    gas_performance = {}

    for game_id in top100_games:
        game_info = get_game_info(sock, game_id)
        if game_info:
            gas = game_info["game_stats"].get("auth")
            sunk_ships = game_info["game_stats"].get("sunk_ships", 0)

            if gas not in gas_performance:
                gas_performance[gas] = {"count": 0, "total_sunk": 0}

            gas_performance[gas]["count"] += 1
            gas_performance[gas]["total_sunk"] += sunk_ships
    
    sorted_gas_performance = sorted(
        ((gas, stats["count"], stats["total_sunk"] / stats["count"])
        for gas, stats in gas_performance.items()),
        key=lambda x: x[1],
        reverse=True
    )

    # Create a CSV file for GAS performance without headers
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(sorted_gas_performance)
    
    return sorted_gas_performance

# Function to normalize cannon placement into an 8-digit string
def normalize_cannon_placement(cannon_placement):
    # Step 1: Count the number of cannons in each row
    row_counts = [0] * 5 
    
    for placement in cannon_placement:
        row = placement[1] 
        row_counts[row] += 1
    
    # Step 2: Count the number of rows with exactly i cannons
    cannon_counts = [0] * 8  

    for count in row_counts:
        if count < 8:
            cannon_counts[count] += 1
    
    # Step 3: Construct the 8-digit string
    normalized_string = ''.join(map(str, cannon_counts))
    
    return normalized_string

# Function to analyze the best cannon placements and generate a CSV file
def analyze_best_cannon_placements(sock, output_file):
    top100_games = get_paginated_data(sock, "/api/rank/escaped")
    cannon_placements = {}

    for game_id in top100_games:
        game_info = get_game_info(sock, game_id)
        if game_info:
            cannon_placement = game_info["game_stats"].get("cannons", [])
            escaped_ships = game_info["game_stats"].get("escaped_ships", 0)
            normalized_placement = normalize_cannon_placement(cannon_placement)

            if normalized_placement not in cannon_placements:
                cannon_placements[normalized_placement] = {"count": 0, "total_escaped": 0}

            cannon_placements[normalized_placement]["count"] += 1
            cannon_placements[normalized_placement]["total_escaped"] += escaped_ships

    sorted_placements = sorted(
        ((placement, stats["total_escaped"] / stats["count"])
        for placement, stats in cannon_placements.items()),
        key=lambda x: x[1]
    )

    # Create a CSV file for cannon placements without headers
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(sorted_placements)
    
    return sorted_placements

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: ./client <IP> <port> <analysis> <output>")
        sys.exit(1)

    IP = sys.argv[1]
    PORT = int(sys.argv[2])
    ANALYSIS = int(sys.argv[3])
    OUTPUT_FILE = os.path.join(os.path.abspath(os.path.curdir), sys.argv[4]) # Output file path
 
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((IP, PORT))
        
        if ANALYSIS == 1:
            analyze_gas_best_performance(sock, OUTPUT_FILE)
        elif ANALYSIS == 2:
            analyze_best_cannon_placements(sock, OUTPUT_FILE)
        else:
            print("Invalid analysis option. Use 1 or 2.")
            sys.exit(1)

    print(f"Analysis completed. Results saved to {OUTPUT_FILE}")
