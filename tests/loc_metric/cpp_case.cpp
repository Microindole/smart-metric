#include <iostream>
#include <vector>

int sumPositive(const std::vector<int>& nums) {
    int total = 0;
    for (int value : nums) {
        if (value > 0) {
            total += value;
        } else {
            total -= 1;
        }
    }
    return total;
}

int main() {
    std::vector<int> nums = {1, 3, -1, 5};
    // show result
    std::cout << sumPositive(nums) << std::endl;
    return 0;
}
