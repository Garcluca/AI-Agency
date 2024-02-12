
def roman_to_number(roman_numeral):
    """
    A function that converts Roman numerals to their corresponding integer values.
    
    :param roman_numeral: A Roman numeral represented as a string.
    :return: The integer value corresponding to the Roman numeral.
    """
    roman_numerals = {
        'I': 1, 'V': 5, 'X': 10, 'L': 50,
        'C': 100, 'D': 500, 'M': 1000
    }
    number = 0
    
    i = 0
    while i < len(roman_numeral):
        if i+1 < len(roman_numeral) and roman_numerals[roman_numeral[i]] < roman_numerals[roman_numeral[i+1]]:
            number += roman_numerals[roman_numeral[i+1]] - roman_numerals[roman_numeral[i]]
            i += 2
        else:
            number += roman_numerals[roman_numeral[i]]
            i += 1
    
    return number
