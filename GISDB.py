# coding=utf8
# !/usr/bin/python3
import PyScreen
import pygame
import sys
import time
import os
import random
import threading
import traceback
from tkinter import messagebox
import tkinter


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


class GISItem:
	def __init__(self):
		self.DicOpenLength = 128
		self.Type = None  # Point, Line, Polygon
		self.Hint = ""  # Hint的任一Key不能是其他Key的前缀
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
				if p[0] < self.X0: self.X0 = p[0]
				if p[0] > self.X1: self.X1 = p[0]
				if p[1] < self.Y0: self.Y0 = p[1]
				if p[1] > self.Y1: self.Y1 = p[1]
		else:
			self.X0 = self.XY[0]
			self.X1 = self.XY[0]
			self.Y0 = self.XY[1]
			self.Y1 = self.XY[1]

	def HintDicGen(self):
		if len(self.Hint) > self.DicOpenLength:
			self.Dic = dict()
			pos = self.Hint.find("[")
			while pos != -1:
				split = self.Hint.find(":", pos + 1)
				end = self.Hint.find("]", split + 1)
				self.Dic[self.Hint[pos + 1: split]] = self.Hint[split + 1: end]
				pos = self.Hint.find("[", end + 1)

	def HintFill(self, Hint):
		if Hint is None: Hint = ""
		self.Hint = Hint
		self.Dic = None
		self.HintDicGen()

	def HintPut(self, key, value):
		if key is None: return
		if value is None: value = ""
		pos = self.Hint.find(key)
		if pos == -1:
			self.Hint = "[" + key + ":" + value + "]" + self.Hint
		else:
			split = self.Hint.find(":", pos + 1)
			end = self.Hint.find("]", split + 1)
			self.Hint = self.Hint[: pos] + "[" + key + ":" + value + "]" + self.Hint[end + 1:]

		if self.Dic is not None:
			self.Dic[key] = value
		elif len(self.Hint) > self.DicOpenLength:
			self.HintDicGen()

	def HintGet(self, key):
		if key is None: return None
		if key == "": return ""
		if len(self.Hint) > self.DicOpenLength:
			return self.Dic.get(key)
		else:
			pos = self.Hint.find(key)
			if pos == -1: return None
			split = self.Hint.find(":", pos + 1)
			end = self.Hint.find("]", split + 1)
			return self.Hint[split + 1: end]

	def Fill(self, Type, XY, Hint):
		self.Type = Type
		self.SetXY(XY)
		self.HintFill(Hint)

class GISDB:
	def __init__(self, HWACC=0, fullscreen=True, width=1024, height=768):
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
		self.PNGDic = dict()
		self.DefaultBufferImageNumber = 188
		self.default_rgb = (0, 0, 255)
		self.ScreenItem.SCREEN_DEFAULT_SIZE = (width, height)
		self.ScreenItem.LOGICAL_DEFAULT_SIZE = (640, 480)
		self.ScreenItem.LOGICAL_DEFAULT_P0 = (-280, -190)
		pygame.display.set_caption("GISDB Python Version")
		pygame.display.set_icon(pygame.image.load("globe.png"))
		self.ScreenItem.fullscreen = fullscreen
		self.ScreenItem.HWACC = HWACC
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

	def Query(self, Type, L_R_U_D_Box=None, PrimaryKey=""):
		if PrimaryKey is None: PrimaryKey = ""
		self.DataLock.read_acquire()
		try:
			pass
		except:
			print(traceback.format_exc())
			os._exit(0)
		self.DataLock.read_release()

	def Update(self, Type, L_R_U_D_Box=None, PrimaryKey="", UpdateWhat=""):
		if PrimaryKey is None: PrimaryKey = ""
		if UpdateWhat is None: UpdateWhat = ""
		self.DataLock.write_acquire()
		try:
			pass
		except:
			print(traceback.format_exc())
			os._exit(0)
		self.DataLock.write_release()

	def remove(self, Type, L_R_U_D_Box=None, PrimaryKey=""):
		if PrimaryKey is None: PrimaryKey = ""
		self.DataLock.read_acquire()
		try:
			pass
		except:
			print(traceback.format_exc())
			os._exit(0)
		self.DataLock.read_release()

	def KeyListener(self, KeyChar):
		if KeyChar == "left":
			self.ClearListener()
			self.ScreenItem.ScreenInput = self.ScreenItem.ScreenInput[ : -len(KeyChar)]
			P0 = self.ScreenItem.LOGICAL_DEFAULT_P0
			self.ScreenItem.LOGICAL_DEFAULT_P0 = (P0[0] - self.ScreenItem.LOGICAL_DEFAULT_SIZE[0]/10, P0[1])
			self.ScreenItem.screen.fill(self.ScreenItem.SCREEN_DEFAULT_COLOR)
		elif KeyChar == "right":
			self.ClearListener()
			self.ScreenItem.ScreenInput = self.ScreenItem.ScreenInput[: -len(KeyChar)]
			P0 = self.ScreenItem.LOGICAL_DEFAULT_P0
			self.ScreenItem.LOGICAL_DEFAULT_P0 = (P0[0] + self.ScreenItem.LOGICAL_DEFAULT_SIZE[0] / 10, P0[1])
			self.ScreenItem.screen.fill(self.ScreenItem.SCREEN_DEFAULT_COLOR)
		elif KeyChar == "up":
			self.ClearListener()
			self.ScreenItem.ScreenInput = self.ScreenItem.ScreenInput[: -len(KeyChar)]
			P0 = self.ScreenItem.LOGICAL_DEFAULT_P0
			self.ScreenItem.LOGICAL_DEFAULT_P0 = (P0[0] , P0[1] + self.ScreenItem.LOGICAL_DEFAULT_SIZE[1] / 10)
			self.ScreenItem.screen.fill(self.ScreenItem.SCREEN_DEFAULT_COLOR)
		elif KeyChar == "down":
			self.ClearListener()
			self.ScreenItem.ScreenInput = self.ScreenItem.ScreenInput[: -len(KeyChar)]
			P0 = self.ScreenItem.LOGICAL_DEFAULT_P0
			self.ScreenItem.LOGICAL_DEFAULT_P0 = (P0[0] , P0[1] - self.ScreenItem.LOGICAL_DEFAULT_SIZE[1] / 10)
			self.ScreenItem.screen.fill(self.ScreenItem.SCREEN_DEFAULT_COLOR)
		else:
			print(self.name + " : " + KeyChar)

	def CMLListener(self, CML):
		print(self.name + " : " + CML)
		if CML == "exit":
			os._exit(0)
		elif CML == "resetdbscreen":
			self.ScreenItem.LOGICAL_DEFAULT_SIZE = (540, 480)
			self.ScreenItem.LOGICAL_DEFAULT_P0 = (-280, -190)
		elif CML == "help":
			LocalFrame = tkinter.Tk()
			LocalFrame.withdraw()
			messagebox.showinfo(title="帮助与介绍", message=("本程序是Python版本的GISDB，用于存储、计算和展示时空地理数据\n"
			"键盘输入以下命令将在以红字在底部栏展示，回车确认执行并刷屏\n"
			"=============================\nexit命令退出程序\n"
			"resetscreen命令屏幕左下角自动对齐到(0,0)原点\n"
			"resetdbscreen命令将展示西经180度到东经180度，南纬90度到北纬90度的矩形线性空间\n"))
			LocalFrame.destroy()

	def ClickListener(self, button, PixelPos, LogicalPos):
		if not PyScreen.CheckInRegion(LogicalPos[0], LogicalPos[1], self.LogicalLeft, self.LogicalRight, self.LogicalUp, self.LogicalDown): return
		if (not button == 1) and (not button == 3): return
		for LogListener in self.LogBoxListener:
			if not PyScreen.CheckInRegion(LogicalPos[0], LogicalPos[1], LogListener[0], LogListener[1], LogListener[2], LogListener[3]): continue
			LogListener[4](LogicalPos[0], LogicalPos[1], button)

		for PixListener in self.PixBoxListener:
			if not PyScreen.CheckInRegion(PixelPos[0], PixelPos[1], PixListener[0], PixListener[1], PixListener[2], PixListener[3]): continue
			PixListener[4](PixelPos[0], PixelPos[1], button)

		print(self.name + " : " + str(button) + " " + str(PixelPos) + " " + str(LogicalPos))

	def ClearListener(self):
		fill_pos = self.ScreenItem.Log2Pix((self.LogicalLeft - self.Padding, self.LogicalUp + self.Padding))
		fill_pos_end = self.ScreenItem.Log2Pix((self.LogicalRight + self.Padding, self.LogicalDown - self.Padding))
		fill_scale = (fill_pos_end[0] - fill_pos[0] + 8, fill_pos_end[1] - fill_pos[1] + 8)
		pygame.draw.rect(self.ScreenItem.screen, self.ScreenItem.SCREEN_DEFAULT_COLOR, pygame.Rect(fill_pos, fill_scale))

	def run(self):
		while True:
			time.sleep(0.25)
			self.draw()

	def start(self):
		GISThread = threading.Thread(target=self.run)
		GISThread.start()

	def TranslateRGB(self, RgbValue):
		if RgbValue is None: return 128, 128, 128
		if RgbValue == "": return 128, 128, 128
		return int(RgbValue[2:4], 16), int(RgbValue[4:6], 16), int(RgbValue[6:8], 16)

	def InputAlignedMapDir(self, filedir):
		for (root, dirs, files) in os.walk(filedir):
			# root 表示当前正在访问的文件夹路径
			# dirs 表示该文件夹下的子目录名list
			# files 表示该文件夹下的文件list

			# 遍历文件
			for f in files:
				image = os.path.join(root, f)
				if (image.find("AlignedMap_") == -1):
					continue;
				if (image.find(".png") == -1):
					continue;
				DB.Insert("Point", (0, 0), "[PNG:" + image + "]")
				print(image)

	# 遍历所有的文件夹
	# for d in dirs:
	#	 print(os.path.join(root, d))

	def draw(self):
		self.ClearListener()
		self.ScreenItem.DrawLogicalRect(self.LogicalLeft, self.LogicalRight, self.LogicalUp, self.LogicalDown, self.default_rgb)
		# 上句画出逻辑数据的合法矩形边界线条
		self.DataLock.read_acquire()
		try:
			DrawCount = 0
			for item in self.GISData:
				if DrawCount > self.MaxDrawNum: break

				if item.Type == "Point":
					PNGPath = item.HintGet("PNG")
					AlignedPos = -1 if PNGPath is None else PNGPath.find("AlignedMap_")
					if AlignedPos == -1:
						if (item.X1 < self.LogicalLeft) or (item.X1 < self.ScreenItem.LOGICAL_DEFAULT_P0[0]): continue
						if (item.X0 > self.LogicalRight) or (item.X0 > self.ScreenItem.LOGICAL_DEFAULT_P0[0] + self.ScreenItem.LOGICAL_DEFAULT_SIZE[0]): continue
						if (item.Y1 < self.LogicalDown) or (item.Y1 < self.ScreenItem.LOGICAL_DEFAULT_P0[1]): continue
						if (item.Y0 > self.LogicalUp) or (item.Y0 > self.ScreenItem.LOGICAL_DEFAULT_P0[1] + self.ScreenItem.LOGICAL_DEFAULT_SIZE[1]): continue
					if item.HintGet("PointVisible") == "" or AlignedPos != -1:
						if not PNGPath is None:
							RelocScreenXY = None
							if AlignedPos != -1:
								LocList = PNGPath[ AlignedPos : ].split("_")
								PixelLeftDown = self.ScreenItem.Log2Pix((float(LocList[1]), float(LocList[2])))
								if PixelLeftDown[0] > self.ScreenItem.SCREEN_DEFAULT_SIZE[0]: continue
								if PixelLeftDown[1] < 0: continue
								PixelRightUp = self.ScreenItem.Log2Pix((float(LocList[3]), float(LocList[4])))
								if PixelRightUp[0] < 0: continue
								if PixelRightUp[1] > self.ScreenItem.SCREEN_DEFAULT_SIZE[1]: continue
								RePNGSize = (int(PixelRightUp[0] - PixelLeftDown[0]), int(PixelLeftDown[1] - PixelRightUp[1]))
								Ratio = (RePNGSize[0] + RePNGSize[1]) / (self.ScreenItem.SCREEN_DEFAULT_SIZE[0] + self.ScreenItem.SCREEN_DEFAULT_SIZE[1])
								if (Ratio < 0.33) or (Ratio > 3): continue
								RelocScreenXY = (PixelLeftDown[0], PixelRightUp[1])

							if self.PNGDic.__contains__(PNGPath): PNGImage = self.PNGDic.get(PNGPath)
							else:
								if not os.path.exists(PNGPath): PNGImage = pygame.image.load("layers.png")
								else: PNGImage = pygame.image.load(PNGPath)
								if len(self.PNGDic) > self.DefaultBufferImageNumber: self.PNGDic.clear()
								self.PNGDic[PNGPath] = PNGImage
							DrawCount += 1
							if RelocScreenXY is None: self.ScreenItem.screen.blit(PNGImage, self.ScreenItem.Log2Pix(item.XY))
							else: self.ScreenItem.screen.blit(pygame.transform.scale(PNGImage, RePNGSize), RelocScreenXY)
							if AlignedPos != -1: continue

						DrawCount += 1
						PointSize = item.HintGet("PointSize")
						self.ScreenItem.DrawLogicalPoint(item.XY, self.TranslateRGB(item.HintGet("PointRGB")), 4 if PointSize is None else int(PointSize))
						if item.HintGet("WordVisible") == "":
							text = self.ScreenItem.font.render(item.Hint, 1, self.TranslateRGB(item.HintGet("WordRGB")))
							text_pos = self.ScreenItem.Log2Pix(item.XY)
							self.ScreenItem.screen.blit(text, (text_pos[0] + 2, text_pos[1] - 20))
				else:
					if (item.X1 < self.LogicalLeft) or (item.X1 < self.ScreenItem.LOGICAL_DEFAULT_P0[0]): continue
					if (item.X0 > self.LogicalRight) or (item.X0 > self.ScreenItem.LOGICAL_DEFAULT_P0[0] + self.ScreenItem.LOGICAL_DEFAULT_SIZE[0]): continue
					if (item.Y1 < self.LogicalDown) or (item.Y1 < self.ScreenItem.LOGICAL_DEFAULT_P0[1]): continue
					if (item.Y0 > self.LogicalUp) or (item.Y0 > self.ScreenItem.LOGICAL_DEFAULT_P0[1] + self.ScreenItem.LOGICAL_DEFAULT_SIZE[1]): continue
					if item.Type == "Line" and item.HintGet("LineVisible") == "":
						DrawCount += 1
						LineWidth = item.HintGet("LineWidth")
						self.ScreenItem.DrawLogicalLine(item.XY, self.TranslateRGB(item.HintGet("LineRGB")), 2 if LineWidth is None else int(LineWidth))
						if item.HintGet("WordVisible") == "":
							text = self.ScreenItem.font.render(item.Hint, 1, self.TranslateRGB(item.HintGet("WordRGB")))
							self.ScreenItem.screen.blit(text, self.ScreenItem.Log2Pix(item.XY[0]))
					elif item.Type == "Polygon" and item.HintGet("PolygonVisible") == "":
						DrawCount += 1
						LineWidth = item.HintGet("LineWidth")
						self.ScreenItem.DrawLogicalPolygon(item.XY, self.TranslateRGB(item.HintGet("PolygonRGB")), 4 if LineWidth is None else int(LineWidth))
						if item.HintGet("WordVisible") == "":
							text = self.ScreenItem.font.render(item.Hint, 1, self.TranslateRGB(item.HintGet("WordRGB")))
							self.ScreenItem.screen.blit(text, self.ScreenItem.Log2Pix(item.XY[0]))
		except:
			print(traceback.format_exc())
			os._exit(0)
		self.DataLock.read_release()
		#FlushScreen
		if self.ScreenItem.screen.get_flags() & pygame.OPENGL: pygame.display.flip()
		else: pygame.display.update(pygame.Rect(0, 20, self.ScreenItem.SCREEN_DEFAULT_SIZE[0], self.ScreenItem.SCREEN_DEFAULT_SIZE[1] - 40))

	def test(self):
		def ClickOnButton1(x, y, button):
			self.ScreenItem.ScreenInput = "You Click On Button1 From " + self.name

		self.LogBoxListener.append(
			(self.LogicalLeft, self.LogicalLeft + 70, self.LogicalUp, self.LogicalUp - 16, ClickOnButton1))

		def ClickOnButton2(x, y, button):
			self.ScreenItem.ScreenInput = "You Click On Button2 From " + self.name

		self.LogBoxListener.append(
			(self.LogicalLeft, self.LogicalLeft + 32, self.LogicalDown + 32, self.LogicalDown, ClickOnButton2))

		while self.ScreenItem.running:
			time.sleep(0.02)
			self.ClearListener()
			# 下句画出逻辑点的合法矩形边界线条
			self.ScreenItem.DrawLogicalRect(self.LogicalLeft, self.LogicalRight, self.LogicalUp, self.LogicalDown, self.default_rgb)

			for i in range(10):
				rect_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
				self.ScreenItem.DrawLogicalPoint(LogicalPoint=(random.randint(self.LogicalLeft, self.LogicalRight), random.randint(self.LogicalDown, self.LogicalUp)), rgb=rect_color, radius=2)
				p1 = (random.randint(self.LogicalLeft, self.LogicalRight - 80), random.randint(self.LogicalDown, self.LogicalUp - 80))
				p2 = (p1[0] + 12, p1[1] + 36)
				p3 = (p2[0] + 31, p2[1] + 17)
				self.ScreenItem.DrawLogicalLine(LogicalPointList=(p1, p2, p3), rgb=rect_color, width=2)
				pa = (p1[0] / 2 + p2[0] / 2, p1[1] / 2 + p2[1] / 2)
				pb = (p2[0] / 2 + p3[0] / 2, p2[1] / 2 + p3[1] / 2)
				pc = (p3[0] / 2 + p1[0] / 2, p3[1] / 2 + p1[1] / 2)
				self.ScreenItem.DrawLogicalPolygon(LogicalPointList=(pa, pb, pc), rgb=rect_color)

			text = pygame.transform.scale(self.ScreenItem.font.render(u'鼠标点击', 1, (255, 0, 0)), self.ScreenItem.LogSize2Pixel((70, 16)))  # button1
			self.ScreenItem.screen.blit(text, self.ScreenItem.Log2Pix((self.LogicalLeft, self.LogicalUp)))
			self.ScreenItem.DrawLogicalRect(self.LogicalLeft, self.LogicalLeft + 70, self.LogicalUp, self.LogicalUp - 16)
			icon = pygame.transform.scale(pygame.image.load("plane.jpg"), self.ScreenItem.LogSize2Pixel((32, 32)))  # button2
			self.ScreenItem.screen.blit(icon, self.ScreenItem.Log2Pix((self.LogicalLeft, self.LogicalDown + 32)))
			self.ScreenItem.DrawLogicalRect(self.LogicalLeft, self.LogicalLeft + 32, self.LogicalDown + 32, self.LogicalDown)
			if self.ScreenItem.screen.get_flags() & pygame.OPENGL: pygame.display.flip()
			else: pygame.display.update()


if __name__ == "__main__":
	DB = GISDB(HWACC=pygame.FULLSCREEN | pygame.HWSURFACE)
	# DB = GISDB(HWACC=pygame.FULLSCREEN | pygame.HWSURFACE | pygame.OPENGL | pygame.DOUBLEBUF)
	# DB.test()
	DB.start()
	import platform
	opsys = str(platform.platform())
	if opsys == "Windows-10-10.0.14393-SP0":
		DB.InputAlignedMapDir("C:\\Users\\SamJohnKing\\Desktop\\ShanghaiOSM_120km_WholeCity_8mPerPixel")
		DB.InputAlignedMapDir("C:\\Users\\SamJohnKing\\Desktop\\ShanghaiOSM_45km_MainCity_1mPerPixel_2kPics")
	elif opsys == "Windows-8.1-6.3.9600-SP0":
		DB.InputAlignedMapDir("C:\\Users\\SamJohnKing\\Desktop\\ShanghaiOSM_45km_MainCity_1mPerPixel_2kPics")
	elif opsys == "Windows-7-6.1.7601-SP1":
		DB.InputAlignedMapDir("D:\\shanghai remote sensing image\\ShanghaiOSM_120km_WholeCity_8mPerPixel")
		DB.InputAlignedMapDir("D:\\shanghai remote sensing image\\ShanghaiOSM_45km_MainCity_1mPerPixel_2kPics")
	print(opsys)

	DB.Insert("Point", (121, 31),"[PointRGB:0x123456][Title:Geo][WordRGB:0x880000][PointVisible:][PointSize:8][PNG:layers-2x.png][WordVisible:]")
	DB.Insert("Line", [(121.2431, 31.4362), (121.5568, 31.7435)],"[LineRGB:0xAA00AA][Title:Geo][WordRGB:][LineVisible:][LineWidth:3]")
	DB.Insert("Polygon", [(121.150, 31.43), (121.33, 31.20), (121.55, 31)],"[Title:World!][WordRGB:0x00cc00][PolygonVisible:][WordVisible:][PolygonRGB:0x00FF00]")

	DB.ScreenItem.LOGICAL_DEFAULT_P0 = (121.47232076710037, 31.238546796792217)
	DB.ScreenItem.LOGICAL_DEFAULT_SIZE = (0.012, 0.008)
	DB.ScreenItem.GlobalFlushSpan = -1
	scan_st = (121.2616, 31.13878)
	scan_en = (121.66912, 31.385)
	x_stride = 0.002
	y_stride = 0.0015
	y_ptr = scan_st[1]
	while y_ptr < scan_en[1]:
		x_ptr = scan_st[0]
		while x_ptr < scan_en[0]:
			DB.ScreenItem.LogicalMoveCenter((x_ptr, y_ptr))
			print((x_ptr, y_ptr))
			time.sleep(2)
			x_ptr += x_stride
		y_ptr += y_stride
	print("ScanFinished")



