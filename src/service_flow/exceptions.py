class StopFlowException(Exception):
    """ 
    an exception to stop the execution of subsequent middlewares 
    """

class RetryException(Exception):
    """ 
    an exception to stop the execution of subsequent middlewares and signal for re-process the same input overall again
    """

class FatalException(Exception):
    """ 
    an exception to stop the execution of subsequent middlewares and for the processor to exit and start fresh
    """
