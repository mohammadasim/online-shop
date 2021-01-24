from .cart import Cart


def cart(request):
    """
    A context processor in python is a function
    that takes the request object as an argument
    and returns a dictionary that gets added to the
    request context. Context processors come in handy
    when you need to make something available globally to
    all templates.
    This context processor needs to be added to the settings file.
    :param request:
    :return:
    """
    return {'cart': Cart(request)}
