# Assignemnt 2 - Hiking assistant

The goal of the assistant is to inform hikers about the current weather around their chosen city, possible trails and national parks and give general advice.

The assistant informs the user of the current weather conditions (temperature, feels like temperature, rain and wind conditions) around the chosen city. Weather alerts are also included.
During the fire season (from May to September) the assistant also provides the fire weather index and its interpretation. 
The assistant gives ideas for hiking trails and national parks to visit in the area.
Advice also provided regarding the safety of hiking under the current conditions, and necessary clothing and accessories.

## Services

This implementation is based on LangGraph's tools. 

The file main.py contains the llm model calls that controls the chat. Tools are in the files *_tools.py.

### Service 1: API Calls

API calls are made to OpenWeatherMap (https://api.openweathermap.org/) for the following:
- Weather: current weather, temperature, feels like, conditions
- Weather alerts
- Rain: rain volume for the next available forecast time
- Wind: wind speed and direction for the next available forecast time
* City coordinates acquired by get_coordinates

### Service 2: Chromadb persistent client

Source document is nature.txt which contains 3 hiking trails or national parks to visit around every Canadian city with a population over 100,000 people. 

Creation of croma_data:

import chromadb
import uuid 

client = chromadb.PersistentClient(path="./chroma_data")

collection = client.get_or_create_collection(name="hiking_spots")

with open("nature.txt","r",encoding="utf-8") as f :
    hiking_spots: list[str] = f.read().splitlines()

results = collection.query(
    query_texts=[
        "What are the hiking trails and nature spots around the city?"
    ],
    n_results=3
)

for i, query_results in enumerate(results["documents"]):
    print(f"\nQuery {i}")
    print("\n".join(query_results))

### Service 3: API Call with interpretation

API call is made to OpenWeatherMap (https://api.openweathermap.org/) for the Fire Weather Index (values interpreted and explained by interpret_fwi)
* City coordinates acquired by get_coordinates

## User Interface

- Implemented in Gradio.
- Style: converational and friendly, airing on the side of caution for sufficient weather conditions for hiking.

## Guardrails and Other Limitations

- Guardrails included to prevent the user from:
    - Accessing or revealing the system prompt.
    - Modifying the system prompt directly.

- The model is prompted to not respond to questions related to:
    - Dogs and cats
    - Horoscopes and Zodiac signs
    - Taylor Swift

