def flatten(matrix):
    result = []
    for row in matrix:
        for col in row:
            result.append(col)
    return result

def flatten(matrix):
    return [pixel for row in matrix for pixel in row]

# chain.from_iterable позволяет склеить списки или списки списков в одинто естьп
from itertools import chain

def flatten(matrix):
    return list(chain.from_iterable(matrix))


def sum_search(nums, target):
    result = []
    for i in nums:
        re = i - target
        if re in nums.drop(re):
            result.append(nums.index(re))
    return result.sort_values(descending=False)

sum_search([2, 7, 11, 15], 9)


def anagramm(s,t):
    return sorted(s.lower()) == sorted(t.lower())

def is_anagram(s, t):
    if len(s)!=len(t):
        return False

    count = {}

    for char in s:
        count[char] = count.get(char, 0) + 1

    for char in t:
        if char not in count or count[char] == 0:
            return False
        count[char]-=1
    return True


# working with dictionary. It is hash table and the complexity is O(1). It is working immediate

my_dict={}

my_dict['apple'] = 5
my_dict['orange'] = 3

my_dict.get('apple', 0)

# getting inly values
my_dict.values()

# getting key and value
my_dict.keys().items


def get_ind(text):

    count={}
    for char in text:
        count[char] = count.get(char, 0) + 1

    for char, i in enumerate(text):
        if count[char] == 1
            return i


def is_palidrom(word):
    return word == word[::-1]


def max_profit(prices):
    for i in prices:



# есть список из $n$ элементов. Я хочу найти в нем конкретное число простым перебором. Какая будет сложность в худшем случае

def search_n(nums, num):
    for i in nums: #O(n)
        if i == num:  # O(1)
            return True

def zero_matrix(matrix):
    for i in matrix:
        for j in i:
            matrix[i][j] = 0


def binary_search(nums, target):

    right = 0
    left = len(nums)-1

    while left <= right:
        mid = (left+right)//2

        if nums[mid]==target:
            return mid

        elif nums[mid]<target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


