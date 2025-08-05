def get_next_letter(current_letter):
    """
    Minor Function to get the variant_designation_letter of multi-layer variants.
    :param current_letter: The variant_designation_letter of the variant on its last variation.
    :return: A string of one capital letter to be the next variant_designation_letter.
    """
    # Get the ASCII value of the current letter and adds 1 to get the ASCII of the next
    next_char_code = ord(current_letter) + 1
    
    # If it goes past "Z", wrap around to "A"
    if next_char_code > ord("Z"):
        next_char_code = ord("A")
    
    # Converts back to chr and outputs as a string of a standard capital letter
    return chr(next_char_code)