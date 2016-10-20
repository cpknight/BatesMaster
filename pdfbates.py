#!/usr/bin/env python3

import sys
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from io import BytesIO

if (len(sys.argv) < 3):
  print("Usage: " + sys.argv[0] + " [input PDF] [prefix string]")
  print("   eg. " + sys.argv[0] + " DOC00001.pdf \"DOC00001\"")
  print("   eg. " + sys.argv[0] + " DOC00001.pdf \"\"")
  print("       Notes: - both arguments are mandatory.")
  print("              - output file has \"-bates-numbered.pdf\" appended to the filename.")
  sys.exit(1)

orig_pdf = PdfFileReader(open(sys.argv[1], "rb"))
num_pages = orig_pdf.getNumPages()
page_size = orig_pdf.getPage(0).mediaBox
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
  num_length = len("000")
  canv.setFont("Courier", 10) #need to reset font for each page
  canv.setFillColorRGB(200,0,0)
  bates = str(canv.getPageNumber()).zfill(3) 
  text = sys.argv[2] + bates
  mode = "top-r"
  config[mode]["func"](config[mode]["x"],config[mode]["y"],text)
  canv.showPage() 
canv.save()

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
outputStream = open((sys.argv[1] + "-bates-numbered.pdf"), "wb")
output.write(outputStream)
outputStream.close()
