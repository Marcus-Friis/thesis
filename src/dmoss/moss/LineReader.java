/*----------------------------------------------------------------------
  File    : LineReader.java
  Contents: class for readers for line notation based table formats
            for graph data sets
  Author  : Christian Borgelt
  History : 2007.03.04 file created as TableFmt.java
            2007.06.26 split into reader and writer
            2016.04.07 StringBuffer replaced by StringBuilder
            2020.10.23 separated from pure table reader
----------------------------------------------------------------------*/
package moss;

import java.io.IOException;
import java.io.Reader;
import java.io.StringReader;
import java.io.FileReader;
import java.io.FileWriter;

/*--------------------------------------------------------------------*/
/** Class for readers for simple table formats for graph data sets.
 *  @author Christian Borgelt
 *  @since  2007.03.04 */
/*--------------------------------------------------------------------*/
public class LineReader extends GraphReader {

  /*------------------------------------------------------------------*/
  /*  instance variables                                              */
  /*------------------------------------------------------------------*/
  /** the fields of a record */
  private String[] record;
  /** whether there is a pushed back record */
  private boolean  pbrec;

  /*------------------------------------------------------------------*/
  /** Create a table reader with default character flags.
   *  <p>By default the following character settings are used:<br>
   *  record separators: "\n", field separators: " \t", blanks: " \r\t",
   *  comment characters: "#".</p>
   *  @param  reader the reader to work on
   *  @param  mode   the read mode
   *  @param  ntn    the notation of the graphs
   *  @since  2006.10.05 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public LineReader (Reader reader, int mode, Notation ntn)
  {                             /* --- create a table reader */
    super(reader, mode);        /* store the arguments */
    this.mode  &= ~DIRECTED;    /* and remove direction flag */
    this.ntn    = (ntn != null) ? ntn : new SMILES();
    this.record = new String[TableWriter.HEADER[this.mode].length];
    this.pbrec  = false;        /* create a record buffer */
  }  /* LineReader() */

  /*------------------------------------------------------------------*/
  /** Read the next record of the table.
   *  @return whether a record could be read
   *          (otherwise the end of the input has been reached)
   *  @throws IOException if an i/o error occurs
   *  @since  2007.06.26 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  private boolean readRecord () throws IOException
  {                             /* --- read a graph name/identifier */
    int i, n;                   /* loop variable, number of fields */

    if (this.readField() < 0)   /* read the first field and */
      return false;             /* check for end of input */
    n = this.record.length;     /* get the number of fields */
    for (i = 0; true; ) {       /* read the fields of the record */
      this.record[i] = this.field;
      if (++i >= n) break;      /* if all fields read, abort loop */
      if (this.delim != 0)      /* check for a field separator */
        throw new IOException("too few fields" +this.rno());
      this.readField();         /* read the next field */
    }
    if (this.delim != 1)        /* check for a record separator */
      throw new IOException("too many fields" +this.rno());
    return true;                /* return 'record successfully read' */
  }  /* readRecord() */

  /*------------------------------------------------------------------*/
  /** Read an (optional) table header.
   *  @return whether a header was present
   *          (otherwise the end of the input has been reached)
   *  @throws IOException if an i/o error occurs
   *  @since  2007.03.04 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public boolean readHeader () throws IOException
  {                             /* --- read an (optional) header */
    int      i;                 /* loop variable */
    String[] hdr;               /* buffer for the header fields */

    if (!this.readRecord())     /* try to read a record and */
      return false;             /* check for end of input */
    hdr = TableWriter.HEADER[this.mode];
    for (i = this.record.length; --i >= 0; )
      if (!this.record[i].equals(hdr[i])) break;
    this.pbrec = (i >= 0);      /* check the field names */
    return i < 0;               /* return whether a header was found */
  }  /* readHeader() */

  /*------------------------------------------------------------------*/
  /** Read the next graph description.
   *  <p>The next graph description is read and split into the graph
   *  name/identifier, the graph description, the associated value
   *  (only in mode <code>GRAPHS</code>), and the support information
   *  (only in mode <code>SUBS</code>).</p>
   *  These properties may then be retrieved with the functions
   *  <code>getName()<code>, <code>getDesc()</code>,
   *  <code>getValue()</code> etc.</p>
   *  @return whether a graph description could be read
   *          (otherwise the end of the input has been reached)
   *  @throws IOException if an i/o error occurs
   *  @since  2007.03.04 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public boolean readGraph () throws IOException
  {                             /* --- get the next graph description */
    String s = null;            /* buffer for a field */

    if (!this.pbrec             /* if there is no pushed back record */
    &&  !this.readRecord())     /* and no new record can be read, */
      return false;             /* the end of the input is reached */
    this.pbrec = false;         /* buffered record is now processed */
    this.graph = null;          /* clear the graph */
    try {                       /* try to get/parse the fields */
      this.name = this.record[0];  /* get the graph identifier */
      if (this.mode != SUBS) {  /* if graphs */
        this.value = Float.parseFloat(s = this.record[1]);
        this.desc  = this.record[2];
        this.nodes = this.edges = -1;
        this.srel  = this.crel  = 0.0F;
        this.sabs  = this.cabs  = 0; }
      else {                    /* if substructures */
        this.desc  = this.record[1];
        this.nodes = Integer.parseInt(s = this.record[2]);
        this.edges = Integer.parseInt(s = this.record[3]);
        this.sabs  = Integer.parseInt(s = this.record[4]);
        this.srel  = Float.parseFloat(s = this.record[5]);
        this.cabs  = Integer.parseInt(s = this.record[6]);
        this.crel  = Float.parseFloat(s = this.record[7]);
      } }                       /* get description and values */
    catch (NumberFormatException e) {
      throw new IOException("malformed number '"+s+"'"+this.rno(-1)); }
    return true;                /* return that a graph was read */
  }  /* readGraph() */

  /*------------------------------------------------------------------*/
  /** Get the current graph or substructure.
   *  @return the current graph
   *  @throws IOException if a parse error occurs
   *  @since  2007.03.04 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public Graph getGraph () throws IOException
  {                             /* --- get the current graph */
    if (this.graph != null)     /* if there is a graph, */
      return this.graph;        /* simply return it */
    if (this.desc == null)      /* if there is no description, */
      return null;              /* there is no graph to be had */
    StringReader srdr = new StringReader(this.desc);
    this.graph = this.ntn.parse(srdr);
    if ((ntn.getDelim() >= 0) || (srdr.read() >= 0))
      throw new IOException("garbage at end of graph description"
                            +this.rno(-1));
    srdr.close();               /* parse the graph description */
    return this.graph;          /* and return the parsed graph */
  }  /* getGraph() */

  /*------------------------------------------------------------------*/
  /** Main function for testing basic functionality.
   *  @param  args the command line arguments
   *  @since  2007.06.26 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public static void main (String[] args)
  {                             /* --- main function for testing */
    Notation   ntn;             /* notation for the graphs */
    LineReader reader;          /* reader for the input  file */
    LineWriter writer;          /* writer for the output file */

    if (args.length != 2) {     /* if wrong number of arguments */
      System.err.println("usage: java moss.LineReader <in> <out>");
      return;                   /* print a usage message */
    }                           /* and abort the program */

    try {                       /* try to read the file */
      ntn    = new SMILES();    /* with a SMILES notation */
      reader = new LineReader(new FileReader(args[0]), GRAPHS, ntn);
      writer = new LineWriter(new FileWriter(args[1]), GRAPHS, ntn);
      if (reader.readHeader())  /* create a reader and a writer */
        writer.writeHeader();   /* and copy a possible header */
      while (reader.readGraph()) {
        writer.setName(reader.getName());
        writer.setGraph(reader.getGraph());
        writer.setValue(reader.getValue());
        writer.writeGraph();    /* while there are more graphs, */
      }                         /* read and write graphs */
      reader.close(); writer.close(); }
    catch (IOException e) {     /* catch and report parse errors */
      System.err.println(e.getMessage()); }
  }  /* main() */

}  /* class LineReader */
