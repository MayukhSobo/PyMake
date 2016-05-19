# importing python 3 print function in python 2
from __future__ import print_function
import re
import sys

data = """
headerFiles {
	hello.h,
	hi.h,
}

sourceFiles {
	hello.c,
	hi.c,
	main.cpp,
}

 """

# data = "Hello World!"


# def prune(tag=None, desc=None):
# 	importanceValues = ["mandatory", "optional"]
# 	if desc is None:
# 		desc = {}
# 		desc['importance'] = "mandatory"
# 		desc['levels'] = 1
# 	elif r'importance' not in desc:
# 		desc['importance'] = "mandatory"
# 	elif r'levels' not in desc:
# 		desc['levels'] = 1
# 	else:
# 		try:
# 			if desc['importance'] not in importanceValues:
# 				raise AttributeError("Unsupported IMPORTANCE value")
# 				sys.exit()
# 			if desc['levels'] < 0:
# 				raise ValueError("Can not prune any negative levels")
# 		except KeyError:
# 			raise AttributeError("Unsupported pruning option")
# 			sys.exit()
# 	if tag is None:
# 		raise ValueError("No tag value passed")
# 	###########  Start checking the grammar ###########

# 	### Validation for mandatory tags ###
# 	if desc['importance'] == 'mandatory':
# 		regex = tag
# 		count = len(re.findall(regex, data, re.IGNORECASE))
# 		try:
# 			if count < 1:
# 				raise SyntaxError("Source Files are not given")
# 			elif count > 1:
# 				raise SyntaxError("Multiple entries of sourcefiles")
# 		except SyntaxError as what:
# 			err = "SyntaxError: %s" % str(what)
# 			print(err, file=sys.stderr)
# 			sys.exit()
# 	#####################################

# prune(tag=r'sourcefiles')

############# Checking for unique tag occurances ############
regex = r'sourceFiles'
count = len(re.findall(regex, data))
try:
	if count < 1:
		raise SyntaxError("Source Files are not given")
	elif count > 1:
		raise SyntaxError("Multiple entries of sourcefiles")
except SyntaxError as what:
	err = "SyntaxError: %s" % str(what)
	print(err, file=sys.stderr)
	sys.exit()
#############################################################

############ Checking for brace mismatching  ###########
try:
	braceCount = 0
	# tagData = ""
	for each in data:
		# tagData += each
		if each == r"{":
			# tag = re.match(r'.*?(\w+)\s*\{', tagData, re.DOTALL).group(1)
			# tagData = ""
			braceCount += 1
		elif each == r"}":
			braceCount -= 1
		if braceCount > 1 or braceCount < 0:
			if braceCount > 1:
				e = "Expected matching }"
			else:
				e = "Expected matching {"
			raise SyntaxError(e)
	if braceCount == 1:
		e = r"Expected matching }"
		raise SyntaxError(e)
except SyntaxError as what:
	err = "SyntaxError: %s" % str(what)
	print(err, file=sys.stderr)
	sys.exit()
########################################################

# print(re.findall(regex, data, re.IGNORECASE))
# try:
# 	if len(re.findall(regex, data, re.DOTALL)[0].split(r"}")) < 2:
# 		raise SyntaxError(r"Expected matching } at the end of sourcefiles tag")
# 	if len(re.findall(regex, data, re.DOTALL)[0].split(r"{")) < 2:
# 		raise SyntaxError(r"Expected matching { afrer sourcefiles tag")
# 	if len(re.findall(regex, data, re.DOTALL)[0].split(r"}")) > 2 or len(re.findall(regex, data, re.DOTALL)[0].split(r"{")) > 2:
# 		raise SyntaxError(r"Only a single pair of matching braces allowed")
# except SyntaxError as what:
# 	err = "SyntaxError: %s" % str(what)
# 	print(err, file=sys.stderr)
# 	sys.exit()

########## Core for further checks ############
regex = r'sourceFiles\s*\{(?:\n*\s*(.*?))\}'
match = re.findall(regex, data, re.DOTALL)
entries = match[0].split()
###############################################

#################  Removing spaces before Line Ending ##############

for i in xrange(len(entries)):
	try:
		if not entries[i].endswith(r",") and entries[i + 1] == r",":
			entries.pop(i + 1)
			entries[i] += r","
		if len(entries[i].split(r".")) > 2:
			e = "Expected , in  %s" % str(entries[i][0:-1])
			if r"," in entries[i][0:-1] and r", " not in entries[i][0:-1]:
				e = "Expected space after , in  %s" % str(entries[i][0:-1])
			raise SyntaxError(e)
	except IndexError:
		pass
	except SyntaxError as what:
		err = "SyntaxError: %s" % str(what)
		print(err, file=sys.stderr)
		sys.exit()
#####################################################################

##################  Line-ending and empty tags verification ###############
try:
	if not entries:
		raise AttributeError("No source file(s) given")
	else:
		for each in entries:
			if not each.endswith(r","):
				if each[-1].isalpha():
					e = "Expected , after %s" % str(each)
				else:
					e = "Expected , instead of %s in %s" % (str(each)[-1], str(each)[0:-1])
				# e = "Expected , after %s" % str(each)
				raise SyntaxError(e)
except AttributeError as what:
	err = "AttributeError: %s" % str(what)
	print(err, file=sys.stderr)
except SyntaxError as what:
	err = "SyntaxError: %s" % str(what)
	print(err, file=sys.stderr)
	sys.exit()
else:
	sources = [each.split()[0].split(r",")[0] for each in entries]
	print(sources)
###########################################################################
