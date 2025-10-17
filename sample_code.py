def inefficient_function(data):
    for i in range(len(data)):
        for j in range(len(data)):
            if data[i] == data[j]:
                print("Duplicate found")

def calculate_sum(n):
    total = 0
    for i in range(n):
        total += i
    return total
