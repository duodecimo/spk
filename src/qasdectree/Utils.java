/*
 For the case of a variable with two values, appearing with fractions f and (1-f), 
the gini and entropy are given by: 
gini = 2*f(1-f) 
entropy = f*ln(1/f) + (1-f)*ln(1/(1-f)) 
Gini:Gini(E)= 1−(∑ from j=1 to c) p**2j

Lets assume we have 3 classes and 80 objects. 
19 objects are in class 1, 21 objects in class 2, 
and 40 objects in class 3 (denoted as (19,21,40) ).
The Gini index would be: 
1- [ (19/80)^2 + (21/80)^2 + (40/80)^2] = 0.6247 
i.e. costbefore = Gini(19,21,40) = 0.6247

calcular gini_t de todas as mensagens, com todas as palavras
calcular gini_mi das mensagens de cada palavra
O ganho de cada mi vai ser gini_t - #mi/t * gini_mi
Selecione a palavra com maior ganho

 */
package qasdectree;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;

/**
 *
 * @author duo
 */
public class Utils {
    public static int bestWord(Dataset dataset) {
        String[] words = getHeaders(dataset);
        String sqlTxt;
        int v;
        Map<Integer, Integer> messages = new HashMap<>();
        float gini, bestGini = 0.0F, totGini =0.0F, sums;
        String bestW;
        for(int i=0; i<words.length; i++) {
            messages = new HashMap<>();
            sqlTxt = "select MsgId from dataset where " + words[i] + " = 1";
            Dataset msgw = dataset.sqlContext().sql(sqlTxt);
            List<Row> list = msgw.sqlContext().sql(sqlTxt).collectAsList();
            List<Integer> longs = list.stream().map(row -> row.getInt(0)).collect(Collectors.toList());
            if(messages.containsKey(longs.get(i))) {
                v = messages.get(longs.get(i));
            } else {
                v = 0;
            }
            messages.put(longs.get(i), v+1);
        }
        // calculo do gini total
        sums = 0.0F;
        for(int i=0; i<messages.size(); i++) {
            sums+=(messages.get(i)/messages.size())*(messages.get(i)/messages.size());
        }
        totGini = 1 - sums;
        // procura pelo melhor gini
        return 0;
    }

    public static String[] getHeaders(Dataset dataset) {
        return dataset.schema().fieldNames();
    }
}
