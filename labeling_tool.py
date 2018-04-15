import json

import numpy as np
import cv2


FINAL_LINE_COLOR = (0, 255, 0)

class PolygonDrawer(object):
    def __init__(self, window_name, pic, polygons):
        self.window_name = window_name # Name for our window
        self.polydone = False
        self.dump = False
        # Current position
        # we can draw the line-in-progress
        self.current = (0, 0)
        # List of points defining our polygon
        self.polypoints = []
        self.img = pic.copy()
        self.orig = pic.copy()
        self.polygons = polygons
        if self.polygons:
            for poly in polygons:
                cv2.fillPoly(self.img, np.array([poly]),
                             FINAL_LINE_COLOR)

    def on_mouse(self, event, x, y, buttons, u_args):
        # Mouse callback that gets called for every mouse event

        if self.polydone: # Nothing more to do
            return

        if event == cv2.EVENT_MOUSEMOVE:
            self.current = (x, y)
            
        elif event == cv2.EVENT_LBUTTONDOWN:
            # Left click means adding a point at current position
            # to the list of points
            print("Adding point #%d with position(%d,%d)"
                  % (len(self.polypoints), x, y))
            self.polypoints.append((x, y))
        elif event == cv2.EVENT_RBUTTONDOWN:
        # Right click means deleting last point
            self.polypoints = self.polypoints[:-1]
            print("Removing point #%d" % (len(self.polypoints)))

            self.img = self.orig.copy()
            for poly in self.polygons:
                cv2.fillPoly(self.img, np.array([poly]),
                             FINAL_LINE_COLOR)
            cv2.polylines(self.img, np.array([self.polypoints]),
                          False,
                          FINAL_LINE_COLOR, 1)
        elif event == cv2.EVENT_LBUTTONDBLCLK:
            # Left double click means we're done with polygon
            print("Completing polygon with %d points."
                  % len(self.polypoints))
            self.polydone = True

    def drawPoly(self):
        self.polydone = False
        self.polypoints = []
        
        #  disable a context menu on right button click
        GUI_NORMAL = 16 
        
        # Creating working window
        # set a mouse callback to handle events
        
        cv2.namedWindow(self.window_name,
                        flags=(cv2.WINDOW_NORMAL|GUI_NORMAL))
        cv2.imshow(self.window_name, self.img)
        cv2.setMouseCallback(self.window_name, self.on_mouse)

        while not self.polydone:
            # Continuously draw new images
            # and show them in the named window
            
            if len(self.polypoints) > 1:
                # Draw all the current polygon segments
                cv2.polylines(self.img,
                              np.array([self.polypoints]),
                              False, FINAL_LINE_COLOR, 1)

            # Update the window
            cv2.imshow(self.window_name, self.img)
            
            # Wait 50ms before next iteration
            # (this will pump window messages meanwhile)
            cv2.waitKey(50)

        # User finised entering the polygon points
        # making the final drawing
        # of a filled polygon
        
        if self.polypoints:
            cv2.fillPoly(self.img,
                         np.array([self.polypoints]),
                         FINAL_LINE_COLOR)
        # Show final result
        cv2.imshow(self.window_name, self.img)
        # Waiting for the user to press any key

    def run(self):
        i = 1
        while not self.dump:
            self.drawPoly()
            if len(self.polypoints) == 4:
                self.polygons.append(self.polypoints)
                print("polygon #%d finished"%i)
                i += 1
                confirm = False
            else:
                print("Slot should contains exactly 4 dots. Currently added slot will be removed.")
                self.img = self.orig.copy()
                for poly in self.polygons:
                    cv2.fillPoly(self.img,
                                     np.array([poly]),
                                     FINAL_LINE_COLOR)
                confirm = False
                    
            while not confirm:
                rval = cv2.waitKey(0)
                
                if rval == ord('c'):
                    print("Confirmed")
                    confirm = True
                elif rval == ord('s'):
                    print("Saved")
                    self.dump = True
                    confirm = True
                elif rval == ord('z'):
                    print("Canceled")
                    i -= 1
                    self.polygons = self.polygons[:-1]
                    self.img = self.orig.copy()
                    for poly in self.polygons:
                        cv2.fillPoly(self.img,
                                     np.array([poly]),
                                     FINAL_LINE_COLOR)
                                     
                    cv2.imshow(self.window_name, self.img)
        return self.polygons


def typeOfWork():
    print("Type n to start placing slots or c to continue placing slots")
    while True:
        rval = input()
        if rval == 'n':
            return True
        elif rval == 'c':
            return False
        else:
            print("Invalid input.\nType n for new work or c to continue work")

if __name__ == "__main__":

    global_polygons = []

if typeOfWork():
    # code for new work
    # for new picture one argument - path to picture
    # parse path and pass it to imread method
    print("Print path to image file (includin file).\nEx.:/home/user/folder/image.jpg")
    pathToImg = input()
else:
    # code for continueing work
    # arguments - path to picture and path to json file
    # parse both paths
    # pass picture to imread method and draw all polygons
    print("Print path to image file (includin file).\nEx.:/home/user/folder/image.jpg")
    pathToImg = input()
    print("Print path to json file (includin file).\nEx.:/home/user/folder/labels.json")
    pathToJson = input()
    global_polygons = json.load(open(pathToJson))
    # print(global_polygons)

print("\nTo add point \t\t- left mouse click\nTo cancel point \t- right mouse click\nTo confirm point \t- double left mouse click\nTo confirm changes \t- press C\nTo cancel changes \t- press Z\nTo save coordinates \t- press S")
img = cv2.imread(pathToImg, 1)
pd = PolygonDrawer("Polygon", img, global_polygons)
global_polygons = pd.run()

cv2.destroyWindow(pd.window_name)
for pol in global_polygons:
    cv2.fillPoly(img, np.array([pol]), FINAL_LINE_COLOR)
cv2.imwrite("polygon.png", img)
with open('coords.json', 'w') as f:
    f.write(json.dumps(global_polygons))
print("Polygons = %s" % str(global_polygons))
