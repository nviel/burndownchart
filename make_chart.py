#!/usr/bin/python3
# -*- coding: utf-8 -*-
#import PIL
#import Image
#import ImageDraw

from PIL import Image, ImageDraw
from datetime import date
from iteration import Iteration

#------------------------------------------------------------------------------
def drawChart(width, height, it):
	# margins' definition.
	l_m = 30 
	r_m = u_m = b_m = 20

	im = Image.new('RGB',(width,height)) 
	draw=ImageDraw.Draw(im)
	# fond blanc
	draw.rectangle((0,0,width,height), fill=(255,255,255))
	# axes
	draw.line([ (l_m, u_m), 
	            (l_m, height - b_m),
	            (width - r_m, height - b_m)
	          ], 
	          fill=(0,0,0))
	# étiquettes
	draw.text((2, height - b_m +2), it.startDate, fill=(0,0,0))
	draw.text((width - 2 - draw.textsize(it.endDate)[0], height - b_m +2), it.endDate, fill=(0,0,0))
	draw.text((2, height - b_m - 8), "0", fill=(0,0,0))
	
	# tracé théorique (si toute l'équipe travaillait parfaitement selon les prévisions).
	# TODO
	
	if len(it.stats) == 0:
		return im
	
	# tracé réel (courbe issue des mesures)
	valmax=0   # valeur maximum de la courbe
	for (t,v) in it.stats:
		if v > valmax:
			valmax = v
			
	# facteur d'échelle x et y
	y_coef = (height - u_m - b_m) / valmax
	x_coef = (width - l_m - r_m) / it.duration
	draw.text((2, height - b_m - int(y_coef * it.stats[0][1]) - 3), str(it.stats[0][1]), fill=(0,0,0))
	
	# tracé 
	xy = []
	for (t,v) in it.stats:
		xy.append(l_m + int(x_coef * t))
		xy.append(height - b_m - int(y_coef * v))
	draw.line(xy, fill=(0,0,200), width=3)
	
	return im

#------------------------------------------------------------------------------
def build_chart_file(chart_file_name, it):
	im = drawChart(400,300, it)
	im.save(chart_file_name)


if __name__ == '__main__':
	iteration = Iteration()
	print(iteration)
	build_chart_file('TEST_CHART.png', iteration)


