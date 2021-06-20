from pycocotools.coco import COCO # pip install pycocotools
import requests
import os
import sys
import threading

def makeDirectory(dirName):
    try:
        os.mkdir(dirName)
        print(f"\nMade {dirName} Directory.\n")
    except:
        pass

def getImagesFromClassName(className, image_number = 0):
    makeDirectory(f'downloaded_images/{className}')
    catIds = coco.getCatIds(catNms=[className])
    imgIds = coco.getImgIds(catIds=catIds )
    images = coco.loadImgs(imgIds)

    if image_number != 0:
        count_images = True
        counter = 0
    else:
        count_images = False

    print(f"Total Images: {len(images)} for class '{className}'")

    for im in images:
        if count_images:
            if counter >= image_number:
                print("Downloaded " + str(counter) + " images from " + className)
                break
            counter += 1

        image_file_name = im['file_name']
        label_file_name = im['file_name'].split('.')[0] + '.txt'

        fileExists = os.path.exists(f'downloaded_images/{className}/{image_file_name}')
        if(not fileExists):
            img_data = requests.get(im['coco_url']).content
            annIds = coco.getAnnIds(imgIds=im['id'], catIds=catIds, iscrowd=None)
            anns = coco.loadAnns(annIds)    
            print(f"{className}. Downloading - {image_file_name}")
            for i in range(len(anns)):
                # Yolo Format: center-x center-y width height
                # All values are relative to the image.
                topLeftX = anns[i]['bbox'][0] / im['width']
                topLeftY = anns[i]['bbox'][1] / im['height']
                width = anns[i]['bbox'][2] / im['width']
                height = anns[i]['bbox'][3] / im['height']
                
                s = "0 " + str((topLeftX + (topLeftX + width)) / 2) + " " + \
                str((topLeftY + (topLeftY + height)) / 2) + " " + \
                str(width) + " " + \
                str(height)
                
                if(i < len(anns) - 1):
                    s += '\n'
            
            with open(f'downloaded_images/{className}/{image_file_name}', 'wb') as image_handler:
                image_handler.write(img_data)
            with open(f'downloaded_images/{className}/{label_file_name}', 'w') as label_handler:
                label_handler.write(s)
        else:
           print(f"{className}. {image_file_name} - Already Downloaded.")

argumentList = sys.argv

specify_number = argumentList[-2]
check_number = False

# check if flag is specified
if specify_number == "-number":
    check_number = True
    classes_number = argumentList[-1]
    classes = argumentList[1:-2]
else:
    classes = argumentList[1:]

classes = [class_name.lower() for class_name in classes] # Converting to lower case

if(classes[0] == "--help"):
    with open('classes.txt', 'r') as fp:
        lines = fp.readlines()
    print("**** Classes ****\n")
    [print(x.split('\n')[0]) for x in lines]
    exit(0)     

print("\nClasses to download: ", classes, end = "\n\n")

if check_number:
    print("Downloading " + classes_number + " images from each class")

makeDirectory('downloaded_images')

coco = COCO('instances_train2017.json')
cats = coco.loadCats(coco.getCatIds())
nms=[cat['name'] for cat in cats]


for name in classes:
    if(name not in nms):
        print(f"{name} is not a valid class, Skipping.")
        classes.remove(name)

threads = []

# Creating threads for every class provided.
for i in range(len(classes)):
    if check_number:
        t = threading.Thread(target=getImagesFromClassName, args=(classes[i],int(classes_number),)) 
        threads.append(t)
    else:
        t = threading.Thread(target=getImagesFromClassName, args=(classes[i],)) 
        threads.append(t)
    
for t in threads:
    t.start()

for t in threads:
    t.join()

print("Done.")
