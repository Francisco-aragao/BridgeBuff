import json
from fastapi import FastAPI, Response, status

PATH_DB = '../data/scores.json'
app = FastAPI()

# Function to fix the JSON format of the database
def transformDBToListfDicts():
    with open(PATH_DB, 'r') as file:
        content = file.read()
    
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

    if (id < 0 or id > len(DATA_FORMATTED)):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"Please, inform a valid game ID"}
    
    for game in DATA_FORMATTED:
        if (game['id'] == id):
            gameInfo['game_id'] = id
            gameInfo['game_stats'] = game
            response.status_code = status.HTTP_200_OK

            return gameInfo

if __name__ == "__main__":
    print("To run the server, use the command --> fastapi dev server.py")
