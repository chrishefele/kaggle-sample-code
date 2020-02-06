import nimfa
import numpy
import numpy.random

V = nimfa.examples.medulloblastoma.read(normalize = True)
print V.shape

"""
fctr = nimfa.mf(V, seed = 'random_vcol', method = 'lsnmf', rank = 40, max_iter = 65)
fctr_res = nimfa.mf_run(fctr)
"""

pnrg = numpy.random.RandomState()

# Example call of LFNMF with algorithm specific parameters set    
rank=10
fctr = nimfa.mf(V, seed = None,
                   W = abs(pnrg.randn(V.shape[0], rank)), 
                   H = abs(pnrg.randn(rank, V.shape[1])),
                   rank = 10, 
                   method = "lfnmf", 
                   max_iter = 12, 
                   initialize_only = True,
                   alpha = 0.01
               )
fctr_res = nimfa.mf_run(fctr)

print 'Rss: %5.4f' % fctr_res.fit.rss()
print 'Evar: %5.4f' % fctr_res.fit.evar()
print 'K-L divergence: %5.4f' % fctr_res.distance(metric = 'kl')
print 'Sparseness, W: %5.4f, H: %5.4f' % fctr_res.fit.sparseness()


