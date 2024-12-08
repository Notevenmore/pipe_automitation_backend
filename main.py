from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from lib import DE_Best_1, DE_Best_2, DE_Current_Best_1, DE_Current_Rand_1, DE_Rand_1_Origin, DE_Rand_2, DE_Rand_Best_1
from pydantic import BaseModel
from encoders import custom_jsonable_encoder as cje

app = FastAPI()

# origins = [
#     "http://127.0.0.1:3001",
#     "http://localhost:3000",  # Ensure this is included for testing
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Make sure this matches the actual domain you're sending requests from
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Requested(BaseModel):
  ps: float
  length_b1_b2: float
  length_b1_b3: float
  ps1: float
  ps2: float
  requested: str


@app.post("/api/automated")
async def automated(data: Requested):
    ps = data.ps
    length_b1_b2 = data.length_b1_b2
    length_b1_b3 = data.length_b1_b3
    ps1 = data.ps1
    ps2 = data.ps2
    requested = data.requested
    print(requested);
    try:
      if(requested == "de_best_1"):
        result = DE_Best_1(ps, length_b1_b2, length_b1_b3, ps1, ps2) # Testing succeed
      elif(requested == "de_best_2"):
        result = DE_Best_2(ps, length_b1_b2, length_b1_b3, ps1, ps2) # Testing succeed
      elif(requested == "de_current_best_1"):
        result = DE_Current_Best_1(ps, length_b1_b2, length_b1_b3, ps1, ps2) # Testing succeed
      elif(requested == "de_current_rand_1"):
        result = DE_Current_Rand_1(ps, length_b1_b2, length_b1_b3, ps1, ps2) # Testing succeed
      elif(requested == "de_rand_1_origin"):
        result = DE_Rand_1_Origin(ps, length_b1_b2, length_b1_b3, ps1, ps2) # Testing succeed
      elif(requested == "de_rand_2"):
        result = DE_Rand_2(ps, length_b1_b2, length_b1_b3, ps1, ps2) # Testing succeed
      elif(requested == "de_rand_best_1"):
        result = DE_Rand_Best_1(ps, length_b1_b2, length_b1_b3, ps1, ps2) # Testing succeed
      else:
        raise HTTPException(status_code=400, detail="Your request method has not been accepted!")
      
      keys = ["ps", "pd", "l", "d", "Q"]

      best_all_converted = [
          dict(zip(keys, row)) for row in result.best_all
      ]

      k_converted = [float(k) for k in result.K]
      
      cost_converted = float(result.cost)
      
      converted_data = {
          "best_all": best_all_converted,
          "k": k_converted,
          "cost": cost_converted
      }
      
      return converted_data
    except Exception as e:
      print(f"Error occurred: {str(e)}")
      raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "ok"}
