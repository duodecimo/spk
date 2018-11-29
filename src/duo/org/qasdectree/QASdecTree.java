package duo.org.qasdectree;

import org.apache.commons.lang.time.DurationFormatUtils;
import org.apache.log4j.Level;
import org.apache.log4j.Logger;
import org.apache.spark.sql.DataFrameReader;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;

import static java.lang.Math.max;
import static java.lang.Math.pow;
import static org.apache.spark.sql.functions.col;

import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 *
 * @author duo 16/11/2018.
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
    private final boolean debugging;
    private final boolean saveDebugging;
    private final String TEST;
    private final double PERCENTAGE;
    private DebugLog debugLog;
    private final long startTime;
    private final List<String> words;

    private QASdecTree() {
        /*
        debugging = true para mostrar mensagens do programa no console
         */
        debugging = true;
        /*
        saveDebugging = true para gravar um aquivo de log na pasta de dados
         */
        saveDebugging = true;
        try {
            debugLog = new DebugLog();
        } catch (IOException e) {
            debugLog = null;
            e.printStackTrace();
        }

        startTime = System.currentTimeMillis();
        Logger.getLogger("org").setLevel(Level.ERROR);


        SparkSession session = SparkSession.builder()
                .appName("qasdectree")
                .master("local[*]")
                .config("spark.sql.codgen", true) /* compile or not queries to java bytecode */
                .config("spark.sql.inMemoryColumnarStorage.batchSize", 1200) /* default = 1000 - smaller to avoid out of memory when caching */
                .config("spark.dynamicAllocation.enabled", true)
                .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
                .config("spark.kryoserializer.buffer.max", "128m")
                .config("spark.kryoserializer.buffer", "64m")
                .config("spark.driver.memory", "2g") /* it is recommended to pass it in command line --driver-memory=2g as java is already started here */
                .getOrCreate();

        DataFrameReader dataFrameReader = session.read();

        /*
        Carga do conjunto de mensagens
         */
        /*
        descomente a opção abaixo para rodar com o dataset inteiro.
         */
        //TEST = "/extra2/mySpark/javaNetbeans/data/Training.csv";
        /*
        descomente a opção abaixo para rodar com o pequeno dataset de teste.
         */
        TEST = "/extra2/mySpark/javaNetbeans/data/teste.csv";
        /*
        Descomente a opção abaixo para rodar o dataset completo
         */
        //PERCENTAGE = 1.0d;
        /*
        Descomente a opção abaixo para rodar com uma amostra parcial do dataset.
        o valor 0.1d por exemplo corresponde a 10%
         */
        PERCENTAGE = 0.9d;
        Dataset<Row> messages;
        if(PERCENTAGE < 1.0d) {
            messages = dataFrameReader.option("header","true").csv(TEST).sample(true, PERCENTAGE);
        } else {
            messages = dataFrameReader.option("header","true").csv(TEST);
        }


        //messages.cache();

        /*
        spark configuration report
         */
        mydebug("===================");
        mydebug("Utilizando os dados extraidos de ".concat(TEST));
        if(PERCENTAGE < 1.0d) {
            mydebug("Aplicada taxa de redução nos dados originais de " + PERCENTAGE);
        }
        mydebug("-------------------");
        mydebug("Spark Configuration");
        mydebug("spark.sql.codgen".concat(" = ").concat(session.conf().get("spark.sql.codgen")));
        mydebug("spark.sql.inMemoryColumnarStorage.batchSize".concat(" = ").concat(session.conf().get("spark.sql.inMemoryColumnarStorage.batchSize")));
        mydebug("spark.dynamicAllocation.enabled".concat(" = ").concat(session.conf().get("spark.dynamicAllocation.enabled")));
        mydebug("spark.driver.memory".concat(" = ").concat(session.conf().get("spark.driver.memory")));
        mydebug("-------------------");
        mydebug("Tempo decorrido para carregar os dados: " + elapsedTime());
        mydebug("===================");

        /*
        obter array com os cabeçalhos das colunas
         */
        String[] headers = messages.columns();
        /*
        obter uma lista das palavras (são os cabeçalhos sem a primeira coluna, que é a de respostas (Answers)
         */
        words = new ArrayList<>(Arrays.asList(headers));
        words.remove(headers[0]);

        /*
        criar a árvore de decisão
         */
        Node QASdecisionTree = createNode(messages, words, headers[0], "root");
        /*
        persistir a arvore
         */
        ObjectOutputStream objectOutputStream = null;
        try {
            objectOutputStream = new ObjectOutputStream(
                    new FileOutputStream("/extra2/mySpark/javaNetbeans/data/dTree.ser"));
        } catch (IOException e) {
            e.printStackTrace();
        }
        try {
            if (objectOutputStream != null) {
                objectOutputStream.writeObject(QASdecisionTree);
                objectOutputStream.close();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

        /*
        Fim!
         */
        mydebug("Tempo decorrido total: " + elapsedTime());
        session.stop();

    }

    private Node createNode(Dataset<Row> messages, List<String> words, String answersRow, String nodeName) {
        messages.cache();

        /*
        quantidade total de mensagens
         */
        double qm = (double) messages.count();
        mydebug("quantidade total de mensagens: " + qm);

        /*
        escolher uma resposta para iniciar o processo:
        a resposta com maior número de ocorrências.
        */
        Dataset<Row> groupedMessages = messages.groupBy(answersRow).count();
        String choosenAnswer = groupedMessages
                .reduce((a, b) -> a.getLong(1) > b.getLong(1) ? a : b).getString(0);
        mydebug("Resposta escolhida: " + choosenAnswer);

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
        dataset apenas com as linhas da resposta escolhida
         */
        Dataset<Row> remessages = messages.filter(col(answersRow).equalTo(choosenAnswer));

        remessages.cache();

        /*
        quantidade de mensagens com a resposta escolhida
         */
        double qmre = (double) remessages.count();
        //mydebug("quantidade de mensagens com a resposta escolhida: " + qmre);
        /*
        pcm = taxa de mensagens com a resposta escolhida (C)
         */
        double tmre = qmre / qm;
        //mydebug("taxa de mensagens com a resposta escolhida: " + tmre);
        /*
        pam = taxa de mensagens sem a resposta escolhida (A)
         */
        double tmre_ = (qm - qmre) / qm;
        //mydebug("taxa de mensagens sem a resposta escolhida: " + tmre_);
        double giniO = 1 - (pow(tmre, 2) + pow(tmre_, 2));
        /*
        gini negativo não faz sentido ...
         */
        giniO = max(0, giniO);
        mydebug("GINI de O: " + giniO);
        mydebug("Tempo decorrido: " + elapsedTime());

        /*
        calculando o gini de cada palavra
         */
        int wordCount = 0;
        Map<String, Double> wordsGini = new ConcurrentHashMap<>();
        for (String word: words) {
            //mydebug("=========================");
            //mydebug("Palavra sendo avaliada: " + word);
            //mydebug("=========================");

            /*
            quantidade  de mensagens com a palavra sendo avaliada

            pode ser que aquí possa ser feito um grande aprimoramento:

            se a palavra não está em nenhuma das mensagens, ela pode
            ser removida da lista de palavras, e desta forma, não ser mais propagada
            na árvore.
            Naturalmente, a lista de palavras tem que ser copiada e passada como parametro
            para o próximos nós.
            O laço (loop) pod3 ser abandonado neste caso (palavra ausente das mensagens).
             */
            double qmpa = (double) messages.filter(col(word).like("1")).count();
            if(qmpa==0.0d) {
                /*
                remover da lista de palavras
                 */
                words.remove(word);
                /*
                interromper o laço
                 */
                continue;
            }

            //mydebug("quantidade  de mensagens com a palavra sendo avaliada: " + qmpa);
            /*
            quantidade de mensagens com a resposta escolhida com a palavra avaliada
             */
            double qmepa = (double) remessages.filter(col(word).like("1")).count();
            //mydebug("quantidade  de mensagens com a resposta escolhida e palavra sendo avaliada: " + qmepa);
            /*
            taxa de mensagens com a palavra sendo analisada e a resposta escolhida
             */
            double tmpare = qmpa==0.0d ? 0.0d : qmepa/qmpa;
            //mydebug("taxa de mensagens com a palavra sendo analisada e a resposta escolhida: " + tmpare);
            /*
            taxa de mensagens com a palavra sendo analisada e a resposta diferente da escolhida
             */
            double tmpare_ = qmpa == 0.0d ? 0.0d : (qmpa - qmepa)/qmpa;
            //mydebug("taxa de mensagens com a palavra sendo analisada e a resposta diferenta da escolhida: " + tmpare_);
            /*
            gini das mensagens com a palavra sendo avaliada e com a resposta escolhida
             */
            double ginipare = 1 - (pow(tmpare, 2) + pow(tmpare_, 2));
            //mydebug("gini das mensagens com a palavra sendo avaliada e com a resposta escolhida: " + ginipare);
            /*
            quantidade de mensagens sem a palavra avaliada com a resposta escolhida
             */
            double qmpa_re = qmre - qmepa;
            //mydebug("quantidade de mensagens sem a palavra avaliada com a resposta escolhida: " + qmpa_re);
            /*
            taxa de mensagens com a resposta escolhida sem a palavra avaliada
             */
            double tmpa_re = qmpa == 0.0d ? 0.0d : qmpa_re / qmpa;
            //mydebug("taxa de mensagens com a resposta escolhida sem a palavra avaliada: " + tmpa_re);
            /*
            taxa de mensagens sem a palavra avaliada e resposta diferente da escolhida
             */
            double tmpa_re_ = qmpa == 0.0d ? 0.0d : (qmpa - qmpa_re)/qmpa;
            //mydebug("taxa de mensagens sem a palavra avaliada e resposta diferente da escolhida: " + tmpa_re_);
            /*
            gini das mensagens sem a palavra sendo avaliada e com a resposta escolhida
             */
            double ginipa_re =  1 - (pow(tmpa_re, 2) + pow(tmpa_re_, 2));
            //mydebug("gini das mensagens sem a palavra sendo avaliada e com a resposta escolhida: " + ginipa_re);
            /*
            calculando o gini da palavra
             */
            double ginipa = giniO - ((ginipare * qm == 0.0d ? 0.0d : qmpa / qm) + (ginipa_re * qm == 0.0d ? 0.0d : qmpa_re / qm));
            /*
            gini negativo não faz sentido ...
             */
            ginipa = max(0, ginipa);
            wordsGini.put(word, ginipa);
            //mydebug("gini da palavra avaliada: " + ginipa);
            wordCount++;
            if(wordCount % 20 == 0) {
                mydebug("processadas "  + wordCount + "/" + words.size() + " em " + elapsedTime());
            }
            //mydebug("Tempo decorrido para calcular o GINI da palavra "  + word +
            //        "(" + wordCount + "/" + words.size() + ") : " + elapsedTime());
        }
        String bestGiniWord = "";
        double bestGini = -1.0d;
        for (String key : wordsGini.keySet()) {
            if(bestGiniWord.isEmpty()) {
                bestGini = wordsGini.get(key);
                bestGiniWord =key;
            }
            if(wordsGini.get(key)> bestGini) {
                bestGini = wordsGini.get(key);
                bestGiniWord =key;
            }
        }
        mydebug("==========================================");
        mydebug("No: " + nodeName);
        mydebug("Palavra com melhor gini: " + bestGiniWord + " (gini " + bestGini + ")");
        mydebug("==========================================");

        Node node = new Node(bestGiniWord, null);
        /*
        dividir as mensagens entre as que contém a palavra com melhor GINI e as que não.
         */
        Dataset<Row> messagespa = messages.filter(col(bestGiniWord).like("1"));
        Dataset<Row> messagespa_ = messages.filter(col(bestGiniWord).like("0"));
        /*
        remove a palavra deste nó
         */
        words.remove(bestGiniWord);

        List<String> nodeWords = new ArrayList<>(words);

        /*
        verifica a expansão da árvore
         */
        Dataset<Row> groupedMessagesPa = messagespa.groupBy(answersRow).count();
        /*
        verifica expansão à esquerda
         */
        if(groupedMessagesPa.count() ==1) {
            /*
            so existe uma resposta: é uma folha com decisão de resposta
             */
            String sans = groupedMessagesPa.reduce((a, b) -> a.getLong(1) > b.getLong(1) ? a : b).getString(0);
            node.setLeft(new Node(null, sans));
            mydebug("Folha a esquerda com resposta: " + sans);
        } else if(groupedMessagesPa.count() <1 || nodeWords.size() == 0) {
            /*
            não existe resposta ou esgotaram-se as palavras sem atingir uma única resposta (teria sido capturado acima)
            É uma folha sem decisão de resposta
             */
            node.setLeft(new Node(null, null));
            mydebug("Folha à esquerda sem resposta.");
        } else {
            /*
            a expansão à esquerda continua
             */
            node.setLeft(createNode(messagespa, nodeWords, answersRow, nodeName.concat(".L")));
        }

        Dataset<Row> groupedMessagesPa_ = messagespa_.groupBy(answersRow).count();
        /*
        verifica expansão à direita
         */
        if(groupedMessagesPa_.count() ==1) {
            /*
            so existe uma resposta: é uma folha com decisão de resposta
             */
            String sans = groupedMessagesPa_.reduce((a, b) -> a.getLong(1) > b.getLong(1) ? a : b).getString(0);
            node.setRight(new Node(null, sans));
            mydebug("Folha à direita com resposta: " + sans);
        } else if(groupedMessagesPa_.count() <1 || nodeWords.size() == 0) {
            /*
            não existe resposta ou esgotaram-se as palavras sem atingir uma única resposta (teria sido capturado acima)
            É uma folha sem decisão de resposta
             */
            node.setRight(new Node(null, null));
            mydebug("Folha à direita sem resposta.");
        } else {
            /*
            a expansão à direita continua
             */
            node.setRight(createNode(messagespa_, nodeWords, answersRow, nodeName.concat(".R")));
        }
        return node;

    }

    private void mydebug(String s) {
        if(debugging) {
            System.out.println(s);
        }
        if(saveDebugging && debugLog!=null) {
            try {
                debugLog.writeMsg(s);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    private String elapsedTime() {
        long millis = System.currentTimeMillis() - startTime;
        return DurationFormatUtils.formatDuration(millis, "HH:mm:ss.S");
    }

    public static void main(String[] args) {
        @SuppressWarnings("unused") QASdecTree qaSdecTree = new QASdecTree();
    }
}
