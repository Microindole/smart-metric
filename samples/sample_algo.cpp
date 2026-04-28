#include <iostream>
#include <numeric>
#include <string>
#include <vector>

class GradeBook {
private:
    std::string studentName;
    std::vector<int> scores;
    int warningCount;

public:
    GradeBook(const std::string& name) : studentName(name), warningCount(0) {}

    void addScore(int score) {
        int normalized = normalize(score);
        scores.push_back(normalized);
        warningCount += normalized < 60 ? 1 : 0;
    }

    double average() const {
        if (scores.empty()) return 0.0;
        int total = std::accumulate(scores.begin(), scores.end(), 0);
        return static_cast<double>(total) / scores.size();
    }

    bool isAtRisk() const {
        return average() < 65.0 || warningCount >= 2;
    }

    void printSummary() const {
        std::cout << "Student: " << studentName
                  << ", avg=" << average()
                  << ", warnings=" << warningCount
                  << ", risk=" << (isAtRisk() ? "yes" : "no")
                  << std::endl;
    }

private:
    int normalize(int score) const {
        int lowerBound = score < 0 ? 0 : score;
        return lowerBound > 100 ? 100 : lowerBound;
    }
};

int main() {
    GradeBook book("Bob");
    book.addScore(92);
    book.addScore(58);
    book.addScore(76);
    book.printSummary();
    return 0;
}
