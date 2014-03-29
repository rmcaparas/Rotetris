import pygame
from pygame.locals import *

from time import time, sleep
from random import *
from os import path

from particle import *
from globals import *
from classes import *
from sprites import *
from mechanics import *

def load_image(file, colorkey = None):
	surf = pygame.image.load(path.join('resource', file)).convert()
	if colorkey is not None:
		if colorkey is -1:
			colorkey = surf.get_at((0,0))
		surf.set_colorkey(colorkey, RLEACCEL)
	return surf

class EventQ():

	def __init__(self, board, level):
		self.board = board
		self.board.eq = self
		self.tet = None
		self.alist = []
		self.level = level
		for i in xrange(4):
			self.alist.append(load_image(D_LIST[i][2], -1))
			self.alist[i].set_alpha(150)
		self.arrow = None
		
		self.hshift =  False
		self.hold  =  None

		self.pause = False

	def next_tetrimo(self, layout = None):
		self.tet = None
		if not layout:
			if(self.level == EASY):
				self.tet = Tetrimo(choice(B_LIST), (self.board.spawn+1, self.board.spawn+1), choice([NORTH, SOUTH]))
			else:	
				self.tet = Tetrimo(choice(B_LIST), (self.board.spawn+1, self.board.spawn+1), choice(D_LIST))
		else:
			if(self.level == EASY):
				self.tet = Tetrimo(layout, (self.board.spawn+1, self.board.spawn+1), choice([NORTH, SOUTH]))
			else:
				self.tet = Tetrimo(layout, (self.board.spawn+1, self.board.spawn+1), choice(D_LIST))
		self.board.add_tetrimo(self.tet)
		self.arrow = self.alist[D_LIST.index(self.tet.direction)]
		self.hshift = False

	def move_left(self):
		self.board.move(D_LIST[(D_LIST.index(self.tet.direction) + 1)%4])

	def move_right(self):
		self.board.move(D_LIST[D_LIST.index(self.tet.direction) - 1])

	def shift(self):
		if not self.hshift:
			self.hshift = True
			if(self.hold):
				tmp = self.hold
				self.hold = self.tet.ttype
				self.board.remove(self.tet)
				self.next_tetrimo(tmp)
				self.hshift = True

			else:
				self.hold = self.tet.ttype
				self.board.remove(self.tet)
				self.next_tetrimo()
				self.hshift = True

	def pauseG(self):
		self.pause = True

	def playG(self):
		self.pause = False

class Game():

	def __init__(self, level, screen):
		self.level = level
		self.screen = screen

		self.bg = load_image("Board.png")
		self.bgm = pygame.mixer.Sound(path.join("resource", "music", "dubstep.ogg"))
		self.bgm.play(-1)
		
		o = load_image("overlay.png").convert()
		o = pygame.transform.scale(o, (BWIDTH - 1, BWIDTH - 1))
		o.set_alpha(100)
		BoardSprite.overlay = [o, o.copy(), o.copy(), o.copy()]

		self.allsprite = pygame.sprite.Group()
		self.board = BoardSprite()
		self.allsprite.add(self.board)
		self.speed = 1.00

		self.font = pygame.font.Font(path.join("resource", "font", "arro_terminal.ttf"), 30)
		self.tsprite = Timer(self.font, (700, 115))
		self.lcsprite = Text(self.font, lambda: self.board.lineclears, (700, 260))
		self.mdsprite = Text(self.font, lambda: MODETEXT[self.level], (700, 330))
		self.spsprite = Text(self.font, lambda: self.speed, (700, 375))
		self.allsprite.add(self.tsprite, self.lcsprite, self.mdsprite, self.spsprite)

		self.eq = EventQ(self.board, level)
		self.eq.next_tetrimo()

		self.mechanics = RandomEvents(self, self.eq, self.board, self.screen)

		self.clock = pygame.time.Clock()
		if(self.level > NORMAL): self.speed *= 2
		self.running = True

		self.timer = time()

	def start(self):
		tthread = self.tsprite.start()
		if(self.level > EASY): mthread = self.mechanics.start()

		while(self.running):
			self.clock.tick(FPS)

			if(time() - self.timer >= 1/self.speed):
				self.timer = time()
				self.board.move()

			self.event()

			if(self.board.is_over()):
				self.running = False

			self.allsprite.update()
		
			while(self.eq.pause):
				pass

			self.screen.blit(self.bg, (0, 0))
			self.allsprite.draw(self.screen)
			self.screen.blit(self.eq.arrow, (50, 35))
			pygame.display.update()

		self.tsprite.stop()
		self.mechanics.stop()
		tthread.join()
		if(self.level > EASY): mthread.join()
		if(self.board.is_over()):
			self.gameover()
		self.bgm.stop()

	def event(self):
		for event in pygame.event.get():
			if event.type == QUIT:
				self.running = False
			elif event.type == KEYDOWN or event.type == KEYUP:
				self.keydown(event)

	def pause(self):
		while(True):
			for event in pygame.event.get():
				if event.type == QUIT:
					return
				elif event.type == KEYDOWN:
					if event.key == K_p:
						return
	
	def keydown(self, event):
		if(self.level == HARD or self.level == EXTREME):
			if(event.type == KEYDOWN):
				if event.key == K_UP:
					self.eq.tet.rotateL()
				elif event.key == K_DOWN:
					self.speed = 4.50
				elif event.key == K_LEFT:
					self.eq.move_left()
				elif event.key == K_RIGHT:
					self.eq.move_right()
			elif event.type == KEYUP:
				if event.key == K_DOWN:
					self.speed = 1.00
		else:
			if(event.type == KEYDOWN):
				if event.key == K_UP:
					if self.eq.tet.direction == NORTH:
						self.speed = 4.50
					elif self.eq.tet.direction == SOUTH:
						self.eq.tet.rotateL()
					elif self.eq.tet.direction == WEST:
						self.eq.move_left()
					else:
						self.eq.move_right()
				elif event.key == K_DOWN:
					if self.eq.tet.direction == NORTH:
						self.eq.tet.rotateL()
					elif self.eq.tet.direction == SOUTH:
						self.speed = 4.50
					elif self.eq.tet.direction == WEST:
						self.eq.move_right()
					else:
						self.eq.move_left()
				elif event.key == K_LEFT:
					if self.eq.tet.direction == NORTH:
						self.eq.move_right()
					elif self.eq.tet.direction == SOUTH:
						self.eq.move_left()
					elif self.eq.tet.direction == WEST:
						self.speed = 4.50
					else:
						self.eq.tet.rotateL()
				elif event.key == K_RIGHT:
					if self.eq.tet.direction == NORTH:
						self.eq.move_left()
					elif self.eq.tet.direction == SOUTH:
						self.eq.move_right()
					elif self.eq.tet.direction == WEST:
						self.eq.tet.rotateL()
					else:
						self.speed = 4.50
			elif event.type == KEYUP:
				if event.key == K_UP and self.eq.tet.direction == NORTH:
					self.speed = 1.00
				elif event.key == K_DOWN and self.eq.tet.direction == SOUTH:
					self.speed = 1.00
				elif event.key == K_LEFT and self.eq.tet.direction == WEST:
					self.speed = 1.00
				elif event.key == K_RIGHT and self.eq.tet.direction == EAST:
					self.speed = 1.00
		if event.type == KEYDOWN:
			if event.key == K_p or event.key == K_ESCAPE:
				self.pause()
			elif event.key == K_LSHIFT:
				self.eq.shift()
			elif event.key == K_SPACE:
				self.board.drop()
			elif event.key == K_z:
				self.eq.tet.rotateL()
			elif event.key == K_x:
				self.eq.tet.rotateR()

	def gameover(self):
		img = load_image("gameover.png")
		rect = img.get_rect()
		self.screen.blit(img, (0, 0))
		pygame.display.update()
		sleep(3)

if __name__ == '__main__':

	pygame.init()
	pygame.font.init()
	pygame.key.set_repeat(100, 70)

	SCREEN = pygame.display.set_mode((800, 600))
	FONT = pygame.font.Font(None, 30)
	
	g = Game(EASY, SCREEN)
	g.start()
	
	pygame.quit()
