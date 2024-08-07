import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import socket

# Import your existing functions here
from client import analyze_gas_best_performance, analyze_best_cannon_placements

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_items(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# route to call the client functions to use BridgBuff
@app.post("/sendParametersToBridgeBuffClient", response_class=HTMLResponse)
async def analyze(request: Request):
    form = await request.form()
    ip = form.get('ip')
    port = int(form.get('port'))
    analysis_type = form.get('analysis')
    output_file = form.get('output')
    output_file = os.path.join('..', 'output_data', output_file) # Output file path

    # Connect to the client functions (running fastpi) and perform the analysis
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))

        infoToHTML = ''
        
        if analysis_type == '1':
            result_message  = analyze_gas_best_performance(sock, output_file)

            for info in result_message:
                infoToHTML += f"<div>Gas: {info[0]}</div>"
                infoToHTML += f"<div>Games: {info[1]}</div>"
                infoToHTML += f"<div>Average sunk ships: {info[2]}</div>"
                infoToHTML += "<br>"

        elif analysis_type == '2':
            result_message = analyze_best_cannon_placements(sock, output_file)

            for info in result_message:
                infoToHTML += f"<div>Normalized cannon placement: {info[0]}</div>"
                infoToHTML += f"<div>Average number of escaped: {info[1]}</div>"
                infoToHTML += "<br>"

        else:
            return HTMLResponse(content="Invalid analysis type", status_code=400)

    # return a html page with results
    html_content = f"""
    <html>
        <head>
            <title>Results</title>
        </head>
        <body>
            <h1>Results BridgeBuff</h1>
            <div id="result">{infoToHTML}</div>
            <div>
                <a href="/">Go back to the index page</a>
            </div>
        </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)