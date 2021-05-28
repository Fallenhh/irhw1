f = open('qrels.ohsu.88-91','r')
lines = f.readlines()
f.close()

f = open('qrels','w')
for line in lines:
    w = line.split()
    f.write('{} Q0 {} {}\n'.format(w[0],w[1],w[2]))
f.close()

