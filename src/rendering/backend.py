"""Load CMU Graphics only when drawing; logic imports remain headless."""

def drawImage(*args, **kwargs):
    from cmu_graphics import drawImage as draw
    return draw(*args, **kwargs)

def drawRect(*args, **kwargs):
    from cmu_graphics import drawRect as draw
    return draw(*args, **kwargs)

def drawLabel(*args, **kwargs):
    from cmu_graphics import drawLabel as draw
    return draw(*args, **kwargs)

def rgb(*args, **kwargs):
    from cmu_graphics import rgb as draw
    return draw(*args, **kwargs)
