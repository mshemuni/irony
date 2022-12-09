class EmissionValueError(Exception):
    """
    Raised on Emission error
    """
    pass


class NoiseValueError(Exception):
    """
    Raised on Noise error
    """
    pass


class ImageCountError(Exception):
    """
    Raised when number of fits files is insufficient
    """
    pass


class OperationValueError(Exception):
    """
    Raised on Operation error
    """
    pass


class RejectionValueError(Exception):
    """
    Raised on Rejection error
    """
    pass


class OperandValueError(Exception):
    """
    Raised on Operand error
    """
    pass


class ScaleValueError(Exception):
    """
    Raised on Scale error
    """
    pass


class NothingToDoError(Exception):
    """
    Raised on when no action can be taken
    """
    pass


class NumberOfElementError(Exception):
    """
    Raised when number of elements is insufficient
    """
    pass


class AlignError(Exception):
    """
    Raised on Align error
    """
    pass
