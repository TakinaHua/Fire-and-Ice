"""Legacy level-specific floor heights, separated from the event loop.

Stage 2 migration boundary: convert these hand-coded regions to platform
geometry once gameplay-parity tests exist for each level.
"""
def update_ground_levels(app):
    if app.gamemode == 'level0' or app.gamemode == 'level1':
        if (320 <= app.fireboyy <500 or app.platformY>185) and app.fireboyx<860:
            app.fireboyground =350
        if (320 <= app.icegirly <400 or app.platformY>185) and app.icegirlx<860: 
            app.icegirlground = 350 
        if 0 <= app.fireboyy <200 and (app.fireboyx>=180 or app.platformY<=185):
            app.fireboyground = 150
        if 0 <= app.icegirly <200 and (app.icegirlx>=180 or app.platformY<=185):
            app.icegirlground = 150 
        if ((800 <= app.fireboyx <= app.width and app.fireboyy >= 250) or 
            (0 <= app.fireboyx <= 800 and app.fireboyy >= 400)): 
            app.fireboyground = 655
        if ((800 <= app.icegirlx <= app.width and app.icegirly >= 250 ) or 
            (0 <= app.icegirlx <=800 and app.icegirly >=400)):
            app.icegirlground = 655

    if app.gamemode == 'level2':
        
        if ((0 <= app.fireboyx < 309 and 516<=app.fireboyy<700) or 
            (309 <= app.fireboyx < 475 and 230 <= app.fireboyy < 700)):
            app.fireboyground = 645
        if ((0 <= app.icegirlx < 309 and 516 <= app.icegirly<700) or 
            (309 <= app.icegirlx < 475 and 230 <= app.icegirly < 700)):
            app.icegirlground = 645
        if ((525 <= app.fireboyx < 685 and 230 <= app.fireboyy < 700) or 
            (685 <= app.fireboyx and 516 <= app.fireboyy < 700)):
            app.fireboyground = 645
        if ((525 <= app.icegirlx < 685 and 230 <= app.icegirly < 700) or 
            (685 <= app.icegirlx and 516 <= app.icegirly < 700)):
            app.icegirlground = 645

 
        if app.fireboyx<309 and ((app.platformY1>209)or(230<=app.fireboyy<497)):
            app.fireboyground = 460
        if app.icegirlx<309 and ((app.platformY1>209)or(230<=app.icegirly<497)):
            app.icegirlground = 460
        if app.fireboyx>685 and ((app.platformY2>209)or(230<=app.fireboyy<497)):
            app.fireboyground = 460
        if app.icegirlx>685 and ((app.platformY2>209)or(230<=app.icegirly<497)):
            app.icegirlground = 460
 
        if (app.fireboyy < 240) and ((152 <= app.fireboyx < 833) or 
            (app.platformY1 <= 209 and app.platformY2 <= 209)):
            app.fireboyground = 180

        if (app.icegirly < 240) and ((152 <= app.icegirlx < 833) or 
            (app.platformY1 <= 209 and app.platformY2 <= 209)):
            app.icegirlground = 180

