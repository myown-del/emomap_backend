import abc

class BaseController(abc.ABC):
    # Controllers might not always need a shared base __init__
    # if their dependencies vary significantly.
    pass 