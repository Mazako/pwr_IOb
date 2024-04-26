import numpy as np


class Scene:
    """Container class for objects, light and camera."""
    def __init__(
            self,
            objects,
            light,
            camera
    ):
        self.objects = objects
        self.light = light
        self.camera = camera
        self.ambient = np.array([0.1, 0.1, 0.1])
        self.background = np.array([0, 0, 0])
