import arrr
from pyscript import document
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles


def translate_english(event):
    input_text = document.querySelector("#english")
    english = input_text.value
    output_div = document.querySelector("#output")
    output_div.innerText = arrr.translate(english)
app = FastAPI()

# Mount the static directory to serve static files
app.mount("/static", StaticFiles(directory="./"), name="interface")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("./interface.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.post("/my_function")
async def my_function(request: Request):
    data = await request.json()
    message = data.get("message", "No message received")
    response_message = f"Received message: {message}"
    return JSONResponse({"message": response_message})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=7000, log_level="info")