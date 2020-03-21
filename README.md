# simple_api

Simple API implementation to find available rentals in NYC.

Documentation was generated using Pycco (not needed to run the API).

## How to get started. (Linux/Unix)

1. Install Python3 and pip
2. Run command `pip install -r requirements.txt` to install all python dependencies
    - or `pip3 install -r requirements.txt` depending on your setup.
3. (Optional) Load data onto the database using `python3 data_connection.py path_to_csv_file.csv`
4. Use the "run.sh" script to start up Flask service
5. (Optional) Run "curltest.sh" to do quick curl API calls.

## Description

Main focus:

- Distance calculations and finding coordinates wihtin a certain zone.
  - Spent a lot of time trying to do calculations on paper.
  - Decided to just look up a solution online to implement a solution more quickly.
  - Links below on sources.
- Query search using Python and Data input into a data structure or database.
  - Originally planned for MongoDB due to schemaless inputs.
  - Was having problems connecting to my MongoDB
  - Decided to just dump everything into a Dictionary for now, just ran out of time to fully implement.
  - Tried to use standard Pythong libraries to digest into, but csv lib had issues with special characters (as warned by requirements)
  - Created a function to manual process the CSV input line by line.
- Supportability and Maintainability
  - Starting programming it out, and the source files were becoming really large.
    - Large within the context of the amount of lines.
  - Broke the code into smaller functions after that.
  - Dumped a lot of thoughts into the comments to explain why
- Flask API Library usage
  - Personally I'm more familiar with CherryPy because of it's simplicity.
  - Tried out Flask because of it's popularity
  - Flask is also a werkzeug wrapper.
- Please see docs/*.html for my other thoughts during development.

## Example queries:

```BASH
# Given example of query test 1
curl -i -H "Content-Type: application/json" -X GET  -d '{"latitude": 40.7306, "longitude": -73.9352, "distance": 1000, "query": "two bedroom"}' http://127.0.0.1:5000/findnearby

# Given example of query test 2
curl -i -H "Content-Type: application/json" -X GET  -d '{"latitude": 41, "longitude": -73, "distance": 300.7, "query": "near the empire state building"}' http://127.0.0.1:5000/findnearby

# Quick test ot test out fuzzy search
curl -i -H "Content-Type: application/json" -X GET  -d '{"latitude": 40.70485, "longitude": -74, "distance": 1000, "query": "Beautiful duplex with terrace."}' http://127.0.0.1:5000/findnearby

# Quick test to add rental information
# As Long as ID exists, it will pass (as of right now.)
curl -i -H "Content-Type: application/json" -X PUT -d '{"id": 938472938728, "hello":"world"}' http://127.0.0.1:5000/addrental
```

## Sources and Libraries

[Flask API Documentation](https://flask.palletsprojects.com/en/1.1.x/)

[Github: Fuzzy Wuzzy Search Lib](https://github.com/seatgeek/fuzzywuzzy)

[StackOverflow: Calculate Distance between 2 Coordinates](https://stackoverflow.com/questions/837872/calculate-distance-in-meters-when-you-know-longitude-and-latitude-in-java)

[StackOverflow: Given Start Coordinate, Bearing, and Distance, Find End Coordinate](https://stackoverflow.com/questions/7222382/get-lat-long-given-current-point-distance-and-bearing)

[Documentation Generator: Pycco](https://pycco-docs.github.io/pycco/)

## Requirements

- Project Suggestions
  - Appreciate clean, well-documented code
  - See how you approach problems and make tradeoffs.
  - Discuss your design and architecture choices as we are to see a working app.
  - Run out of time, then focus on what's important.

- API Requirements
  - Basic Serach API
  - requests made to find a room to rent.

- Whatever DB system
  - NOSQL datastore
  - Search platform
  - something custom.

- Python (werkzeug) for services.
  - Parse and import data often
  - subtle issues in formatting or serialization.
  - provided data in form of CSV.
  - Response from API: structured list of data
  - rooms that match api request

- API Request:
  - search string
  - latitude and/or longitude
  - distance in meters
  - Results should be rooms within a distance radius from provided location.
  - text part of query works up to developer. Hint: Be creative.
  - Always have results.
  - order data useful to a user.

- Open source libraries or frameworks.
  - properly attribute other people's work.

- Submission.
  - Create Github repository
  - Relevant instructions on how to run it.
  - Share link to the repository
  - Include a description of the application.
