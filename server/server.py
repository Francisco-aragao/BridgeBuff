import json
from fastapi import FastAPI

PATH_DB = '../data/scores.json'

# Function to fix the JSON format of the database
def transform_db_list_of_dicts():
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

if __name__ == "__main__":
    print(transform_db_list_of_dicts())
