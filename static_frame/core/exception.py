

class ErrorInit(RuntimeError):
    '''Error in Container initialization.
    '''

class ErrorInitSeries(ErrorInit):
    '''Error in Series initialization.
    '''

class ErrorInitFrame(ErrorInit):
    '''Error in Frame (and derived Frame) initialization.
    '''

class ErrorInitIndex(ErrorInit):
    '''Error in IndexBase (and derived Index) initialization.
    '''
