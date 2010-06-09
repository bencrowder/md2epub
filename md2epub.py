#!/usr/bin/python
#
# md2epub.py
#
# by Ben Crowder
# http://bencrowder.net/
#
# Based off Matt Turner's GetBook.py
# http://staff.washington.edu/mdturner
#

import urllib, re, os, zipfile, glob, shutil, sys, markdown2, string, datetime


class Chapter:
	title = ''
	filename = ''
	htmlfile = ''
	id = ''


class EPub:
	title = ''
	author = ''
	lang = 'en-US'
	basename = ''			# base name of ePub (before the extension)
	path = ''				# directory ePub will be stored in
	bookid = ''				# unique identifier
	url = ''				# URL for this book
	css = ''				# CSS file
	images = []				# list of images to be included
	content = []			# list of Chapters

	def cleanup(self):
		os.rmdir(self.path)

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
		<dc:identifier id="bookid">''' + self.url + '''</dc:identifier>
	</metadata>
	<manifest>
		<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml" />
''')

			if self.css:
				f.write('\t\t<item id="style" href="' + os.path.basename(self.css) + '" media-type="application/css" />')

			for chapter in self.content:
				f.write('''
		<item id="''' + chapter.id + '''" href="''' + chapter.htmlfile + '''" media-type="application/xhtml+xml" />''')

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

			for chapter in self.content:
				f.write('''
		<itemref idref="''' + chapter.id + '''"/>''')

			f.write('''
	</spine>
</package>''')

			f.close()

			# make toc.ncx
			f = open('toc.ncx','w')
			f.write('''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
	<head>
		<meta name="dtb:uid" content="''' + self.url + '''" />
		<meta name="dtb:depth" content="1" />
		<meta name="dtb:totalPageCount" content="0" />
		<meta name="dtb:maxPageNumber" content="0" />
	</head>
	<docTitle>
		<text>''' + self.title + '''</text>
	</docTitle>
	<navMap>''')

			n = 1
			for chapter in self.content:
				f.write('''
		<navPoint id="''' + chapter.id + '''" playOrder="''' + str(n) + '''">
			<navLabel><text>''' + chapter.title + '''</text></navLabel>
			<content src="''' + chapter.htmlfile + '''" />
		</navPoint>''')
				n += 1

			f.write('''
	</navMap>
</ncx>''')

			f.close()

			# convert the texts to Markdown and save in the directory
			for chapter in self.content:
				input = open('../../' + chapter.filename, 'r')
				f = open(chapter.htmlfile, 'w')
				sourcetext = input.read()
				input.close()

				# write HTML header
				f.write('''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<title>''' + self.title + '''</title>''')
				if self.css:
					f.write('\n\t<link rel="stylesheet" type="text/css" href="' + os.path.basename(self.css) + '" />')
				f.write('''
	<meta http-equiv="Content-Type" content="application/xhtml+xml; charset=utf-8" /> 
</head>
<body>''')

				# write the Markdowned text
				f.write(markdown2.markdown(sourcetext).encode('utf-8'))

				# write HTML footer
				f.write('''
</body>
</html>''')

				f.close()

			# if there's a CSS file, copy it in
			if self.css:
				css = open('../../' + self.css, 'r')
				csstext = css.read()
				css.close()
				f = open(os.path.basename(self.css), 'w')
				f.write(csstext)
				f.close()

			# copy images into the directory
			for image in self.images:
				dest = os.path.basename(image)
				shutil.copyfile('../../' + image, dest)

			# now zip the ePub up
			os.chdir('../..')
			file = zipfile.ZipFile(self.basename + '.epub', "w")
			os.chdir(self.path)

			file.write('mimetype','mimetype', zipfile.ZIP_STORED)
			file.write('META-INF/container.xml', 'META-INF/container.xml', zipfile.ZIP_DEFLATED)
			for filename in glob.glob("OEBPS/*"):
				file.write(filename, filename, zipfile.ZIP_DEFLATED)

			# and remove the directory
			os.chdir('..')
			shutil.rmtree(self.path)
		except:
			# if something went wrong, remove the temp directory
			os.chdir(cwd)
			shutil.rmtree(self.path)


def process_book(filename):
	epub = EPub()

	now = datetime.datetime.now()
	epub.basename = filename.split('.')[0]
	epub.path = '%s_%s-%s-%s_%s-%s-%s' % (epub.basename, now.year, now.month, now.day, now.hour, now.minute, now.second)
	epub.url = 'http://localhost/' + epub.path		# dummy URL, replaced in control file

	fh = open(filename, 'r')
	for line in fh.readlines():
		if ':' in line:					# keywords
			values = line.split(':')
			keyword = values[0].strip()
			value = values[1].strip()
			if keyword == 'Title':
				epub.title = value
			elif keyword == 'Author':
				epub.author = value
			elif keyword == 'Language':
				epub.lang = value
			elif keyword == 'URL':
				epub.url = ''.join([values[1].strip(), ':', values[2].strip()])
			elif keyword == 'Image' or keyword == 'Images':
				images = value.split(',')
				# split list
				for image in images:
					epub.images.append(image.strip())
			elif keyword == 'CSS':
				epub.css = value
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

			# for the ID, lowercase it all, strip punctuation, and replace spaces with underscores
			chapter.id = re.sub(r'[^a-zA-Z0-9]', r'', chapter.title.lower()).replace(' ', '_')
		 	# chapter.id = chapter.id.translate(string.maketrans('',''), string.punctuation).replace(' ', '_')

			epub.content.append(chapter)
		else:
			if line[0] == '#' or not line.strip():
				# ignore comments and blank lines
				pass
			else:
				print 'Error!'

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
