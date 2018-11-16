/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package qasdectree;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Vector;
import org.apache.log4j.Level;
import org.apache.log4j.Logger;
import org.apache.spark.api.java.JavaPairRDD;
import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.function.PairFunction;
import org.apache.spark.sql.Dataset;
 import org.apache.spark.sql.Encoders;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.RowFactory;
import org.apache.spark.sql.SparkSession;
import scala.Tuple2;

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
        training.printSchema();
        // get an array with headers
        String[] headers = training.columns();
        // to get a list of data columns (words)
        List<String> words = new ArrayList<>();
        JavaPairRDD<String, Vector> messages = training.toJavaRDD().
                mapToPair((Row row) -> new Tuple2<String, Vector>((String) 
                        row.get(0), (Vector) row.get(3)));
        
        /*
            JavaPairRDD<Long, Vector> jpRDD = dataFrame.toJavaRDD().mapToPair(new PairFunction<Row, Long, Vector>() {
                public Tuple2<Long, Vector> call(Row row) throws Exception {
                    return new Tuple2<Long, Vector>((Long) row.get(0), (Vector) row.get(3));
                }
            });
JavaRDD<String> airportsNameAndCityNames = airportsInUSA.map(line -> {
                    String[] splits = line.split(Utils.COMMA_DELIMITER);
                    return StringUtils.join(new String[]{splits[1], splits[6]}, ",");
                }
        );
        */
        
        
        words.addAll(Arrays.asList(headers));
        // and remove first column, that is Answer
        words.remove(0);
        int windex = 0;
        System.out.println("Showing column names");
        for(String word : words) {
            System.out.println(String.format("|Index %4d |%s|", windex, word));
            windex++;
        }
        String res = training.reduce((a, b) -> RowFactory.create(a.toString().concat(b.toString()))).mkString();
        System.out.println("Reduced result: " + res);
    }

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        SandBox sandBox = new SandBox();
    }
}
