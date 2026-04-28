import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class SampleStudent {
    private String id;
    private String name;
    private String major;
    private int year;
    private int creditsEarned;
    private double gpa;
    private int attendanceDays;
    private int absenceDays;
    private boolean probation;
    private int warningCount;
    private List<Integer> scores;
    private Map<String, Integer> courseCredits;

    public SampleStudent(String id, String name, String major, int year) {
        this.id = id;
        this.name = name;
        this.major = major;
        this.year = year;
        this.creditsEarned = 0;
        this.gpa = 0.0;
        this.attendanceDays = 0;
        this.absenceDays = 0;
        this.probation = false;
        this.warningCount = 0;
        this.scores = new ArrayList<>();
        this.courseCredits = new HashMap<>();
    }

    public void addCourseScore(String courseName, int score, int credit) {
        int normalized = normalizeScore(score);
        scores.add(normalized);
        courseCredits.put(courseName, credit);
        creditsEarned += Math.max(credit, 0);
        recalculateGpa();
        if (normalized < 60) {
            warningCount++;
        }
    }

    public void updateAttendance(boolean present) {
        if (present) {
            attendanceDays++;
        } else {
            absenceDays++;
            if (absenceDays > 5 && attendanceRate() < 0.8) {
                warningCount++;
            }
        }
    }

    public double attendanceRate() {
        int total = attendanceDays + absenceDays;
        if (total == 0) {
            return 1.0;
        }
        return (double) attendanceDays / total;
    }

    public int passedCredits() {
        int passed = 0;
        for (Map.Entry<String, Integer> entry : courseCredits.entrySet()) {
            if (entry.getValue() > 0) {
                passed += entry.getValue();
            }
        }
        return passed;
    }

    public boolean isAtRisk() {
        boolean lowGpa = gpa < 2.0;
        boolean lowAttendance = attendanceRate() < 0.75;
        boolean tooManyWarnings = warningCount >= 3;
        probation = lowGpa || lowAttendance || tooManyWarnings;
        return probation;
    }

    public void promoteYear() {
        if (!isAtRisk() && passedCredits() >= year * 18) {
            year++;
        } else {
            warningCount++;
        }
    }

    public String display() {
        return id + ":" + name + ":" + major + ":Y" + year + ":GPA=" + gpa;
    }

    private int normalizeScore(int score) {
        if (score < 0) {
            return 0;
        }
        if (score > 100) {
            return 100;
        }
        return score;
    }

    private void recalculateGpa() {
        if (scores.isEmpty()) {
            gpa = 0.0;
            return;
        }
        double totalPoint = 0.0;
        for (int score : scores) {
            totalPoint += scoreToPoint(score);
        }
        gpa = totalPoint / scores.size();
    }

    private double scoreToPoint(int score) {
        if (score >= 90) {
            return 4.0;
        }
        if (score >= 80) {
            return 3.2;
        }
        if (score >= 70) {
            return 2.4;
        }
        if (score >= 60) {
            return 1.6;
        }
        return 0.0;
    }
}
