#include <stdio.h>

// Function to calculate sum of array
int sumArray(int arr[], int size) {
    int sum = 0;
    for(int i = 0; i < size; i++) {
        sum += arr[i];
    }
    return sum;
}

// Function with nested loops
void printPairs(int arr[], int size) {
    for(int i = 0; i < size; i++) {
        for(int j = 0; j < size; j++) {
            printf("Pair: %d, %d\n", arr[i], arr[j]);
        }
    }
}

// Function that is unused
void unusedFunction() {
    printf("This function is never called.\n");
}

int main() {
    int numbers[5] = {1,2,3,4,5};
    printf("Sum: %d\n", sumArray(numbers, 5));
    printPairs(numbers, 5);
    return 0;
}
