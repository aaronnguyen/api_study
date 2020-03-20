# simple_api

Simple API implementation.

## Requirements

- Project Suggestions
  - Flexibility to this exercise
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

Example queries:

```JSON
{"latitude": 40.7306, "longitude": -73.9352, "distance": 1000, "query": "two bedroom"}
{"latitude": 41, "longitude": -73, "distance": 300.7, "query": "near the empire state building"}
```

- Open source libraries or frameworks.
  - properly attribute other people's work.

- Submission to EarnUp.
  - Create Github repository
  - Relevant instructions on how to run it.
  - Share link to the repository
  - Include a description of the application.
