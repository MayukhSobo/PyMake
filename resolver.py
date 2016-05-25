from __future__ import print_function
import sys
from abc import ABCMeta
import re
from pyparsing import Word, alphas, Literal
import os
# import pyparsing
# import string


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

        if automateFile is None:
            print("Cannot resolve the path for the automate file", file=sys.stderr)
            sys.exit()

        if not automateFile.lower().endswith('automate'):
            print("Invalid automate file", file=sys.stderr)
            sys.exit()

        with open(automateFile, 'r') as af:
            self.data = af.read()
        self.mTags = [{'tag': 'proto', 'typed': 'mono1'}, {'tag': 'workspace', 'typed': 'null'}, {'tag': 'project', 'typed': 'null'}]
        self.oTags = [{'tag': 'run_test', 'typed': 'multi'}, {'tag': 'summary', 'typed': 'mono2'}]
        self.rmTag = [{'tag': 'codeline', 'typed': 'null'}]
        self.aTags = self.mTags + self.rmTag + self.oTags
        # print(self.aTags)
        self._allData = {
                    'proto': [],
                    'codeline': None,
                    'workspace': None,
                    'project': None,
                    'summary': [],
                    'batches': {}
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
            regex = tag + r'\s*:\s*(.*)'
            self._allData[tag] = re.findall(regex, self.data, re.IGNORECASE)[0]

        elif typed == "mono1" or typed == "mono2":
            regex = tag + r"\s*\{(?:\n*\s*(.*?))\}"
            match = re.findall(regex, self.data, re.DOTALL | re.IGNORECASE)
            try:
                entries = match[0].split()
            except IndexError:
                if tag != r'proto':
                    return None
            for i in xrange(len(entries)):
                try:
                    if not entries[i].endswith(r",") and entries[i + 1] == r",":
                        entries.pop(i + 1)
                        entries[i] += r","
                    if not entries[i].endswith(r":") and entries[i + 1] == r":":
                        entries.pop(i + 1)
                        entries[i] += r":"
                    # if entries[i][-1] not in string.punctuation and entries[i + 1][-1] in string.punctuation:
                    #     t = entries.pop(i + 1)
                    #     entries[i] += t
                except IndexError:
                    pass
        elif typed == "multi":
            regex = tag + r"\s*\{(?:\n*\s*(.*?))\}"
            match = re.findall(regex, self.data, re.DOTALL | re.IGNORECASE)
            try:
                entries = match[0].split()
            except IndexError:
                return None
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
                        e = "Expected %s after '%s' in %s" % (str(delimit), str(each), str(tag).upper())
                    else:
                        e = "Expected %s instead of %s in %s" % (str(delimit), str(each)[-1], str(each)[0:-1])
                    raise SyntaxError(e)
        except SyntaxError as what:
            err = "SyntaxError: %s" % str(what)
            print(err, file=sys.stderr)
            sys.exit()
        else:
            if delimit == ",":
                self._allData['summary'] = [each.split()[0].split(delimit)[0] for each in entries]
            if tag == "proto":
                self._allData['proto'] = [each.split()[0].split(delimit)[0] for each in entries]

    def _delimit(self):
        for each in self.aTags:
            entries = self.__core__(each['tag'], each['typed'])
            if entries is None:
                continue
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
            elif each['typed'] == 'multi':
                toolkit = False
                browser = False
                framework = False
                if r'toolkit' in entries:
                    toolkit = True
                if r'browser' in entries:
                    browser = True
                if r'framework' in entries:
                    framework = True
                try:
                    if not (toolkit and browser and framework):
                        raise ValueError("Can not find all codelines in RUN_TEST")
                except ValueError as what:
                    err = "ValueError: %s" % str(what)
                    err += r"....If you have provided all, please give space after them"
                    print(err, file=sys.stderr)
                    sys.exit()

                for each in entries:
                    if each == r"[]":
                        e = "Space is expected between braces in []"
                        raise SyntaxError(e)
                openBraceIndex = [i for i, x in enumerate(entries) if x == r"["]
                closeBraceIndex = [i for i, x in enumerate(entries) if x == r"]"]
                BraceIndex = zip(openBraceIndex, closeBraceIndex)
                if len(openBraceIndex) > len(closeBraceIndex):
                    e = "Extra/Unmatched '[' found in the RUN_TEST tag"
                    raise SyntaxError(e)
                elif len(openBraceIndex) < len(closeBraceIndex):
                    e = "Extra/Unmatched ']' found in the RUN_TEST tag"
                    raise SyntaxError(e)
                if len(BraceIndex) > 3:
                    e = "Unnecessary square braces found in RUN_TEST"
                    raise SyntaxError(e)
                if len(BraceIndex) < 3:
                    e = "Not all codelines are surrounded by square braces in RUN_TEST"
                    raise SyntaxError(e)
                # toolkitIndex = entries.index(r'toolkit')

                # temp = ['toolkit', 'browser', 'framework']
                # temp.remove(entries[BraceIndex[0][0] - 1])
                _Batches = {'toolkitBatches': None, 'frameworkBatches': None, 'browserBatches': None}
                if self._allData['codeline'] == 'toolkit':
                    if entries[BraceIndex[0][0] - 1].lower() == r"toolkit":
                        k = 0
                    elif entries[BraceIndex[1][0] - 1].lower() == r"toolkit":
                        k = 1
                    elif entries[BraceIndex[2][0] - 1].lower() == r"toolkit":
                        k = 2
                    # print()
                    # print("ToolKit Batches: ", end="")
                    # print("k = ", k)
                    _Batches['toolkitBatches'] = entries[BraceIndex[k][0] + 1: BraceIndex[k][1]]
                    # print()
                elif self._allData['codeline'] == 'framework':
                    if entries[BraceIndex[0][0] - 1].lower() == r"framework":
                        k = 0
                    elif entries[BraceIndex[1][0] - 1].lower() == r"framework":
                        k = 1
                    elif entries[BraceIndex[2][0] - 1].lower() == r"framework":
                        k = 2
                    # print()
                    # print("FrameWork Batches: ", end="")
                    _Batches['frameworkBatches'] = entries[BraceIndex[k][0] + 1: BraceIndex[k][1]]
                    # print()
                elif self._allData['codeline'] == 'browser':
                    if entries[BraceIndex[0][0] - 1].lower() == r"browser":
                        k = 0
                    elif entries[BraceIndex[1][0] - 1].lower() == r"browser":
                        k = 1
                    elif entries[BraceIndex[2][0] - 1].lower() == r"browser":
                        k = 2
                    # print()
                    # print("Browser Batches: ", end="")
                    _Batches['browserBatches'] = entries[BraceIndex[k][0] + 1: BraceIndex[k][1]]
                    # print()
                # print(Batches)
                # for each in _Batches:
                #     if _Batches[each] is not None:
                #         temp = _Batches[each]
                #         print(temp)
                #         for i in xrange(len(temp)):
                #             if i % 2 == 0 and temp[i][-1] != r":":
                #                 e = "Expected : after %s" % str(temp[i])
                #                 raise SyntaxError(e)
                #         Batches = _Batches[each]
                # print(self._allData)
                s = _Batches[self._allData['codeline'] + "Batches"]
                _batches = "".join(s)
                # print(_batches)
                # _batches = "batch1:(!product5)"
                # print(_batches)
                digits = "0123456789"
                comma = ","
                no = "!"
                every = "*"
                underscore = "_"
                dash = "-"

                batchName = Word(alphas + digits + underscore)
                colons = Literal(":")
                openBrace = Literal("(")
                entries = Word(alphas + comma + no + every + digits + underscore + dash)
                closeBrace = Literal(")")
                batchEntry = batchName + colons + openBrace + entries + closeBrace

                rs = len(_batches)
                while rs > 0:
                    k = batchEntry.parseString(_batches)
                    self._allData['batches'][k[0]] = k[3].split(r",")
                    m = len("".join(k))
                    rs -= m
                    _batches = _batches[m::]
            elif each['typed'] == 'null':
                pass

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

    @staticmethod
    def get_raw_data(self):
        return self._allData


class Resolver(Grammar):
    def __init__(self, automateFile=None):
        Grammar.__init__(self, automateFile)
        self.allData = Grammar.get_raw_data(self)
        self.protos = []
        self.test = None
        self.workspace = None
        self.project = None
        self.summary = []
        self.batch = {}

    def verify_protos(self):
        self.protos = self.allData['proto']
        return True

    def verify_workspace(self):
        self.workspace = self.allData['workspace']
        return os.path.exists(self.allData['workspace'])

    def verify_project(self):
        self.project = self.allData['project']
        return os.path.exists(os.path.join(self.allData['workspace'], 'source', self.allData['project']))

    def verify_summary(self):
        # print(self.allData['summary'])
        self.summary.append(self.allData['summary'][0].lower())

        if self.summary[0] == "yes":
            try:
                self.summary.append(self.allData['summary'][1])
                if not os.path.exists(self.summary[1]):
                    self.summary[1] = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.summary[1])
                    return os.path.exists(self.summary[1])
            except IndexError:
                return False
        return True

    def resolve_batches(self):
        self.test = "yes"
        if not self.allData['batches']:
            self.test = "no"
        else:
            var = False
            for each in self.allData['batches']:
                if self.allData['batches'][each] == ['!*']:
                    m = False
                    self.batch[each] = None
                else:
                    m = True

                    if len(self.allData['batches'][each]) > 1:
                        self.batch[each] = self.allData['batches'][each]
                    else:
                        if self.allData['batches'][each] == ['*']:
                            self.batch[each] = self.allData['proto']
                        else:
                            blklst = self.allData['batches'][each][0][1::]
                            prts = self.allData['proto'][:]
                            prts.remove(blklst)
                            self.batch[each] = prts
                var = var or m
            if not var:
                self.test = "no"

        # pass

if __name__ == '__main__':
    try:
        rs = Resolver(r"tester.automate")
        if not rs.verify_workspace():
            e = "Can not resolve the workspace"
            raise ValueError(e)
        if not rs.verify_project():
            e = "Can not resolve the project in the workspace"
            raise ValueError(e)
        if not rs.verify_summary():
            e = "Path for summary is either none or invalid"
            raise ValueError(e)
    except ValueError as what:
        err = "ValueError: %s" % str(what)
        print(err, file=sys.stderr)
        sys.exit()
    except IOError:
        err = "Can not access/open the .automate file"
        print(err, file=sys.stderr)
        sys.exit()
    rs.verify_protos()
    rs.resolve_batches()
    print("Batches", rs.batch)
    print("test", rs.test)
    print("Summary", rs.summary)
    print("Workspace", rs.workspace)
    print("Project", rs.project)
    print("Protos", rs.protos)

