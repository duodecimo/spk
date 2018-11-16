package duo.org.qasdectree;

import org.apache.commons.lang.time.DurationFormatUtils;
import org.apache.log4j.Level;
import org.apache.log4j.Logger;
import org.apache.spark.sql.DataFrameReader;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;

import static java.lang.Math.pow;
import static org.apache.spark.sql.functions.col;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

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
public class QASdecTree implements Serializable {
    private boolean debugging = true;
    private long startTime;

    public QASdecTree() {
        startTime = System.currentTimeMillis();
        Logger.getLogger("org").setLevel(Level.ERROR);
        SparkSession session = SparkSession.builder().appName("qasdectree").master("local[*]").getOrCreate();

        DataFrameReader dataFrameReader = session.read();

        /*
        Carga do conjunto de mensagens
         */
        Dataset<Row> messages = dataFrameReader.option("header","true").csv("/extra2/mySpark/javaNetbeans/data/Training.csv");
        //Dataset<Row> messages = dataFrameReader.option("header","true").csv("in/teste.csv");

        //messages.cache();

        mydebug("Tempo decorrido para carregar os dados: " + elapsedTime());
        /*
        obter array com os cabeçalhos das colunas
         */
        String[] headers = messages.columns();
        /*
        obter uma lista das palavras (são os cabeçalhos sem a primeira coluna, que é a de respostas (Answers)
         */
        List<String> words = new ArrayList<>(Arrays.asList(headers));
        words.remove(0);
        /*
        vamos garantir que as colunas de palavras tenham tipo de dado inteiro

        messages.cache();
        int countColumns = 0;
        for (String c: words) {
            messages = messages.withColumn(c, messages.col(c).cast("integer"));
            countColumns++;
            if(countColumns % 10 == 0) {
                mydebug("Convertidas " + countColumns + "/" + words.size()  + " colunas tempo decorrido " + elapsedTime());
            }
        }
        mydebug("Tempo decorrido para tranformar os tipos dos dados: " + elapsedTime());
         */

        //System.out.println("=== Mostrar o schema das mensagens ===");
        //messages.printSchema();

        //System.out.println("=== Mostrar a tabela de mensagens ===");
        //messages.show();

        /*
        vamos escolher uma resposta para iniciar o processo:
        a resposta com maior número de ocorrências.
         */
        Dataset<Row> groupedMessages = messages.groupBy(headers[0]).count();
        // groupedMessages.show();
        String choosenAnswer = groupedMessages
                .reduce((a, b) -> a.getLong(1) > b.getLong(1) ? a : b).getString(0);
        System.out.println("Resposta escolhida: " + choosenAnswer);


        /*
        calculando gini de O (O = conjunto de mensagens e suas respostas)

        convenção para a nomeclatura das variáveis:
        q quantidade
        t taxa
        m mensagens
        me mensagem escolhida
        r respostas
        re resposta escolhida
        p palavras
        pa palavra sendo analisada
        _ negativa
         */


        /*
        quantidade total de mensagens
         */
        double qm = (double) messages.count();
        mydebug("quantidade total de mensagens: " + qm);
        /*
        dataset apenas com as linhas da resposta escolhida
         */
        Dataset<Row> remessages = messages.filter(col(headers[0]).equalTo(choosenAnswer));

        //remessages.cache();

        /*
        quantidade de mensagens com a resposta escolhida
         */
        double qmre = (double) remessages.count();
        mydebug("quantidade de mensagens com a resposta escolhida: " + qmre);
        /*
        pcm = taxa de mensagens com a resposta escolhida (C)
         */
        double tmre = qmre / qm;
        mydebug("taxa de mensagens com a resposta escolhida: " + tmre);
        /*
        pam = taxa de mensagens sem a resposta escolhida (A)
         */
        double tmre_ = (qm - qmre) / qm;
        mydebug("taxa de mensagens sem a resposta escolhida: " + tmre_);
        double giniO = 1 - (pow(tmre, 2) + pow(tmre_, 2));
        mydebug("GINI de O: " + giniO);
        mydebug("Tempo decorrido para calcular o GINI de O: " + elapsedTime());

        /*
        calculando o gini de cada palavra
         */
        int wordCount = 0;
        Map<String, Double> wordsGini = new ConcurrentHashMap<>();
        for (String word: words) {
            mydebug("=========================");
            mydebug("Palavra sendo avaliada: " + word);
            mydebug("=========================");
            /*
            quantidade  de mensagens com a palavra sendo avaliada
             */
            double qmpa = (double) messages.filter(col(word).like("1")).count();
            mydebug("quantidade  de mensagens com a palavra sendo avaliada: " + qmpa);
            /*
            quantidade de mensagens com a resposta escolhida com a palavra avaliada
             */
            double qmepa = (double) remessages.filter(col(word).like("1")).count();
            mydebug("quantidade  de mensagens com a resposta escolhida e palavra sendo avaliada: " + qmepa);
            /*
            taxa de mensagens com a palavra sendo analisada e a resposta escolhida
             */
            double tmpare = qmpa==0.0d ? 0.0d : qmepa/qmpa;
            mydebug("taxa de mensagens com a palavra sendo analisada e a resposta escolhida: " + tmpare);
            /*
            taxa de mensagens com a palavra sendo analisada e a resposta diferente da escolhida
             */
            double tmpare_ = qmpa == 0.0d ? 0.0d : (qmpa - qmepa)/qmpa;
            mydebug("taxa de mensagens com a palavra sendo analisada e a resposta diferenta da escolhida: " + tmpare_);
            /*
            gini das mensagens com a palavra sendo avaliada e com a resposta escolhida
             */
            double ginipare = 1 - (pow(tmpare, 2) + pow(tmpare_, 2));
            mydebug("gini das mensagens com a palavra sendo avaliada e com a resposta escolhida: " + ginipare);
            /*
            quantidade de mensagens sem a palavra avaliada com a resposta escolhida
             */
            double qmpa_re = qmre - qmepa;
            mydebug("quantidade de mensagens sem a palavra avaliada com a resposta escolhida: " + qmpa_re);
            /*
            taxa de mensagens com a resposta escolhida sem a palavra avaliada
             */
            double tmpa_re = qmpa == 0.0d ? 0.0d : qmpa_re / qmpa;
            mydebug("taxa de mensagens com a resposta escolhida sem a palavra avaliada: " + tmpa_re);
            /*
            taxa de mensagens sem a palavra avaliada e resposta diferente da escolhida
             */
            double tmpa_re_ = qmpa == 0.0d ? 0.0d : (qmpa - qmpa_re)/qmpa;
            mydebug("taxa de mensagens sem a palavra avaliada e resposta diferente da escolhida: " + tmpa_re_);
            /*
            gini das mensagens sem a palavra sendo avaliada e com a resposta escolhida
             */
            double ginipa_re =  1 - (pow(tmpa_re, 2) + pow(tmpa_re_, 2));
            mydebug("gini das mensagens sem a palavra sendo avaliada e com a resposta escolhida: " + ginipa_re);
            /*
            calculando o gini da palavra
             */
            double ginipa = giniO - ((ginipare * qm == 0.0d ? 0.0d : qmpa / qm) + (ginipa_re * qm == 0.0d ? 0.0d : qmpa_re / qm));
            wordsGini.put(word, ginipa);
            mydebug("gini da palavra avaliada: " + ginipa);
            wordCount++;
            mydebug("Tempo decorrido para calcular o GINI da palavra "  + word +
                    "(" + wordCount + "/" + words.size() + ") : " + elapsedTime());
        }
        mydebug("==========================================");
        mydebug("resumo dos gini:");
        String bestGiniWord = "";
        double bestGini = -1.0d;
        for (String key : wordsGini.keySet()) {
            if(bestGiniWord.isEmpty()) {
                bestGini = wordsGini.get(key);
                bestGiniWord =key;
            }
            System.out.println(key + " " + wordsGini.get(key));
            if(wordsGini.get(key)> bestGini) {
                bestGini = wordsGini.get(key);
                bestGiniWord =key;
            }
        }
        mydebug("==========================================");
        mydebug("Palavra com melhor gini: " + bestGiniWord + " (gini " + bestGini + ")");
        mydebug("==========================================");

        /*
        Fim!
         */
        mydebug("Tempo decorrido total: " + elapsedTime());
        session.stop();
    }


    private boolean mydebug(String s) {
        if(debugging = true) {
            System.out.println(s);
        }
        return debugging;
    }

    private String elapsedTime() {
        long millis = System.currentTimeMillis() - startTime;
        return DurationFormatUtils.formatDuration(millis, "HH:mm:ss.S");
    }

    public static void main(String[] args) {
        QASdecTree qaSdecTree = new QASdecTree();
    }
}
