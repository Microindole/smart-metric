public class JavaCase {
    private String id;
    private String name;
    private int score;

    public JavaCase(String id, String name) {
        this.id = id;
        this.name = name;
        this.score = 0;
    }

    public void updateScore(int delta) {
        if (delta > 0) {
            score = score + delta;
        } else {
            score = score - 1;
        }
    }

    public String formatProfile() {
        String level = computeLevel();
        return id + "-" + name + "-" + level;
    }

    public void normalizeName() {
        for (int i = 0; i < name.length(); i++) {
            if (name.charAt(i) == '_') {
                name = name.replace('_', '-');
            }
        }
    }

    private String computeLevel() {
        if (score >= 90) {
            return "A";
        }
        if (score >= 60) {
            return "B";
        }
        return "C";
    }

    public String exportSummary() {
        normalizeName();
        String profile = formatProfile();
        return profile + ":" + score;
    }
}
