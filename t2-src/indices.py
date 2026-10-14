import sys, copy
sys.path.insert(0,'.')
from simulador import load_model, simular, lcg
def indices(cfg, tempos, perdas, T):
    out={}
    for q,d in cfg['queues'].items():
        c=d['servers']; mu=2.0/(d['minService']+d['maxService'])
        tot=sum(tempos[q].values()); pi={n:t/tot for n,t in tempos[q].items()}
        N=sum(n*p for n,p in pi.items()); X=sum(min(n,c)*mu*p for n,p in pi.items())
        U=sum(min(n,c)*p for n,p in pi.items())/c
        out[q]=dict(N=N,X=X,U=U,R=N/X if X else 0,loss=perdas[q],mu=mu,pi=pi,K=d.get('capacity'),c=c)
    return out
def run(path,seed=1,n=100000):
    cfg=load_model(path); r=simular(cfg,lcg(seed,n)); return cfg,r,indices(cfg,*r)
if __name__=='__main__':
    for p in sys.argv[1:]:
        for s in (1,2,3):
            cfg,r,ix=run(p,s)
            print(p,'seed',s,'T=%.1f'%r[2])
            for q,v in ix.items(): print('  %s N=%.3f X=%.4f U=%.3f R=%.2f loss=%d'%(q,v['N'],v['X'],v['U'],v['R'],v['loss']))
