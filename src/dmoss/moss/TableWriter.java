/*----------------------------------------------------------------------
  File    : TableWriter.java
  Contents: class for writers for table formats
  Author  : Christian Borgelt
  History : 2007.03.04 file created as TableFmt.java
            2007.06.26 split into reader and writer
            2020.10.23 split of from line notation based reader
----------------------------------------------------------------------*/
package moss;

import java.io.IOException;
import java.io.Writer;
import java.io.BufferedWriter;

/*--------------------------------------------------------------------*/
/** Class for writers for simple table formats for graph data sets.
 *  @author Christian Borgelt
 *  @since  2007.03.04 */
/*--------------------------------------------------------------------*/
public class TableWriter extends BufferedWriter {

  /*------------------------------------------------------------------*/
  /*  constants                                                       */
  /*------------------------------------------------------------------*/
  /** the field names for the different file types */
  protected static final String[][] HEADER = {
    { "id", "value", "description" },          /* GRAPHS */
    { "id", "description", "nodes", "edges",   /* SUBS */
      "s_abs", "s_rel", "c_abs", "c_rel" } };

  /*------------------------------------------------------------------*/
  /*  instance variables                                              */
  /*------------------------------------------------------------------*/
  /** the record separator */
  protected char recsep = '\n';
  /** the field separator */
  protected char fldsep = ',';

  /*------------------------------------------------------------------*/
  /** Create a simple table format writer.
   *  @param  writer the writer to write to
   *  @since  2007.03.04 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public TableWriter (Writer writer)
  { super(writer, 1024); }

  /*------------------------------------------------------------------*/
  /** Set the record and field separators.
   *  @param  recsep the record separator
   *  @param  fldsep the field  separator
   *  @since  2007.06.26 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void setChars (char recsep, char fldsep)
  { this.recsep = recsep; this.fldsep = fldsep; }

  /*------------------------------------------------------------------*/
  /** Write a field (string).
   *  @param  field the field to write
   *  @param  last  whether this is the last field in a record
   *  @since  2020.10.23 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void writeField (String field, boolean last)
      throws IOException
  { this.write(field +(last ? this.recsep : this.fldsep)); }

  /*------------------------------------------------------------------*/
  /** Write a field (int).
   *  @param  field the field to write
   *  @param  last  whether this is the last field in a record
   *  @since  2020.10.23 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void writeField (int field, boolean last) throws IOException
  { this.write("" +field +(last ? this.recsep : this.fldsep)); }

  /*------------------------------------------------------------------*/
  /** Write a field (double).
   *  @param  field the field to write
   *  @param  last  whether this is the last field in a record
   *  @since  2020.10.23 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void writeField (double field, boolean last) throws IOException
  { this.write("" +field +(last ? this.recsep : this.fldsep)); }

}  /* class TableWriter */
