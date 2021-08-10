#coding=utf8
#!/usr/bin/python3
import PyScreen
import pygame
import sys
import time
import os
import random
import threading
import traceback

class RWLock(object):
	def __init__(self):
		self.rlock = threading.Lock() 
		self.wlock = threading.Lock()
		self.reader = 0

	def write_acquire(self):
		self.wlock.acquire()

	def write_release(self):
		self.wlock.release()

	def read_acquire(self):
		self.rlock.acquire()
		self.reader += 1
		if self.reader == 1:
			self.wlock.acquire()
		self.rlock.release()

	def read_release(self):
		self.rlock.acquire()
		self.reader -= 1
		if self.reader == 0:
			self.wlock.release()
		self.rlock.release()

class GISItem():
	def __init__(self):
		self.DicOpenLength = 128
		self.Type = None #Point, Line, Polygon, PNG
		self.Hint = "" #Hint的任一Key不能是其他Key的前缀
		self.XY = None
		self.Dic = None
		self.X0 = 1e100
		self.Y0 = 1e100
		self.X1 = -1e100
		self.Y1 = -1e100

	def SetXY(self, value):
		self.XY = value
		if isinstance(self.XY, list):
			for p in self.XY:
				if(p[0] < self.X0): self.X0 = p[0]
				if(p[0] > self.X1): self.X1 = p[0]
				if(p[1] < self.Y0): self.Y0 = p[1]
				if(p[1] > self.Y1): self.Y1 = p[1]
		else:
			self.X0 = self.XY[0]
			self.X1 = self.XY[0]
			self.Y0 = self.XY[1]
			self.Y1 = self.XY[1]

	def HintDicGen(self):
		if(len(self.Hint) > self.DicOpenLength):
			self.Dic = dict()
			pos = self.Hint.find("[")
			while(pos != -1):
				split = self.Hint.find(":", pos + 1)
				end = self.Hint.find("]", split + 1)
				self.Dic[self.Hint[pos + 1: split]] = self.Hint[split + 1 : end]
				pos = self.Hint.find("[", end + 1)

	def HintFill(self, Hint):
		if(Hint == None): Hint = ""
		self.Hint = Hint
		self.Dic = None
		self.HintDicGen()

	def HintPut(self, key, value):
		if(key == None): return
		if(value == None): value = ""
		pos = self.Hint.find(key)
		if(pos == -1): 
			self.Hint = "[" + key + ":" + value + "]" + self.Hint
		else:
			split = self.Hint.find(":", pos + 1)
			end = self.Hint.find("]", split + 1)
			self.Hint = self.Hint[ : pos] + "[" + key + ":" + value + "]" + self.Hint[end + 1 :]
		
		if(self.Dic != None):
			self.Dic[key] = value
		elif(len(self.Hint) > self.DicOpenLength): 
			self.HintDicGen()

	def HintGet(self, key):
		if(key == None): return None
		if(key == ""): return ""
		if(len(self.Hint) > self.DicOpenLength):
			return self.Dic[key]
		else:
			pos = self.Hint.find(key)
			if(pos == -1): return None
			split = self.Hint.find(":", pos + 1)
			end = self.Hint.find("]", split + 1)
			return self.Hint[split + 1 : end]

	def Fill(self, Type, XY, Hint):
		self.Type = Type
		self.SetXY(XY)
		self.HintFill(Hint)

class GISDB():
	def __init__(self):
		self.GISData = []
		self.DataLock = RWLock()
		self.MaxDrawNum = 25000
		self.ScreenItem = PyScreen.PyScreen()
		self.ScreenItem.KeyListener.append(self.KeyListener)
		self.ScreenItem.CMLListener.append(self.CMLListener)
		self.ScreenItem.ClickListener.append(self.ClickListener)
		self.ScreenItem.ClearListener.append(self.ClearListener)
		self.LogicalLeft = -180
		self.LogicalRight = 180
		self.LogicalUp = 90
		self.LogicalDown = -90
		self.Padding = 8
		self.LogBoxListener = []
		self.PixBoxListener = []
		self.name = "GISDB"
		self.default_rgb = (0, 0, 255)
		self.ScreenItem.SCREEN_DEFAULT_SIZE = (1080, 960)
		self.ScreenItem.LOGICAL_DEFAULT_SIZE = (540, 480)
		self.ScreenItem.LOGICAL_DEFAULT_P0 = (-280, -190)
		self.ScreenItem.start()
		while not self.ScreenItem.running: time.sleep(1)

	def Insert(self, Type, XY, Hint):
		self.DataLock.write_acquire()
		try:
			Item = GISItem()
			Item.Fill(Type, XY, Hint)
			self.GISData.append(Item)
		except:
			print(traceback.format_exc())
			os._exit(0)
		self.DataLock.write_release()

	def Query(self, Type, L_R_U_D_Box = None, PrimaryKey = ""):
		if(PrimaryKey == None): PrimaryKey = ""
		self.DataLock.read_acquire()
		try:
			pass
		except:
			print(traceback.format_exc())
			os._exit(0)
		self.DataLock.read_release()

	def Update(self, Type, L_R_U_D_Box = None, PrimaryKey = "", UpdateWhat = ""):
		if(PrimaryKey == None): PrimaryKey = ""
		if(UpdateWhat == None): UpdateWhat = ""
		self.DataLock.write_acquire()
		try:
			pass
		except:
			print(traceback.format_exc())
			os._exit(0)
		self.DataLock.write_release()

	def remove(self, Type, L_R_U_D_Box = None, PrimaryKey = ""):
		if(PrimaryKey == None): PrimaryKey = ""
		self.DataLock.read_acquire()
		try:
			pass
		except:
			print(traceback.format_exc())
			os._exit(0)
		self.DataLock.read_release()

	def KeyListener(self, KeyChar):
		print(self.name + " : " + KeyChar)

	def CMLListener(self, CML):
		print(self.name + " : " + CML)
		if(CML == "exit"): os._exit(0)
		elif(CML == "resetdbscreen"):
			self.ScreenItem.LOGICAL_DEFAULT_SIZE = (540, 480)
			self.ScreenItem.LOGICAL_DEFAULT_P0 = (-280, -190)

	def ClickListener(self, button, PixelPos, LogicalPos):
		if not PyScreen.CheckInRegion(LogicalPos[0], LogicalPos[1], self.LogicalLeft, self.LogicalRight, self.LogicalUp, self.LogicalDown): return
		if (not button == 1) and (not button == 3): return 
		for LogListener in self.LogBoxListener:
			if not PyScreen.CheckInRegion(LogicalPos[0], LogicalPos[1], LogListener[0], LogListener[1], LogListener[2], LogListener[3]): continue
			LogListener[4](LogicalPos[0], LogicalPos[1], button)

		for PixListener in self.PixBoxListener:
			if not PyScreen.CheckInRegion(PixelPos[0], PixelPos[1], PixListener[0], PixListener[1], PixListener[2], PixListener[3]): continue
			PixListener[4](PixelPos[0], PixelPos[1], button)

		print(self.name + " : "  + str(button) + " " + str(PixelPos) + " " + str(LogicalPos))

	def ClearListener(self):
		fill_pos = self.ScreenItem.Log2Pix((self.LogicalLeft - self.Padding, self.LogicalUp + self.Padding))
		fill_pos_end = self.ScreenItem.Log2Pix((self.LogicalRight + self.Padding, self.LogicalDown - self.Padding))
		fill_scale = (fill_pos_end[0] - fill_pos[0] + 8, fill_pos_end[1] - fill_pos[1] + 8)
		pygame.draw.rect(self.ScreenItem.screen, self.ScreenItem.SCREEN_DEFAULT_COLOR, pygame.Rect(fill_pos, fill_scale))

	def run(self):
		while True:
			time.sleep(0.02)
			self.draw()

	def start(self):
		GISThread = threading.Thread(target = self.run)
		GISThread.start()

	def TranslateRGB(self, RgbValue):
		if(RgbValue == None): return (128, 128, 128)
		if(RgbValue == ""): return (128, 128, 128)
		return (int(RgbValue[2:4], 16), int(RgbValue[4:6], 16), int(RgbValue[6:8], 16))

	def draw(self):
		self.ClearListener()
		self.ScreenItem.DrawLogicalRect(self.LogicalLeft, self.LogicalRight, self.LogicalUp, self.LogicalDown, self.default_rgb)
		self.DataLock.read_acquire()
		try:
			DrawCount = 0
			for item in self.GISData:
				if (item.X1 < self.LogicalLeft) or (item.X1 < self.ScreenItem.LOGICAL_DEFAULT_P0[0]): continue
				if (item.X0 > self.LogicalRight) or (item.X0 > self.ScreenItem.LOGICAL_DEFAULT_P0[0] + self.ScreenItem.LOGICAL_DEFAULT_SIZE[0]): continue
				if (item.Y1 < self.LogicalDown) or (item.Y1 < self.ScreenItem.LOGICAL_DEFAULT_P0[1]): continue
				if (item.Y0 > self.LogicalUp) or (item.Y0 > self.ScreenItem.LOGICAL_DEFAULT_P0[1] + self.ScreenItem.LOGICAL_DEFAULT_SIZE[1]): continue
				DrawCount += 1
				if(DrawCount > self.MaxDrawNum): break;
				if(item.Type == "Point"):
					self.ScreenItem.DrawLogicalPoint(item.XY, self.TranslateRGB(item.HintGet("PointRGB")), 4)
					text = self.ScreenItem.font.render(item.Hint, 1, self.TranslateRGB(item.HintGet("WordRGB")))
					self.ScreenItem.screen.blit(text, self.ScreenItem.Log2Pix(item.XY))
				elif(item.Type == "Line"):
					self.ScreenItem.DrawLogicalLine(item.XY, self.TranslateRGB(item.HintGet("LineRGB")), 2)
					text = self.ScreenItem.font.render(item.Hint, 1, self.TranslateRGB(item.HintGet("WordRGB")))
					self.ScreenItem.screen.blit(text, self.ScreenItem.Log2Pix(item.XY[0]))
				elif(item.Type == "Polygon"):
					self.ScreenItem.DrawLogicalPolygon(item.XY, self.TranslateRGB(item.HintGet("PolygonRGB")), 0)
					text = self.ScreenItem.font.render(item.Hint, 1, self.TranslateRGB(item.HintGet("WordRGB")))
					self.ScreenItem.screen.blit(text, self.ScreenItem.Log2Pix(item.XY[0]))
				else:
					pass
		except:
			print(traceback.format_exc())
			os._exit(0)
		self.DataLock.read_release()

	def test(self):
		def ClickOnButton1(x, y, button):
			self.ScreenItem.Info = "You Click On Button1 From " + self.name
		self.LogBoxListener.append((self.LogicalLeft, self.LogicalLeft + 70, self.LogicalUp, self.LogicalUp - 16, ClickOnButton1))
		def ClickOnButton2(x, y, button):
			self.ScreenItem.Info = "You Click On Button2 From " + self.name
		self.LogBoxListener.append((self.LogicalLeft, self.LogicalLeft + 32, self.LogicalDown + 32, self.LogicalDown, ClickOnButton2))

		while self.ScreenItem.running:
			time.sleep(0.2)
			self.ClearListener()
			self.ScreenItem.DrawLogicalRect(self.LogicalLeft, self.LogicalRight, self.LogicalUp, self.LogicalDown, self.default_rgb)
			t0 = time.time()

			for i in range(10):
				rect_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
				self.ScreenItem.DrawLogicalPoint(LogicalPoint = (random.randint(self.LogicalLeft, self.LogicalRight), random.randint(self.LogicalDown, self.LogicalUp)), rgb = rect_color, radius = 2)
				p1 = (random.randint(self.LogicalLeft, self.LogicalRight - 80), random.randint(self.LogicalDown, self.LogicalUp - 80))
				p2 = (p1[0] + 12, p1[1] + 36)
				p3 = (p2[0] + 31, p2[1] + 17)
				self.ScreenItem.DrawLogicalLine(LogicalPointList = (p1, p2, p3), rgb = rect_color, width = 2)
				pa = (p1[0]/2 + p2[0]/2, p1[1]/2 + p2[1]/2)
				pb = (p2[0]/2 + p3[0]/2, p2[1]/2 + p3[1]/2)
				pc = (p3[0]/2 + p1[0]/2, p3[1]/2 + p1[1]/2)
				self.ScreenItem.DrawLogicalPolygon(LogicalPointList = (pa, pb, pc), rgb = rect_color)

			text = pygame.transform.scale(self.ScreenItem.font.render(u'鼠标点击', 1, (255, 0, 0)), self.ScreenItem.LogSize2Pixel((70, 16)))	#button1
			self.ScreenItem.screen.blit(text, self.ScreenItem.Log2Pix((self.LogicalLeft, self.LogicalUp)))
			self.ScreenItem.DrawLogicalRect(self.LogicalLeft, self.LogicalLeft + 70, self.LogicalUp, self.LogicalUp - 16)
			icon = pygame.transform.scale(pygame.image.load("plane.jpg"), self.ScreenItem.LogSize2Pixel((32, 32)))			#button2
			self.ScreenItem.screen.blit(icon, self.ScreenItem.Log2Pix((self.LogicalLeft, self.LogicalDown + 32)))
			self.ScreenItem.DrawLogicalRect(self.LogicalLeft, self.LogicalLeft + 32, self.LogicalDown + 32, self.LogicalDown)

			pygame.display.update()



if __name__ == "__main__":
	DB = GISDB()
	DB.start()
	DB.Insert("Point", (100, 50), "[PointRGB:0x123456][Title:Geo][WordRGB:0x880000]")
	DB.Insert("Line", [(-177, -33), (-12, 12), (88, 88)], "[LineRGB:0xAA00AA][Title:Geo][WordRGB:]")
	DB.Insert("Polygon", [(-50, 43), (33, 20), (120, 30)], "[Title:World!][WordRGB:0x00cc00]")