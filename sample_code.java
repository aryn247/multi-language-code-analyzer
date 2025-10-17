public class Sample {

    public static void main(String[] args) {
        System.out.println("Hello World");
        int result = add(5, 3);
        System.out.println("Sum: " + result);
    }

    public static int add(int a, int b) {
        return a + b;
    }

    public static void loopExample(int n) {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                System.out.println(i * j);
            }
        }
    }
}
