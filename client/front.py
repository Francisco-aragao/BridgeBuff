import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import socket

# the client developed was used as a library, being called by the front-end
from client import analyze_gas_best_performance, analyze_best_cannon_placements

# the project structure works as follows:
# server is executed (back-end)
# front-end is executed, receiving the user parameters on the web page and calling the client functions
# the client then makes the HTTP requests to the server
# the responses are then returned to the front-end to be returned on the web page

app = FastAPI()

# it is necessary to load a web page in the front-end, so the template (index.html) is loaded to be used by fastapi
templates = Jinja2Templates(directory="templates")

# route to the initial page that loads the index.html
@app.get("/", response_class=HTMLResponse)
async def indexPage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# route to call the client functions to use BridgBuff
@app.post("/sendParametersToBridgeBuffClient", response_class=HTMLResponse)
async def analyze(request: Request):
    form = await request.form() # forms that receives the user input
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

            for info in result_message: # handling the results to display in the web page
                infoToHTML += f"<div>Gas: {info[0]}</div>"
                infoToHTML += f"<div>Games: {info[1]}</div>"
                infoToHTML += f"<div>Average sunk ships: {info[2]}</div>"
                infoToHTML += "<br>"

        elif analysis_type == '2':
            result_message = analyze_best_cannon_placements(sock, output_file)

            for info in result_message: # handling the results to display in the web page
                infoToHTML += f"<div>Normalized cannon placement: {info[0]}</div>"
                infoToHTML += f"<div>Average number of escaped: {info[1]}</div>"
                infoToHTML += "<br>"

        else:
            return HTMLResponse(content="Invalid analysis type", status_code=400)

    # return a simple html page with results
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