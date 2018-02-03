a1 = list(map(int, input().split()))
a2 = list(map(int, input().split()))
res = []
#assuming the elements in the lists are sorted
l1 = len(a1)
l2 = len(a2)
ind1, ind2 = 0, 0
while ind1 < l1 and ind2 < l2:
    if a1[ind1] <= a2[ind2]:
        res.append(a1[ind1])
        ind1 += 1
    else:
        res.append(a2[ind2])
        ind2 += 1
while ind1 != l1:
    res.append(a1[ind1])
    ind1 += 1
while ind2 != l2:
    res.append(a2[ind2])
    ind2 += 1
print(*res, sep=" ")    
