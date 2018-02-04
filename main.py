import curses;
import curses.textpad;
#from PIL import Image; # THIS IS NOT BEING USED
import numpy as np;
import os;
from PyPDF2 import PdfFileWriter, PdfFileMerger, PdfFileReader;

class QnD_CursesEngineFrontEnd:
	def __init__(self, mainscreen):
		self.title = "PDF Merger"
		self.static_configurations()
		self.height = mainscreen.getmaxyx()[0] - 1; 
		self.width  = mainscreen.getmaxyx()[1] - 0;
		self.mainscreen = mainscreen
		self.activescreen = mainscreen
		self.introduction()
		self.setUpCanvas()
		starters = [self.backend.loadDirectories, self.backend.loadAllFiles, self.backend.loadAllTags, self.backend.loadNameWriter]
		loopers  = [self.loop_folderExplorer, self.loop_initialSearch, self.loop_secondSearch, self.loop_writeName]
		end = False
		for p in range(len(starters)):
			if not end:
				self.resetCanvas()
				starters[p]()
				end = self.inputLoop(loopers[p])
		if not end:
			self.backend.mergeIntoSingleFile()
	
	def static_configurations(self):
		curses.noecho()
		curses.cbreak()
		curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)	
		curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
		curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_RED)
		self.backend = QnD_CursesEngineBackEnd()
		self.pos = {}
		self.pos['RIGHT'] = [ 1, 0];self.pos['LEFT' ] = [-1, 0]
		self.pos['UP'   ] = [ 0,-1];self.pos['DOWN' ] = [ 0, 1]
		self.deathKeys = ['^[', "KEY_F(1)", "^C"]
	
	def introduction(self):
		pass
	
	def setUpCanvas(self):
		self.mainscreen.addstr(self.title, curses.A_REVERSE)
		self.mainscreen.move(self.height-1,0)
		self.mainscreen.addstr("[F1] to EXIT / [F2] to (UN)HIDE CURSOR / [ENTER] to CONTINUE \n[Arrows] to MOVE / [w] to SHIFT UP / [s] to SHIFT DOWN / [SPACE] to CHANGE CONFIGURATION")
		curses.textpad.rectangle(self.mainscreen, 1, 0, self.height - 1 - 1, self.width -1 - 0);
		begin_x = 1; 
		begin_y = 2; 	
		self.wind = self.mainscreen.subpad((self.height - 4), self.width - 2, begin_y, begin_x)	
		self.wind.bkgd("-", curses.color_pair(2))
		self.backend.configureWindow(self.wind)
		self.wind.scrollok(True)
		self.resetCanvas()
		
	def resetCanvas(self):	
		self.wind.move(0,0)
		self.wind.refresh()
		self.wind.cursyncup()

	def inputLoop(self, loop_function):
		i = 0
		self.mainscreen.move(0,i)
		pointer_capture = False
		a = str(self.mainscreen.getkey())
		while not a in self.deathKeys and a!='\n':
			i = (i+1)%len(self.title)
			if not pointer_capture:
				self.mainscreen.move(0,i)
			
			if a == "KEY_F(2)":
				pointer_capture = not pointer_capture
			else:
				loop_function(a)
				
			self.wind.refresh()
			if pointer_capture:
				self.wind.cursyncup()
			a = str(self.mainscreen.getkey())
		return a != "\n"	

	def loop_folderExplorer(self,a):
		if a in ['KEY_' + x for x in ['RIGHT', 'LEFT', 'UP', 'DOWN']] :
			mov_x,mov_y = self.pos[a[4:]]
			self.moveCursor(mov_x, mov_y, len(self.backend.paths), origin = "directories", offsety = 1)
		elif a == " ":
			y = self.wind.getyx()[0]
			ypfl = y - 1 + self.backend.firstLine
			string = self.backend.paths[ypfl]
			os.chdir(self.backend.paths[ypfl])
			self.backend.loadDirectories()
		else:
			pass

	def loop_initialSearch(self,a):
		if a in ['KEY_' + x for x in ['RIGHT', 'LEFT', 'UP', 'DOWN']] :
			mov_x,mov_y = self.pos[a[4:]]
			self.moveCursor(mov_x, mov_y, len(self.backend.files), origin = "files")
		if a in ["s", "w"]:
			mov_x = 0
			mov_y = {"s":1, "w":-1}[a]
			self.moveCursor(mov_x,mov_y, len(self.backend.files), 'change_text', origin = "files")
		elif a == " ":
			y = self.wind.getyx()[0]
			ypfl = y + self.backend.firstLine
			self.backend.ticks[ypfl] = not self.backend.ticks[ypfl]
			self.wind.addch(y,1,"x" if self.backend.ticks[ypfl] else " ")
		else:
			pass
			
	def loop_secondSearch(self,a):
		if a in ['KEY_' + x for x in ['RIGHT', 'LEFT', 'UP', 'DOWN']] :
			mov_x,mov_y = self.pos[a[4:]]
			self.moveCursor(mov_x, mov_y, len(self.backend.tags), origin = "tags")
		elif a == " ":
			y = self.wind.getyx()[0]
			yp = y + self.backend.firstLine
			
			oldt1 = self.backend.ticks[yp]
			self.backend.ticks[yp]  = self.backend.ticks2[yp]
			self.backend.ticks2[yp] = not oldt1
			
			self.wind.addch(y, 6,"Y"  if self.backend.ticks[yp] else "N")
			self.wind.addch(y,21,"Y" if self.backend.ticks2[yp] else "N")
		else:
			pass

	def loop_writeName(self,a):
		if a in [curses.KEY_BACKSPACE, "^?", "\b"]:
			self.wind.addch(a)
			self.wind.addch(" ")
			self.wind.addch(a)
			self.backend.outputname = self.backend.outputname[:-1] 
		elif len(a) == 1:
			self.wind.addch(a)
			self.backend.outputname += a
		else:
			pass
			
	def moveCursor(self, mov_x,mov_y, entries,additionals = 'none', origin = 'none', offsety = 0):
		flags = additionals.split("/") 
		y,x = self.wind.getyx()
		y -= offsety
		new_y = y + mov_y
		new_x = x + mov_x
		full_maxy, maxx = self.wind.getmaxyx()
		full_maxy -= offsety
		maxy = min(full_maxy, entries)
			
		if ((new_y < 0) or (new_y >= maxy and full_maxy <= entries)):
			if self.backend.moreLines(mov_y, origin,offsety):
				lines_saved = []
				for tosave in range(0,offsety):				
					lines_saved.append(self.wind.instr(tosave,0, maxx).decode('UTF-8'))
				self.wind.scroll(mov_y)
				self.backend.firstLine += mov_y
				y -= mov_y
				new_y -= mov_y
				self.wind.insstr(new_y + offsety,0,self.backend.getLine(0 if (mov_y == -1) else -1, origin, offsety))
				for tosave in range(0,offsety):				
					self.wind.insstr(tosave,0,lines_saved[tosave])
				
		if new_y >= 0 and new_y < maxy and new_x >= 0 and new_x < maxx:
			if (mov_y != 0):
				if 'change_text' in flags:
					old_string = self.wind.instr(y,0, maxx).decode('UTF-8')
					self.wind.insstr(y,0, self.wind.instr(new_y,0).decode('UTF-8'))
					self.wind.insstr(new_y,0, old_string)
					old_strings = self.backend.files[y + self.backend.firstLine]
					self.backend.files[y + self.backend.firstLine] = self.backend.files[new_y + self.backend.firstLine]
					self.backend.files[new_y + self.backend.firstLine] = old_strings
					old_truth = self.backend.ticks[y + self.backend.firstLine]
					self.backend.ticks[y + self.backend.firstLine] = self.backend.ticks[new_y + self.backend.firstLine]
					self.backend.ticks[new_y + self.backend.firstLine] = old_truth
				self.backend.changeLineColor(new_y + offsety,curses.color_pair(1))
				self.backend.changeLineColor(y + offsety,curses.color_pair(2))
			self.wind.move(new_y+offsety,new_x)
	
class QnD_CursesEngineBackEnd:
	def __init__(self):
		self.wind      =  None
		self.paths     = [     ]
		self.files     = [     ]
		self.ticks     = [     ]
		self.ticks2    = [     ]
		self.tags      = [     ]
		self.firstLine =    0
		self.maxLines  =    0
		self.maxLength =    0
		self.outputname = "output"
	
	# THIS IS NOT MINE, I GOT IT FROM A GOOGLE SEARCH
	# IT'S A FAIRLY SMALL [IMAGE-TO-ASCII] CONVERTER	
	#
	#def asciiImageLoad(self,file, scale, factor):
	#	f, SC, GCF, WCF = file, scale, factor, 7/4 
	#	chars = np.asarray(list(' .,:;irsXA253hMHGS#9B&@'))
	#	img = Image.open(f)
	#	S = ( round(img.size[0]*SC*WCF), round(img.size[1]*SC) )
	#	img = np.sum( np.asarray( img.resize(S) ), axis=2)
	#	img -= img.mina()
	#	img = (1.0 - img/img.max())**GCF*(chars.size-1)
	#	lines = ("".join(r) for r in chars[img.astype(int)])
	#	return(lines)

	def configureWindow(self, wind):
		self.wind = wind
		self.maxLines, self.maxLength =  self.wind.getmaxyx()
	

	def loadDirectories(self):
		self.wind.clear()
		self.paths = []
		for path in [".."] + os.listdir(os.getcwd()):
			if not os.path.isfile(os.path.join(os.getcwd(), path)):
				self.paths.append(path)
		self.wind.move(0,0)
		self.wind.addstr(os.getcwd())
		y = 0
		maxy = self.maxLines
		for x in range(0,min(self.maxLines - 1, len(self.paths))):
			y+=1
			self.wind.move(y,0)
			self.wind.addstr(self.getLine(x, "directories"))
		self.wind.move(1,0)
		self.changeLineColor(1,curses.color_pair(1))
		self.wind.refresh()
		self.wind.cursyncup()
	
	def loadAllFiles(self):
		self.wind.clear()
		self.firstLine = 0
		for file in os.listdir(os.getcwd()):
			if file.endswith(".pdf"):
				self.files.append(str(file))
				self.ticks.append(True)
		y = -1
		maxy = self.maxLines
		for x in range(0,min(self.maxLines, len(self.files))):
			y+=1
			self.wind.move(y,0)
			self.wind.addstr(self.getLine(x, "files"))
		self.wind.move(0,0)
		self.changeLineColor(0,curses.color_pair(1))
		self.wind.refresh()
		self.wind.cursyncup()
		
		
	def loadAllTags(self):
		self.wind.clear()
		self.firstLine = 0
		self.tags = [self.files[x] for x in range(0,len(self.files)) if self.ticks[x]]
		self.ticks =  [True for x in self.tags]
		self.ticks2 = [True for x in self.tags]
		y = -1
		for x in range(0,min(self.maxLines, len(self.tags))):
			y+=1
			self.wind.move(y,0)
			self.wind.addstr(self.getLine(x,"tags"))
		self.wind.move(0,0)
		self.changeLineColor(0,curses.color_pair(1))
		self.wind.refresh()
		self.wind.cursyncup()

	def loadNameWriter(self):
		self.wind.clear()
		self.wind.move(0,0)
		self.wind.addstr("Write output name (without pdf extention)")
		self.changeLineColor(0,curses.color_pair(3))
		self.wind.move(1,0)
		self.wind.addstr(self.outputname)
		#self.wind.move(0,0)
		self.wind.refresh()
		self.wind.cursyncup()
		
	def moreLines(self, direction, origen, offset = 0):
		length = 0
		if origen == "directories":
			length = len(self.paths)
		elif origen == "files":
			length = len(self.files)
		elif origen == "tags":
			length = len(self.tags)
		else:
			raise Exception("More lines receives a wrong origin parameter ({})".format(origen))
		return list([self.firstLine > 0, self.firstLine + self.maxLines - offset < length])[int((direction + 1)/2)]
	
	def getLine(self, number, origin = "", offset = 0):
		if number == -1:
			number = self.firstLine + self.maxLines - offset - 1
		else:
			number += self.firstLine
		return self.stringLines(number,origin)
	
	def stringLines(self,i,origin):
		assert(i != -1)
		if origin == "directories":
			return ">>'{}'".format(self.paths[i][:self.maxLength-4])
		elif origin == "files":
			return '[{}] "{}"'.format("x" if self.ticks[i] else " ", self.files[i][:self.maxLength-6])
		elif origin == "tags":
			return 'List?({}) ImportTags?({}) >> "{}"'.format("Y" if self.ticks[i] else "N", "Y" if self.ticks2[i] else "N", self.tags[i][:self.maxLength-29])
		else:
			raise Exception("stringLines was called with the wrong 'origin' parameter ({})".format(origin))
	
	def mergeIntoSingleFile(self):
		files = [[self.tags[x],self.ticks[x],self.ticks2[x]] for x in range(len(self.tags))]
		if files != []:
			merger = PdfFileMerger()
			for fname,ftag, ftag2 in files:
				merger.append(PdfFileReader(open (fname, 'rb')), bookmark = fname if ftag2 else None, import_bookmarks=ftag)
			merger.write(self.outputname + ".pdf")
		
	def changeLineColor(self, y, newcolor):
		self.wind.chgat(y,0,newcolor)

curses.wrapper(QnD_CursesEngineFrontEnd)
