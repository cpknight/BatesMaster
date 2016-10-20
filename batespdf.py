#!/usr/bin/env python3

from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from io import BytesIO

orig_pdf = PdfFileReader(open("test.pdf", "rb"))
# print "document1.pdf has %d pages." % input1.getNumPages()
num_pages = orig_pdf.getNumPages()
page_size = orig_pdf.getPage(0).mediaBox

### inputs ####
#font_size = 10
#prefix = "BB"
#starting_number_str = "00067"
# mode = "right" #"left" and "center"

input_config = {
                # "top-l" : {"mode":"top-l" ,"font_size":12,"starting_num":"3","prefix":"TL-"},
                "top-r" : {"mode":"top-r" ,"font_size":10,"starting_num":"000","prefix":"FILENAME."},
                # "left"  : {"mode":"left"  ,"font_size":12,"starting_num":"1","prefix":"LEFT-"},
                # "center": {"mode":"center","font_size":10,"starting_num":"2","prefix":"CENTER-"},
                # "right" : {"mode":"right" ,"font_size":12,"starting_num":"3","prefix":"RIGHT-"},
                }
#input_config = {
#                "left"  : {"mode":"left"  ,"font_size":10,"starting_num":""     ,"prefix":"CONFIDENTIAL - ATTORNEYS EYES ONLY"},
#                "center": {"mode":"center","font_size":10,"starting_num":""     ,"prefix":""},
#                "right" : {"mode":"right" ,"font_size":10,"starting_num":"00067","prefix":""},
#                }

### and figure few things out based on inputs ###
height = float(page_size[3]/72)*inch
width = float(page_size[2]/72)*inch
margin = 0.1*inch

config = {
          "top-l" :{"x":margin        ,"y":height-(margin*2), "func": lambda x,y,text : canv.drawString(x,y,text)},
          "top-r" :{"x":width-margin  ,"y":height-(margin*2), "func": lambda x,y,text : canv.drawRightString(x,y,text)},
          "right" :{"x":width-margin  ,"y":margin, "func": lambda x,y,text : canv.drawRightString(x,y,text)},
          "left"  :{"x":margin        ,"y":margin, "func": lambda x,y,text : canv.drawString(x,y,text)},
          "center":{"x":width/2       ,"y":margin, "func": lambda x,y,text : canv.drawCentredString(x,y,text)}
          }

# the temp file should be same size as the original document
packet = BytesIO()
canv = canvas.Canvas(packet,pagesize=(width,height))

for i in range(0,num_pages):
    for j in input_config:
        
        #figure out few things about the starting number
        num_length = len(str(input_config[j]["starting_num"]))
#        page_number_offset = int(input_config[j]["starting_num"] if input_config[j]["starting_num"] != "" else -1)
#        page_number_offset = int(input_config[j]["starting_num"])

        canv.setFont("Courier", input_config[j]["font_size"]) #need to reset font for each page
        # canv.setStrokeColorRGB(1,0,0)
        canv.setFillColorRGB(200,0,0)
            
#        bates = str(canv.getPageNumber()+page_number_offset).zfill(num_length) if page_number_offset > 0 else ""
        bates = str(canv.getPageNumber()).zfill(3) 
        
        text = input_config[j]["prefix"] + bates
        mode = input_config[j]["mode"]
        # print canv.getPageNumber(),text, width, config[mode]["x"]
    
        config[mode]["func"](config[mode]["x"],config[mode]["y"],text)
    canv.showPage() #move to the next page
canv.save()

# Time to merge
#move to the beginning of the StringIO buffer
packet.seek(0)
new_pdf = PdfFileReader(packet)
# read your existing PDF
output = PdfFileWriter()
# add the "watermark" (which is the new pdf) on the existing page
for i in range(0,num_pages):
    page = orig_pdf.getPage(i)
    page.mergePage(new_pdf.getPage(i))
    output.addPage(page)
# finally, write "output" to a real file
outputStream = open("test_bates.pdf", "wb")
output.write(outputStream)
outputStream.close()
