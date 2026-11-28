import sys, os, glob, time; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import formula as F
for f in sorted(glob.glob(sys.argv[1] + '/*.csv')):
    t = time.time(); r = F.montar(F.ler(f)[0], f)
    marc = sum(len(g['marcadas']) for g in r['grupos'])
    print('%-55s reg=%-6d grupos=%-3d totais=%-3d sem_id=%-2d marcadas=%-4d %4.1fs' % (r['arquivo'][:55], r['registros'], len(r['grupos']), len(r['totais']), r['sem_id'], marc, time.time() - t))
