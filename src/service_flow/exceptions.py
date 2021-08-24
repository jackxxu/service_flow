class StopFlowException(Exception):
    """ 
    an exception to stop the execution of subsequent middlewares 
    """

class RetryException(Exception):
    """ 
    an exception to stop the execution of subsequent middlewares and signal for re-process the same input overall again
    """