from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from lib import DE_Best_1, DE_Best_2, DE_Current_Best_1
from pydantic import BaseModel

app = FastAPI()
origins = [
  "http://localhost:3000",
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"]
)

class Requested(BaseModel):
  ps: float
  length_b1_b2: float
  length_b1_b3: float
  ps1: float
  ps2: float
  requested: str


@app.post("/automated")
async def automated(data: Requested):
    ps = data.ps
    length_b1_b2 = data.length_b1_b2
    length_b1_b3 = data.length_b1_b3
    ps1 = data.ps1
    ps2 = data.ps2
    requested = data.requested
    print(ps)
    print(length_b1_b2)
    print(length_b1_b3)
    print(ps1)
    print(ps2)
    print(requested)
    try:
      if(requested == "de_best_1"):
        result = DE_Best_1(ps, length_b1_b2, length_b1_b3, ps1, ps2)
      elif(requested == "de_best_2"):
        result = DE_Best_2(ps, length_b1_b2, length_b1_b3, ps1, ps2)
      elif(requested == "de_current_best_1"):
        result = DE_Current_Best_1(ps, length_b1_b2, length_b1_b3, ps1, ps2)
      # elif(requested == "de_current_rand_1"):
      #   result = DE_Current_Rand_1(ps, length_b1_b2, length_b1_b3, ps1, ps2)
      else:
        raise HTTPException(status_code=400, detail="Your request method has not been accepted!")
      return {"best_all": result.best_all, "k": result.K}
    except Exception as e:
      raise HTTPException(status_code=500, detail="Internal Server Error", error=e)