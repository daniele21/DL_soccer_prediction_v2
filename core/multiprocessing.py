from multiprocessing import Process

def run_mp(fn, args):
    """

    Args:
        fn: function to be run into multiprocess way
        args: tuple of args --> (arg1. arg2, ...)

    Returns:

    """
    proc = Process(target=fn, args=args)
    proc.start()
    proc.join()