/*----------------------------------------------------------------------
  File    : SDfileReader.java
  Contents: class for readers for SDfiles (Structure-Data files)
  Author  : Christian Borgelt
  History : 2007.02.24 file created as SDfileFmt.java
            2007.06.26 split into reader and writer
            2016.04.07 StringBuffer replaced by StringBuilder
            2017.10.17 added constructor with notation argument
----------------------------------------------------------------------*/
package moss;

import java.io.IOException;
import java.io.Reader;
import java.io.FileReader;
import java.io.FileWriter;

/*--------------------------------------------------------------------*/
/** Class for readers for structure-data files (SDfile, Elsevier MDL).
 *  @author Christian Borgelt
 *  @since  2007.02.24 */
/*--------------------------------------------------------------------*/
public class SDfileReader extends GraphReader {

  /*------------------------------------------------------------------*/
  /*  instance variables                                              */
  /*------------------------------------------------------------------*/
  /** the notation for line descriptions */
  private Notation      smiles;
  /** the buffer for an input line */
  private StringBuilder buf;

  /*------------------------------------------------------------------*/
  /** Create a reader for SDfiles.
   *  @param  reader the reader to read from
   *  @param  mode   the read mode
   *  @param  ntn    the notation to use
   *  @since  2007.03.04 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public SDfileReader (Reader reader, int mode, Ctab ntn)
  {                             /* --- create an SDfile reader */
    super(reader, mode);        /* store the arguments */
    this.mode  &= ~DIRECTED;    /* and remove direction flag */
    this.ntn    = ntn;          /* create notation and read buffer */
    this.buf    = new StringBuilder();
    this.smiles = null;         /* clear the line notation */
  }  /* SDfileReader() */

  /*------------------------------------------------------------------*/
  /** Create a reader for SDfiles.
   *  @param  reader the reader to read from
   *  @param  mode   the read mode
   *  @since  2007.03.04 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public SDfileReader (Reader reader, int mode)
  { this(reader, mode, new Ctab()); }

  /*------------------------------------------------------------------*/
  /** Read the next input line.
   *  @return the next input line or <code>null</code>
   *          if the end of the input stream has been reached
   *  @throws IOException if an i/o error occurs
   *  @since  2007.02.24 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  protected String readLine () throws IOException
  {                             /* --- read the next input line */
    int c = this.read();        /* read the next character */
    if (c < 0) return null;     /* and check for end of input */
    this.buf.setLength(0);      /* clear the read buffer for a line */
    while ((c >= 0) && (c != '\n')) {
      this.buf.append((char)c); /* append current character */
      c = this.read();          /* to the read buffer and */
    }                           /* read the next character */
    return this.buf.toString(); /* return the input line read */
  }  /* readLine() */

  /*------------------------------------------------------------------*/
  /** Read an (optional) header.
   *  <p>This function always returns <code>false</code> and reads
   *  nothing, since headers are not supported with SDfiles.</p>
   *  @return <code>false</code>, since SDfile do not have a header
   *  @throws IOException if an i/o error occurs
   *  @since  2007.03.04 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public boolean readHeader () throws IOException
  { return false; }

  /*------------------------------------------------------------------*/
  /** Get the next graph description.
   *  <p>The next graph description is read and split into the graph
   *  name, the associated value and the actual graph description.</p>
   *  These individual parts may then be retrieved with the functions
   *  <code>getName()<code>, <code>getValue()</code> and
   *  <code>getDesc()</code>.</p>
   *  @return whether a graph description could be read
   *          (otherwise the end of the input has been reached)
   *  @throws IOException if an i/o error or a parse error occurs
   *  @since  2007.03.02 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public boolean readGraph () throws IOException
  {                             /* --- get the next graph description */
    int    i, k;                /* indices in input line */
    String line, s = null;      /* buffer for an input line/a field */

    this.desc  = null;          /* clear the line description */
    this.name  = this.readLine();
    if (this.name == null) return false;
    if (this.readLine() == null)
      throw new IOException("missing information line");
    if (this.readLine() == null)
      throw new IOException("missing comments line");
    this.graph = this.ntn.parse(this);
    this.nodes = this.graph.getNodeCount();
    this.edges = this.graph.getEdgeCount();
    this.srel  = this.crel = this.value = 0.0F;
    this.sabs  = this.cabs = 0; /* clear the additional information */
    try {                       /* read to the data items and */
      while (true) {            /* extract the relevant values */
        line = this.readLine(); /* read the next line */
        if (line == null)       /* check for end of molecule block */
          throw new IOException("missing end line '$$$$'");
        if (line.startsWith("$$$$")) break;
        if (!line.startsWith(">")) continue;
        i = line.indexOf('<');  /* get the start of the field name */
        if (i < 0) continue;    /* skip lines without a field name */
        k = line.indexOf('>', i+1);
        if (k < 0) continue;    /* get the end of the field name */
        line = line.substring(i+1, k); /* extract the field name */
        if (line.equalsIgnoreCase("value")) {
          if (this.mode == SUBS) continue;
          line = this.readLine();
          if (line == null)     /* get the graph value (activity) */
            throw new IOException("missing graph value");
          this.value = Float.parseFloat(s = line.trim()); }
        else if (line.equalsIgnoreCase("support")) {
          if (this.mode != SUBS) continue;
          line = this.readLine();
          if (line == null)     /* get the support in the focus */
            throw new IOException("missing support");
          i = line.indexOf(' ');/* split into absolute */
          if (i < 0)            /* and relative support */
            throw new IOException("bad support '" +line +"'");
          s = line.substring(0,i).trim();
          this.sabs = Integer.parseInt(s);
          s = line.substring(i+1).trim();
          this.srel = Float.parseFloat(s);
          line = this.readLine();
          if (line == null)     /* get the support in the complement */
            throw new IOException("missing support");
          i = line.indexOf(' ');/* split into absolute */
          if (i < 0)            /* and relative support */
            throw new IOException("bad support '" +line +"'");
          s = line.substring(0,i).trim();
          this.cabs = Integer.parseInt(s);
          s = line.substring(i+1).trim();
          this.crel = Float.parseFloat(s);
        }                       /* store the parse support values */
        line = this.readLine(); /* check for a blank line at the end */
        if (line == null) throw new IOException("missing blank line");
      } }
    catch (NumberFormatException e) {
      throw new IOException("malformed number '" +s +"'"); }
    return true;                /* return that a graph was read */
  }  /* readGraph() */

  /*------------------------------------------------------------------*/
  /** Get a (line) description of the current graph.
   *  <p>Since a connection table is not a line description,
   *  it is reformatted into the SMILES format.</p>
   *  @return a line description (SMILES) of the current graph
   *  @since  2007.03.04 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public String getDesc ()
  {                             /* --- get a (line) description */
    if (this.desc == null) {    /* if there is no description */
      if (this.graph == null) return null;
      if (this.smiles == null)  /* create a line notation */
        this.smiles = new SMILES();
      this.desc = this.smiles.describe(this.graph);
    }                           /* create a description if possible */
    return this.desc;           /* return the description */
  }  /* getDesc() */

  /*------------------------------------------------------------------*/
  /** Main function for testing basic functionality.
   *  @param  args the command line arguments
   *  @since  2007.06.26 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public static void main (String[] args)
  {                             /* --- main function for testing */
    SDfileReader reader;        /* reader for the input  file */
    SDfileWriter writer;        /* writer for the output file */

    if (args.length != 2) {     /* if wrong number of arguments */
      System.err.println("usage: java moss.SDfileReader <in> <out>");
      return;                   /* print a usage message */
    }                           /* and abort the program */

    try {                       /* try to read an SDfile */
      reader = new SDfileReader(new FileReader(args[0]), GRAPHS);
      writer = new SDfileWriter(new FileWriter(args[1]), GRAPHS);
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

}  /* class SDfileReader */
