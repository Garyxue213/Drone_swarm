from PIL import Image

def make_transparent():
    # Load the JPEG that has a .png extension
    img = Image.open('webots_swarm/drone.png')
    img = img.convert("RGBA")
    
    datas = img.getdata()
    newData = []
    
    for item in datas:
        # white background threshold
        if item[0] > 230 and item[1] > 230 and item[2] > 230:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    
    img.putdata(newData)
    img.save('webots_swarm/drone_actual.png', "PNG")
    print("Converted and saved to drone_actual.png")

if __name__ == "__main__":
    make_transparent()
