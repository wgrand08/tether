"""Fix silly lack-of-API problems in logging module

Adds constants to the log objects.
Adds getException(err) to log objects to retrieve 
formatted exception or err if traceback not available.


ENABLE_ERROR_LOGGING -- If True, then wrap functions with 
	error-logging operations so that exceptions will be 
	reported to the passed log in logOnFail
ENABLE_FULL_LOGGING -- If True, then wrap functions with 
	logging which reports each call along with its arguments
	to the passed log in logOnFail
"""
try:
	from cStringIO import StringIO
except ImportError, err:
	from StringIO import StringIO
import traceback, logging

getLog = logging.getLogger

ENABLE_ERROR_LOGGING = False
ENABLE_FULL_LOGGING = False

def getException(error):
	"""Get formatted traceback from exception"""
	exception = str(error)
	file = StringIO()
	try:
		traceback.print_exc( limit=10, file = file )
		exception = file.getvalue()
	finally:
		file.close()
	return exception
logging.Logger.getException = staticmethod( getException )
logging.Logger.err = logging.Logger.error
logging.Logger.DEBUG = logging.DEBUG 
logging.Logger.WARN = logging.WARN 
logging.Logger.INFO = logging.INFO 
logging.Logger.ERR = logging.Logger.ERROR = logging.ERROR

def logOnFail( function, log ):
	"""Produce possible log-wrapped version of function

	function -- callable object to be wrapped
	log -- the log to which to log information
	
	Uses ENABLE_ERROR_LOGGING and ENABLE_FULL_LOGGING
	to determine whether/how to wrap the function.
	"""
	if ENABLE_ERROR_LOGGING:
		if ENABLE_FULL_LOGGING:
			def loggedFunction( *args, **named ):
				argRepr = []
				for arg in args:
					argRepr.append( repr(arg) )
				for key,value in named.items():
					argRepr.append( '%s = %s'%( key,repr(value)) )
				argRepr = ",".join( argRepr )
				log.info( '%s( %s )', loggedFunction.__name__, argRepr )
				try:
					return function( *args, **named )
				except Exception, err:
					log.warn(
						"""Failure on %s: %s""", function.__name__, log.getException( err )
					)
					raise
		else:
			def loggedFunction( *args, **named ):
				try:
					return function( *args, **named )
				except Exception, err:
					log.warn(
						"""Failure on %s: %s""", function.__name__, log.getException( err )
					)
					raise
		try:
			loggedFunction.__name__ = function.__name__
		except (TypeError,AttributeError), err:
			pass
		try:
			loggedFunction.__doc__ = function.__doc__
		except (TypeError,AttributeError), err:
			pass
		try:
			loggedFunction.__dict__.update( function.__dict__ )
		except (TypeError,AttributeError), err:
			pass
		return loggedFunction
	else:
		return function
