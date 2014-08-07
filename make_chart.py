# -*- coding: utf-8 -*-
import Image
import ImageDraw
from datetime import date

# entree: une chaine du type "aaaa-mm-jj"
# retourne le nombre de jour depuis le 01-01-01
#------------------------------------------------------------------------------
def str2day(s_date):
	t = map(int,s_date.split('-'))
	return date(t[0],t[1],t[2]).toordinal()

#------------------------------------------------------------------------------
def loadValues(filename, sprint_start, sprint_end):
	res = []
	t0 = str2day(sprint_start)
	t1 = str2day(sprint_end)
	dt = t1 - t0
	f = open(filename)
	for line in f:
		line = line.strip()
		if len(line) == 0: continue
		(s_date, val) = line.split()
		t = str2day(s_date) - t0
		if t < 0 or t > dt:
			continue
		res.append((t, float(val)))
	return (res, dt)

def drawChart(width, height, vals, sprint_start, sprint_end, dt):
	l_m = 30 
	r_m = u_m = b_m = 20

	im = Image.new('RGB',(width,height)) #FIXME: image en gray ou palette de couleur.
	draw=ImageDraw.Draw(im)
	draw.rectangle((0,0,width,height), fill=(255,255,255))
	# axes
	draw.line([(l_m, u_m), 
	           (l_m, height - b_m),
	           (width - r_m, height - b_m)], 
			   fill=(0,0,0))
	# étiquettes
	draw.text((2, height - b_m +2), sprint_start, fill=(0,0,0))
	draw.text((width - 2 - draw.textsize(sprint_end)[0], height - b_m +2), sprint_end, fill=(0,0,0))
	draw.text((2, height - b_m - 8), "0", fill=(0,0,0))
	# tracé théorique
	# tracé réel
		# valmax
	valmax=0
	for (t,v) in vals:
		if v > valmax:
			valmax = v
	# facteur d'échelle x et y
	y_coef = (height - u_m - b_m) / valmax
	x_coef = (width - l_m - r_m) / dt
	draw.text((2, height - b_m - int(y_coef * vals[0][1]) - 3), str(vals[0][1]), fill=(0,0,0))
	
	# tracé 
	xy = []
	for (t,v) in vals:
		xy.append(l_m + int(x_coef * t))
		xy.append(height - b_m - int(y_coef * v))
	draw.line(xy, fill=(0,0,200), width=3)
	
	im.save("chart.png")
		
#------------------------------------------------------------------------------
(sprint_start, sprint_end) = ("2014-06-30", "2014-07-21")
(vals, dt) = loadValues("test.log", sprint_start, sprint_end)
drawChart(400,300, vals, sprint_start, sprint_end, dt)
