"""entities / enemies extracted from the original game."""



def ghostMove(app):
    if app.frameCount >= app.ghostActivationTime:
        app.ghostActive = True
    if app.ghostActive:
        if app.ghostX < app.fansX + 40 and app.ghostY > 350:
            app.ghostX += app.ghostSpeed
        elif app.ghostY > 350 and  app.platformX - 180 < app.ghostX:
            app.ghostY -= app.ghostSpeed
        elif app.ghostX > 90 and app.ghostY > 150:
            app.ghostX -= app.ghostSpeed
        elif app.ghostY > 150:
            app.ghostY -= app.ghostSpeed
        elif app.ghostY <= 150 and app.ghostX < 800:
            app.ghostX += app.ghostSpeed
