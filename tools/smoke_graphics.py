"""Render all game screens offscreen with real CMU Graphics; no camera access."""
import os,sys
from pathlib import Path
os.environ['CI']='1'
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
CMU_GRAPHICS_NO_UPDATE = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from engine.state import initialstats
from levels.state import level1initialstat,level2initialstat
from rendering.screens import redrawAll
import cmu_graphics
from cmu_graphics import app
count=0

def onAppStart(app):
    app.levelUnlock=[0,1,2]
    app.levelLocked=[]
    app.useHandGestures=False
    app.instructionScreenActive=False
    initialstats(app)
    app.stepsPerSecond=30

def onStep(app):
    global count
    modes=['desktopInitialize','levelSelection','level0','level1','level2']
    if count>=len(modes):
        print('Actual CMU renderer passed all five screens', flush=True)
        cmu_graphics.app._app.quit()
        return
    initialstats(app)
    app.gamemode=modes[count]
    if count in (2,3): level1initialstat(app)
    if count==4: level2initialstat(app)
    count+=1

print('CMU loaded from:',cmu_graphics.__file__,flush=True)
cmu_graphics.runApp()
assert count==5
