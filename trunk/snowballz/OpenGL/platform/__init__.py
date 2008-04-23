"""Abstraction for the platform-specific code in PyOpenGL

Each supported platform has a module which provides the
specific functionality required to support the base OpenGL 
functionality on that platform.  These modules are 
registered using plugins in the:

	OpenGL.platform.implementation

namespace using the pkg_resources module (by the setup.py
module).  You can register new platform implementations 
via pkg_resources to support an as-yet unsupported platform,
though you are encouraged to donate the module to the 
project.

See baseplatform.BasePlatform for the core functionality 
of a platform implementation.  See the various platform 
specific modules for examples to use when porting.
"""
import os, sys, pkg_resources

def _findPlatform( platform ):
	"""Find platform implementation by name"""
	for entrypoint in pkg_resources.iter_entry_points(
		"OpenGL.platform.implementation"
	):
		if entrypoint.name == platform:
			return entrypoint.load()
	raise RuntimeError(
		"""Unable to find an implementation for the %r platform (os.name)"""%(
			platform,
		)
	)

def _load( ):
	"""Load the os.name plugin for the platform functionality"""
	
	for platform in (sys.platform,os.name):
		try:
			plugin_class = _findPlatform( platform )
		except RuntimeError, err:
			pass 
		else:
	
			# create instance of this platform implementation
			plugin = plugin_class()
	
			# install into the platform module's namespace now
			plugin.install(globals())
			return plugin
	raise RuntimeError(
		"""Unable to find an implementation for the %r (%r) platform"""%(
			sys.platform, os.name,
		)
	)

_load()
