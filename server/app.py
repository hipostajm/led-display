from flask import Flask
from flask import request
from flask import redirect
import requests
from PIL import Image
from sys import path
from werkzeug.utils import secure_filename
from PIL import Image
from io import BytesIO
from functions.resize_image import resize_image
from functions.flat_matrix import flat_image
from classes.AppApiConnector import AppApiConnector
from classes.AppController import AppController 
from classes.AppController import NoImageSentException
from classes.AppController import WrongExtensionsOfImageException
from classes.HSV import HSV

path.append("")


IP = "http://192.168.1.41:5000"
height, width = requests.get(url=IP+"/size/", verify=False).json().values()

app = Flask(__name__)

ALLOWED_EXTENSIONS = {"jpg", "png", "webp", 'jpeg'}
ANIMATED_ALLOWED_EXTESIONS = {"gif",}

appApiConnector = AppApiConnector()
appController = AppController(IP, ALLOWED_EXTENSIONS, ANIMATED_ALLOWED_EXTESIONS, width, height, appApiConnector) 
 

@app.get("/")
def get_home():
    return app.redirect("/image/"), 200

@app.get("/image/")
def get_image():
    with open("./html/image-form.html") as form:
        return form.read() 

@app.post("/image/")
def post_image():

    try:
        if "image" not in request.files:
            raise NoImageSentException

        file = request.files["image"]
        
        hue = int(request.form["hue"])
        saturation = int(request.form["saturation"])
        value = int(request.form["value"])
        
        rotation_mode = int(request.form["rotate"])
        flip_horizontal = 1 if "flip-horizontal" in request.form else 0
        flip_vertical = 1 if "flip-vertical" in request.form else 0        
        
        hsv = HSV(hue, saturation, value)
                
        image = Image.open(BytesIO(file.stream.read()))
        appController.post_image(image, file.filename, hsv, rotation_mode, flip_horizontal, flip_vertical)
        return app.redirect("/image/"), 200
    except NoImageSentException:
        return "No image was sended ;(", 400
    except WrongExtensionsOfImageException:
        return "Wrong Extesion of image ;(", 400
    # except:
        # return "some error happend idk what :3c", 500
        
@app.get("/draw/")
def draw_image():
    css = """  
    
*{
    padding: 0;
    margin: 0;
}
     
table, th, td{
    border: solid 2px black;
}

td{
    width: 20px;
    height: 20px;
    padding: 0; 
}

button{
    width: 100%;
    height: 100%;
    border: 0;
    margin: 0;
    padding: 0;
}

button:hover{
    cursor: pointer;
}
}"""
    
    js = """
    const draw = (x, y, color) =>{
    fetch("http://192.168.1.41:5000/set/", {
        method: "POST",
        body: JSON.stringify({
            "x": x,
            "y": y,
            "color": color,
        }),
        headers: {
            "Content-type": "application/json",
        }
    })
    }
    """
    
    table = ""
    
    
    for y in range(10):
        tr = "<tr>"
        for x in range(10):
            tr+=f"<td><button onclick=\"draw({x}, {y}, 7)\"></button></td>"
        tr += "</tr>"
        table += tr
            
    html = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>led mask</title>
    <style> 
    
    """ + css + """
    
    </style>
</head>
<body>
    <table>
        """ + table + """
    </table>
    <script>
    """ + js + """
    </script>
</body>
</html>"""

    return html, 200

@app.post("/draw/")
def post_draw():
   ... 
