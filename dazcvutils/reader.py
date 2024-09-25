import os
import orjson

with open("data.json", "r", encoding="utf-8") as f:
    content = orjson.loads(f.read())
    
