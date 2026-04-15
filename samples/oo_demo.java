class Person {
    private String name;

    public String getName() {
        return name;
    }
}

class User extends Person {
    private int score;
    private Account account;

    public void login(String password) {
        if (password != null && password.length() > 6) {
            score++;
        }
        account = new Account();
    }

    public int getScore() {
        return score;
    }
}

class Account {
    public void touch() {
    }
}
