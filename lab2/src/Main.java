import java.util.Arrays;

public class Main {

    // Глубина дерева — 5 уровней
    static final int DEPTH = 5;

    // Фиксированные значения листьев (2^5 = 32 значения)
    static final int[] LEAVES = {
            3,5,2,9,12,5,23,23, 1,3,2,2,0,1,9,8,
            7,4,8,5,6,3,2,4,   8,9,1,5,2,0,7,6
    };

    // Счётчики количества просмотренных узлов (для сравнения эффективности)
    static long nodesMM, nodesAB;

    public static void main(String[] args) {
        // Проверяем, что количество листьев соответствует глубине дерева
        if (LEAVES.length != (1 << DEPTH)) {
            throw new IllegalStateException("Ожидается " + (1 << DEPTH) +
                    " листьев, а задано: " + LEAVES.length);
        }

        // Обычный минимакс
        nodesMM = 0;
        long startMM = System.nanoTime();
        int valueMM = minimax(0, 0, true); // старт с корня, игрок MAX
        long endMM = System.nanoTime();

        // Минимакс с альфа-бета отсечением
        nodesAB = 0;
        long startAB = System.nanoTime();
        int valueAB = alphabeta(0, 0, true, Integer.MIN_VALUE, Integer.MAX_VALUE);
        long endAB = System.nanoTime();

        // Вывод результатов
        System.out.println("Листовые значения (" + LEAVES.length + "): " + Arrays.toString(LEAVES));
        System.out.println("Глубина: " + DEPTH + ", ширина: 2 (полное бинарное дерево)\n");

        System.out.println("=== Обычный минимакс ===");
        System.out.println("Значение в корне: " + valueMM);
        System.out.println("Посещено узлов:  " + nodesMM);
        System.out.printf("Время: %.3f ms%n%n", toMs(endMM - startMM));

        System.out.println("=== Альфа-бета отсечение ===");
        System.out.println("Значение в корне: " + valueAB);
        System.out.println("Посещено узлов:  " + nodesAB);
        System.out.printf("Время: %.3f ms%n%n", toMs(endAB - startAB));

        // Определяем, в какую сторону пойдёт первый ход MAX — влево или вправо
        int left = minimaxNoCount(1, 0, false);   // левое поддерево
        int right = minimaxNoCount(1, 1, false);  // правое поддерево
        System.out.println("Выбор на первом ходе (MAX): left=" + left + ", right=" + right +
                " -> идём в " + (left >= right ? "ЛЕВОЕ" : "ПРАВОЕ") + " поддерево");
    }

    /**
     * Рекурсивный алгоритм минимакс без отсечений.
     * @param d    текущая глубина (0 у корня)
     * @param pos  индекс листа, к которому ведёт текущая ветка
     * @param isMax чей ход: true — MAX, false — MIN
     */
    static int minimax(int d, int pos, boolean isMax) {
        nodesMM++;  // считаем посещённые узлы
        if (d == DEPTH) return LEAVES[pos]; // достигли листа

        // левый и правый потомки формируются побитовым сдвигом
        int left  = minimax(d + 1, pos << 1,      !isMax);
        int right = minimax(d + 1, (pos << 1) | 1, !isMax);
        return isMax ? Math.max(left, right) : Math.min(left, right);
    }

    /**
     * Минимакс с альфа-бета отсечением.
     * @param alpha — текущая нижняя граница для MAX
     * @param beta  — текущая верхняя граница для MIN
     * Если alpha >= beta, дальнейшие ветви не просматриваются.
     */
    static int alphabeta(int d, int pos, boolean isMax, int alpha, int beta) {
        nodesAB++;
        if (d == DEPTH) return LEAVES[pos];

        if (isMax) {
            int best = Integer.MIN_VALUE;

            // Левый ребёнок
            int v = alphabeta(d + 1, pos << 1, false, alpha, beta);
            best = Math.max(best, v);
            alpha = Math.max(alpha, best);
            if (alpha >= beta) return best; // отсечение правой ветви

            // Правый ребёнок
            v = alphabeta(d + 1, (pos << 1) | 1, false, alpha, beta);
            best = Math.max(best, v);
            alpha = Math.max(alpha, best);
            return best;
        } else {
            int best = Integer.MAX_VALUE;

            // Левый ребёнок
            int v = alphabeta(d + 1, pos << 1, true, alpha, beta);
            best = Math.min(best, v);
            beta = Math.min(beta, best);
            if (alpha >= beta) return best; // отсечение правой ветви

            // Правый ребёнок
            v = alphabeta(d + 1, (pos << 1) | 1, true, alpha, beta);
            best = Math.min(best, v);
            beta = Math.min(beta, best);
            return best;
        }
    }

    /**
     * Та же логика минимакса, но без счётчиков — чтобы отдельно вычислить left/right после тестов.
     */
    static int minimaxNoCount(int d, int pos, boolean isMax) {
        if (d == DEPTH) return LEAVES[pos];
        int left  = minimaxNoCount(d + 1, pos << 1,      !isMax);
        int right = minimaxNoCount(d + 1, (pos << 1) | 1, !isMax);
        return isMax ? Math.max(left, right) : Math.min(left, right);
    }

    // Перевод наносекунд в миллисекунды для вывода
    static double toMs(long ns) {
        return ns / 1e6;
    }
}
