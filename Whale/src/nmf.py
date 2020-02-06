import nimfa
import numpy
import numpy.random

V = nimfa.examples.medulloblastoma.read(normalize = True)

V = numpy.random.random((60,50))
V = numpy.random.random((50,60))
V = numpy.random.random((50,50))
print V.shape


fctr = nimfa.mf(V, seed = 'random_vcol', method = 'lsnmf', rank = 40, max_iter = 65)
fctr_res = nimfa.mf_run(fctr)


#assert 1==2

pnrg = numpy.random.RandomState()

print "running lfnmf"
# Example call of LFNMF with algorithm specific parameters set    
fctr = nimfa.mf(V, 
                   #seed = None,
                   seed = 'random',
                   #W = abs(pnrg.randn(V.shape[0], rank)), 
                   #H = abs(pnrg.randn(rank, V.shape[1])),
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


