# Run in (or via) RoboFont

# clear output
from mojo.UI import OutputWindow
OutputWindow().clear()

# imports
import os
import shutil
import tempfile
import defcon
from fontTools.designspaceLib import *


# make sources folder
folder = 'sources'
if os.path.exists(folder):
    shutil.rmtree(folder)
os.makedirs(folder)

# get a ds and font
doc = DesignSpaceDocument()
f = CurrentFont()

#####
# parameters
#####

# do and dont
doSlant = True
# if False these next two are False by default 
doSlant_Back = False
doSlant_Forward = True

doWidths = True # Width? Proportion? 
# same here
doCondensed = True
doExpanded = False

doRotate = False

addCharSetAxis = True

# parameter values

slantFactor = 1 # How much the pixel in the next row will shift in pixel-widths
slantAxisMax = 50 # will be negative if back slant 

condensedFactor = .5
expandedFactor = 2
proportionAxisMin = 50
proportionAxisMax = 150

rotationSteps = 12 # how many masters for full circle?


pixels = []
pixelValues = []

for gn in f.keys():
	if "pixel." in gn:# and "none" not in gn:
		pixels.append(gn)
		pixelValues.append(int(gn.split(".")[1]))
names = {}
for p in pixels:
	g = f[p]
	if g.note:
		names[p] = g.note 


if not doWidths:
	doCondensed = False
	doExpanded = False
if not doSlant:
	doSlant_Forward = False
	doSlant_Back = False


knownLocs = []


#defs

def getMaxCharSets():
    l = list(f.keys())
    c=1
    for i in l:
        if "A." in i:
            c+=1
    return(c)

def addSource(file, locs, doc):
	source = SourceDescriptor()
	source.path = file
	loc = {}
	if "pixel" in locs:
		loc['pixel'] = locs['pixel']
	else:
		loc['pixel'] = 0
	if doSlant:
		if "slant" in locs:
			loc['slant'] = locs['slant']
		else:
			loc['slant'] = 0
	if doWidths:
		if "proportion" in locs:
			loc['proportion'] = locs['proportion']
		else:
			loc['proportion'] = 100
	if doRotate:
		if "rotate" in locs:
			loc['rotate'] = locs['rotate']
		else:
			loc['rotate'] = 0

	# print(loc)
	if loc in knownLocs:
	    print("known!", loc)
	    knownLocs.append(loc)
	source.location = loc
	source.familyName = "Piksels"
	# source.styleName = str(location)
	doc.addSource(source)


# make an axis
a = AxisDescriptor()
a.minimum = 0
a.maximum = max(pixelValues) 
a.default = 0
a.name = "pixel"
a.tag = "PIXL"
# a.labelNames[u'fa-IR'] = u"قطر"
a.labelNames[u'en'] = u"Pixel"
# a.map = [(1.0, 10.0), (400.0, 66.0), (1000.0, 990.0)]
# add it to ds
doc.addAxis(a)



if addCharSetAxis:
    csa = AxisDescriptor()
    csa.minimum = 0
    csa.maximum = getMaxCharSets()-1
    csa.default = 0
    csa.name = "charset"
    csa.tag = "CHAR"
    # a.labelNames[u'fa-IR'] = u"قطر"
    csa.labelNames[u'en'] = u"Character Set"
    # a.map = [(1.0, 10.0), (400.0, 66.0), (1000.0, 990.0)]
    # add it to ds
    doc.addAxis(csa)    



# widths:
if doWidths:
	a = AxisDescriptor()
	if doCondensed:
		a.minimum = proportionAxisMin
	else:
		a.minimum = 100
	if doExpanded:
		a.maximum = proportionAxisMax
	else:
		a.maximum = 100
	a.default = 100
	a.name = "proportion"
	a.tag = "PROP"
	# a.labelNames[u'fa-IR'] = u"قطر"
	a.labelNames[u'en'] = u"Proportion"
	# a.map = [(1.0, 10.0), (400.0, 66.0), (1000.0, 990.0)]
	# add it to ds
	doc.addAxis(a)


# slant
if doSlant:
	a = AxisDescriptor()
	if doSlant_Back:
		a.minimum = -slantAxisMax
	else:
		a.minimum = 0
	if doSlant_Forward:
		a.maximum = slantAxisMax
	else:
		a.maximum = 0
	a.default = 0
	a.name = "slant"
	a.tag = "slnt"
	a.labelNames[u'en'] = u"Slant"
	doc.addAxis(a)

# slant
if doRotate:
	a = AxisDescriptor()
	a.minimum = 0
	a.maximum = 360
	a.default = 0
	a.name = "rotate"
	a.tag = "ROTA"
	a.labelNames[u'en'] = u"Rotate"
	doc.addAxis(a)




for p in pixels:
	# print(p)
	tf = f.copy()
	#tf.removeLayer("achtergrondje")
	tf.removeGlyph("pixel")
	location = int(p.split(".")[1])
	pixel = location

	if location: # means l is not zero:
		tf.features.text = ""
		tf.groups.clear()
		for gn in tf.keys():
			if gn != p:
				tf.removeGlyph(gn)
			else:
				tf[p].name = "pixel"

	if location == 0:
		# fea = open('TheBitmap.fea', "r") 
		# feaText = fea.read()
		# fea.close()
		# tf.features.text = feaText
		for otherPixel in pixels:
			# print(otherPixel)
			if otherPixel != p:
				tf.removeGlyph(otherPixel)
			else:
				tf[p].name = "pixel"


	try:shutil.rmtree("sources/%s.ufo"%p)
	except:pass
	tf.save("sources/%s.ufoz"%p, fileStructure='zip')
	# add as source
	source = SourceDescriptor()
	source.path = "sources/%s.ufoz"%p

	if location == 0:
		source.copyLib = True
		source.copyInfo = True
		source.copyFeatures = True

	loc = dict(pixel=location)
	if doSlant:  loc['slant']     = 0
	if doWidths: loc['proportion']= 100

	source.location = loc
	source.familyName = "Piksels"
	source.styleName = str(location)
	doc.addSource(source)

	#rotate
	if doRotate:
		rotate = tf.copy()
		g = rotate['pixel']
		if g.anchors:
			x,y = g.anchors[0].position[0], g.anchors[0].position[1] 
			#print(x,y)
			for angle in range(int(360/rotationSteps),361,int(360/rotationSteps)):
				g.translate((-x,-y))
				# if g.mark == RED or g.mark==GREEN or g.mark ==BLUE:
				g.rotate(-(360/rotationSteps))
				g.translate((x,y))
				rotate.save("sources/%s_r%s.ufoz"%(p,angle), fileStructure='zip')
				addSource(
					file="sources/%s_r%s.ufoz"%(p,angle),
					locs= {"pixel":pixel, "rotate":angle}, 
					doc=doc
					)

	# slant
	if doSlant:
		if doSlant_Forward:
			forwardSlant = tf.copy()
			for g in forwardSlant:
				for c in g.components:
					offset = list(c.offset)
					adder = offset[1]*slantFactor
					offset[0] += adder
					c.offset = offset
			forwardSlant.save("sources/%s_fw.ufoz"%p, fileStructure='zip')
			addSource(
						file="sources/%s_fw.ufoz"%p,
						locs= {"pixel":pixel,"slant":slantAxisMax}, 
						doc=doc
						)
				


		if doSlant_Back:
			backSlant = tf.copy()
			for g in backSlant:
				for c in g.components:
					offset = list(c.offset)
					adder = offset[1]*slantFactor
					offset[0] += -adder
					c.offset = offset
			backSlant.save("sources/%s_bw.ufoz"%p, fileStructure='zip')
			addSource(
						file="sources/%s_bw.ufoz"%p,
						locs= {"pixel":pixel,"slant":-slantAxisMax}, 
						doc=doc
						)

	# now make a narrow /expanded one
	if doWidths:
		if doCondensed:
			narrow = tf.copy()
			for g in narrow:
				for c in g.components:
					offset = list(c.offset)
					offset[0] *= condensedFactor
					c.offset = offset
				g.width *= condensedFactor
			narrow.save("sources/%s_n.ufoz"%p, fileStructure='zip')
			addSource(
						file="sources/%s_n.ufoz"%p,
						locs= {"pixel":pixel,"proportion":proportionAxisMin}, 
						doc=doc
						)	
	if doExpanded:
		expanded = tf.copy()
		for g in expanded:
			for c in g.components:
				offset = list(c.offset)
				offset[0] *= expandedFactor
				c.offset = offset
			g.width *= expandedFactor
		expanded.save("sources/%s_x.ufoz"%p, fileStructure='zip')
		addSource(
						file="sources/%s_x.ufoz"%p,
						locs= {"pixel":pixel,"proportion":proportionAxisMax}, 
						doc=doc
						)


	# slant
	if doCondensed and doSlant_Forward:
		forwardSlantN = narrow.copy()
		for g in forwardSlantN:
			for c in g.components:
				offset = list(c.offset)
				adder = offset[1]*slantFactor
				offset[0] += adder
				c.offset = offset
		forwardSlantN.save("sources/%s_n_fw.ufoz"%p, fileStructure='zip')
		addSource(
						file="sources/%s_n_fw.ufoz"%p,
						locs= {"pixel":pixel,"proportion":proportionAxisMin, "slant":slantAxisMax}, 
						doc=doc
						)

	if doExpanded and doSlant_Forward:

		forwardSlantX = expanded.copy()
		for g in forwardSlantX:
			for c in g.components:
				offset = list(c.offset)
				adder = offset[1]*slantFactor
				offset[0] += adder
				c.offset = offset
		forwardSlantX.save("sources/%s_x_fw.ufoz"%p, fileStructure='zip')
		addSource(
						file="sources/%s_x_fw.ufoz"%p,
						locs= {"pixel":pixel,"proportion":proportionAxisMax, "slant":slantAxisMax}, 
						doc=doc
						)

	if doCondensed and doSlant_Back:

		backSlantN = narrow.copy()
		for g in backSlantN:
			for c in g.components:
				offset = list(c.offset)
				adder = offset[1]*slantFactor
				offset[0] -= adder
				c.offset = offset
		backSlantN.save("sources/%s_n_bw.ufoz"%p, fileStructure='zip')
		addSource(
						file="sources/%s_n_bw.ufoz"%p,
						locs= {"pixel":pixel,"proportion":proportionAxisMin, "slant":-slantAxisMax}, 
						doc=doc
						)

	if doExpanded and doSlant_Back:	
		backSlantX = expanded.copy()
		for g in backSlantX:
			for c in g.components:
				offset = list(c.offset)
				adder = offset[1]*slantFactor
				offset[0] -= adder
				c.offset = offset
		backSlantX.save("sources/%s_x_bw.ufoz"%p, fileStructure='zip')
		addSource(
						file="sources/%s_x_bw.ufoz"%p,
						locs= {"pixel":pixel,"proportion":proportionAxisMax, "slant":-slantAxisMax}, 
						doc=doc
						)


	tf.close()


# named instances
for gn, name in names.items():
	location = int(gn.split(".")[1])
	# print(location)
	i = InstanceDescriptor()
	i.styleName = "%s" % (name)
	loc = dict(pixel=location)
	if doWidths: loc['proportion'] = 100
	if doSlant: loc['slant'] = 0
	if doRotate: loc['rotate'] = 0
	i.location = loc
	doc.addInstance(i)

	if doCondensed:
		i = InstanceDescriptor()
		i.styleName = "%s %s" % (name, "Condensed")
		loc = dict(pixel=location)
		if doWidths: loc['proportion'] = 63.69
		if doSlant: loc['slant'] = 0
		i.location = loc
		doc.addInstance(i)


doc.write("Piksels.designspace")    





# get GSUB FeatureVariations

# set the values here

axisIndex = 1
nrOfCharSets = getMaxCharSets()-1
RVRNIndex = 0
LookupIndex = 0

step = 1/nrOfCharSets



def getFeatureVariations(LookupIndex):
	feavar = """
    <FeatureVariations>
      <Version value="0x00010000"/>
      """

	FeatureRecord = FR = """      
      <FeatureVariationRecord index="{FVRI}">
        <ConditionSet>
          <ConditionTable index="0" Format="1">
            <AxisIndex value="{axisIndex}"/>
            <FilterRangeMinValue value="{_from}"/>
            <FilterRangeMaxValue value="{_till}"/>
          </ConditionTable>
        </ConditionSet>
        <FeatureTableSubstitution>
          <Version value="0x00010000"/>
          <SubstitutionRecord index="0">
            <FeatureIndex value="{RVRNIndex}"/>
            <Feature>
              <LookupListIndex index="0" value="{LookupIndex}"/>
            </Feature>
          </SubstitutionRecord>
        </FeatureTableSubstitution>
      </FeatureVariationRecord>\n"""

	# assume 0-1 axis
	for FVRI in range(1,nrOfCharSets):

		_from = 1/((nrOfCharSets-1)*2)*(FVRI+(FVRI-1))
		_till = 1/((nrOfCharSets-1)*2)*(FVRI+(FVRI+1))

		if FVRI == nrOfCharSets-1: _till=1

		feavar += (FR.format(
						FVRI=FVRI,
						axisIndex=axisIndex,
						_from=_from,
						_till=_till,
						RVRNIndex=RVRNIndex,
						LookupIndex=LookupIndex))
		LookupIndex += 1
	feavar+="\n    </FeatureVariations>"
	return feavar
		
FeaVar = getFeatureVariations(LookupIndex)
with open("FeatureVariations.ttx", "w+") as file:
	file.write(FeaVar)
