/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package qasdectree;

import java.util.ArrayList;
import java.util.List;
import org.apache.log4j.Level;
import org.apache.log4j.Logger;
import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.RowFactory;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.sql.types.StructType;

/**
 *
 * @author duo
 */
public class OtherSandBox {

    private final SparkSession spark;

    public OtherSandBox() {
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

        this.spark = SparkSession.builder().appName("CsvSandbox").master("local[4]").getOrCreate();
        JavaSparkContext jsc = new JavaSparkContext(spark.sparkContext());
        List<Row> list = new ArrayList<>();
        list.add(RowFactory.create("one"));
        list.add(RowFactory.create("two"));
        list.add(RowFactory.create("three"));
        list.add(RowFactory.create("four"));
        List<org.apache.spark.sql.types.StructField> listOfStructField = new ArrayList<>();
        listOfStructField.add(DataTypes.createStructField("test", DataTypes.StringType, true));
        StructType structType = DataTypes.createStructType(listOfStructField);
        Dataset<Row> data = spark.createDataFrame(list, structType);
        data.show();
        List<Row> nums = new ArrayList<>();
        nums.add(RowFactory.create(1));
        nums.add(RowFactory.create(2));
        nums.add(RowFactory.create(3));
        nums.add(RowFactory.create(4));
        listOfStructField = new ArrayList<>();
        listOfStructField.add(DataTypes.createStructField("values", DataTypes.IntegerType, true));
        structType = DataTypes.createStructType(listOfStructField);
        Dataset<Row> numdata = spark.createDataFrame(nums, structType);
        numdata.show();
        list = new ArrayList<>();
        list.add(RowFactory.create("one", 1));
        list.add(RowFactory.create("two", 2));
        list.add(RowFactory.create("three", 3));
        list.add(RowFactory.create("four", 4));
        listOfStructField = new ArrayList<>();
        listOfStructField.add(DataTypes.createStructField("test", DataTypes.StringType, true));
        listOfStructField.add(DataTypes.createStructField("values", DataTypes.IntegerType, true));
        structType = DataTypes.createStructType(listOfStructField);
        Dataset<Row> sdata = spark.createDataFrame(list, structType);
        sdata.show();
        sdata.groupBy("test").pivot("values").min("values").show();
    }

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        OtherSandBox otherSandBox = new OtherSandBox();
    }
}
