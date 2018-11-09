/*


*/
package qasdectree;

import java.io.IOException;
import static java.lang.Math.pow;
import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Iterator;
import java.util.List;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.log4j.Level;
import org.apache.log4j.Logger;
import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.api.java.function.FlatMapFunction;
import org.apache.spark.api.java.function.MapFunction;
import org.apache.spark.sql.Encoders;
import org.apache.spark.sql.functions;

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

    private final SparkSession spark;
    //private final JavaSparkContext jsc;
    private final Dataset<Row> awDataset;
    private final Dataset<Row> waDataset;
    private final WriterResults writerResults;
    private int treeNodes;
    private final boolean debug = false;

    /**
     * This method reads the data and builds the QAS DecisionTree
     * @throws java.io.IOException
     */
    public QASdecTree() throws IOException {
        Logger.getLogger(this.getClass()).getLevel();
        /*
        levels list:
        OFF (most specific, no logging)
        FATAL (most specific, little data)
        ERROR
        WARN
        INFO
        DEBUG
        TRACE (least specific, a lot of data)
        ALL (least specific, all data)
        */
        Logger.getLogger("org").setLevel(Level.ERROR);
        Logger.getLogger("akka").setLevel(Level.ERROR);

        /*
        no mini, com debug = false, 4 minutos 2 segundos
        no mini, com debug = true,  4 minutos 6 segundos
        */
        

        treeNodes = 0;
        writerResults = new WriterResults("qtest.txt");
        this.spark = SparkSession.builder().appName("CsvTests").master("local[4]").getOrCreate();
        //this.jsc = new JavaSparkContext(spark.sparkContext());
        /*
        obs: the original csv had spaces in the header starting from the second column.
        Some answers has accents, and non letter or digits or _ chars too.
        I coded a pair of python programs (for the convenience of python csv classes)
        to fix it (see javaNetbeans/data csvAdjust.py and csvAdjust2.py)
        */

        /*
         * read csvs into Dataset object to use on spark and benefit from distribution.
         */
        awDataset = spark.read().format("csv")
                .option("sep", ",")
                .option("inferSchema", "true")
                .option("header", "true")
                //.load("/extra2/mySpark/javaNetbeans/data/aw.csv");
                .load("/extra2/mySpark/javaNetbeans/data/miniaw.csv");
        waDataset = spark.read().format("csv")
                .option("sep", ",")
                .option("inferSchema", "true")
                .option("header", "true")
                //.load("/extra2/mySpark/javaNetbeans/data/wa.csv");
                .load("/extra2/mySpark/javaNetbeans/data/miniwa.csv");
        /*
        Com trainingCor, começando em:
         */

        /*
        turn into temporary view to apply sql
        */
        //awDataset.createOrReplaceGlobalTempView("awDataset");
        awDataset.createOrReplaceTempView("awDataset");
        waDataset.createOrReplaceTempView("waDataset");
        long countingAnsw = awDataset.groupBy("0").count().count();
        //long countingAnsw = spark.sql("select count() from awDataset group by ANSWER").count();
        writerResults.writeMsg("--- timestamp: " + new Timestamp(System.currentTimeMillis()));
        writerResults.writeMsg("Counting answers on awDataset: " + countingAnsw);
        /*
        local debug
        */
        awDataset.groupBy("0").count().show();
        System.out.println("Counting answers on awDataset: " + countingAnsw);
        if(countingAnsw <= 1L) {
            writerResults.writeMsg("Exiting due to no ANSWER");
            spark.stop();
            System.exit(0);
        }
        writerResults.writeMsg("Data loaded. Starting tree");
        /*
        extrac the attributes
        */
        List<String> attributes;
        attributes = new ArrayList<>(Arrays.asList(awDataset.schema().fieldNames()));
        /*
        attribute that i created, no need to process
        */
        writerResults.writeMsg("Number of attributes: " + attributes.size());
        /*
        attributes.remove("MSGID");
        attributes that are causing problem for having accent
        attributes.remove("VTRSÁBADO");
        attributes.remove("NOCÃ");
        writerResults.writeMsg("Number ofattributes: " + attributes.size());
        */
        /*
        create decision tree
        */
        Node decisionTree = new Node();
        /*
        build the tree
        */
        buildTree(decisionTree, attributes, awDataset, " 1");
    }
    
    private void buildTree(Node node, List<String> attributes, Dataset awDataset, String alias) throws IOException {
        awDataset.createOrReplaceTempView("awDataset");
        treeNodes++;
        node.setAttribute(chooseNodeBestAttribute(attributes, awDataset));
        writerResults.writeMsg("Node " + alias + ": " + node.getAttribute());
        writerResults.writeMsg("--- timestamp: " + new Timestamp(System.currentTimeMillis()));
        /*
        remove the attribute from attributs list
        */
        attributes.remove(node.getAttribute());

        /*
        System.out.println("\n\n===============================================\n\n");
        System.out.println("Mostrando o completo: ");
        awDataset.show(10);
        writerResults.writeMsg("awDataset show: " + 
                awDataset.sqlContext().sql("select ANSWER, " + 
                        node.getAttribute() + " from awDataset").showString(10, 20, true));
        System.out.println("\n\n===============================================\n\n");
        */

        /*
        grow for left recursively
        */
        Dataset<Row> leftDataset = awDataset.filter("" + node.getAttribute() + " = 1");
        //leftDataset.createOrReplaceTempView("leftDataset");
        System.out.println("\n\n===============================================\n\n");
        System.out.println("Mostrando o left: ");
        leftDataset.show(10);
        System.out.println("Possui " + leftDataset.count() + " registros.");
        if (debug) {
            writerResults.writeMsg("leftDataset show: "
                    + leftDataset.showString(10, 20, true));
        }
        System.out.println("\n\n===============================================\n\n");
        if(!checkForEndingOfNodeSplit(attributes, leftDataset)) {
            node.left = new Node();
            buildTree(node.left, attributes, leftDataset, alias + ".1");
        } else {
            writerResults.writeMsg("leaf reached: " + node.getAttribute() + alias);
        }
        /*
        grow for right recursively
        */
        Dataset<Row> rightDataset = awDataset.filter("" + node.getAttribute() + " = 0");
        //rightDataset.createOrReplaceTempView("rightDataset");
        System.out.println("\n\n===============================================\n\n");
        System.out.println("Mostrando o right: ");
        rightDataset.show(10);
        System.out.println("Possui " + rightDataset.count() + " registros.");
        if (debug) {
            writerResults.writeMsg("rightDataset show: "
                    + rightDataset.showString(10, 20, true));
        }
        System.out.println("\n\n===============================================\n\n");
        if(!checkForEndingOfNodeSplit(attributes, rightDataset)) {
            node.right = new Node();
            buildTree(node.right, attributes, rightDataset, alias + ".2");
        } else {
            writerResults.writeMsg("leaf reached: " + node.getAttribute() + alias);
        }
    }

    /**
     * 
     * Answers are c1, c2, ..., c3
     * Let's derive tree on the first answer, then,
     * next division for 2nd, and so on.
     * 
     * calculate gini of awDataset
     * 
     * T = total messages
     * C = total messages with Answer ci
     * CP = C/T
     * A = T - C (total other than C messages)
     * AP = A/T
     * awDatasetGini = 1 - ((CP*CP + AP*AP))
     * 
     * calculate impact of each word (w1, w2, ..., wn) on the
     * awDataset with answer cj
     * 
     * C = total messages with Answer cj and word wi
     * A = total messages with Answer not cj but with word wi
     * T = C+A
     * CP = C/T
     * AP = A/T
     * wiGini = 1 - ((CP*CP) + (AP*AP))
     * 
     * (Here I think it's better do not use the gini of absence of wi).
     * 
     * calculate discrimination power of each wi on cj
     * 
     * dpi = awDatasetGini - (wiGini * (C/A))
     * 
     * done, return max dpi
     *  - use wi (with max dpi) as tree node
     *  - remove wi from list of words
     *  - send data with answer cj to the left
     *  - send data with answer not cj to the right
     * 
     * @param attributes
     * @param awDataset
     * @return
     * @throws IOException 
     *      */
    protected String chooseNodeBestAttribute(List<String> attributes, Dataset awDataset) throws IOException {
        awDataset.createOrReplaceTempView("awDataset");
        /*
        Answers are c1, c2, ..., c3.
        Obs.: If the node has only one answer, thats it!
        
        Let's derive tree spliting node on a picked answer, then, next division for 2nd, and so on.
        pick first answer on node awDataset.
        
        Let's pick up first the answer with max lines, to maximaze the splitting:
        
        System.out.println("trying to get the answer with max lines:");
        awDataset.groupBy("ANSWER").count().orderBy(functions.column("count").desc()).show(20);
        */
        Dataset<Row> consAnswer = awDataset.groupBy("0").count().orderBy(functions.column("count").
                desc());
        int answer = consAnswer.first().getInt(0);
        if (debug) {
            writerResults.writeMsg("Choosing best attribute. Picked answer: " + answer);
        }
        System.out.println("Choosing best attribute. Picked answer: " + answer);
        /*
        calculate gini of awDataset:
        T = total messages
        C = total messages with Answer ci
        CP = C/T
        A = T - C (total other than C messages)
        AP = A/T
        awDatasetGini = 1 - ((CP*CP + AP*AP))
        */
        double totalAnswers = (double) consAnswer.count();
        double msgWithAnswer = (double) consAnswer.first().getLong(1);
        double pMsgWithAnswer = msgWithAnswer / totalAnswers;
        double pMsgWithoutAnswer = (totalAnswers - msgWithAnswer) / totalAnswers;
        double awDatasetGini = 1.0D - (pow(pMsgWithAnswer, 2) + pow(pMsgWithoutAnswer, 2));
        System.out.println("Total answers: " + totalAnswers +
                " messages with answer " + answer + ": " + msgWithAnswer);
        System.out.println("Datset Gini = " + awDatasetGini);
        /*
        calculate impact of each word (w1, w2, ..., wn) on the
        awDataset with answer cj.
        so, awDataset can be reduced to lines with answer cj.
        */
        Dataset<Row> filteredToAnswer = awDataset.filter("Answer = " + answer);
        String[] colsFta = filteredToAnswer.columns();
        
        Dataset<Row> sFilteredToAnswer = filteredToAnswer.groupBy("" + answer).sum(colsFta);
        sFilteredToAnswer.show(20);
        String[] sColsFta = sFilteredToAnswer.columns();

        int aa=10;
        // opera em uma coluna, aceita valores externos
        // posso usar em wa com a coluna da resposta escolhida, calculando o gini de todas
        // as palavras, para verificar qual o maior ...
        Dataset<Integer> damn = waDataset.select("" + answer).flatMap((FlatMapFunction<Row, Integer>) value -> {
            return Arrays.asList((value.getInt(0)<0 ? 0: value.getInt(0) * aa)).iterator();
                }, Encoders.INT());
        Iterator<Integer> it = damn.collectAsList().iterator();
        int max = -1;
        int val;
        while(it.hasNext()) {
            val = it.next();
            if(val>max) {
                max = val;
            }
        }
        System.out.println("Maior valor: " + max);
        /*
            Cw = total messages with Answer cj and word wi
            Aw = total messages with Answer not cj but with word wi
            Tw = total messages with word wi
            Tw = Cw+Aw
            CPw = Cw/Tw
            APw = Aw/Tw
            wiGini = 1 - ((CPw*CPw) + (APw*APw))

            (Here I think it's better do not use the gini of absence of wi).

            calculate discrimination power of each wi on cj
            dpi = awDatasetGini - (wiGini * (C/A))
            done, return max dpi
         */

        
        /*
        
        List res = psfAw.collect();
        //JavaRDD psfAw = jsc.parallelize(sfAw.collect());
        JavaPairRDD<Integer, Integer> pairs;
        pairs = sfAw.mapToPair((Object s) -> new Tuple2(1, new Integer(s.toString())));
        Object []apairs = pairs.collectAsMap().keySet().toArray();
        System.out.println("Some keys ...");
        for(int i = 0; i<20; i++) {
        System.out.println("key " + i + "= " + (Integer) apairs[i]);
        }
        //List res = sfAw.filter(v -> new Integer(v.toString()) != 0).collect();
        
        for(int i=0; i<res.size() && i<5; i++) {
            System.out.println("JavaRDD element " + i + " = " + res.get(i).toString());
        }
        */
        spark.stop();
        System.exit(0);
        
        System.out.println("Reduced to Answer " + answer +
                " size: " + filteredToAnswer.count());
        /*
        I wonder if I need:
        filteredToAnswer.createOrReplaceTempView("filteredToAnswer");
        */
        
        /*
        iterate over attributes
        */
        double attrGini;
        double maxAttrGini = 0.0D;
        String maxAttribute = "";
        int countAttributes = 0;
        for(String attribute : attributes) {
            countAttributes++;
            System.out.println("Checking attribute " + countAttributes + " of " + 
                attributes.size() + ".");

           /*
            C = total messages with Answer cj and word wi
            A = total messages with Answer not cj but with word wi
            T = total messages with word wi
            T = C+A
            CP = C/T
            AP = A/T
            wiGini = 1 - ((CP*CP) + (AP*AP))

            (Here I think it's better do not use the gini of absence of wi).

            calculate discrimination power of each wi on cj
            dpi = awDatasetGini - (wiGini * (C/A))
            done, return max dpi
            */

            /*
            C = total messages with Answer cj and word wi.
            */
            double tot_c = (double)filteredToAnswer.filter("" + attribute + " = 1").count();
            /*
            well, if the answer (attribute) does not yields the answer, 
            it cannot be considered of any influence on it.
            */
            if(tot_c == 0.0D) {
                continue;
            }
            /*
            A = total messages with Answer not cj but with word wi.
            */
            double total = (double)awDataset.filter("" + attribute + " =1").count();
            double tot_a = total - tot_c;
            /*
            CP = C/T
            */
            double ptot_c = tot_c/total;
            /*
            AP = A/T
            */
            double ptot_a = tot_a/total;
            /*
            wiGini = 1 - ((CP*CP) + (AP*AP))
            */
            attrGini = 1 - (pow(ptot_c,2) + pow(ptot_a, 2));
            if(maxAttribute.isEmpty()) {
                maxAttrGini = attrGini;
                maxAttribute = attribute;
            }
            if(attrGini > maxAttrGini) {
                maxAttrGini = attrGini;
                maxAttribute = attribute;
            }
            System.out.println("Gini of " + attribute + " = " + attrGini);
            System.out.println("Best Gini up to now is for " + maxAttribute + " = " + maxAttrGini);
        }


        /*
        done, return attribute of max discrimination power for the answer
        */
        return maxAttribute;
    }

    protected boolean checkForEndingOfNodeSplit(List<String> attributes, Dataset awDataset) throws IOException {
        /*
        if there are no more attributes to check, stop splitting
        */
        if(attributes.isEmpty()) {
            writerResults.writeMsg("Stopping: attributes list is empty!");
            return true;
        }
        /*
        if there is only one answer on data, stop splitting
        */
        awDataset.createOrReplaceTempView("awDataset");
        if(awDataset.groupBy("ANSWER").count().count() <= 1L) {
            writerResults.writeMsg("Only one (or none) answers on awDataset, stoping branch.");
            /*
            local debug
            */
            System.out.println("Only one (or none) answers on awDataset, stoping branch.");
            awDataset.groupBy("ANSWER").count().show();
            return true;
        }
        return false;
    }


    /**
     * @param args the command line arguments
     * @throws java.io.IOException
     */
    public static void main(String[] args) throws IOException {
        QASdecTree qaSdecTree = new QASdecTree();
    }
}
