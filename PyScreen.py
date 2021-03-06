# coding=utf8
# !/usr/bin/python3
import pygame
import random
import sys
import time
import threading
import os
import tkinter
from tkinter import messagebox
import traceback


class PyScreen(threading.Thread):
	def __init__(self):
		self.SCREEN_DEFAULT_SIZE = (1024, 768)
		self.SCREEN_DEFAULT_COLOR = (0, 0, 0)
		self.LOGICAL_DEFAULT_SIZE = (1024, 768)
		self.LOGICAL_DEFAULT_P0 = (0, 0)  # 屏幕左下角逻辑原点
		self.running = False
		self.ScreenInput = u""
		self.Message = u"等待键盘输入命令行(help, exit, resetscreen)并回车确认刷屏, 按esc与alt可以最小化, 也可以鼠标拖拽点击缩放！"
		self.StatusDefault = u"待命"
		self.Status = self.StatusDefault
		self.MouseDownPos = (0, 0)
		self.MouseUpPos = (0, 0)
		self.CMLListener = []
		self.KeyListener = []
		self.ClickListener = []
		self.ClearListener = []
		self.GlobalFlushSpan = 8 # 大于0代表全局刷新秒数，否则不刷新
		self.FlushTime = time.time()
		self.fullscreen = True
		self.HWACC = 0
		self.screenlock = threading.Lock()
		super().__init__()

	def Log2Pix(self, Log):
		Pix_x = (Log[0] - self.LOGICAL_DEFAULT_P0[0]) / self.LOGICAL_DEFAULT_SIZE[0] * self.SCREEN_DEFAULT_SIZE[0]
		Pix_y = (self.LOGICAL_DEFAULT_SIZE[1] - Log[1] + self.LOGICAL_DEFAULT_P0[1]) / self.LOGICAL_DEFAULT_SIZE[1] * \
		        self.SCREEN_DEFAULT_SIZE[1]
		return Pix_x, Pix_y

	def Pix2Log(self, Pix):
		Log_x = Pix[0] / self.SCREEN_DEFAULT_SIZE[0] * self.LOGICAL_DEFAULT_SIZE[0] + self.LOGICAL_DEFAULT_P0[0]
		Log_y = - Pix[1] / self.SCREEN_DEFAULT_SIZE[1] * self.LOGICAL_DEFAULT_SIZE[1] + self.LOGICAL_DEFAULT_P0[1] + \
		        self.LOGICAL_DEFAULT_SIZE[1]
		return Log_x, Log_y

	def DrawLogicalRect(self, LogicalLeft, LogicalRight, LogicalUp, LogicalDown, rgb=(128, 128, 128), width=2):
		pygame.draw.lines(self.screen, rgb, 1, (
		self.Log2Pix((LogicalLeft, LogicalDown)), self.Log2Pix((LogicalRight, LogicalDown)),
		self.Log2Pix((LogicalRight, LogicalUp)), self.Log2Pix((LogicalLeft, LogicalUp))), width)

	def DrawLogicalPoint(self, LogicalPoint, rgb=(128, 128, 128), radius=2):
		pygame.draw.circle(self.screen, rgb, self.Log2Pix(LogicalPoint), radius, 0)

	def DrawLogicalLine(self, LogicalPointList, rgb=(128, 128, 128), width=2):
		PixelList = []
		for Point in LogicalPointList:
			PixelList.append(self.Log2Pix(Point))
		pygame.draw.lines(self.screen, rgb, 0, PixelList, width)

	def DrawLogicalPolygon(self, LogicalPointList, rgb=(128, 128, 128), width=0):  # width == 0 for fullfill
		PixelList = []
		for Point in LogicalPointList:
			PixelList.append(self.Log2Pix(Point))
		pygame.draw.polygon(self.screen, rgb, PixelList, width)

	def LogSize2Pixel(self, size):
		return int(size[0] / self.LOGICAL_DEFAULT_SIZE[0] * self.SCREEN_DEFAULT_SIZE[0]), int(
			size[1] / self.LOGICAL_DEFAULT_SIZE[1] * self.SCREEN_DEFAULT_SIZE[1])

	def LogicalMoveCenter(self, CenterPoint):
		self.screenlock.acquire()
		self.LOGICAL_DEFAULT_P0 = (CenterPoint[0] - self.LOGICAL_DEFAULT_SIZE[0]/2, CenterPoint[1] - self.LOGICAL_DEFAULT_SIZE[1]/2)
		self.screenlock.release()

	def run(self):
		pygame.init()
		if self.fullscreen or self.HWACC != 0:
			infoObject = pygame.display.Info()
			self.SCREEN_DEFAULT_SIZE = (infoObject.current_w, infoObject.current_h)
		if self.HWACC != 0: self.screen = pygame.display.set_mode(self.SCREEN_DEFAULT_SIZE, self.HWACC | pygame.NOFRAME, 32)
		else: self.screen = pygame.display.set_mode(self.SCREEN_DEFAULT_SIZE, pygame.NOFRAME, 32)
		self.screen.fill(self.SCREEN_DEFAULT_COLOR)
		self.font = pygame.font.Font(pygame.font.match_font('kaiti'), 18)
		self.running = True
		self.FlushTime = time.time()
		while self.running:
			time.sleep(0.05)
			if (self.GlobalFlushSpan > 0) and (time.time() - self.FlushTime > self.GlobalFlushSpan):#周期性更新屏幕
				self.screenlock.acquire()
				self.screen.fill(self.SCREEN_DEFAULT_COLOR)
				if self.screen.get_flags() & pygame.DOUBLEBUF: pygame.display.flip()
				else: pygame.display.update()
				self.FlushTime = time.time()
				self.screenlock.release()
			self.screenlock.acquire()
			pygame.draw.rect(self.screen, self.SCREEN_DEFAULT_COLOR, pygame.Rect((0, self.SCREEN_DEFAULT_SIZE[1] - 20), (self.SCREEN_DEFAULT_SIZE[0], 20)))
			text = self.font.render(self.ScreenInput, 1, (255, 0, 0))
			self.screen.blit(text, (4, self.SCREEN_DEFAULT_SIZE[1] - 20))
			pygame.draw.rect(self.screen, self.SCREEN_DEFAULT_COLOR, pygame.Rect((0, 0), (self.SCREEN_DEFAULT_SIZE[0], 20)))
			text = self.font.render(self.Status + " | " + self.Message, 1, (0, 255, 0))
			self.screen.blit(text, (4, 0))
			if self.screen.get_flags() & pygame.DOUBLEBUF: pygame.display.flip()
			else: pygame.display.update([pygame.Rect(0 ,0, self.SCREEN_DEFAULT_SIZE[0], 20), pygame.Rect(0, self.SCREEN_DEFAULT_SIZE[1] - 20, self.SCREEN_DEFAULT_SIZE[0], 20)])
			self.screenlock.release()
			#上述语句更新上下两条status bar
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					os._exit(0)
				elif event.type == pygame.KEYDOWN:
					KeyChar = pygame.key.name(event.key)
					print("Key Pressed " + KeyChar)
					if KeyChar == "return":
						print("CML >>> " + self.ScreenInput)
						if self.ScreenInput == "resetscreen":
							self.LOGICAL_DEFAULT_SIZE = self.SCREEN_DEFAULT_SIZE;
							self.LOGICAL_DEFAULT_P0 = (0, 0)
						elif self.ScreenInput.startswith("globalflushspan="):
							self.GlobalFlushSpan = float(self.ScreenInput[16 : ])
						else:
							for Listener in self.CMLListener:
								Listener(self.ScreenInput)
						self.ScreenInput = ""
						self.screenlock.acquire()
						self.screen.fill(self.SCREEN_DEFAULT_COLOR) #回车键更新全局屏幕
						if self.screen.get_flags() & pygame.DOUBLEBUF: pygame.display.flip()
						else: pygame.display.update()
						self.FlushTime = time.time()
						self.screenlock.release()
					elif KeyChar == "backspace":
						self.ScreenInput = self.ScreenInput[:-1]
					elif KeyChar == "escape" or KeyChar == "left alt" or KeyChar == "right alt":
						pygame.display.iconify()
					else:
						self.ScreenInput += KeyChar
						for Listener in self.KeyListener:
							Listener(KeyChar)
				elif event.type == pygame.MOUSEBUTTONDOWN:
					self.MouseDownPos = pygame.mouse.get_pos()
				elif event.type == pygame.MOUSEBUTTONUP:
					self.MouseUpPos = pygame.mouse.get_pos()
					dx = self.MouseUpPos[0] - self.MouseDownPos[0]
					dy = self.MouseUpPos[1] - self.MouseDownPos[1]
					if abs(dx) + abs(dy) > 10:  # Drag
						self.screenlock.acquire()
						# for Listener in self.ClearListener:
						# 	Listener()
						Log_dPos = self.Pix2Log((dx, dy))
						newx = self.LOGICAL_DEFAULT_P0[0] - (Log_dPos[0] - self.LOGICAL_DEFAULT_P0[0])
						newy = self.LOGICAL_DEFAULT_P0[1] - (
									Log_dPos[1] - self.LOGICAL_DEFAULT_P0[1] - self.LOGICAL_DEFAULT_SIZE[1])
						self.LOGICAL_DEFAULT_P0 = (newx, newy)
						self.screen.fill(self.SCREEN_DEFAULT_COLOR)
						self.screenlock.release()
					elif event.button == 4:  # Wheel Up
						self.screenlock.acquire()
						# for Listener in self.ClearListener:
						# 	Listener()
						Log_cursor = self.Pix2Log(self.MouseDownPos)
						newx = Log_cursor[0] - (Log_cursor[0] - self.LOGICAL_DEFAULT_P0[0]) * 0.9
						newy = Log_cursor[1] - (Log_cursor[1] - self.LOGICAL_DEFAULT_P0[1]) * 0.9
						self.LOGICAL_DEFAULT_SIZE = (self.LOGICAL_DEFAULT_SIZE[0] * 0.9, self.LOGICAL_DEFAULT_SIZE[1] * 0.9)
						self.LOGICAL_DEFAULT_P0 = (newx, newy)
						self.screen.fill(self.SCREEN_DEFAULT_COLOR)
						self.screenlock.release()
					elif event.button == 5:  # Wheel Down
						self.screenlock.acquire()
						# for Listener in self.ClearListener:
						# 	Listener()
						Log_cursor = self.Pix2Log(self.MouseDownPos)
						newx = Log_cursor[0] - (Log_cursor[0] - self.LOGICAL_DEFAULT_P0[0]) / 0.9
						newy = Log_cursor[1] - (Log_cursor[1] - self.LOGICAL_DEFAULT_P0[1]) / 0.9
						self.LOGICAL_DEFAULT_SIZE = (self.LOGICAL_DEFAULT_SIZE[0] / 0.9, self.LOGICAL_DEFAULT_SIZE[1] / 0.9)
						self.LOGICAL_DEFAULT_P0 = (newx, newy)
						self.screen.fill(self.SCREEN_DEFAULT_COLOR)
						self.screenlock.release()
					else:  # Click
						print("You Button Pressed At " + str(event.button))
						print("You Click At Pixel " + str(self.MouseUpPos))
						print("You Click At LogicalPos " + str(self.Pix2Log(self.MouseUpPos)))
						for Listener in self.ClickListener:
							Listener(event.button, self.MouseUpPos, self.Pix2Log(self.MouseUpPos))
				else:
					pass


def CheckInRegion(x, y, Left, Right, Up, Down):
	if x < Left: return False
	if x > Right: return False
	if y < Down: return False
	if y > Up: return False
	return True


if __name__ == "__main__":
	ScreenItem = PyScreen()
	ScreenItem.SCREEN_DEFAULT_SIZE = (1080, 960)
	ScreenItem.LOGICAL_DEFAULT_SIZE = (1080, 960)
	ScreenItem.start()
	while not ScreenItem.running: time.sleep(1)


	def Drawer(ScreenItem, rgb=(64, 64, 64), name="unnamed", LogicalBox=(0, 640, 640, 0, 8)):
		LogicalLeft = LogicalBox[0];
		LogicalRight = LogicalBox[1];
		LogicalUp = LogicalBox[2];
		LogicalDown = LogicalBox[3];
		Padding = LogicalBox[4]

		def KeyListener(KeyChar):
			print(name + " : " + KeyChar)

		def CMLListener(CML):
			print(name + " : " + CML)
			if CML == "exit": os._exit(0)

		LogBoxListener = [];
		PixBoxListener = []

		def ClickListener(button, PixelPos, LogicalPos):
			if not CheckInRegion(LogicalPos[0], LogicalPos[1], LogicalLeft, LogicalRight, LogicalUp, LogicalDown): return
			if (not button == 1) and (not button == 3): return
			for LogListener in LogBoxListener:
				if not CheckInRegion(LogicalPos[0], LogicalPos[1], LogListener[0], LogListener[1], LogListener[2], LogListener[3]): continue
				LogListener[4](LogicalPos[0], LogicalPos[1], button)

			for PixListener in PixBoxListener:
				if not CheckInRegion(PixelPos[0], PixelPos[1], PixListener[0], PixListener[1], PixListener[2], PixListener[3]): continue
				PixListener[4](PixelPos[0], PixelPos[1], button)

			print(name + " : " + str(button) + " " + str(PixelPos) + " " + str(LogicalPos))

		def ClearListener():
			fill_pos = ScreenItem.Log2Pix((LogicalLeft - Padding, LogicalUp + Padding))
			fill_pos_end = ScreenItem.Log2Pix((LogicalRight + Padding, LogicalDown - Padding))
			fill_scale = (fill_pos_end[0] - fill_pos[0] + 8, fill_pos_end[1] - fill_pos[1] + 8)
			pygame.draw.rect(ScreenItem.screen, ScreenItem.SCREEN_DEFAULT_COLOR, pygame.Rect(fill_pos, fill_scale))

		ScreenItem.KeyListener.append(KeyListener)
		ScreenItem.CMLListener.append(CMLListener)
		ScreenItem.ClickListener.append(ClickListener)
		ScreenItem.ClearListener.append(ClearListener)

		def ClickOnButton1(x, y, button):
			ScreenItem.ScreenInput = "You Click On Button1 From " + name

		LogBoxListener.append((LogicalLeft, LogicalLeft + 70, LogicalUp, LogicalUp - 16, ClickOnButton1))

		def ClickOnButton2(x, y, button):
			ScreenItem.ScreenInput = "You Click On Button2 From " + name

		LogBoxListener.append((LogicalLeft, LogicalLeft + 32, LogicalDown + 32, LogicalDown, ClickOnButton2))

		while ScreenItem.running:
			time.sleep(0.02)
			ClearListener()
			# pygame.draw.lines(Surface, color, closed, pointlist, width=1)
			ScreenItem.DrawLogicalRect(LogicalLeft, LogicalRight, LogicalUp, LogicalDown, rgb)
			# pygame.draw.lines(ScreenItem.screen, rgb, 1, (ScreenItem.Log2Pix((LogicalLeft, LogicalDown)),ScreenItem.Log2Pix((LogicalRight, LogicalDown)),ScreenItem.Log2Pix((LogicalRight, LogicalUp)),ScreenItem.Log2Pix((LogicalLeft, LogicalUp))))
			t0 = time.time()

			for i in range(10):
				rect_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
				ScreenItem.DrawLogicalPoint(
					LogicalPoint=(random.randint(LogicalLeft, LogicalRight), random.randint(LogicalDown, LogicalUp)),
					rgb=rect_color, radius=2)
				p1 = (random.randint(LogicalLeft, LogicalRight - 80), random.randint(LogicalDown, LogicalUp - 80))
				p2 = (p1[0] + 12, p1[1] + 36)
				p3 = (p2[0] + 31, p2[1] + 17)
				ScreenItem.DrawLogicalLine(LogicalPointList=(p1, p2, p3), rgb=rect_color, width=2)
				pa = (p1[0] / 2 + p2[0] / 2, p1[1] / 2 + p2[1] / 2)
				pb = (p2[0] / 2 + p3[0] / 2, p2[1] / 2 + p3[1] / 2)
				pc = (p3[0] / 2 + p1[0] / 2, p3[1] / 2 + p1[1] / 2)
				ScreenItem.DrawLogicalPolygon(LogicalPointList=(pa, pb, pc), rgb=rect_color)

			text = pygame.transform.scale(ScreenItem.font.render(u'鼠标点击', 1, (255, 0, 0)), ScreenItem.LogSize2Pixel((70, 16)))  # button1
			ScreenItem.screen.blit(text, ScreenItem.Log2Pix((LogicalLeft, LogicalUp)))
			ScreenItem.DrawLogicalRect(LogicalLeft, LogicalLeft + 70, LogicalUp, LogicalUp - 16)
			icon = pygame.transform.scale(pygame.image.load("plane.jpg"), ScreenItem.LogSize2Pixel((32, 32)))  # button2
			ScreenItem.screen.blit(icon, ScreenItem.Log2Pix((LogicalLeft, LogicalDown + 32)))
			ScreenItem.DrawLogicalRect(LogicalLeft, LogicalLeft + 32, LogicalDown + 32, LogicalDown)
			if ScreenItem.screen.get_flags() & pygame.DOUBLEBUF: pygame.display.flip()
			else: pygame.display.update()


	drawer1 = threading.Thread(target=Drawer, args=(ScreenItem, (255, 0, 0), "RED  ", (100, 420, 420, 100, 8)))
	drawer1.start()
	drawer1.join(2)

	drawer2 = threading.Thread(target=Drawer, args=(ScreenItem, (0, 255, 0), "GREEN", (500, 1000, 1000, 500, 8)))
	drawer2.start()
	drawer2.join(2)

	print(threading.current_thread().getName() + " EXIT ")
