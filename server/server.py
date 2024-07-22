import json
from fastapi import FastAPI, Response, status

PATH_DB = '../data/scores.json'
app = FastAPI()

# Function to fix the JSON format of the database
def transformDBToListfDicts():
    try:
        with open(PATH_DB, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        try:
            with open('data/scores.json', 'r') as file:
                content = file.read()
        except FileNotFoundError:
            raise FileNotFoundError("Database file not found in either path.")
    
    # Split the content into individual JSON objects
    json_objects = content.split('\n')
    
    # Convert each JSON object to a dictionary and add to the list
    list_of_dicts = []
    for obj in json_objects:
        if obj.strip():
            list_of_dicts.append(json.loads(obj))
    
    return list_of_dicts

DATA_FORMATTED = transformDBToListfDicts()

# Route to return game status by the game ID informed
@app.get("/api/game/{id}")
def returnGameInfoByID(id: int , response: Response):
    gameInfo : dict = {'game_id': 0, "game_stats": {}}

    if (id < 0):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"Please, inform a valid game ID"}
    
    if (id > len(DATA_FORMATTED)):
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Game with ID " + str(id) + " not found"}
    
    for game in DATA_FORMATTED:
        if (game['id'] == id):
            gameInfo['game_id'] = id
            gameInfo['game_stats'] = game
            response.status_code = status.HTTP_200_OK

            return gameInfo
    
# Route to return a page of games with the largest number of ships sunk
@app.get("/api/rank/sunk")
def returnPageOfGamesByTopSunkShips(limit: int, start:int, response: Response):

    # Verifing parameters values
    if (limit < 0 or limit > 50):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"Please, inform a limit between 0 and 50"}

    if (start < 0):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"Please, inform a valid start value"}
    
    if (start > len(DATA_FORMATTED)):
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Please, inform a start value in the range of the database"}
    
    # Create response object    
    response_content: dict = {'ranking': str, "limit": limit, "start": start, "games": [], "prev": str, "next": str}

    response_content['ranking'] = "sunk"

    # Handling games with not 'sunk_ships' key
    for game in DATA_FORMATTED:
        if (not 'sunk_ships' in game.keys()):
            DATA_FORMATTED.remove(game)            

    # Sorting data by 'sunk_ships' key
    data_sorted = sorted(DATA_FORMATTED, key=lambda x: x['sunk_ships'], reverse=True)

    for i in range(start, start + limit):
        if (i < len(data_sorted)):
            response_content['games'].append(data_sorted[i]['id'])
    
    # Handling prev cases
    startAndLimitInDataRange = (start - limit) >= 0
    startLowerThanLimit = (start - limit) < 0

    if startAndLimitInDataRange:
        response_content['prev'] = "/api/rank/sunk?limit=" + str(limit) + "&start=" + str(start - limit)
    elif startLowerThanLimit:
        response_content['prev'] = "/api/rank/sunk?limit=" + str(start) + "&start=" + str(0)
    else:
        response_content['prev'] = None

    # Handling next cases
    startAndLimitInDataRange = (start + limit) < len(data_sorted)

    if (startAndLimitInDataRange):
        response_content['next'] = "/api/rank/sunk?limit=" + str(limit) + "&start=" + str(start + limit)
    else:
        response_content['next'] = None

    response.status_code = status.HTTP_200_OK
    return response_content

#Route to retrieve a page of games with smallest number of escaped ships

@app.get("/api/rank/escaped")
def returnPageOfGamesByTopEscapedShips(limit: int, start:int, response: Response):

    # Verifing parameters values
    if (limit < 0 or limit > 50):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"Please, inform a limit between 0 and 50"}

    if (start < 0):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"Please, inform a valid start value"}
    
    if (start > len(DATA_FORMATTED)):
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Please, inform a start value in the range of the database"}
    
    # Create response object    
    response_content = {'ranking': str, "limit": limit, "start": start, "games": [], "prev": str, "next": str}

    response_content['ranking'] = "escaped"

    # Handling games with not 'escaped_ships' key
    for game in DATA_FORMATTED:
        if (not 'escaped_ships' in game.keys()):
            DATA_FORMATTED.remove(game)            

    # Sorting data by 'escaped_ships' key
    data_sorted = sorted(DATA_FORMATTED, key=lambda x: x['escaped_ships'], reverse=False)

    for i in range(start, start + limit):
        if (i < len(data_sorted)):
            response_content['games'].append(data_sorted[i]['id'])
    
    # Handling prev cases
    startAndLimitInDataRange = (start - limit) >= 0
    startLowerThanLimit = (start - limit) < 0

    if startAndLimitInDataRange:
        response_content['prev'] = "/api/rank/escaped?limit=" + str(limit) + "&start=" + str(start - limit)
    elif startLowerThanLimit:
        response_content['prev'] = "/api/rank/escaped?limit=" + str(start) + "&start=" + str(0)
    else:
        response_content['prev'] = None

    # Handling next cases
    startAndLimitInDataRange = (start + limit) < len(data_sorted)

    if (startAndLimitInDataRange):
        response_content['next'] = "/api/rank/escaped?limit=" + str(limit) + "&start=" + str(start + limit)
    else:
        response_content['next'] = None

    response.status_code = status.HTTP_200_OK
    return response_content



if __name__ == "__main__":
    print("To run the server, use the command --> fastapi dev server.py")
