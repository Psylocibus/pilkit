from pilkit.lib import Image


class ColorOverlay(object):
    """
    Overlay a color mask with a the given opacity
    """

    def __init__(self, color, overlay_opacity=0.5):
        """
        :pamra color: `ImageColor` instance to overlay on the original image
        :param overlay_opacity: Define the fusion factor for the overlay mask

        """
        self.color = color
        self.overlay_opacity = overlay_opacity

    def process(self, img):
        original = img = img.convert('RGB')
        overlay = Image.new('RGB', original.size, self.color)
        mask = Image.new('RGBA', original.size, (0,0,0,int((1.0 - self.overlay_opacity)*255)))
        img = Image.composite(original, overlay, mask).convert('RGB')
        return img


class ImageOverlay(object):
    """
    Overlay an image (i.e watermark) with a given opacity over the original image.
    Position can be :
    - ABSOLUTE coordinate in px
    - RELATIVE coordinate in % of available space
        x=0 will be on the left, 
        x=50 will be centered, 
        x=100 will be on the right
    - GRID coordinate : 
        x = 0 for LEFT, 
        x = 1 for CENTER, 
        x=2 for RIGHT,
        y = 0 for TOP,
        y = 1 for MIDDLE,
        y = 2 for BOTTOM
    """

    AVAILABLE_POSITION_TYPES = [
        "ABSOLUTE",
        "RELATIVE",
        "GRID"
    ]

    def __init__(self, overlay_img:Image, position:tuple[int,int] = (0,0), position_type:str="ABSOLUTE", margin:int=0):
        """
        :param overlay_img: PIL `Image` instance to overlay on the original image
        :param position: coordinate (x,y) of the top left corner of the overlay image on the original image. 
        :param position_type: ABSOLUTE, RELATIVE
        :param margin: size (in px) of the margin that shall not be covered by the overlay image
        """
        self.overlay_img=overlay_img
        self.position_type = position_type
        self.position = position
        self.margin = margin

    def process(self, img):
        #Create the mask (image of same dimension as the original, with the overlay at the right location, with the given opacity)
        mask = Image.new("RGBA",(img.width, img.height),(0,0,0,0)) #transparent image with the same dimensions as original image
        
        #Compute the position of the watermark
        match self.position_type :
            case "ABSOLUTE" :
                paste_position = [int(self.position[0]),int(self.position[1])] #variable that stores the final absolute coordinates
        
            case "RELATIVE" :
                #if relative, coordinates in self.position are a value in percent
                available_width = img.width - self.overlay_img.width - 2*self.margin
                available_height = img.height - self.overlay_img.height - 2*self.margin
                #coordinate of the top left corner is margin+position%*available width
                paste_position = [self.margin+int(self.position[0]*available_width/100),
                                    self.margin+int(self.position[1]*available_height/100)]

            case _:
                #raise error
                raise ValueError("position_type shall be a string in the following list : 'RELATIVE', 'ABSOLUTE'")

        #Paste the overlay image on the mask at the computed location
        mask.paste(self.overlay_img, paste_position) #put the overlay image at the computed location

        #Render the picture overlayed
        if img.mode != "RGBA" :
            tmp = Image.alpha_composite(img.convert("RGBA"), mask) #apply the overlay (both images need to be in "RGBA" mode with alpha_composite())
            img = tmp.convert(img.mode) #convert back to the original mode
        else :
            img = Image.alpha_composite(img, mask)
        return img