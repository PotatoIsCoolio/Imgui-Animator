class AnimationKeyframe: 
    def __init__(self, frame, x=0, y=0, rotation=0, scale=1.0, opacity=1.0):
        self.frame = frame
        self.x = x
        self.y = y
        self.rotation = rotation
        self.scale = scale
        self.opacity = opacity
    
    def toDict(self):
        return {
            "frame": self.frame,
            "x": self.x,
            "y": self.y,
            "rotation": self.rotation,
            "scale": self.scale,
            "opacity": self.opacity
        }
    
    @classmethod
    def fromDict(cls, data):
        return cls(
            data["frame"], 
            data["x"], 
            data["y"], 
            data["rotation"], 
            data["scale"], 
            data["opacity"]
        )
