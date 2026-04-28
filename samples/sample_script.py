class CourseRecord:
    school_name = "SmartMetric University"

    def __init__(self, course, credit, score):
        self.course = course
        self.credit = credit
        self.score = score

    def is_passed(self):
        return self.score >= 60

    def grade_point(self):
        if self.score >= 90:
            return 4.0
        if self.score >= 80:
            return 3.2
        if self.score >= 70:
            return 2.4
        if self.score >= 60:
            return 1.6
        return 0.0


class StudentAnalyzer:
    default_threshold = 2.3

    def __init__(self, student_id, name):
        self.student_id = student_id
        self.name = name
        self.records = []
        self.warnings = 0

    def add_record(self, course, credit, score):
        record = CourseRecord(course, credit, score)
        self.records.append(record)
        if not record.is_passed():
            self.warnings += 1

    def total_credits(self):
        return sum(r.credit for r in self.records if r.is_passed())

    def gpa(self):
        if not self.records:
            return 0.0
        total_points = sum(r.grade_point() for r in self.records)
        return total_points / len(self.records)

    def is_risky(self):
        return self.gpa() < self.default_threshold or self.warnings >= 2

    def summary(self):
        return {
            "student_id": self.student_id,
            "name": self.name,
            "credits": self.total_credits(),
            "gpa": round(self.gpa(), 2),
            "risky": self.is_risky(),
        }


if __name__ == "__main__":
    analyzer = StudentAnalyzer("S01", "Alice")
    analyzer.add_record("Software Metrics", 3, 92)
    analyzer.add_record("Compiler", 4, 58)
    analyzer.add_record("Data Mining", 3, 85)
    print(analyzer.summary())
