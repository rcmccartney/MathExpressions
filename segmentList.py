def segment(input):
    seg_len = len(input)
    resList = []
    resList.append(input)
    for i in range(1, seg_len):
        prefix = input[0:i]
        suffix = input[i:seg_len]
        seg_suffix = segment(suffix)
        for j in seg_suffix:
            res = prefix + " " + j
            resList.append( res )
    return resList
    
res = segment('abcde')
print(res)
print(len(res))