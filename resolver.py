from __future__ import print_function
import sys
from abc import ABCMeta, abstractmethod
import re


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
        self.mTags = ['proto', 'workspace', 'project']
        self.oTags = ['run_test', 'summary']
        self.rmTag = ['codeline']
        self.uTags = self.uTags = self.mTags + self.oTags + self.rmTag
        self.aTags = self.uTags
        self._verify_syntax()

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
        for each in self.uTags:
            regex = each
            count = len(re.findall(regex, self.data.lower()))
            try:
                if count < 1:
                    e = "Can not find %s" % str(each).upper()
                    raise SyntaxError(e)
                elif count > 1:
                    e = "Multiple entries of %s" % str(each).upper()
                    raise SyntaxError(e)
            except SyntaxError as what:
                err = "SyntaxError: %s" % str(what)
                print(err, file=sys.stderr)
                sys.exit()

    def __core__(self, tag, typed):
        """
        Method to handle low level
        line ending of the .automate file
        and also returns self.entries which
        is used for some further operations

        It takes an argument called "typed" which
        may have following values
                1. null:  No pruning on tag
                2. mono:  Single level prining on tag
                3. multi: Multi level pruning on tag

        :CAUTION: Very low level magic method
                  and should not be used even
                  in the Derived class

        :param tag:  str
        :param typed: str (null, mono, multi)

        :return: str (self.entries)
        """
        entries = None

        if typed == "null":
            pass
        elif typed == "mono":
            regex = tag + r"\s*\{(?:\n*\s*(.*?))\}"
            entries = re.findall(regex, self.data, re.DOTALL | re.IGNORECASE)
            print(entries)
        elif typed == "multi":
            pass
        return entries


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

class Resolver(Grammar):
    def __init__(self, automateFile=None):
        Grammar.__init__(self, automateFile)

if __name__ == '__main__':
    rs = Resolver(r"sample.txt")

