# palidrome слово, которое читается одинаково в обе стороны.

# простое решение сложностью O(n)
def is_palidrome(word):
    return word == word[::-1]

# слодное решение сложностью O(n)
def is_palidrome_fast(word):
    s = ''.join(w.lower() for w in word if w.isalpha())

    left, right = 0, len(word)-1

    while left < right:
        if word[left] != word[right]:
            return False
        left +=1
        right -=1

    return True