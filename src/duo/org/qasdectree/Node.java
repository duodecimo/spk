package duo.org.qasdectree;

import java.io.Serializable;

/**
 * @author duo
 * Uma árvore binária de decisão para um problema de Perguntas e Respostas.
 * A chave de cada nó é uma palavra.
 * Um nó folha possui chave nula, e possui ou não uma resposta.
 * Quando a árvore for utilizada para classificar uma mensagem, percorra a arvore a partir da raiz:
 * A cada nó (não folha), se a mensagem possui a palavra da chave, vá para a esquerda,
 * caso não para direita.
 * Ao atingir uma folha, se ela possuir uma resposta, utilize-a.
 * Caso não, o algoritmo não foi capaz de classificar a mensagem.
 */
public class Node implements Serializable {
    private static final long serialVersionUID = 1L;
    private String key;
    private Node left;
    private Node right;
    private String answer;
    public Node() {
    }

    public Node(String key, String answer) {
        super();
        this.key = key;
        this.answer = answer;
    }

    public String getKey() {
        return key;
    }

    public void setKey(String key) {
        this.key = key;
    }

    public Node getLeft() {
        return left;
    }

    public void setLeft(Node left) {
        this.left = left;
    }

    public Node getRight() {
        return right;
    }

    public void setRight(Node right) {
        this.right = right;
    }

    public String getAnswer() {
        return answer;
    }

    public void setAnswer(String answer) {
        this.answer = answer;
    }
}
