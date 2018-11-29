/*
List<Integer> data = Arrays.asList(1, 2, 3, 4, 5);
JavaRDD<Integer> distData = sc.parallelize(data);
 */
package qasdectree;

import java.util.Arrays;
import java.util.Iterator;
import org.apache.log4j.Level;
import org.apache.log4j.Logger;
import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.api.java.function.*;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Encoders;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;

/**
 *
 * @author duo
 */
public class SandBox2 {

    private final SparkSession spark;

    public SandBox2() {
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


        Dataset<Row> aw = spark.read().format("csv")
                .option("sep", ",")
                .option("inferSchema", "true")
                .option("header", "true")
                //.load("/extra2/mySpark/javaNetbeans/data/aw.csv");
                .load("/extra2/mySpark/javaNetbeans/data/miniaw.csv")
                ;
        int aa=10;
        // opera em uma coluna, aceita valores externos
        // posso usar em wa com a coluna da resposta escolhida, calculando o gini de todas
        // as palavras, para verificar qual o maior ...
        Dataset<Integer> damn = aw.select("" + 0).flatMap((FlatMapFunction<Row, Integer>) value -> {
            return Arrays.asList((value.getInt(0)<400 ? 0: value.getInt(0) * aa)).iterator();
                }, Encoders.INT());
        damn.show(20, true);
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
        spark.stop();
        System.exit(0);

        // converte uma única coluna para 0
        //Dataset<Integer> iaw = 
        //        aw.map((MapFunction<Row, Integer>) row -> row.<Integer>getAs("0"), 
        //                Encoders.INT());
        
        //iaw.show(20, true);

        //Dataset<Integer> nres = iaw.flatMap((FlatMapFunction<Integer, Integer>) value -> {
        //    return Arrays.asList(value * aa).iterator();
        //        }, Encoders.INT());
        //nres.show(20, true);

/*
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
*/

    }

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        SandBox2 sandBox2 = new SandBox2();
    }
}
