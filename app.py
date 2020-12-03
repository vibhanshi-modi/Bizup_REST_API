from flask import Flask
from flask_restful import Api, Resource, reqparse
from PIL import Image
import requests
from io import BytesIO
import extcolors
import webcolors
import numpy as np
from dominant_color_detection import detect_colors


app = Flask(__name__)
api = Api(app)


class User(Resource):
    def get(self,name):
        colors={}
        if(name=='color_picker'):
            parser = reqparse.RequestParser()
            parser.add_argument("src")
            args = parser.parse_args()
            #url of image is passed as parameter
            url=args["src"]
            border_color_hex_value=self.get_border_color(url)
            colors['logo_border']=border_color_hex_value
            dom_color_hex_val=self.get_dominant_color(url)
            colors['dominant_color']=dom_color_hex_val;
            return colors,200            
        return "No such functionality",404

    def unique_count_app(self,a):
        #returning the rgb tuple that has occured maximum number of times
        colors, count = np.unique(a.reshape(-1,a.shape[-1]), axis=0, return_counts=True)
        return colors[count.argmax()]

    def get_border_color(self,url):
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        height=img.size[0]
        width=img.size[1]
        img=img.convert("RGB") 
        rgb=[]
        #Iterating over a border of 5 pixels and appending the rgb values of each pixel to 'rgb' array
        for i in range(5):
            for j in range(width):
                rgb.append(img.getpixel((i,j)))
        for i in range(height):
            for j in range(width-5,width):
                rgb.append(img.getpixel((i,j)))
        for i in range(height-5,height):
            for j in range(width):
                rgb.append(img.getpixel((i,j)))
        for i in range(height):
            for j in range(5):
                rgb.append(img.getpixel((i,j)))
        rgb=np.array(rgb)
        return webcolors.rgb_to_hex(tuple(self.unique_count_app(rgb)))


    def get_dominant_color(self,url):
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        colors, pixel_count = extcolors.extract_from_image(img) 
        #returns the rgb values, count in descending order, hence considering element at 0th index for most dominant color
        return webcolors.rgb_to_hex(colors[0][0])
      
api.add_resource(User, "/<string:name>")

app.run(debug=True)