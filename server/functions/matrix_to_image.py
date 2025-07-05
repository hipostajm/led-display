from PIL import Image

def matrix_to_image(matrix: list|tuple[list|tuple[int, int, int]]):
    height, width = len(matrix), len(matrix[0])
    
    image = Image.new("RGB", (width, height))
    for y in range(height):
        for x in range(width):
            image.putpixel((x,y), tuple(matrix[y][x]))
            
    return image
    