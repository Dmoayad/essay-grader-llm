from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from grading import grade

app = FastAPI()

# class Essay(BaseModel):
    # text: str

class Item(BaseModel):
    name: str
    value: int

class Essay(BaseModel):  # Define a Pydantic model for the incoming JSON
    text: str

@app.post("/grade_essay")
async def grade_essay(essay: Essay):  # Receive JSON and validate with Pydantic
    try:
        text = essay.text  # Access the text from the validated object
        result = grade(text)
        # ... your essay processing logic ...
        # Example (replace with your logic)
        results = {"summary": text}
        return result  # Return a Python dictionary (will be converted to JSON automatically)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

# @app.post("/grade_essay")
# async def grade_essay(text: str):
#     try:
#         result = text
#         return "this is a return" + result
#         # result = grade(essay)
#         # result.pop("essay")
#         # return result["summary"]
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.post("/process_data")
async def process_data(item: Item):
    try:
        # ... (your data processing logic as before) ...
        return {"message": "Item added successfully", "item": item}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

# This is important!  Only run the Uvicorn server when this file is executed directly.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
