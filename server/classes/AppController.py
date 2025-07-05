from flask import Request
from io import BytesIO
from PIL import Image
from functions.resize_image import resize_image
from functions.flat_matrix import flat_image
from classes.AppApiConnector import AppApiConnector
from functions.matrix_to_image import matrix_to_image
from classes.HSV import HSV
from functions.rgb_image_to_hsv import rgb_matrix_to_hsv
from functions.hsv_matrix_to_rgb import hsv_matrix_to_rgb
from functions.rotate_matrix import rotate_matrix
from functions.flip_matrix_horizontal import flip_matrix_horizontal
from functions.flip_matrix_vertical import flip_matrix_vertical
from functions.image_to_matrix import image_to_matrix

class NoImageSentException(Exception):
    pass

class WrongExtensionsOfImageException(Exception):
    pass

class AppController:
    def __init__(self, IP: str, ALLOWED_EXTENSIONS: set|list|tuple, ANIMATED_ALLOWED_EXTENSIONS: list|tuple|set, width: int, height: int, appApiConnector:AppApiConnector):
        self.IP = IP
        self.ALLOWED_EXTENSIONS = ALLOWED_EXTENSIONS
        self.ANIMATED_ALLOWED_EXTENSIONS = ANIMATED_ALLOWED_EXTENSIONS
        self.width = width
        self.height = height
        self.appApiConnector = appApiConnector
    
    def allowd_file(self, filename: str, extensions: list|tuple|set):
        return '.' in filename and filename.rsplit('.', 1)[-1].lower() in extensions
    
    def post_image(self, image: Image, filename: str, hsv: HSV, rotation_mode: int, flip_horizontal: int, flip_vertical: int):
        
        if self.allowd_file(filename, self.ALLOWED_EXTENSIONS):
            image = self.addapt_image(image, hsv, rotation_mode, flip_horizontal, flip_vertical)
            self.appApiConnector.send_image(self.IP, image)
        
        elif self.allowd_file(filename, self.ANIMATED_ALLOWED_EXTENSIONS):
            animeted_image = self.addapt_animated_image(image, hsv, rotation_mode, flip_horizontal, flip_vertical)
            self.appApiConnector.send_animated_image(self.IP, animeted_image)
        
        else:
            raise WrongExtensionsOfImageException

    def addapt_image(self, image: Image, hsv: HSV, rotation_mode: int, flip_horizontal: int, flip_vertical: int):
        
        image.convert("RGBA")
        image = image_to_matrix(image)
        
        if rotation_mode:
            image = rotate_matrix(image, rotation_mode)
            
        if flip_horizontal:
            image = flip_matrix_horizontal(image)
        
        if flip_vertical:
            image = flip_matrix_vertical(image)
            
        if len(image) != 32 and len(image[0]) != 64:
            image = resize_image(image, self.width, self.height)
        
        if not hsv.is_empty():
            image = self.add_to_matrix_with_hsv(image, hsv) 
            
        image = flat_image(image, self.width, self.height)
        return image

    def add_to_matrix_with_hsv(self, image: list[list[int,int,int]], hsv: HSV):
        image = rgb_matrix_to_hsv(image)
        
        for y in range(len(image)):
            for x in range(len(image[0])):
                image[y][x] = (
                              (image[y][x][0] + hsv.hue) if (image[y][x][0] + hsv.hue) < 360 else (image[y][x][0] + hsv.hue - 360), 
                               min(max(image[y][x][1] + hsv.saturation, 0),100), 
                               min(max(image[y][x][2] + hsv.value, 0), 100)
                               )

        image = hsv_matrix_to_rgb(image)
        
        return image

    def addapt_animated_image(self, image: Image, hsv: HSV, rotation_mode: int, flip_horizontal: int, flip_vertical: int):        
        frames = []   

        image_copy = image.copy().convert("RGBA") # idk why ask pil developers bc i cant get diff method to get first frame aaaaaa gotta kms
        first_frame = self.addapt_image(image_copy, hsv, rotation_mode, flip_horizontal, flip_vertical)
        frames.append({"duration": image_copy.info["duration"]/1000, "frame": first_frame})

        try:
            while 1:
                image.seek(image.tell() + 1)
                # duration = image.info["duration"]
                image.convert("RGBA")
                frame = self.addapt_image(image, hsv, rotation_mode, flip_horizontal, flip_vertical)
                frames.append({"duration": image.info["duration"]/1000, "frame": frame})
        except EOFError:
                pass
        
        return frames
                

