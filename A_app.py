def integrate_strings(original, edited):
    original_list =  original.strip()
    edited_list = edited.strip()

    original_len = len(original_list)
    edited_len = len(edited_list)
    integreted = ""
    print(original_list)
    print(edited_list)
    original_index = 0
    edited_index = 0
    while True:
        o_word = original_list[original_index]
        e_word = edited_list[edited_index]
        if o_word == e_word:
            integreted += o_word
        else:
            integreted += e_word



        count += 1




    return integreted


# Example usage:
original = "hello world today."
edited = "hallo welt today."
integrated = integrate_strings(original, edited)
print(integrated)