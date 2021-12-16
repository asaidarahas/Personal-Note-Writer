#test image generator --> save image to easily accessible folder

import tkinter as tk
from PIL import Image,ImageDraw
from PIL import EpsImagePlugin
import io
import ghostscript
EpsImagePlugin.gs_windows_binary =  r"C:\Program Files\gs\gs9.55.0\bin\gswin64.exe" 

#initialize the window
class ImageGenerator:
    def __init__(self,parent,posx,posy,*kwargs):
        self.parent = parent
        self.posx = posx
        self.posy = posy
        self.sizex = 700
        self.sizey = 700
        self.b1 = "up"
        self.xold = None
        self.yold = None 
        self.drawing_area=tk.Canvas(self.parent,width=self.sizex,height=self.sizey)
        self.drawing_area.place(x=self.posx,y=self.posy)
        self.drawing_area.bind("<Motion>", self.motion)
        self.drawing_area.bind("<ButtonPress-1>", self.b1down)
        self.drawing_area.bind("<ButtonRelease-1>", self.b1up)
        self.button=tk.Button(self.parent,text="Done!",width=10,bg='white',command=self.save_file)
        self.button.place(x=self.sizex/7,y=self.sizey+20)
        self.button1=tk.Button(self.parent,text="Clear!",width=10,bg='white',command=self.clear)
        self.button1.place(x=(self.sizex/7)+80,y=self.sizey+20)

        self.image=Image.new("RGB",(700,700),(255,255,255))
        self.draw=ImageDraw.Draw(self.image)

    #save the image off the canvas
    def save_file(self):
      
        self.drawing_area.update()
        ps = self.drawing_area.postscript(colormode='color')
        img = Image.open(io.BytesIO(ps.encode('utf-8')))
        img.save(r"C:\Users\Peter McGurk\Desktop\Cornell\ECE MEng\Embedded OS\Final Project\test_img.jpg")

    def clear(self):
        self.drawing_area.delete("all")
        self.image=Image.new("RGB",(700,700),(255,255,255))
        self.draw=ImageDraw.Draw(self.image)

    def b1down(self,event):
        self.b1 = "down"

    def b1up(self,event):
        self.b1 = "up"
        self.xold = None
        self.yold = None
        
    #code to draw lines
    def motion(self, event):
      
     if self.b1 == "down":
            if self.xold and self.yold:
                self.drawing_area.create_line(self.xold,self.yold,event.x,event.y,width=10,fill="black",capstyle='round',smooth=True,splinesteps=36)
            self.xold = event.x
            self.yold = event.y

#run code on startup
if __name__ == "__main__":
    root=tk.Tk()
    root.wm_geometry("%dx%d+%d+%d" % (1000, 1000, 10, 10))
    root.config(bg='white')
    ImageGenerator(root,10,10)
    root.mainloop()