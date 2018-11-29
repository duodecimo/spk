/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package qasdectree;

import java.util.Arrays;
import org.apache.log4j.Level;
import org.apache.log4j.Logger;
import org.apache.spark.SparkConf;
import org.apache.spark.SparkContext;
import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;

/**
 *
 * @author duo
 */
public class RddAproach {

    private final SparkSession session;

    public RddAproach() {

        Logger.getLogger("org").setLevel(Level.ERROR);

        session = SparkSession.builder().appName("rddaproach")
                .master("local[3]").getOrCreate();
        SparkContext sc = session.sparkContext();
        JavaSparkContext jc = JavaSparkContext.fromSparkContext(sc);

        JavaRDD<String> teste = jc.textFile("/extra2/mySpark/javaNetbeans/data/teste.csv");
        teste.collect().forEach((line) -> {
            System.out.println("" + line);
        });
        /*
        Answer,alo,ola,ali,acola,fim
        1,1,0,0,1,0
        1,0,0,1,1,0
        1,1,0,0,0,1
        2,1,1,1,0,0
        2,0,1,0,0,1
        3,0,0,0,0,1
        3,0,1,1,0,1
        1,1,0,0,0,0
        */
        String head = teste.first();
        
    }

    public static void main(String[] args) {
        RddAproach rddAproach = new RddAproach();
    }
}
