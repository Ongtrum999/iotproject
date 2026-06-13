from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI()

class TimerRequest(BaseModel):
    text: str

@app.post("/parse_time")
def parse_time(req: TimerRequest):
    text = req.text.lower()
    seconds = 0
    
    # Logic bóc tách số phút và giây từ câu nói tiếng Anh
    match_min = re.search(r'(\d+)\s*minute', text)
    match_sec = re.search(r'(\d+)\s*second', text)
    
    if match_min:
        seconds += int(match_min.group(1)) * 60
    if match_sec:
        seconds += int(match_sec.group(1))
        
    return {"seconds": seconds}