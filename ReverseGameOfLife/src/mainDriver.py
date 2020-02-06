from cellModels import boardCellNeighborsModel, preTrainModels, CVtrainModels
from cellModels import loadModels, saveModels, makeSubmission
import sys,  os.path

MAXPATTERNS = 0  # 0=unlimited, use >0 to set a limit (e.g. 10M) to save memory
NEIGHBOR_RADII = (1,2,2,2,2,2)

def echoArg(tag, argIndex, default):
    if len(sys.argv) > argIndex:
        arg = sys.argv[argIndex]
    else:
        arg = default
    print tag, arg
    return arg

def mainDriver():
    print '\n*** Kaggle Contest: Reverse Game-of-Life ***\n'

    nBoards     = int(echoArg('number of boards  :', 1, 50000))
    model_fin   =     echoArg('input  models file:', 2, 'models.pkl')
    model_fout  =     echoArg('output models file:', 3, '')
    submission_fout = echoArg('submission file   :', 4, '')
    print 'neighbor radii    :', NEIGHBOR_RADII,'\n'

    if not os.path.isfile(model_fin):
        # models = [boardCellEvolutionModel(GENERATIONS) for c in xrange(MAX_DELTA+1)]
        models = [boardCellNeighborsModel(radius, maxPatterns=MAXPATTERNS) for radius in NEIGHBOR_RADII]
        print 'initializing:', model_fin
        saveModels(models, model_fin) 
        
    models = loadModels(model_fin)
    models = preTrainModels(models, nBoards)
    CVtrainModels(models, n_folds=1, modelsPreTrained=True) # just to print CV results
    if model_fout:
        saveModels(models, model_fout) 
    if submission_fout:
        makeSubmission(models, submission_fout)

if __name__ == '__main__':
    mainDriver()

