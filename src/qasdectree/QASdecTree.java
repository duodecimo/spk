/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package qasdectree;

import java.io.IOException;
import static java.lang.Math.pow;
import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.log4j.Level;
import org.apache.log4j.Logger;

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
    private final Dataset<Row> dataset;
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
        /*
        obs: the original csv had spaces in the header starting from the second column.
        Some answers has accents, and non letter or digits or _ chars too.
        I coded a pair of python programs (for the convenience of python csv classes)
        to fix it (see javaNetbeans/data csvAdjust.py and csvAdjust2.py)
        */

        /*
         * read csv into Dataset object to use on spark and benefit from distribution.
         */
        dataset = spark.read().format("csv")
                .option("sep", ",")
                .option("inferSchema", "true")
                .option("header", "true")
                //.load("/extra2/mySpark/javaNetbeans/data/trainingCor.csv");
                .load("/extra2/mySpark/javaNetbeans/data/miniTrainingCor.csv");
        /*
        Com trainingCor, começando em:
         */

        /*
        turn into temporary view to apply sql
        */
        //dataset.createOrReplaceGlobalTempView("dataset");
        dataset.createOrReplaceTempView("dataset");
        long countingAnsw = dataset.groupBy("ANSWER").count().count();
        //long countingAnsw = spark.sql("select count() from dataset group by ANSWER").count();
        writerResults.writeMsg("--- timestamp: " + new Timestamp(System.currentTimeMillis()));
        writerResults.writeMsg("Counting answers on dataset: " + countingAnsw);
        /*
        local debug
        */
        dataset.groupBy("ANSWER").count().show();
        System.out.println("Counting answers on dataset: " + countingAnsw);
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
        attributes = new ArrayList<>(Arrays.asList(dataset.schema().fieldNames()));
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
        buildTree(decisionTree, attributes, dataset, " 1");
    }
    
    private void buildTree(Node node, List<String> attributes, Dataset dataset, String alias) throws IOException {
        dataset.createOrReplaceTempView("dataset");
        treeNodes++;
        node.setAttribute(chooseNodeBestAttribute(attributes, dataset));
        writerResults.writeMsg("Node " + alias + ": " + node.getAttribute());
        writerResults.writeMsg("--- timestamp: " + new Timestamp(System.currentTimeMillis()));
        /*
        remove the attribute from attributs list
        */
        attributes.remove(node.getAttribute());

        /*
        System.out.println("\n\n===============================================\n\n");
        System.out.println("Mostrando o completo: ");
        dataset.show(10);
        writerResults.writeMsg("dataset show: " + 
                dataset.sqlContext().sql("select ANSWER, " + 
                        node.getAttribute() + " from dataset").showString(10, 20, true));
        System.out.println("\n\n===============================================\n\n");
        */

        /*
        grow for left recursively
        */
        Dataset<Row> leftDataset = dataset.filter("" + node.getAttribute() + " = 1");
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
        Dataset<Row> rightDataset = dataset.filter("" + node.getAttribute() + " = 0");
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
     * calculate gini of dataset
     * 
     * T = total messages
     * C = total messages with Answer ci
     * CP = C/T
     * A = T - C (total other than C messages)
     * AP = A/T
     * datasetGini = 1 - ((CP*CP + AP*AP))
     * 
     * calculate impact of each word (w1, w2, ..., wn) on the
     * dataset with answer cj
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
     * dpi = datasetGini - (wiGini * (C/A))
     * 
     * done, return max dpi
     *  - use wi (with max dpi) as tree node
     *  - remove wi from list of words
     *  - send data with answer cj to the left
     *  - send data with answer not cj to the right
     * 
     * @param attributes
     * @param dataset
     * @return
     * @throws IOException 
     *      */
    protected String chooseNodeBestAttribute(List<String> attributes, Dataset dataset) throws IOException {
        dataset.createOrReplaceTempView("dataset");
        long totalAttributes = attributes.size();
        long visitedAttributes = 0;
        /*
        Answers are c1, c2, ..., c3.
        Obs.: If the node has only one answer, thats it!
        
        Let's derive tree spliting node on the first answer, then, next division for 2nd, and so on.
        pick first answer on node dataset.
        */
        int answer = dataset.groupBy("ANSWER").count().select("ANSWER").first().getInt(0);
        if (debug) {
            writerResults.writeMsg("Choosing best attribute. Picked answer: " + answer);
        }
        System.out.println("Choosing best attribute. Picked answer: " + answer);
        /*
        calculate gini of dataset:
        T = total messages
        C = total messages with Answer ci
        CP = C/T
        A = T - C (total other than C messages)
        AP = A/T
        datasetGini = 1 - ((CP*CP + AP*AP))
        */
        double totalAnswers = (double) dataset.count();
        double msgWithAnswer = (double) dataset.groupBy("ANSWER").count().select("count").first().getLong(0);
        double pMsgWithAnswer = msgWithAnswer / totalAnswers;
        double pMsgWithoutAnswer = (totalAnswers - msgWithAnswer) / totalAnswers;
        double datasetGini = 1.0D - (pow(pMsgWithAnswer, 2) + pow(pMsgWithoutAnswer, 2));
        System.out.println("Total answers: " + totalAnswers +
                " messages with answer " + answer + ": " + msgWithAnswer);
        System.out.println("Datset Gini = " + datasetGini);
        /*
        calculate impact of each word (w1, w2, ..., wn) on the
        dataset with answer cj.
        so, dataset can be reduced to lines with answer cj.
        */
        Dataset<Row> reducedToAnswer = dataset.filter("Answer = " + answer);
        System.out.println("Reduced to Answer " + answer +
                " size: " + reducedToAnswer.count());

        /*
        
        C = total messages with Answer cj and word wi
        A = total messages with Answer not cj but with word wi
        T = C+A
        CP = C/T
        AP = A/T
        wiGini = 1 - ((CP*CP) + (AP*AP))
        
        (Here I think it's better do not use the gini of absence of wi).
        
        calculate discrimination power of each wi on cj
        dpi = datasetGini - (wiGini * (C/A))
        done, return max dpi
        */

        spark.stop();
        System.exit(0);


        long[] sumArray  = dataset.groupBy("ANSWER").count().select("count").collectAsList()
                .stream().mapToLong(row -> row.getLong(0)).toArray();
        double sum = 0.0F;
        for(long value: sumArray) {
            if (totalAnswers!=0) {
                sum += pow((double) value / (double) totalAnswers, 2);
            }
        }
        if (debug) {
            writerResults.writeMsg("Dataset Gini = " + datasetGini);
        }
        /*
        now calculate gini for each attribute selecting the greater.
        attributes are binary, so their classes = {0,1}
        */
        String bestAttribute = null;
        double maxAttributeGini = 0.0D;
        long maxAttributeTotalOnes = 0L;
        long totAggZeroes, totAggOnes;
        double sumZeroes, sumOnes;
        double attrGini;
        for (String attribute : attributes) {
            if(attribute.equals("ANSWER")) {
                /*
                ANSWER is target attribute, and not binary btw
                */
                continue;
            }
            /*
            first for class value = 0
            */
            long totalZeroes = dataset.filter("" + attribute + " = 0").count();
            /*
            now aggregate for each answer
            */
            int[] aggZeroes = 
                    dataset.filter("" + attribute + " = 0").groupBy("ANSWER").count().collectAsList()
                            .stream().mapToInt(row -> row.getInt(0)).toArray();
            totAggZeroes = 0;
            sumZeroes = 0.0D;
            for(long value : aggZeroes) {
                totAggZeroes += value;
            }
            for(long value : aggZeroes) {
                if (totAggZeroes!=0) {
                    sumZeroes += pow((double) value / (double) totAggZeroes, 2);
                }
            }
            /*
            now for class value = 1
            */
            long totalOnes = dataset.filter("" + attribute + " = 1").count();
            /*
            now aggregate for each answer
            */
            
            /*
            Doubt: should I use attribute + " >= 1" or attribute + " = 1" on the folowing query?
            or should I use distinct instead of group by?
            because it seems some answers are duplicated among the rows ...
            anyway, for now I'm going with >=1, because if the result can be only 1, it will do no harm.
            */
            int[] aggOnes = 
                    dataset.filter("" + attribute + " >= 1").groupBy("ANSWER").count().collectAsList()
                            .stream().mapToInt(row -> row.getInt(0)).toArray();
            totAggOnes = 0;
            sumOnes = 0.0D;
            for(long value : aggOnes) {
                totAggOnes += value;
            }
            for(long value : aggOnes) {
                if (totAggOnes!=0) {
                    sumOnes += pow((double) value / (double) totAggOnes, 2);
                }
            }
            long totalZerosAndOnes;
            totalZerosAndOnes = totalZeroes+totalOnes;
            attrGini = datasetGini;
            if(totalZerosAndOnes!=0) {
                double ginVarZeros = (double) totalZeroes/((double) totalZeroes+totalOnes)*sumZeroes;
                double ginVarOnes = (double) totalOnes/((double) totalZeroes+totalOnes)*sumOnes;
                double ginVar =  ginVarZeros + ginVarOnes;
                attrGini -=  ginVar;
            } else {
                if (debug) {
                    writerResults.writeMsg("   >>> WARNING: totalZerosAndOnes is zero!!!!!!!");
                }
            }
            // if (debug) {
                writerResults.writeMsg("Gini for " + attribute + " = " + attrGini + 
                        " total ones = " + totalOnes);
            //}
            /*
            keep the greater attribute gini
            */
            if(attrGini > maxAttributeGini) {
                bestAttribute = attribute;
                maxAttributeGini = attrGini;
                maxAttributeTotalOnes = totalOnes;
            }
            //if (debug) {
                writerResults.writeMsg("Best attribute up to now is " + bestAttribute
                        + " with gini = " + maxAttributeGini + " with total ones " + maxAttributeTotalOnes);
            //}
            visitedAttributes++;
            //if (debug) {
                writerResults.writeMsg("attributes: " + visitedAttributes + " of " + totalAttributes);
                writerResults.writeMsg("nodes on tree: " + treeNodes);
                writerResults.writeMsg("--- timestamp: " + new Timestamp(System.currentTimeMillis()));
            //}
        }
        return bestAttribute;
    }

    protected boolean checkForEndingOfNodeSplit(List<String> attributes, Dataset dataset) throws IOException {
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
        dataset.createOrReplaceTempView("dataset");
        if(dataset.groupBy("ANSWER").count().count() <= 1L) {
            writerResults.writeMsg("Only one (or none) answers on dataset, stoping branch.");
            /*
            local debug
            */
            System.out.println("Only one (or none) answers on dataset, stoping branch.");
            dataset.groupBy("ANSWER").count().show();
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
