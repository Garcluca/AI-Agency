
from decimal import Decimal, getcontext

def calculate_pi(num_digits):
    """
    A function that calculates the digits of pi to the number of digits specified by the user.

    Parameters:
    num_digits (int): The number of digits of pi to calculate.
    
    Returns:
    str: A string representing pi to the specified number of digits.
    """
    
    # Set the precision for the calculation
    getcontext().prec = num_digits + 1
    
    # The Chudnovsky algorithm to calculate pi
    def chudnovsky_algorithm():
        C = 426880 * Decimal(10005).sqrt()
        M = 1
        L = 13591409
        X = 1
        K = 6
        S = L
        for i in range(1, num_digits):
            M = (K**3 - 16*K) * M // i**3 
            L += 545140134
            X *= -262537412640768000
            K += 12
            S += Decimal(M * L) / X
        pi = C / S
        return str(pi)
    
    # Calculate pi using the Chudnovsky algorithm
    pi_str = chudnovsky_algorithm()
    
    # Discard the leading '3' and the decimal point
    # since we only want the decimal part for the specified digits
    pi_str = pi_str.replace('.', '')[:num_digits]
    
    return '3.' + pi_str
