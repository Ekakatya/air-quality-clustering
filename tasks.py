# two arrays intersection
# two arrays are give we need to quickly find values that are in both arrays

def two_arrays_intersection(array1, array2):
    array1 = set(array1)
    array2 = set(array2)
    return array1.intersection(array2)

two_arrays_intersection([1, 2, 2, 1], [2, 2])

# if massives are sorted already, we can make faster algorythim
# by using pointers

def intersection_pointers(arr1, arr2):
    i, j = 0, 0
    result = []

    while i <= len(arr1) and j <= len(arr2):
        if arr1[i] == arr2[j]:
            result.append(arr1[i])
            i+=1
            j+=1
        elif arr1[i] > arr2[j]:
            j+=1
        else:
            i+=1
    return result


def merge_int(lis):
    for i in range(len(lis)):
        if lis[i][-1] >lis[i+1][0] and lis[i][-1] < lis[i+1][-1] and lis[i][0] < lis[i+1][0]:
            lis[i][0], lis[i][-1] = lis[i][0],lis[i+1][-1]

    return lis



def string_compression(str):
    count = 1
    result = list()

    for i in range(len(str)-1):
        if str[i] == str[i+1]:
            count+=1
        else:
            result.append([str[i]+str(count)])
            count=1

    result.append(str[-1]+str(count))
    res_str = ''.join(result)

    if len(str) > len(res_str):
        return res_str
    else:
        return str




def binary_search(arr, target):

    left, right = 0, len(arr)-1

    while left <= right:
        mid = (left + right) // 2

        if arr[mid]==target:
            return mid
        elif arr[mid]<target:
            left = mid+1
        else:
            right = mid-1
    return -1


def longest_substring(str):
    lst = set(str)

    return len(str.intersection(lst))