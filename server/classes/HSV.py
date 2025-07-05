class HSV:
    def __init__(self, hue: int, saturation: int, value: int):
        self.hue = hue
        self.saturation = saturation
        self.value = value
    
    def is_empty(self):
        return self.hue == 0 and self.saturation == 0 and self.value == 0

    def __repr__(self):
        return f"H: {self.hue} S: {self.saturation} V: {self.value}"