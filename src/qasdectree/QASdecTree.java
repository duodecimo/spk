/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package qasdectree;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import org.apache.log4j.Level;
import org.apache.log4j.Logger;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;

/**
 *
 * @author duo
 * 
 * Sobre a escolha da melhor palavra:
 * 
 * Em termos formais, para um conjunto O de mensagens e suas respectivas respotas padrões,
 * o poder discriminativo de uma palavra w é dada por:
 * 
 * Delta I(O) = I(O) - (I(O_w) * p_w + I(O_s/w) * p_s/w)
 * 
 * onde
 * 
 * I(O) = Gini de O
 * I(O_w) = Gini do subconjunto de elementos de O contendo a palavra w
 * I(O_s/w) = Gini do subconjunto de elementos de O sem a palavra w
 * 
 * Para um onjunto O de observações e uma classe J de n objetos, Gini é calculado por:
 * 
 * I(O) = 1 - S
 * 
 * S = Sum de i=1 ate n de P(j_i|O) elevado a 2, para j_i pertence a J e
 * P(j_i|O) é a probabilidade da ocorrência de objetos j_i em O.
 * 
 */
public class QASdecTree {
    private final SparkSession session;
    private final Dataset<Row> training;
    public QASdecTree() {
        Logger.getLogger("org").setLevel(Level.ERROR);
        session = SparkSession.builder().appName("QASdecTree")
                .master("local[3]").getOrCreate();
        training = session.read().option("header", "true")
                .csv("/extra2/mySpark/javaNetbeans/data/Training.csv");
        System.out.println("Original training has " + training.columns().length + 
                " columns and " + training.count() + " lines.");
        Dataset<Row> trainingSample = training.sample(0.05);
        System.out.println("Sample training has " + trainingSample.columns().length + 
                " columns and " + trainingSample.count() + " lines.");
        // get an array with headers
        String[] headers = trainingSample.columns();
        // to get a list of data columns (words)
        List<String> words = Arrays.asList(headers);
        // and remove first column, that is Answer
        words.remove(0);
        int windex = 0;
        System.out.println("Showing 30/" + words.size() + " of data column names");
        for(String word : words) {
            System.out.println(String.format("|Index %4d |%s|", windex, word));
            windex++;
            if(windex>30) {
                break;
            }
        }
        // metrics
        Dataset<Row> groupedAnswers = trainingSample.groupBy(headers[0]).count();
        groupedAnswers.cache();
        // total answers
        long totalAnswers = groupedAnswers.count();
        System.out.println("Total answers: " + totalAnswers);
        groupedAnswers.show(10);
        // most frequent answer
        String mostFrequentAnswer = groupedAnswers
                .reduce((a, b) -> a.getLong(1) > b.getLong(1) ? a : b).getString(0);
        System.out.println("Most frequent answer: " + mostFrequentAnswer);
        groupedAnswers.filter(headers[0] + " like \"%1262%\"").show();
    }

    public static void main(String[] args) {
        QASdecTree qASdecTree = new QASdecTree();
    }
}
