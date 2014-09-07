#!/usr/bin/python3
# -*- coding: utf-8 -*-
#import PIL
#import Image
#import ImageDraw

from PIL import Image, ImageDraw
from datetime import date
from iteration import Iteration

class Chart:
	
	def __init__(self, w, h, it):
		self.w = w
		self.h = h
		self.it = it
		self.l_m = 30
		self.r_m = self.u_m = self.b_m = 20
		valmax=0   # valeur maximum de la courbe
		for (t,v) in it.stats:
			if v > valmax:
				valmax = v
		# facteur d'échelle x et y
		self.y_coef = (self.h - self.u_m - self.b_m) / valmax
		self.x_coef = (self.w - self.l_m - self.r_m) / it.duration
		
	def X(self, x):
		return self.l_m + int(self.x_coef * x)
	
	def Y(self, y):
		return self.h - self.b_m - int(self.y_coef * y)
	
	def draw(self):
		im = Image.new('RGB',(self.w,self.h)) 
		draw=ImageDraw.Draw(im)
		# fond blanc
		draw.rectangle((0,0,self.w,self.h), fill=(255,255,255))
		# axes
		draw.line([ (self.l_m, self.u_m), 
			(self.l_m, self.h - self.b_m),
			(self.w - self.r_m, self.h - self.b_m)
			], 
			fill=(0,0,0))
		# étiquettes
		draw.text((2, self.h - self.b_m +2), self.it.startDate, fill=(0,0,0))
		draw.text((self.w - 2 - draw.textsize(self.it.endDate)[0], self.h - self.b_m +2), self.it.endDate, fill=(0,0,0))
		draw.text((2, self.h - self.b_m - 8), "0", fill=(0,0,0))
	
		if len(self.it.stats) == 0:
			return im
	
		draw.text((2, self.Y(self.it.stats[0][1]) - 3), str(self.it.stats[0][1]), fill=(0,0,0))

		# tracé théorique (si toute l'équipe travaillait parfaitement selon les prévisions).
		draw.line((self.X(0), self.Y(self.it.stats[0][1]), self.X(self.it.duration), self.Y(0)), fill=(200,0,0), width=2)
	
		# tracé réel
		xy = []
		for (t,v) in self.it.stats:
			xy.append(self.X(t))
			xy.append(self.Y(v))
		draw.line(xy, fill=(0,0,200), width=3)
	
		return im

#------------------------------------------------------------------------------
def build_chart_file(chart_file_name, it):
	chart = Chart(400,300, it)
	im = chart.draw()
	im.save(chart_file_name)


if __name__ == '__main__':
	iteration = Iteration()
	print(iteration)
	build_chart_file('TEST_CHART.png', iteration)


