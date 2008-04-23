"""Base class for platform implementations
"""
import ctypes
from OpenGL.platform import ctypesloader
import sys
import OpenGL as top_level_module

class BasePlatform( object ):
	"""Base class for per-platform implementations
	
	Attributes of note:
	
		EXPORTED_NAMES -- set of names exported via the platform 
			module's namespace...
	
		GL, GLU, GLUT, GLE, OpenGL -- ctypes libraries
	
		DEFAULT_FUNCTION_TYPE -- used as the default function 
			type for functions unless overridden on a per-DLL
			basis with a "FunctionType" member
		
		GLUT_GUARD_CALLBACKS -- if True, the GLUT wrappers 
			will provide guarding wrappers to prevent GLUT 
			errors with uninitialised GLUT.
		
		EXTENSIONS_USE_BASE_FUNCTIONS -- if True, uses regular
			dll attribute-based lookup to retrieve extension 
			function pointers.
	
	"""
	
	EXPORTED_NAMES = [
		'GetCurrentContext','CurrentContextIsValid','safeGetError',
		'createBaseFunction', 'createExtensionFunction', 'copyBaseFunction',
		'GL','GLU','GLUT','GLE','OpenGL',
		'getGLUTFontPointer',
		'GLUT_GUARD_CALLBACKS',
	]

	
	DEFAULT_FUNCTION_TYPE = None
	GLUT_GUARD_CALLBACKS = False
	EXTENSIONS_USE_BASE_FUNCTIONS = False
	
	def install( self, namespace ):
		"""Install this platform instance into the platform module"""
		for name in self.EXPORTED_NAMES:
			namespace[ name ] = getattr(self,name)
		namespace['PLATFORM'] = self
		return self
	
	def functionTypeFor( self, dll ):
		"""Given a DLL, determine appropriate function type..."""
		if hasattr( dll, 'FunctionType' ):
			return dll.FunctionType
		else:
			return self.DEFAULT_FUNCTION_TYPE

	def createBaseFunction( 
		self,
		functionName, dll, 
		resultType=ctypes.c_int, argTypes=(),
		doc = None, argNames = (),
	):
		"""Create a base function for given name
		
		Normally you can just use the dll.name hook to get the object,
		but we want to be able to create different bindings for the 
		same function, so we do the work manually here to produce a
		base function from a DLL.
		"""
		from OpenGL import wrapper, error
		try:
			func = ctypesloader.buildFunction(
				self.functionTypeFor( dll )(
					resultType,
					*argTypes
				),
				functionName,
				dll,
			)
		except AttributeError, err:
			return self.nullFunction( 
				functionName, dll=dll,
				resultType=resultType, 
				argTypes=argTypes,
				doc = doc, argNames = argNames,
				extension = False,
			)
		else:
			func.__doc__ = doc 
			func.argNames = list(argNames or ())
			func.__name__ = functionName
			func.DLL = dll
			if top_level_module.ERROR_CHECKING:
				func.errcheck = error.glCheckError
			return func

	def createExtensionFunction( 
		self,
		functionName, dll,
		resultType=ctypes.c_int, 
		argTypes=(),
		doc = None, argNames = (),
	):
		"""Create an extension function for the given name
		
		Uses the platform's getExtensionProcedure function to retrieve
		a c_void_p to the function, then wraps in a platform FunctionType
		instance with all the funky code we've come to love.
		"""
		if self.EXTENSIONS_USE_BASE_FUNCTIONS:
			return self.createBaseFunction(
				functionName, dll,
				resultType, 
				argTypes,
				doc, argNames,
			)
		from OpenGL import wrapper, error
		pointer = self.getExtensionProcedure( functionName )
		if not pointer:
			return self.nullFunction( 
				functionName, dll,
				resultType, 
				argTypes,
				doc, argNames,
			)
		func = self.functionTypeFor( dll )(
			resultType,
			*argTypes
		)(
			pointer
		)
		func.__doc__ = doc 
		func.argNames = list(argNames or ())
		func.__name__ = functionName
		func.DLL = dll
		if top_level_module.ERROR_CHECKING:
			func.errcheck = error.glCheckError
		return func

	def copyBaseFunction( self, original ):
		"""Create a new base function based on an already-created function
		
		This is normally used to provide type-specific convenience versions of
		a definition created by the automated generator.
		"""
		from OpenGL import wrapper, error
		if isinstance( original, _NullFunctionPointer ):
			return self.nullFunction(
				original.__name__,
				original.DLL,
				resultType = original.restype,
				argTypes= original.argtypes,
				doc = original.__doc__,
				argNames = original.argNames,
			)
		func = ctypesloader.buildFunction(
			self.functionTypeFor( original.DLL )(
				original.restype,
				*original.argtypes
			),
			original.__name__,
			original.DLL,
		)
		func.__doc__ = original.__doc__
		func.argNames = original.argNames 
		func.__name__ = original.__name__
		if top_level_module.ERROR_CHECKING:
			func.errcheck = error.glCheckError
		return func
	def nullFunction( 
		self,
		functionName, dll,
		resultType=ctypes.c_int, 
		argTypes=(),
		doc = None, argNames = (),
		extension = True,
	):
		"""Construct a "null" function pointer"""
		cls = type( functionName, (_NullFunctionPointer,), {
			'__doc__': doc,
		} )
		return cls(
			functionName, dll, resultType, argTypes, argNames, extension=extension,
		)
	def GetCurrentContext( self ):
		"""Retrieve opaque pointer for the current context"""
		raise NotImplementedError( 
			"""Platform does not define a GetCurrentContext function""" 
		)
	def CurrentContextIsValid( self ):
		"""Return boolean of whether current context is valid"""
		raise NotImplementedError( 
			"""Platform does not define a CurrentContextIsValid function""" 
		)
	def getGLUTFontPointer(self, constant ):
		"""Retrieve a GLUT font pointer for this platform"""
		raise NotImplementedError( 
			"""Platform does not define a GLUT font retrieval function""" 
		)
	def safeGetError( self ):
		"""Safety-checked version of glError() call (checks for valid context first)"""
		raise NotImplementedError( 
			"""Platform does not define a safeGetError function""" 
		)

class _NullFunctionPointer( object ):
	"""Function-pointer-like object for undefined functions"""
	def __init__( self, name, dll, resultType, argTypes, argNames, extension=True ):
		from OpenGL import error
		self.__name__ = name
		self.DLL = dll
		self.argNames = argNames
		self.argtypes = argTypes
		if top_level_module.ERROR_CHECKING:
			self.errcheck = error.glCheckError
		else:
			self.errcheck = None
		self.restype = resultType
		self.extension = extension
		self.pointer = None
	resolved = False
	def __nonzero__( self ):
		"""Make this object appear to be NULL"""
		if self.extension and not self.pointer:
			self.load()
		return self.resolved
	def load( self ):
		"""Attempt to load the function again, presumably with a context this time"""
		from OpenGL import platform
		pointer = platform.PLATFORM.getExtensionProcedure( self.__name__ )
		if pointer:
			func = functionTypeFor( self.DLL )(
				self.restype,
				*self.argtypes
			)(
				pointer
			)
			func.argNames = list(self.argNames or ())
			func.__name__ = self.__name__
			func.DLL = self.DLL
			if top_level_module.ERROR_CHECKING:
				func.errcheck = self.errcheck
			# now short-circuit so that we don't need to check again...
			self.__class__.__call__ = staticmethod( func.__call__ )
			self.resolved = True
			self.pointer = pointer
			return func
		return None
	def __call__( self, *args, **named ):
		if self.extension and self.load():
			return self( *args, **named )
		else:
			from OpenGL import error
			raise error.NullFunctionError(
				"""Attempt to call an undefined function %s, check for bool(%s) before calling"""%(
					self.__name__, self.__name__,
				)
			)
	
