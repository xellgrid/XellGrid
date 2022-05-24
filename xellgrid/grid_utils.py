from six import string_types


def stringify(x):
    if isinstance(x, string_types):
        return x
    else:
        return str(x)