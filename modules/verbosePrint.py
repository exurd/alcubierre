verbose = False
vPrint = None
def toggleVerbosity():
    global verbose
    verbose = not verbose
    print(verbose)
    activateLambda()
def activateLambda():
    global vPrint
    vPrint = print if verbose else lambda *a, **k: None
    vPrint("Verbose mode is now enabled, else you wouldn't be seeing this...")
activateLambda()