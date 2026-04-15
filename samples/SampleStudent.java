public class SampleStudent {
    // student id
    private String id;

    /* name field */
    private String name;

    public SampleStudent(String id, String name) {
        this.id = id;
        this.name = name;
    }

    public String display() {
        return id + ":" + name;
    }
}
