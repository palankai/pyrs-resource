class Hook(object):
    """
    Hooks help to extend the functionality of application. The 3 hooks executed
    in different time of execution.
    This class should be the base class of any further hook.
    """

    def request(self, request):
        """
        Executed when the request is created. It can amend the request.
        If has any return value it will be used as return value of the call,
        the the function will be not called.
        Can raise any exception and that will be treated as the function
        exception, in that case the function will be not called.
        """
        pass

    def response(self, response):
        """
        Executed after successful call of the function.
        Response object created and passed to the hook.
        Can modify the response or give back a new response.
        Have to return the response object.
        """
        return response

    def exception(self, request, exception):
        """
        If the function raise any exception it can be handled with this hook.
        return will be used as response if it gives back any
        (should be `Response` instance or `None`)
        """
        pass
