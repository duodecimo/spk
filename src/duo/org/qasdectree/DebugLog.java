package duo.org.qasdectree;
/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Calendar;

/**
 *
 * @author duo
 */
public class DebugLog {
    BufferedWriter writer;
    File logFile;

    public DebugLog() throws IOException {
        this("/extra2/mySpark/javaNetbeans/data/log".concat(new SimpleDateFormat("yyyyMMdd_HHmmss")
                .format(Calendar.getInstance().getTime())).concat(".txt"));
    }

    public DebugLog(String fileName) throws IOException {
        logFile = new File(fileName);
        writer = new BufferedWriter(new FileWriter(logFile));
    }

    public void writeMsg(String msg) throws IOException {
        this.writer.write(msg + "\n");
        this.writer.flush();
    }

    @Override
    protected void finalize() throws Throwable {
        super.finalize();
        writer.close();
    }

}