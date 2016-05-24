import re

s = ['batch1', ':', '(!', 'product3', ')', 'batch2', ':', '(product1', ',', 'product4', ',', 'product5', ')']
s = "".join(s)
print s
# batch1:(!product3)batch2:(product1,product4,product5)
# {'batch1': ['!product3'], 'batch2': ['product1', 'product4', 'product5']}
# print re.findall(r'(.*?)\:', s)
openBraceIndex = [i for i, x in enumerate(s) if x == r"("]
closeBraceIndex = [i for i, x in enumerate(s) if x == r")"]
print openBraceIndex
print closeBraceIndex

if len(openBraceIndex) != len(closeBraceIndex):
    err = "PROTO names are not enclosed within () in RUN_TEST"
    raise SyntaxError(err)
BraceIndex = zip(openBraceIndex, closeBraceIndex)
for each in BraceIndex:
    temp = s[each[0] + 1: each[1]]
    print temp
