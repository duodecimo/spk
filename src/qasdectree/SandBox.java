/*
List<Integer> data = Arrays.asList(1, 2, 3, 4, 5);
JavaRDD<Integer> distData = sc.parallelize(data);
 */
package qasdectree;

import java.util.Arrays;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.apache.log4j.Level;
import org.apache.log4j.Logger;
import org.apache.spark.api.java.JavaPairRDD;
import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.api.java.function.*;
import org.apache.spark.sql.SparkSession;
import scala.Tuple2;

/**
 *
 * @author duo
 */
public class SandBox {

    private final SparkSession spark;

    public SandBox() {
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
        this.spark = SparkSession.builder().appName("CsvSandbox").master("local[4]").getOrCreate();
        JavaSparkContext jsc = new JavaSparkContext(spark.sparkContext());
        List<Integer> data = Arrays.asList(1, 2, 3, 4, 5);
        JavaRDD<Integer> distData = jsc.parallelize(data);
        System.out.println("Soma: " + distData.reduce((a, b) -> a + b));

        JavaRDD<String> lines = jsc.textFile("drummond.txt");

        JavaRDD<String> words;
        words = lines.flatMap((String s) -> Arrays.asList(s.trim().split(" ")).iterator());

        JavaPairRDD<String, Integer> ones;
        ones = words.mapToPair((String s) -> new Tuple2(s, 1));
        JavaPairRDD<String, Integer> counts;
        counts = ones.reduceByKey((Integer i1, Integer i2) -> i1 + i2);
        Map m = counts.collectAsMap();
        int sum = 0;
        Set ks = m.keySet();
        Iterator ik = ks.iterator();
        String key;
        String sValue;
        while(ik.hasNext()) {
            key = ik.next().toString();
            //if (!key.isEmpty()) {
                sValue = m.get(key).toString();
                System.out.println("map: " + key + " - "
                        + sValue);
                sum += new Integer(sValue);
            //}
        }
        System.out.println("Counting drummond words: " + sum);
    }

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        SandBox sandBox = new SandBox();
    }
}
