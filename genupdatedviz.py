import pandas as pd
import numpy as np
from os import path
from pykml import parser
from lxml import etree
kml_file = "hawaiiwithtl.kml"

def convert_hex(arr):
    addzero = False
    if arr < 16:
        addzero = True
    arr = hex(int(arr))
    arr = arr[2:]
    if addzero:
        arr = '0' + arr
    return arr

def get_scaling(importance):
    return minsize + importance*(maxsize-minsize)

def get_hex_colour(importance):
    diff = hotcolour - coldcolour
    colour = (diff*importance + coldcolour).round()
    hex_array = np.vectorize(convert_hex)(colour)
    return "ff" + "".join(hex_array.tolist())


def get_new_style(importance, colourid, basicstyle):
    copiedstyle = basicstyle.__deepcopy__(basicstyle) #apparently this deepcopies it. Not sure what the basicstyle in the brackets does, but without it I get an error
    copiedstyle.attrib['id'] = "SubStyle" + colourid
    copiedstyle.IconStyle.color._setText(colourid.upper())
    copiedstyle.LabelStyle.color._setText(colourid.upper())
    newscale = get_scaling(importance)
    copiedstyle.IconStyle.scale = newscale
    copiedstyle.LabelStyle.scale = newscale
    return copiedstyle

def get_style_map(colourid, basicstylemap):
    copiedstylemap = basicstylemap.__deepcopy__(basicstylemap)
    copiedstylemap.attrib['id'] = "SubMap" + colourid
    for pair in copiedstylemap.Pair:
        if pair.key.text == 'normal':
            pair.styleUrl._setText('#SubStyle' + colourid)
    return copiedstylemap

def findOccurrences(s, ch):
    return [i for i, letter in enumerate(s) if letter == ch]

with open(kml_file) as f:
    doc = parser.parse(f)

root = doc.getroot()
root.Document.Folder.visibility._setText('1') #set the visibility to one (default might be zero)

buslist = pd.read_csv('busimportance.csv')
maximportance = buslist['busimportance'].max()
buslist['busimportance'] = buslist['busimportance']/maximportance #normalize bus importances




global hotcolour
hotcolour = np.array([0, 0, 255]) #define important colour here
global coldcolour
coldcolour = np.array([255, 0, 0]) #define less important colour here


global minsize #set the scale
global maxsize
minsize = 0.4
maxsize = 1.5

iconn = 'http://maps.google.com/mapfiles/kml/shapes/target.png'
basicstyle = root.Document.Style
for i in basicstyle:
    styletype = i.attrib['id']
    if 'Line' in styletype:
        i.IconStyle.color._setText('00000000')
        i.LabelStyle.color._setText('00000000')
        linewidth = i.LineStyle.width.text
        i.LineStyle.width._setText(str(2*float(linewidth)))
        colour = i.LineStyle.color.text
        colour = 'FF' + colour[2:]
        i.LineStyle.color._setText(colour)
    i.IconStyle.Icon.href._setText(iconn)
    tochange = i.BalloonStyle
    tochange['text']._setText('<b><font color="#CC0000" size="+1">$[name]</font></b><br/><br/><b><u>Description</u></b><br/>$[description]</font><br/>')
    #strr = etree.tostring(tochange, pretty_print=True, encoding="UTF-8")
    #strr = b'<BalloonStyle>\n  <text><![CDATA[<b><font color="#CC0000" size="+1">$[name]</font></b><br/><br/><b><u>Description</u></b><br/>$[description]</font><br/>]]></text>\n</BalloonStyle>\n'
    #i.BalloonStyle = etree.fromstring(strr)
basicstylemap = root.Document.StyleMap
placemarks = root.Document.Folder.Placemark
addedcolours = []

for substation in placemarks:
    substation.visibility._setText('1')
    text = substation.description.text #do .text to convert string element class to a "real" string
    buses = []
    locs = findOccurrences(text, '(') #all buses are preceded by a (
    for loc in locs: #jus get the entire set of numbers before the closing bracket
        added = 2
        while True:
            if text[loc+added] == ')':
                break
            added += 1
        buses.append(int(text[loc+1:loc+added])) #append the number to the list
    importances = buslist[buslist['buses'].isin(buses)]
    subimportance = importances['busimportance'].max()
    colour = get_hex_colour(subimportance) #get the colour relating to that importance
    substation.styleUrl._setText("#SubMap" + colour)
    if colour not in addedcolours:
        newstyle = get_new_style(subimportance, colour, basicstyle)
        newstylemap = get_style_map(colour, basicstylemap)
        root.Document.append(newstyle)
        root.Document.append(newstylemap)
        addedcolours.append(colour)
    text = text.replace('Buses:', 'Buses: <br/>')
    for idx, bus in enumerate(buses):
        altlocs = findOccurrences(text, ')')
        altendloc = text.find('V')
        busimportance = (buslist[buslist['buses'] == bus]['busimportance']).values[0]
        text = text[:altlocs[idx]+2] + 'Importance: ' + str(busimportance.round(3)) + text[altendloc + 1:]
    substation.description._setText(text)



#doc.deannotate(root, cleanup_namespaces=True, xsi_nil=True)
kml_str = etree.tostring(root, pretty_print=True, encoding="UTF-8")

with open("Hawaiikmltogoogleearth.kml", "wb") as f:
    f.write(kml_str)

print("KML file has been written successfully.")



    







