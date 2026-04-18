
def two_sum(nums, target):
    n = len(nums)
    for i in range(n):
        for j in range(i+1, n):
            if nums[i] + nums[j] == target:
                return [i, j]


def two_sum_fast(nums, target):

    prev_num={}

    for i, n in enumerate(nums):
        diff = target - n

        if diff in prev_num:
            return [prev_num[diff], i]
        prev_num[n] = i