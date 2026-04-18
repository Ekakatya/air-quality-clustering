# anagram слово которое состоит из одних и тех же букв

# простое решение сложностью O(nlog(n))
def is_anagram(str1, str2):
    return sorted(str1.lower()) == sorted(str2.lower())

# более быстрое решение
def is_anagram_fast(str1, str2):
    if len(str1) != len(str2):
        return False

    count={}

    for char in str1:
        count[char] = count.get(char, 0)+1

    for char in str2:
        if char not in count or count[char]==0:
            return False
        count[char] -= 1
    return True



# условие: дан список строк, нужно сгруппировать их в списки аннаграм
# алгоритм: создать словарь, где ключ, это отсортированное слово и в качестве значение доьавить исходное слово

def group_anagrams(strs):

    result={}

    for s in strs:
        key = "".join(sorted(s))

        if key not in result:
            result[key] = []

        result[key].append(s)
    return list(result.values())


