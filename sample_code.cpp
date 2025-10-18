#include <iostream>
#include <vector>
using namespace std;

// Function to find max value
int findMax(vector<int> nums) {
    int maxVal = nums[0];
    for(int i = 1; i < nums.size(); i++) {
        if(nums[i] > maxVal)
            maxVal = nums[i];
    }
    return maxVal;
}

// Function with nested loops
void printMatrix(int n) {
    for(int i = 0; i < n; i++) {
        for(int j = 0; j < n; j++) {
            cout << "(" << i << "," << j << ") ";
        }
        cout << endl;
    }
}

// Unused function
void unusedCppFunction() {
    cout << "This function is never called." << endl;
}

int main() {
    vector<int> nums = {3, 7, 2, 9, 5};
    cout << "Max value: " << findMax(nums) << endl;
    printMatrix(3);
    return 0;
}
