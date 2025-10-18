#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define ARRAY_SIZE 5

// Structure example
struct Student {
    int id;
    char name[20];
    float grade;
};

// Function prototypes
void printArray(int arr[], int size);
int findMax(int arr[], int size);
void swap(int *a, int *b);
void printStudent(struct Student s);
int factorial(int n); // recursive function
void stringDemo(char *input);

int main() {
    // Array and functions
    int numbers[ARRAY_SIZE] = {1, 2, 3, 4, 5};
    printArray(numbers, ARRAY_SIZE);
    printf("Max value: %d\n", findMax(numbers, ARRAY_SIZE));

    // Pointers and swap
    int x = 10, y = 20;
    printf("Before swap: x=%d, y=%d\n", x, y);
    swap(&x, &y);
    printf("After swap: x=%d, y=%d\n", x, y);

    // String handling
    char str[100] = "Hello, World!";
    stringDemo(str);

    // Structure usage
    struct Student john = {1, "John", 87.5};
    printStudent(john);

    // Recursion
    int num = 5;
    printf("Factorial of %d is %d\n", num, factorial(num));

    // Dynamic memory allocation
    int *ptr = (int *)malloc(ARRAY_SIZE * sizeof(int));
    for(int i = 0; i < ARRAY_SIZE; i++) ptr[i] = i * i;
    printf("Dynamic array: ");
    printArray(ptr, ARRAY_SIZE);
    free(ptr);

    // Standard library functions
    printf("isupper('A'): %d\n", isupper('A'));
    printf("strlen(\"Test\"): %lu\n", strlen("Test"));

    return 0;
}

// Function definitions

void printArray(int arr[], int size) {
    printf("Array: ");
    for(int i = 0; i < size; i++)
        printf("%d ", arr[i]);
    printf("\n");
}

int findMax(int arr[], int size) {
    int max = arr[0];
    for(int i = 1; i < size; i++)
        if(arr[i] > max) max = arr[i];
    return max;
}

void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

void printStudent(struct Student s) {
    printf("Student Info: ID=%d, Name=%s, Grade=%.2f\n", s.id, s.name, s.grade);
}

int factorial(int n) {
    if(n <= 1) return 1;
    else return n * factorial(n-1);
}

void stringDemo(char *input) {
    printf("String: %s\n", input);
    char copy[100];
    strcpy(copy, input);
    printf("Copied string: %s\n", copy);
    strcat(copy, " Concatenated");
    printf("Concatenated string: %s\n", copy);
}
