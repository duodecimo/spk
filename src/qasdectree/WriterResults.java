/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package qasdectree;

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
public class WriterResults {
    BufferedWriter writer;
    File logFile;

    public WriterResults() throws IOException {
        this(new SimpleDateFormat("yyyyMMdd_HHmmss").format(Calendar.getInstance().getTime()).concat(".txt"));
    }

    public WriterResults(String fileName) throws IOException {
        logFile = new File(fileName);
        writer = new BufferedWriter(new FileWriter(logFile));
        // This will output the full path where the file will be written to...
        System.out.println("logFile path: " + logFile.getCanonicalPath());
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
