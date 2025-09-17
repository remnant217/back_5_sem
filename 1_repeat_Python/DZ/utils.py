def binary_search(my_list, key):
    left = 0
    right = len(my_list) - 1
    while left <= right:
        mid = (left + right) // 2
        value = my_list[mid]
        if value == key:
            return mid
        elif value > key:
            right = mid - 1
        else:
            left = mid + 1
    return None

if __name__ == '__main__':
    nums = [4, 8, 15, 16, 23, 42]
    print(binary_search(nums, 23))