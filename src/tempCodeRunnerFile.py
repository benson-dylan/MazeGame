def start_game():
        if not glfw.init():
            raise Exception("Failed to initialize GLFW")
        window = initialize_glfw()
        if window is None:
            raise Exception("Failed to create GLFW window")
        myApp = App(window)
        return myApp.mainLoop()