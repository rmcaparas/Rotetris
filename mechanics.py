import pygame
from pygame.locals import *

from os import path
from threading import Thread
from time import *
from random import randint, choice

def load_image(file, colorkey = None):
	surf = pygame.image.load(path.join('resource', file)).convert()
	if colorkey is not None:
		if colorkey is -1:
			colorkey = surf.get_at((0,0))
		surf.set_colorkey(colorkey, RLEACCEL)
	return surf

class RandomEvents():

	def __init__(self, game, eq, board, screen):
		self.game = game
		self.eq = eq
		self.board = board
		self.screen = screen
		self.doge_img = load_image("doge.png")
		self.running = False

		self.events = [self.speed_up]

		self.timer = 0

	def run(self):
		while(self.running):
			sleep(1)
			if(time() - self.timer > 10):
				print "evnet"
				n = randint(1, 100)
				if(n <= 100):
					choice(self.events)()
				self.timer = time()

	def stop(self):
		self.running = False

	def start(self):
		self.running = True
		t = Thread(target = self.run)
		self.timer = time()
		t.start()
		return t

	def doge(self):
		self.eq.pauseG()
		self.screen.blit(self.doge_img, (0, 0))
		pygame.display.update()
		sleep(1)
		self.eq.playG()

	def tetrimo_rotate(self):
		choice([self.eq.tet.rotateL, self.eq.tet.rotateL])()

	def board_rotate(self):
		choice([self.board.rotateL, self.board.rotateR])()

	def speed_up(self):
		self.game.speed *= 3.00
		sleep(5)
		self.game.speed /= 3.00

	def speed_down(self):
		pass