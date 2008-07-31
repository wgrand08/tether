# Copyright (c) 2001-2008 Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for error handling in PB.
"""

from twisted.trial import unittest

from twisted.spread import pb, flavors
from twisted.internet import reactor, defer
from twisted.python import log

##
# test exceptions
##
class AsynchronousException(Exception):
    """
    Helper used to test remote methods which return Deferreds which fail with
    exceptions which are not L{pb.Error} subclasses.
    """


class SynchronousException(Exception):
    """
    Helper used to test remote methods which raise exceptions which are not
    L{pb.Error} subclasses.
    """


class AsynchronousError(pb.Error):
    """
    Helper used to test remote methods which return Deferreds which fail with
    exceptions which are L{pb.Error} subclasses.
    """


class SynchronousError(pb.Error):
    """
    Helper used to test remote methods which raise exceptions which are
    L{pb.Error} subclasses.
    """


#class JellyError(flavors.Jellyable, pb.Error): pass
class JellyError(flavors.Jellyable, pb.Error, pb.RemoteCopy):
    pass


class SecurityError(pb.Error, pb.RemoteCopy):
    pass

pb.setUnjellyableForClass(JellyError, JellyError)
pb.setUnjellyableForClass(SecurityError, SecurityError)
pb.globalSecurity.allowInstancesOf(SecurityError)


####
# server-side
####
class SimpleRoot(pb.Root):
    def remote_asynchronousException(self):
        """
        Fail asynchronously with a non-pb.Error exception.
        """
        return defer.fail(AsynchronousException("remote asynchronous exception"))

    def remote_synchronousException(self):
        """
        Fail synchronously with a non-pb.Error exception.
        """
        raise SynchronousException("remote synchronous exception")

    def remote_asynchronousError(self):
        """
        Fail asynchronously with a pb.Error exception.
        """
        return defer.fail(AsynchronousError("remote asynchronous error"))

    def remote_synchronousError(self):
        """
        Fail synchronously with a pb.Error exception.
        """
        raise SynchronousError("remote synchronous error")

    def remote_unknownError(self):
        """
        Fail with error that is not known to client.
        """
        class UnknownError(pb.Error):
            pass
        raise UnknownError("I'm not known to client!")

    def remote_jelly(self):
        self.raiseJelly()

    def remote_security(self):
        self.raiseSecurity()

    def remote_deferredJelly(self):
        d = defer.Deferred()
        d.addCallback(self.raiseJelly)
        d.callback(None)
        return d

    def remote_deferredSecurity(self):
        d = defer.Deferred()
        d.addCallback(self.raiseSecurity)
        d.callback(None)
        return d

    def raiseJelly(self, results=None):
        raise JellyError("I'm jellyable!")

    def raiseSecurity(self, results=None):
        raise SecurityError("I'm secure!")



class PBConnTestCase(unittest.TestCase):
    unsafeTracebacks = 0

    def setUp(self):
        self._setUpServer()
        self._setUpClient()

    def _setUpServer(self):
        self.serverFactory = pb.PBServerFactory(SimpleRoot())
        self.serverFactory.unsafeTracebacks = self.unsafeTracebacks
        self.serverPort = reactor.listenTCP(0, self.serverFactory, interface="127.0.0.1")

    def _setUpClient(self):
        portNo = self.serverPort.getHost().port
        self.clientFactory = pb.PBClientFactory()
        self.clientConnector = reactor.connectTCP("127.0.0.1", portNo, self.clientFactory)

    def tearDown(self):
        return defer.gatherResults([
            self._tearDownServer(),
            self._tearDownClient()])

    def _tearDownServer(self):
        return defer.maybeDeferred(self.serverPort.stopListening)

    def _tearDownClient(self):
        self.clientConnector.disconnect()
        return defer.succeed(None)



class PBFailureTest(PBConnTestCase):
    compare = unittest.TestCase.assertEquals


    def _exceptionTest(self, method, exceptionType, flush):
        def eb(err):
            err.trap(exceptionType)
            self.compare(err.traceback, "Traceback unavailable\n")
            if flush:
                errs = self.flushLoggedErrors(exceptionType)
                self.assertEqual(len(errs), 1)
            return (err.type, err.value, err.traceback)
        d = self.clientFactory.getRootObject()
        def gotRootObject(root):
            d = root.callRemote(method)
            d.addErrback(eb)
            return d
        d.addCallback(gotRootObject)
        return d


    def test_asynchronousException(self):
        """
        Test that a Deferred returned by a remote method which already has a
        Failure correctly has that error passed back to the calling side.
        """
        return self._exceptionTest(
            'asynchronousException', AsynchronousException, True)


    def test_synchronousException(self):
        """
        Like L{test_asynchronousException}, but for a method which raises an
        exception synchronously.
        """
        return self._exceptionTest(
            'synchronousException', SynchronousException, True)


    def test_asynchronousError(self):
        """
        Like L{test_asynchronousException}, but for a method which returns a
        Deferred failing with an L{pb.Error} subclass.
        """
        return self._exceptionTest(
            'asynchronousError', AsynchronousError, False)


    def test_synchronousError(self):
        """
        Like L{test_asynchronousError}, but for a method which synchronously
        raises a L{pb.Error} subclass.
        """
        return self._exceptionTest(
            'synchronousError', SynchronousError, False)


    def _success(self, result, expectedResult):
        self.assertEquals(result, expectedResult)
        return result


    def _addFailingCallbacks(self, remoteCall, expectedResult, eb):
        remoteCall.addCallbacks(self._success, eb,
                                callbackArgs=(expectedResult,))
        return remoteCall


    def _testImpl(self, method, expected, eb, exc=None):
        """
        Call the given remote method and attach the given errback to the
        resulting Deferred.  If C{exc} is not None, also assert that one
        exception of that type was logged.
        """
        rootDeferred = self.clientFactory.getRootObject()
        def gotRootObj(obj):
            failureDeferred = self._addFailingCallbacks(obj.callRemote(method), expected, eb)
            if exc is not None:
                def gotFailure(err):
                    self.assertEquals(len(self.flushLoggedErrors(exc)), 1)
                    return err
                failureDeferred.addBoth(gotFailure)
            return failureDeferred
        rootDeferred.addCallback(gotRootObj)
        return rootDeferred


    def test_jellyFailure(self):
        """
        Test that an exception which is a subclass of L{pb.Error} has more
        information passed across the network to the calling side.
        """
        def failureJelly(fail):
            fail.trap(JellyError)
            self.failIf(isinstance(fail.type, str))
            self.failUnless(isinstance(fail.value, fail.type))
            return 43
        return self._testImpl('jelly', 43, failureJelly)


    def test_deferredJellyFailure(self):
        """
        Test that a Deferred which fails with a L{pb.Error} is treated in
        the same way as a synchronously raised L{pb.Error}.
        """
        def failureDeferredJelly(fail):
            fail.trap(JellyError)
            self.failIf(isinstance(fail.type, str))
            self.failUnless(isinstance(fail.value, fail.type))
            return 430
        return self._testImpl('deferredJelly', 430, failureDeferredJelly)


    def test_unjellyableFailure(self):
        """
        An non-jellyable L{pb.Error} subclass raised by a remote method is
        turned into a Failure with a type set to the FQPN of the exception
        type.
        """
        def failureUnjellyable(fail):
            self.assertEqual(
                fail.type, 'twisted.test.test_pbfailure.SynchronousError')
            return 431
        return self._testImpl('synchronousError', 431, failureUnjellyable)


    def test_unknownFailure(self):
        """
        Test that an exception which is a subclass of L{pb.Error} but not
        known on the client side has its type set properly.
        """
        def failureUnknown(fail):
            self.assertEqual(
                fail.type, 'twisted.test.test_pbfailure.UnknownError')
            return 4310
        return self._testImpl('unknownError', 4310, failureUnknown)


    def test_securityFailure(self):
        """
        Test that even if an exception is not explicitly jellyable (by being
        a L{pb.Jellyable} subclass), as long as it is an L{pb.Error}
        subclass it receives the same special treatment.
        """
        def failureSecurity(fail):
            fail.trap(SecurityError)
            self.failIf(isinstance(fail.type, str))
            self.failUnless(isinstance(fail.value, fail.type))
            return 4300
        return self._testImpl('security', 4300, failureSecurity)


    def test_deferredSecurity(self):
        """
        Test that a Deferred which fails with a L{pb.Error} which is not
        also a L{pb.Jellyable} is treated in the same way as a synchronously
        raised exception of the same type.
        """
        def failureDeferredSecurity(fail):
            fail.trap(SecurityError)
            self.failIf(isinstance(fail.type, str))
            self.failUnless(isinstance(fail.value, fail.type))
            return 43000
        return self._testImpl('deferredSecurity', 43000, failureDeferredSecurity)


    def test_noSuchMethodFailure(self):
        """
        Test that attempting to call a method which is not defined correctly
        results in an AttributeError on the calling side.
        """
        def failureNoSuch(fail):
            fail.trap(pb.NoSuchMethod)
            self.compare(fail.traceback, "Traceback unavailable\n")
            return 42000
        return self._testImpl('nosuch', 42000, failureNoSuch, AttributeError)


    def test_copiedFailureLogging(self):
        """
        Test that a copied failure received from a PB call can be logged
        locally.

        Note: this test needs some serious help: all it really tests is that
        log.err(copiedFailure) doesn't raise an exception.
        """
        d = self.clientFactory.getRootObject()

        def connected(rootObj):
            return rootObj.callRemote('synchronousException')
        d.addCallback(connected)

        def exception(failure):
            log.err(failure)
            errs = self.flushLoggedErrors(SynchronousException)
            self.assertEquals(len(errs), 2)
        d.addErrback(exception)

        return d



class PBFailureTestUnsafe(PBFailureTest):
    compare = unittest.TestCase.failIfEquals
    unsafeTracebacks = 1