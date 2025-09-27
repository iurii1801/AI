import java.util.Scanner;

public class Automaton {
    enum State { q0, q1, q2, q3, qF, qX }

    public static boolean accepts(String word) {
        State st = State.q0;

        for (char ch : word.toCharArray()) {
            switch (st) {
                case q0:
                    st = (ch == 'a') ? State.q1 : State.qX;
                    break;

                case q1:
                    if (ch == 'c') st = State.qF;       // n=0, финальное c
                    else if (ch == 'a') st = State.q2;  // начинаем новый блок abc
                    else st = State.qX;
                    break;

                case q2:
                    st = (ch == 'b') ? State.q3 : State.qX;
                    break;

                case q3:
                    st = (ch == 'c') ? State.q1 : State.qX; // завершили abc-блок
                    break;

                case qF:
                    st = State.qX; // после финального c ничего нельзя
                    break;

                default:
                    st = State.qX;
                    break;
            }
            if (st == State.qX) break; // сразу выходим при ошибке
        }
        return st == State.qF;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        while (true) {
            System.out.print("Введите слово (или 'exit' для выхода): ");
            String input = sc.nextLine();

            if (input.equalsIgnoreCase("exit")) {
                System.out.println("Выход из программы.");
                break;
            }

            if (accepts(input))
                System.out.println("Слово подходит (принимается)");
            else
                System.out.println("Слово не подходит (отклоняется)");
        }
    }
}
