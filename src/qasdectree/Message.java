/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package qasdectree;

/**
 *
 * @author duo
 */
public class Message {
    private String answer;
    private String[] words;

    public Message() {
    }

    public Message(String answer, String[] words) {
        this.answer = answer;
        this.words = words;
    }

    public String getAnswer() {
        return answer;
    }

    public void setAnswer(String answer) {
        this.answer = answer;
    }

    public String[] getWords() {
        return words;
    }

    public void setWords(String[] words) {
        this.words = words;
    }
}
