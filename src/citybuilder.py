
import maya.cmds as cmds
import random
from functools import partial
import math


#creates the GUI
def UI():

	#check to see if window exists
	if(cmds.window("cityBuilder", exists = True)):
		cmds.deleteUI("cityBuilder")

	#create window
	window = cmds.window("cityBuilder", title = "City Builder", width = 265, height=430, s = False, menuBar = True)
		
	cmds.columnLayout( columnAttach=('both', 5), rowSpacing=10, columnWidth=250 )

	#add fields
	cmds.text(label="City Width", al = "left")
	cityWidth = cmds.textField( tx = "700")

	cmds.text(label="City Depth", al = "left")
	cityDepth = cmds.textField( tx = "700")

	cmds.text(label="Maximum Building Height", al = "left")
	maxBuildingHeight = cmds.textField( tx = "70")

	buildingGap = 2

	streetWidth = 16

	#create a button to build
	cmds.button(label = "Build City", c = partial(cityBuilder, cityWidth, cityDepth, maxBuildingHeight, buildingGap, streetWidth))

	#show window
	cmds.showWindow(window)


#creates cityscape
def cityBuilder(cityWidth, cityDepth, maxBuildingHeight, buildingGap, streetWidth, *args):

	
	#grab the input from the GUI
	cityWidth = int(cmds.textField(cityWidth, q=True, text=True))
	cityDepth = int(cmds.textField(cityDepth, q=True, text=True))
	maxBuildingHeight = int(cmds.textField(maxBuildingHeight, q=True, text=True))

	#define some defaults for the max building sizes
	buildingBaseX = 20
	buildingBaseZ = 20
	buildingMinWidth = 5
	buildingMinHeight = 3
	
	#default counters for spacing the buildings
	xSpace = 0
	biggestX = 0
	counter = 0
	xcounter = 0
		
	#create a group that all of the buildings will be under
	cmds.group( em = True, n = "gen_buildings")
	cmds.group( em = True, n = "street")
	cmds.group( em = True, n = "street")
	cmds.group( em = True, n = "street")

	#create a ground plane
	cmds.polyPlane(w = cityWidth, h = cityDepth, n = "ground")
	cmds.move(cityWidth / 2, 0, cityDepth / 2)
	
	#stores the building objects we'll be creating
	buildings = []
	

	#generate columns
	while(xSpace < cityDepth ):
		
		#reset our z value for every new column
		zSpace = 0
		
		#generate rows
		while(zSpace < cityWidth):
				#store our random values so we can use them later
			height = random.randrange(buildingMinHeight, maxBuildingHeight)
			if(random.randrange(0, 100) > 90):
				height = height + (height * 0.7)
			buildingZ = random.randrange(buildingMinWidth, buildingBaseZ)
			buildingX = random.randrange(buildingMinWidth, buildingBaseX)
				
				#check if this is the biggest building in the row. If it is, set that as the gap between this and the next column
			if(buildingX > biggestX):
				biggestX = buildingX
				
				#check and see if placing the next building will intersect where the street should go
			for z in range(zSpace - 1, zSpace + buildingZ + buildingGap + 1):
						#create the street geometry
				streetSegment = cmds.polyPlane( h = streetWidth, w = biggestX + buildingGap, sx = 1, sy = 1)
				cmds.move( xSpace + (biggestX/2), 0.01, z + (streetWidth/2))
				cmds.parent(streetSegment[0], "street")
				zSpace = z + streetWidth + buildingGap
				break
				
			buildingType = random.randrange(0,3)
			building = Building(buildingX, buildingZ, height, buildingType)
				
			buildings.append(building)
			buildings[counter].create()
			cmds.parent( buildings[counter].buildingName, "gen_buildings")

				#move it into place
			buildings[counter].moveBuilding( (xSpace + (buildingX/2)), (height / 2), (zSpace + (buildingZ/2) ) )
			
			#update the progress bar
#			progressInc = cmds.progressBar(progressControl, edit=True, maxValue = (cityDepth), pr = xSpace, vis = True)
			
			#update the spacing for the next row
			zSpace = zSpace + buildingZ + buildingGap
			
			counter += 1
			print "xcounter = " + str(xcounter)
			
		
		if xcounter == 1:
			print "creating street3 piece"
			streetSegment = cmds.polyPlane( h = cityWidth, w = streetWidth + buildingGap, sx = 1, sy = 1)
			cmds.move( xSpace + (streetWidth/2) + biggestX + buildingGap, 0.01, cityWidth/2)
 			cmds.parent(streetSegment[0], "street")

			xSpace = xSpace + streetWidth + biggestX + (buildingGap*2)
			xcounter = 0
		else:
			xcounter += 1
			xSpace = xSpace + (biggestX) + buildingGap
	
	#merge the street geometry
	streets = cmds.listRelatives("street", c = True)
	cmds.select(streets)
	cmds.polyUnite(n = "Combined_Street")
	cmds.delete(ch = True)


class Building:

	buildingCount = 0
	
	#class constructor	
	def __init__(self, inWidth, inDepth, inHeight, typeOfBuilding):
		self.width = inWidth
		self.height = inHeight
		self.depth = inDepth
		self.buildingType = typeOfBuilding
		Building.buildingCount += 1
		self.buildingName = "Building_" + str(self.buildingCount)
		self.xDiv = 10
		self.yDiv = 10
		self.zDiv = 10
	
	
	#function creates the actual building, returns void
	def create(self):
			
		#building type number 1
		if(self.buildingType == 0):
			cmds.polyCube(w = self.width, d = self.depth, h = self.height, n =  str(self.buildingName))
			
		#building type number 2	
		elif(self.buildingType == 1):
		
			cmds.polyCube(w = self.width, d = self.depth, h = self.height, n =  str(self.buildingName))
			
			#random number of upward extrusions
			for i in range(0, random.randrange(0,3)):
				cmds.polyExtrudeFacet(str(self.buildingName) + ".f[1]", kft = False, ls = (0.8, 0.8, 0))
				cmds.polyExtrudeFacet(str(self.buildingName) + ".f[1]", kft = False, ltz = 30)	
			
		#building type number 3	
		else:
			cmds.polyCube(w = self.width, d = self.depth, h = self.height, sx = self.xDiv, sy = self.yDiv, sz = self.zDiv, n = str(self.buildingName))			
			
			sides = []
			
			#select everything except the top and bottom of the building
			for i in range(0, 8):
				if(i != 1 and i != 3):
					sides.append(str(self.buildingName) + ".f[" + str(self.xDiv * self.yDiv * i) + ":" + str((self.xDiv * self.yDiv * (i+1)) - 1) + "]")
			
			#extrude the faces to create windows
			cmds.polyExtrudeFacet(sides[0], sides[1], sides[2], sides[3], sides[4], sides[5], kft = False, ls = (0.8, 0.8, 0))
			windows = cmds.ls(sl = True)
			cmds.polyExtrudeFacet(windows[1], windows[2], windows[3], kft = False, ltz = -0.2)
			cmds.select( self.buildingName)
				
	#function moves the building, returns void	
	def moveBuilding(self, x, y, z):
		cmds.select(self.buildingName)
		cmds.move(x, y, z)
		cmds.select( cl = True)