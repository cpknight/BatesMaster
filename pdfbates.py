#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# pdfbates.py - PDF Bates Stamper for python3
# ----------------------------------------------------------------------------
# Notes: - This code is subject to a BSD 2-clause licence that appears below.
#        - Credit for original fork to https://github.com/adlukasiak and
#          https://github.com/adlukasiak/BatesMaster 
# ----------------------------------------------------------------------------

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

originalPDF    = PdfFileReader(open(sys.argv[1], "rb"))
numberOfPages  = originalPDF.getNumPages()
pageDimensions = originalPDF.getPage(0).mediaBox
pageHeight     = float(pageDimensions[3]/72)*inch
pageWidth      = float(pageDimensions[2]/72)*inch
pageMargin     = 0.1*inch

stampPositionsOnPage = {
    "top-left"     :{"x":pageMargin            ,"y":pageHeight-(pageMargin*2),  "lambdaFunction": lambda x,y,stampString : pageCanvas.drawString(x,y,stampString)        },
    "top-right"    :{"x":pageWidth-pageMargin  ,"y":pageHeight-(pageMargin*2),  "lambdaFunction": lambda x,y,stampString : pageCanvas.drawRightString(x,y,stampString)   },
    "bottom-right" :{"x":pageWidth-pageMargin  ,"y":pageMargin,                 "lambdaFunction": lambda x,y,stampString : pageCanvas.drawRightString(x,y,stampString)   },
    "bottom-left"  :{"x":pageMargin            ,"y":pageMargin,                 "lambdaFunction": lambda x,y,stampString : pageCanvas.drawString(x,y,stampString)        },
    "bottom-center":{"x":pageWidth/2           ,"y":pageMargin,                 "lambdaFunction": lambda x,y,stampString : pageCanvas.drawCentredString(x,y,stampString) }
  }

pageData = BytesIO()
pageCanvas = canvas.Canvas(pageData,pagesize=(pageWidth,pageHeight))

for i in range(0,numberOfPages):
  numberLength = len("000")  # 3, but code retained for future tweaking
  pageCanvas.setFont("Courier", 10) # need to reset font for each page
  pageCanvas.setFillColorRGB(0.25,0,0) # colour needed for post-conversion to TIFF
  batesNumber = str(pageCanvas.getPageNumber()).zfill(numberLength) 
  stampString = sys.argv[2] + batesNumber
  stampPosition = "top-right"
  stampPositionsOnPage[stampPosition]["lambdaFunction"](stampPositionsOnPage[stampPosition]["x"],stampPositionsOnPage[stampPosition]["y"],stampString)
  pageCanvas.showPage() 

pageCanvas.save()
pageData.seek(0)
newPDF = PdfFileReader(pageData)
outputData = PdfFileWriter()

# add the "watermark" (which is the new pdf) on the existing page
for i in range(0,numberOfPages):
  thisPage = originalPDF.getPage(i)
  thisPage.mergePage(newPDF.getPage(i))
  outputData.addPage(thisPage)

outputDataStream = open((sys.argv[1] + "-bates-numbered.pdf"), "wb")
outputData.write(outputDataStream)
outputDataStream.close()

# ----------------------------------------------------------------------------
# Copyright (c) 2016, Christopher P. Knight. All rights reserved.
#
# Redistribution  and  use  in  source  and  binary  forms,  with or  without 
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of  source  code must retain the above copyright notice, 
#    this list of conditions and the following disclaimer.
# 
# 2. Redistributions  in  binary  form  must  reproduce  the  above copyright 
#    notice,  this list  of  conditions  and  the following disclaimer in the 
#    documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND  ANY  EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE  DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
# LIABLE  FOR  ANY DIRECT,  INDIRECT,   INCIDENTAL,  SPECIAL,  EXEMPLARY,  OR 
# CONSEQUENTIAL  DAMAGES  (INCLUDING,  BUT  NOT  LIMITED  TO, PROCUREMENT  OF 
# SUBSTITUTE  GOODS OR SERVICES;  LOSS OF USE, DATA, OR PROFITS;  OR BUSINESS 
# INTERRUPTION) HOWEVER  CAUSED  AND ON ANY  THEORY OF LIABILITY,  WHETHER IN 
# CONTRACT,  STRICT  LIABILITY,  OR TORT  (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING  IN ANY WAY  OUT OF THE USE  OF THIS  SOFTWARE,  EVEN IF ADVISED OF 
# THE POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------
#                                                                          eof