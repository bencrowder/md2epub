#!/usr/bin/python
#
# md2epub.py
#
# by Ben Crowder
# http://bencrowder.net/
#
# Based off Matt Turner's GetBook.py
# http://staff.washington.edu/mdturner/personal.htm


import urllib, re, os, zipfile, glob, shutil, sys, markdown2, string, datetime
from smartypants import smartyPants

class Chapter:
	title = ''
	filename = ''
	htmlfile = ''
	dirname = ''
	id = ''
	children = []

	def __init__(self):
		self.children = []


class EPub:
	title = ''
	author = ''
	lang = 'en-US'
	basename = ''			# base name of ePub (before the extension)
	path = ''				# directory ePub will be stored in
	bookid = ''				# unique identifier
	url = ''				# URL for this book
	css = ''				# CSS file
	cover = ''				# book cover art
	toc = ''				# TOC (relative to the rest of the files)
	images = []				# list of images to be included
	children = []			# list of Chapters

	navpointcount = 1		# used for navpoint counts
	chapterids = []
	maxdepth = 1

	def cleanup(self):
		os.rmdir(self.path)


	# takes a list of chapters and writes the <item> tags for them and their children
	def write_items(self, children, f, pre):
		for chapter in children:
			# For child chapters, prepend the parent id to make this one unique
			if pre:
				id = '_' + pre + '_' + chapter.id
			else:
				id = '_' + chapter.id

			# Make sure we don't put duplicates in
			if id not in self.chapterids:
				self.chapterids.append(id)
			else:
				print 'Duplicate ID: %s' % (id)
				sys.exit(-1)

			# Write it out
			f.write('''
		<item id="''' + id + '''" href="''' + chapter.dirname + '/' + chapter.htmlfile + '''" media-type="application/xhtml+xml" />''')
			if chapter.children:
				self.write_items(chapter.children, f, id)


	# takes a list of chapters and writes the <itemref> tags for them and their children
	def write_itemrefs(self, children, f, pre):
		for chapter in children:
			if pre:
				id = '_' + pre + '_' + chapter.id
			else:
				id = '_' + chapter.id
			f.write('''
		<itemref idref="''' + id + '''"/>''')
			if chapter.children:
				self.write_itemrefs(chapter.children, f, id)


	# takes a list of chapters and writes them and their children to a navmap
	def write_chapter_navpoints(self, children, f, pre):
		for chapter in children:
			# For child chapters, prepend the parent id to make this one unique
			if pre:
				id = '_' + pre + '_' + chapter.id
			else:
				id = '_' + chapter.id

			f.write('''
		<navPoint id="''' + id + '''" playOrder="''' + str(self.navpointcount) + '''">
			<navLabel><text>''' + chapter.title + '''</text></navLabel>
			<content src="''' + chapter.dirname + '/' + chapter.htmlfile + '''" />''')
			self.navpointcount += 1
			if chapter.children:
				self.write_chapter_navpoints(chapter.children, f, id)
			f.write('''
		</navPoint>''')


	# takes a list of chapters and converts them and their children to Markdown
	def convert_chapters_to_markdown(self, children):
		for chapter in children:
			try:
				input = open('../../' + chapter.filename, 'r')
				if not os.path.exists(chapter.dirname):
					os.mkdir(chapter.dirname)
				f = open(chapter.dirname + '/' + chapter.htmlfile, 'w')
			except:
				print 'Error reading file "%s" from table of contents.' % chapter.filename
				sys.exit(-1)
			sourcetext = input.read()
			input.close()

			# write HTML header
			f.write('''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>''' + self.title + '''</title>''')
			if self.css:
				f.write('\n\t<link rel="stylesheet" type="text/css" href="../' + self.css + '" />')
			f.write('''
<meta http-equiv="Content-Type" content="application/xhtml+xml; charset=utf-8" /> 
</head>
<body>''')

			# write the Markdowned text
			htmltext = smartyPants(markdown2.markdown(sourcetext))
			f.write(htmltext.encode('utf-8'))

			# write HTML footer
			f.write('''
</body>
</html>''')

			f.close()

			if chapter.children:
				self.convert_chapters_to_markdown(chapter.children)


	# the main worker
	def save(self):
		# get current working directory
		cwd = os.getcwd()

		# create directory for the ePub
		os.mkdir(self.path)
		os.chdir(self.path)

		try:
			# make mimetype
			f = open('mimetype','w')
			f.write('application/epub+zip')
			f.close()

			# make the META-INF/container.xml
			os.mkdir('META-INF')
			os.chdir('META-INF')
			f = open('container.xml','w')
			f.write('''<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
	<rootfiles>
		<rootfile full-path="OEBPS/metadata.opf" media-type="application/oebps-package+xml" />
	</rootfiles>
</container>''')
			f.close()
			os.chdir('..')

			# make OEBPS/metadata.opf
			os.mkdir('OEBPS')
			os.chdir('OEBPS')
			f = open('metadata.opf','w')
			f.write('''<?xml version="1.0"?>
<package version="2.0" xmlns="http://www.idpf.org/2007/opf"
		 unique-identifier="bookid">
	<metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
		<dc:title>''' + self.title + '''</dc:title>
		<dc:creator opf:role="aut">''' + self.author + '''</dc:creator>
		<dc:language>''' + self.lang + '''</dc:language>
		<dc:identifier id="bookid">''' + self.url + '''</dc:identifier>''')
			if self.cover:
				f.write('\n\t\t<meta name="cover" content="book-cover" />')

			f.write('''
	</metadata>
	<manifest>
		<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml" />
''')

			if self.css:
				f.write('\t\t<item id="style" href="' + self.css + '" media-type="application/css" />')

			if self.cover:
				imagefile = os.path.basename(self.cover)
				ext = os.path.splitext(imagefile)[1][1:]	# get the extension
				if ext == 'jpg':
					ext = 'jpeg'
				f.write('\t\t<item id="book-cover" href="' + self.cover + '" media-type="image/' + ext + '" />')

			# write the <item> tags
			self.write_items(self.children, f, '')

			for image in self.images:
				imagefile = os.path.basename(image)
				ext = os.path.splitext(imagefile)[1][1:]	# get the extension
				if ext == 'jpg':
					ext = 'jpeg'
				f.write('''
		<item id="''' + imagefile + '''" href="''' + imagefile + '''" media-type="image/''' + ext + '''" />''')

			f.write('''
	</manifest>
	<spine toc="ncx">''')

			# write the <itemref> tags
			self.write_itemrefs(self.children, f, '')

			f.write('''
	</spine>''')

			if self.toc:
				f.write('''
	<guide>
		<reference type="toc" title="Table of Contents" href="''' + self.toc + '''.html" />
	</guide>''')

			f.write('''
</package>''')

			f.close()

			# make toc.ncx
			f = open('toc.ncx','w')
			f.write('''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
	<head>
		<meta name="dtb:uid" content="''' + self.url + '''" />
		<meta name="dtb:depth" content="''' + str(self.maxdepth) + '''" />
		<meta name="dtb:totalPageCount" content="0" />
		<meta name="dtb:maxPageNumber" content="0" />
	</head>
	<docTitle>
		<text>''' + self.title + '''</text>
	</docTitle>
	<navMap>''')

			self.write_chapter_navpoints(self.children, f, '')

			f.write('''
	</navMap>
</ncx>''')
			f.close()

			# convert the texts to Markdown and save in the directory
			self.convert_chapters_to_markdown(self.children)

			# if there's a CSS file, copy it in
			if self.css:
				if not os.path.exists('../../' + self.css):
					print "CSS file doesn't exist."
					sys.exit(-1)
				css = open('../../' + self.css, 'r')
				csstext = css.read()
				css.close()

				cssdir = os.path.dirname(self.css)
				if not os.path.exists(cssdir):
					os.mkdir(cssdir)
				f = open(self.css, 'w')
				f.write(csstext)
				f.close()

			# copy cover art into the directory
			if self.cover:
				if not os.path.exists('../../' + self.cover):
					print "Cover art file doesn't exist."
					sys.exit(-1)
				destdir = os.path.dirname(self.cover)
				if not os.path.exists(destdir):
					os.mkdir(destdir)
				shutil.copyfile('../../' + self.cover, self.cover)

			# copy images into the directory
			for image in self.images:
				destdir = os.path.dirname(image)
				if not os.path.exists(destdir):
					os.mkdir(destdir)
				shutil.copyfile('../../' + image, image)

			# now zip the ePub up
			os.chdir('../..')
			file = zipfile.ZipFile(self.basename + '.epub', "w")
			os.chdir(self.path)

			file.write('mimetype','mimetype', zipfile.ZIP_STORED)
			file.write('META-INF/container.xml', 'META-INF/container.xml', zipfile.ZIP_DEFLATED)
			for root, dirs, filenames in os.walk('OEBPS'):
				for filename in filenames:
					filename = os.path.join(root, filename)
					file.write(filename, filename, zipfile.ZIP_DEFLATED)

			# and remove the directory
			os.chdir('..')
			shutil.rmtree(self.path)
		except:
			print "Unexpected error: ", sys.exc_info()[0]

			# if something went wrong, remove the temp directory
			os.chdir(cwd)
			shutil.rmtree(self.path)


def add_chapter(chapter, children, depth):
	# Go recursive
	if depth > 0:
		add_chapter(chapter, children[-1].children, depth - 1)
	else:
		children.append(chapter)


def process_book(filename):
	epub = EPub()

	now = datetime.datetime.now()
	epub.basename = filename.split('.')[0]
	epub.path = '%s_%s-%s-%s_%s-%s-%s' % (epub.basename, now.year, now.month, now.day, now.hour, now.minute, now.second)
	epub.url = 'http://localhost/' + epub.path		# dummy URL, replaced in control file
	epub.maxdepth = 1

	fh = open(filename, 'r')
	for line in fh.readlines():
		if line[0] == '#' or not line.strip():
			pass						# ignore comments and blank lines
		elif ':' in line and '|' not in line:			# keywords
			values = line.split(':', 1)
			keyword = values[0].strip()
			value = values[1].strip()
			if keyword == 'Title':
				epub.title = value
			elif keyword == 'Author':
				epub.author = value
			elif keyword == 'Language':
				epub.lang = value
			elif keyword == 'URL':
				epub.url = value
			elif keyword == 'TOC':
				epub.toc = value
			elif keyword == 'Image' or keyword == 'Images':
				images = value.split(',')
				# split list
				for image in images:
					epub.images.append(image.strip())
			elif keyword == 'CSS':
				epub.css = value
			elif keyword == 'Cover':
				epub.cover = value
		elif '|' in line:				# contents
			values = line.split('|')
			title = values[0].strip()
			filename = values[1].strip()

			chapter = Chapter()
			chapter.title = values[0].strip()
			chapter.filename = values[1].strip()

			# replace extension with .html
			basename = os.path.basename(chapter.filename)
			chapter.htmlfile = os.path.splitext(basename)[0] + '.html'
			chapter.dirname = os.path.dirname(chapter.filename)

			# for the ID, lowercase it all, strip punctuation, and replace spaces with underscores
			chapter.id = re.sub(r'[^a-zA-Z0-9]', r'', chapter.title.lower()).replace(' ', '_')
			
			# if there's no ID left (because the chapter title is all Unicode, for example),
			# use the basename of the file instead
			if not chapter.id:
				chapter.id = os.path.splitext(basename)[0]

			# see how deep in the tree we are
			depth = line.rfind("\t") + 1

			# keep track of maximum depth
			if depth > (epub.maxdepth - 1):
				epub.maxdepth = depth + 1

			# add the current chapter
			add_chapter(chapter, epub.children, depth)
		else:
			print "Error on the following line:\n"
			print line
			sys.exit(-1)

	fh.close()

	# create a (hopefully unique) book ID
	epub.bookid = '[' + epub.title + '|' + epub.author + ']'

	return epub


##### Main

def main():
	if (len(sys.argv) > 1):
		epub = process_book(sys.argv[1])
		epub.save()

if __name__ == "__main__":
	main()
