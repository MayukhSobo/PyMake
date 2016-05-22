from __future__ import print_function
import sys
from abc import ABCMeta
import re
import string


class Grammar(object):
    """
    Grammar class is a generic
    class for .automate file syntax
    verification and made an Abstract
    class and all the derived classes
    will get all the data structures
    where syntax is already verified

    Nevertheless, all derived classes
    may implement an additional level
    of verifications if they want but
    they can not skip any basic syntax
    verifications as indicated by Grammar
    class constructor
    """

    __metaclass__ = ABCMeta

    def __init__(self, automateFile=None):
        with open(automateFile, 'r') as af:
            self.data = af.read()
        self.mTags = [{'tag': 'proto', 'typed': 'mono1'}, {'tag': 'workspace', 'typed': 'null'}, {'tag': 'project', 'typed': 'null'}]
        self.oTags = [{'tag': 'run_test', 'typed': 'multi'}, {'tag': 'summary', 'typed': 'mono2'}]
        self.rmTag = [{'tag': 'codeline', 'typed': 'null'}]
        self.aTags = self.mTags + self.oTags + self.rmTag
        self.allData = {
        			'proto': [],
        			'codeLine': None,
        			'workspace': None,
        			'project': None,
        			'summary': [],
        }
        # self.aTags = self.uTags
        self._verify_syntax()
        # self._final_checks()

    def _braced(self):
        """
        This method is used for
        all the matching brace verification
        this should not be over-ridden and
        should only be used by the abstract
        methods of the Grammar class in all
        the derived classes

        :exception: Several instances of SyntaxError
        :return: None
        """
        try:
            braceCount = 0
            for each in self.data:
                if each == r"{":
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

    def _unique(self):
        """
        This method is used for two purposes
        and run on all the pre defined unique
        tag values

        1. Raise Exception if a tag occured multiple times
        2. Raise Exception if a tag did not occur at all

        :exception: Several instances of SyntaxError
        :return: None
        """

        # Check if all the mandatory tags are present
        for each in self.mTags:
            regex = each['tag']
            count = len(re.findall(regex, self.data.lower()))
            try:
                if count < 1:
                    e = "Can not find %s" % str(each['tag']).upper()
                    raise SyntaxError(e)
            except SyntaxError as what:
                err = "SyntaxError: %s" % str(what)
                print(err, file=sys.stderr)
                sys.exit()

        # Check if all tags are not present more than once
        for each in self.aTags:
            regex = each['tag']
            count = len(re.findall(regex, self.data.lower()))
            try:
                if count > 1:
                    e = "Multiple entries of %s" % str(each['tag']).upper()
                    raise SyntaxError(e)
            except SyntaxError as what:
                err = "SyntaxError: %s" % str(what)
                print(err, file=sys.stderr)
                sys.exit()

        # Check the relationally mandatory tag is present
        try:
        	if re.findall(r'RUN_TEST', self.data, re.IGNORECASE) and not re.findall(r'codeline', self.data, re.IGNORECASE):
        		e = "Can not find CODELINE"
        		raise SyntaxError(e)
        except SyntaxError as what:
            err = "SyntaxError: %s" % str(what)
            print(err, file=sys.stderr)
            sys.exit()

    def __core__(self, tag, typed):
        """
        Method to handle low level
        line ending of the .automate file
        and also returns 'entries' which
        is used for some further operations

        It takes an argument called "typed" which
        may have following values
                1. null:  No pruning on tag
                2. mono:  Single level prining on tag
                3. multi: Multi level pruning on tag

        :CAUTION: Very low level magic method
                  and should not be used even
                  in the Derived class. Do not
                  change this method

        :param tag:  str
        :param typed: str (null, mono, multi)

        :return: str (entries)
        """
        entries = None

        if typed == "null":
            pass
        elif typed == "mono1" or typed == "mono2":
            regex = tag + r"\s*\{(?:\n*\s*(.*?))\}"
            match = re.findall(regex, self.data, re.DOTALL | re.IGNORECASE)
            entries = match[0].split()
            for i in xrange(len(entries)):
				try:
					# if not entries[i].endswith(r",") and entries[i + 1] == r",":
					# 	entries.pop(i + 1)
					# 	entries[i] += r","
					# if not entries[i].endswith(r":") and entries[i + 1] == r":":
					# 	entries.pop(i + 1)
					# 	entries[i] += r":"
					if entries[i][-1] not in string.punctuation and entries[i + 1][-1] in string.punctuation:
						t = entries.pop(i + 1)
						entries[i] += t
				except IndexError:
					pass
        elif typed == "multi":
            pass
        return entries

    def __is_empty(self, entries, tag):
    	"""
    	Check if the tag passed does
    	have some values in the entry.
    	If the 'entries' is empty for the 'tag'
    	it will throw an exception

		:param entries: str (entries for each tag in .automate file)
    	:param tag: str (any possible tag in .automate file)

    	:CAUTION: Low level api and not to be used by derived classes

    	:return: None
    	"""
    	try:
    		if not entries:
    			e = "No entries in %s" % str(tag).upper()
    			raise AttributeError(e)
    	except AttributeError as what:
    		err = "AttributeError: %s" % str(what)
    		print(err, file=sys.stderr)
    		sys.exit()

    def __delimit__(self, entries, delimit, tag):
    	"""
    	Fallback magic method for _delimit() method.

    	It checks if all the 'entries' for a 'tag' 
    	ends with the 'delimit' mentioned

		:param tag: str ('tag' for which entries needed to be found)
    	:param entries: list (entries for the 'tag' in .automate file)
    	:param delimit: str (delimit that should be verified)

    	:exception: SyntaxError() if each values in the 'entries'
    							  doesn't end with the 'delimit'
    	"""
    	try:
    		for each in entries:
    			if not each.endswith(delimit):
    				if each[-1].isalpha() or each[-1].isdigit():
    					e = "Expected %s after %s" % (str(delimit), str(each))
    				else:
    					e = "Expected %s instead of %s in %s" % (str(delimit), str(each)[-1], str(each)[0:-1])
    				raise SyntaxError(e)
    	except SyntaxError as what:
    		err = "SyntaxError: %s" % str(what)
    		print(err, file=sys.stderr)
    		sys.exit()
    	else:
    		print([each.split()[0].split(delimit)[0] for each in entries])

    def _delimit(self):
    	for each in self.aTags:
    		entries = self.__core__(each['tag'], each['typed'])
    		if each['typed'] == 'mono1' or each['typed'] == 'mono2':
    			self.__is_empty(entries, each['tag'])

    		if each['typed'] == 'mono1':
    			# Because all the mono1 tags are ended with ','
	    		self.__delimit__(entries, r",", each['tag'])
	    	elif each['typed'] == 'mono2':
	    		# Because all the mono2 tags are ended with ':' and  ',' both
	    		self.__delimit__([entries[i] for i in xrange(len(entries)) if i % 2 != 0], r",", each['tag'])
	    		self.__delimit__([entries[i] for i in xrange(len(entries)) if i % 2 == 0], r":", each['tag'])
	    		# print([entries[i] for i in xrange(len(entries)) if i % 2 != 0])
	    		# print([entries[i] for i in xrange(len(entries)) if i % 2 == 0])

	def _final_checks(self):
		pass

    def _verify_syntax(self, check_list="All"):
        """
        API which will be used by
        the constructor of the Grammar class
        which are triggered by derived class
        constructors to activate the syntax verification

        :param check_list: provides a list strings
                           for the features that are
                           going to be verified in
                           provied by the Grammar class.

                           Currently the default value is
                           "All" which triggers all the
                           syntax verifications
        """
        if check_list.lower() == "all":
            self._braced()
            self._unique()
            self._delimit()


class Resolver(Grammar):
    def __init__(self, automateFile=None):
        Grammar.__init__(self, automateFile)

if __name__ == '__main__':
    rs = Resolver(r"sample.txt")
