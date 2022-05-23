import json
from PIL import Image
import imageio
import numpy as np

frameId = 0
def draw_sprite(x, y, frame, nSprite, spriteHeadIm, spriteBodyIm, spriteWidth, spriteHeight, headMaskIm):
    global frameId
    spriteId = int(frameId//5) % nSprite
    currSpriteIm = spriteBodyIm.crop([spriteId*spriteWidth, 0, (spriteId+1)*spriteWidth, spriteHeight])
    currSpriteIm = currSpriteIm.resize([currSpriteIm.size[0]*4,currSpriteIm.size[1]*4])
    frame.paste(currSpriteIm, [x-spriteWidth*2,y-spriteWidth*2-48], currSpriteIm)
    headIm = spriteHeadIm.resize([96,96])
    frame.paste(headIm, [x-headIm.size[0]//2,y-headIm.size[1]//2-48], headMaskIm)

    frameId += 1

def walk_map(walkJsonFilename="walk.json"):

    # load parameters 
    with open(walkJsonFilename, "r") as f:
        walkParam = json.loads(f.read())
    walkPath = walkParam["walkPath"]
    fps = walkParam["param"]["fps"]
    step = walkParam["param"]["step"]
    w = walkParam["param"]["width"]
    h = walkParam["param"]["height"]

    im = Image.open(walkParam["walkMap"]).convert("RGBA")
    size = im.size

    spriteMode = False
    if "sprite" in walkParam.keys():
        spriteMode = True
        spriteBodyIm = Image.open(walkParam["sprite"]["body"]["image"])
        nSprite = walkParam["sprite"]["body"]["nSprite"]
        spriteWidth = walkParam["sprite"]["body"]["width"]
        spriteHeight = walkParam["sprite"]["body"]["height"]
        spriteHeadIm = Image.open(walkParam["sprite"]["head"]["image"])
        headMaskIm = Image.open(walkParam["sprite"]["head"]["mask"])
    
    vOut = imageio.get_writer("walk.mp4", fps=fps)
    for i in range(len(walkPath)-1):
        point1 = np.array(walkPath[i][:-1])
        point2 = np.array(walkPath[i+1][:-1])
        dist = int(np.linalg.norm(point1 - point2))
        tween = np.linspace(point1, point2, int(dist//step)).astype(np.int).tolist()
        for j in range(len(tween)):
            frame = im.crop([tween[j][0]-w//2,tween[j][1]-h//2,tween[j][0]+w//2,tween[j][1]+h//2])
            frame0 = frame.copy()
            draw_sprite(w//2, h//2, frame, nSprite, spriteHeadIm, spriteBodyIm, spriteWidth, spriteHeight, headMaskIm)
            frame = frame.convert('RGB')
            vOut.append_data(np.array(frame))
            if j == len(tween) -1 :
                for k in range(walkPath[i][-1]):
                    frame1 = frame0.copy()
                    draw_sprite(w//2, h//2, frame1, nSprite, spriteHeadIm, spriteBodyIm, spriteWidth, spriteHeight, headMaskIm)
                    frame1 = frame1.convert('RGB')
                    vOut.append_data(np.array(frame1))
    vOut.close()

if __name__ == "__main__":
    walk_map()
