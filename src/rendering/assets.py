"""rendering / assets extracted from the original game."""
from pathlib import Path



def getAssetPath(path):
    """Resolve assets against src, independent of the working directory."""
    return str(Path(__file__).resolve().parents[1] / "Team project" / "game it self" / path)


def doorInfo(app):
    doorBoy = getAssetPath('doors/doorboy.png')
    dbwid, dbhei = imageSize(doorBoy)

    doorGirl = getAssetPath('doors/doorgirl.png')

    doorinside = getAssetPath('doors/doorinside.png')
    doorout = getAssetPath('doors/doorout.png')
    dowid, dohei = imageSize(doorout)

    spacing = app.width / (app.totalLevel + 1)
    return (dbwid, dbhei, dowid, dohei, spacing,
            doorBoy, doorGirl, doorinside, doorout)


def imageSize(path):
    """Read dimensions without retaining an open image file."""
    from PIL import Image
    with Image.open(path) as image:
        return image.size
