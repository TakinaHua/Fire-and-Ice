from cmu_graphics import *
from PIL import Image

def onAppStart(app):
    app.gamemode = 'desktopInitialize'
    app.fireboystand = 0
    app.width = 1000
    app.height = 700
    app.fireboyx = app.width/3
    app.fireboyy = app.height/2-15
    app.icegirlstand = 0
    app.icegirlx = app.width/3 *2
    app.icegirly = app.height/2
    app.frameCount = 0  
    app.fireboystatus = 'stand'
    app.icegirlstatus = 'stand'
    app.levelselected = 1
    app.level1 = True
    app.level2 = False
    app.level3 = False

def onStep(app):
    app.frameCount += 1
    if app.frameCount % 4 == 0:
        app.fireboystand = (app.fireboystand + 1) % 5
        app.icegirlstand = (app.icegirlstand + 1) % 11


def redrawAll(app):
    if app.gamemode == 'desktopInitialize' :
        desktopInitialize(app)
    elif app.gamemode == 'levelSelection':
        levelSelection(app)

def onKeyPress(app, keys):
    if app.gamemode == 'desktopInitialize':
        if keys == 'up':
            app.gamemode = 'levelSelection'
    if app.gamemode == 'levelSelection' : 
        if keys == 'down':
            app.gamemode = 'desktopInitialize'
    



#character presentations:

def icegirlstand(app):
    imageicegirlbody = 'icegirl/icegirl stand.png'
    drawImage(imageicegirlbody, app.icegirlx-1, app.icegirly + 30, 
                width = 30,height = 30, align = 'center' )   
 
    imageicegirl = f"icegirl/watergirl_face_{app.icegirlstand}.png"
    drawImage(imageicegirl, app.icegirlx, app.icegirly, width = 55, 
                height = 125, align ='center') 

def fireboystand(app):
    imagefireboybody = 'fireboy/fireboy stand.png'
    drawImage(imagefireboybody, app.fireboyx, app.fireboyy + 47, 
                width = 30,height = 30, align = 'center' ) 
 
    imagefireboy = f"fireboy/fireboy stand {app.fireboystand}.png"
    drawImage(imagefireboy, app.fireboyx, app.fireboyy, width = 45, 
                height = 75, align ='center')  



#screens     
def desktopInitialize(app):
    imaageoftitle = 'desktopinitial/titlescreenbackground.png'
    drawImage(imaageoftitle, app.width/2, app.height/2, width=app.width, 
                height=app.height, align = 'center')
    title = 'desktopinitial/FireboyIcegirlTitle.png'
    drawImage(title,app.width/2, app.height/3,width= app.width/3, 
                height =app.height / 8, align = 'center')
    start = 'desktopinitial/Thumbs-Up-to-Start.png'
    drawImage(start,app.width/2, 2*app.height/3, width= app.width/3, 
                height =app.height / 8, align = 'center' )
    fireboystand(app)
    icegirlstand(app)

def levelSelection(app):
    #background = 'levelSelection/levelselectionBackG.jpg'
    #drawImage(background, app.width/2, app.height/2, width=app.width, 
                #height=app.height, align = 'center')
    drawRect(0, 0, app.width, app.height, fill = 'black')
    doorBoy = 'doors/doorboy.png'
    DB = Image.open(doorBoy)
    dbwid, dbhei = DB.size
    drawImage(doorBoy, app.width/2 - dbwid/2-10, 
              app.height/2+5, align = 'center')


    doorGirl = 'doors/doorgirl.png'
    drawImage(doorGirl, app.width/2 + dbwid/2 + 10, app.height/2 +5, 
              align = 'center')
    doorinside = 'doors/doorinside.png'

        
    doorout = 'doors/doorout.png'
    DO = Image.open(doorout)
    dowid, dohei = DO.size
    drawImage(doorout, app.width/2 - dowid/2, app.height/2, align = 'center')
    drawImage(doorout, app.width/2 + dowid/2, app.height/2, align = 'center')


    #if app.doorselected == Ture:
        #drawImage(doorinside, app.width/2 - dbwid/2)






runApp()