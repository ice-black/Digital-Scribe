def integrate_strings(old , edited, new):
    old = old.split()
    edited = edited.split()
    new = new.split()

    for i in new:
        
        if old[i] == edited[i]:
            old[i] = new[i]

    integreted = " ".join(old)




    return integreted


# Example usage:

old = "hallo world boy today hezron"
edited = "hallo welt boy today hezron."
new = "hello world today hezron. sample string containing words."


integrated = integrate_strings(old , edited, new)
print("-------------------------")
print(integrated)