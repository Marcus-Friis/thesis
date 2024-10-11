/*----------------------------------------------------------------------
  File    : LineWriter.java
  Contents: class for writers for line notation based table formats
            for graph data sets
  Author  : Christian Borgelt
  History : 2007.03.04 file created as TableFmt.java
            2007.06.26 split into reader and writer
            2020.10.23 split of from line notation based reader
----------------------------------------------------------------------*/
package moss;

import java.io.IOException;
import java.io.Writer;

/*--------------------------------------------------------------------*/
/** Class for writers for simple table formats for graph data sets.
 *  @author Christian Borgelt
 *  @since  2007.03.04 */
/*--------------------------------------------------------------------*/
public class LineWriter extends GraphWriter {

  /*------------------------------------------------------------------*/
  /*  constants                                                       */
  /*------------------------------------------------------------------*/
  /** the field names for the different file types */
  protected static final String[][] HEADER = {
    { "id", "value", "description" },          /* GRAPHS */
    { "id", "description", "nodes", "edges",   /* SUBS */
      "s_abs", "s_rel", "c_abs", "c_rel" } };

  /*------------------------------------------------------------------*/
  /** Create a simple table format writer.
   *  @param  writer the writer to write to
   *  @param  mode   the write mode
   *  @param  ntn    the notation for the graph descriptions
   *  @since  2007.03.04 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public LineWriter (Writer writer, int mode, Notation ntn)
  {                             /* --- create a table writer */
    super(writer, mode);        /* store the arguments */
    this.ntn = (ntn != null) ? ntn : new SMILES();
  }  /* LineWriter() */

  /*------------------------------------------------------------------*/
  /** Write a header.
   *  @throws IOException if an i/o error occurs
   *  @since  2007.03.04 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void writeHeader () throws IOException
  {                             /* --- write a table header */
    String[] hdr = HEADER[this.mode];
    for (int i = 0; i < hdr.length; i++) {
      if (i > 0) this.write(this.fldsep);
      this.write(hdr[i]);       /* write the field names */
    }                           /* separated by field separators */
    this.write(this.recsep);    /* terminate the record */
  }  /* writeHeader() */

  /*------------------------------------------------------------------*/
  /** Write a description of the current graph.
   *  @throws IOException if an i/o error occurs
   *  @since  2007.02.24 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void writeGraph () throws IOException
  {                             /* --- write a graph description */
    this.write(this.name);      /* write the graph name */
    if (this.mode != SUBS)      /* write the associated value */
      this.write("" +this.fldsep +this.value);
    this.write(this.fldsep);    /* write the graph description */
    this.ntn.write(this.graph, this);
    if (this.mode == SUBS) {    /* if substructures */
      this.write("" +this.fldsep +this.nodes);
      this.write("" +this.fldsep +this.edges);
      this.write("" +this.fldsep +this.sabs);
      this.write("" +this.fldsep +this.srel);
      this.write("" +this.fldsep +this.cabs);
      this.write("" +this.fldsep +this.crel);
    }                           /* write the support values */
    this.write(this.recsep);    /* terminate the record */
  }  /* writeGraph() */

}  /* class LineWriter */
