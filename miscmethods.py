# this is where we define all of the miscellaneous methods for the term project that we couldn't
# justify making an entire class for.

#take numerical input
def numerical_input(vcp,lowerbound,upperbound,fullin):
    # test for if it's a number
    try:
        input = float(''.join(fullin))
    except:
        raise(TypeError)
    if input > upperbound:
        raise(IndexError)
    elif input < lowerbound:
        raise(IndexError)
    else:
        return input

def saturate(val,upper,lower):
    if val < lower:
        return lower
    elif val > upper:
        return upper
    else:
        return val