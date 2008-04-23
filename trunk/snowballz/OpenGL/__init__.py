"""ctypes-based OpenGL wrapper for Python

This is the PyOpenGL 3.x tree, it attempts to provide
a largely compatible API for code written with the 
PyOpenGL 2.x series using the ctypes foreign function 
interface system.

Configuration Variables:

There are a few configuration variables in this top-level
module.  Applications should be the only code that tweaks 
these variables, mid-level libraries should not take it 
upon themselves to disable/enable features at this level.

	ERROR_CHECKING -- if set to a False value before
		importing an OpenGL.* libraries will completely 
		disable error-checking.  This can dramatically
		improve performance, but makes debugging far 
		harder.
		
		Default: True 

	ERROR_ON_COPY -- if set to a True value before 
		importing the numpy array-support module, will 
		cause array operations to raise 
		OpenGL.error.CopyError if an array operation 
		would cause a data-copy in order to match
		data-types.
		
		This feature allows for optimisation of your 
		application.  It should only be enabled during 
		testing stages to prevent raising errors on 
		recoverable conditions at run-time.  
		
		Note that this feature only works with Numpy 
		arrays at the moment.
		
		Default: False
"""
from OpenGL.version import __version__

ERROR_CHECKING = True
ERROR_ON_COPY = False
