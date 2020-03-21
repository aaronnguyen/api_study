#!/usr/bin/env bash

# Given example of query test 1
curl -i -H "Content-Type: application/json" -X GET  -d '{"latitude": 40.7306, "longitude": -73.9352, "distance": 1000, "query": "two bedroom"}' http://127.0.0.1:5000/findnearby

# Given example of query test 2
curl -i -H "Content-Type: application/json" -X GET  -d '{"latitude": 41, "longitude": -73, "distance": 300.7, "query": "near the empire state building"}' http://127.0.0.1:5000/findnearby

# Quick test ot test out fuzzy search
curl -i -H "Content-Type: application/json" -X GET  -d '{"latitude": 40.70485, "longitude": -74, "distance": 1000, "query": "Beautiful duplex with terrace."}' http://127.0.0.1:5000/findnearby

# Quick test to add rental information
# As Long as ID exists, it will pass (as of right now.)
curl -i -H "Content-Type: application/json" -X PUT -d '{"id": 938472938728, "hello":"world"}' http://127.0.0.1:5000/addrental