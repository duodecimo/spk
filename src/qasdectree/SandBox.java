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
 */
public class SandBox {
    private final SparkSession session;
    private final Dataset<Row> training;

    public SandBox() {
        Logger.getLogger("org").setLevel(Level.ERROR);
        session = SparkSession.builder().appName("QASdecTree")
                .master("local[3]").getOrCreate();

        training = session.read().option("header", "true")
                .csv("/extra2/mySpark/javaNetbeans/data/teste.csv");
        training.show();
        // get an array with headers
        String[] headers = training.columns();
        // to get a list of data columns (words)
        List<String> words = new ArrayList<>();
        words.addAll(Arrays.asList(headers));
        // and remove first column, that is Answer
        words.remove(0);
        int windex = 0;
        System.out.println("Showing column names");
        for(String word : words) {
            System.out.println(String.format("|Index %4d |%s|", windex, word));
            windex++;
        }
    }

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        SandBox sandBox = new SandBox();
    }
}
