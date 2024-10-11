/*----------------------------------------------------------------------
  File    : Predictor.java
  Contents: Predict graph edges with graph association rules
  Author  : Christian Borgelt
  History : 2020.10.09 file created
            2020.10.19 started to program main functions
            2020.10.25 reading patterns, rules and graphs completed
            2020.10.31 prediction function completed
            2020.11.15 various parameters for edge predictions added
            2020.11.17 bug in storing predicted edges fixed
            2021.10.17 (optional) handling edge direction added
----------------------------------------------------------------------*/
package moss;

import java.util.Arrays;
import java.util.Comparator;
import java.util.HashMap;
import java.io.IOException;
import java.io.Reader;
import java.io.FileReader;
import java.io.Writer;
import java.io.FileWriter;
import java.io.PrintStream;

/*--------------------------------------------------------------------*/
/** Class for managing graph rules (for edge prediction).
 *  <p>A graph rule is a list element that indicates (via indices) the
 *  antecedent pattern and the full pattern underlying a graph rule,
 *  the type of the consequent edge (and possibly consequent node),
 *  the support of the antecedent and the full pattern, and the
 *  confidence of the graph rule.</p>
 *  <p>The <code>GraphRule</code> class extends the
 *  <code>Sortable</code> class, which provides sorting functionality
 *  for singly linked lists.</p>
 *  @author Christian Borgelt
 *  @since  2020.10.23 */
/*--------------------------------------------------------------------*/
class GraphRule {

  /*------------------------------------------------------------------*/
  /*  instance variables                                              */
  /*------------------------------------------------------------------*/
  /** the graph pattern of the body/antecedent */
  protected NamedGraph part;
  /** the graph pattern of the full pattern (body+head) */
  protected NamedGraph full;
  /** the index of the consequent edge */
  protected int        edge;
  /** the index of the source      node (reflecting edge direction) */
  protected int        src;
  /** the index of the destination node (reflecting edge direction) */
  protected int        dst;
  /** the index of new node in full pattern (if not in antecedent) */
  protected int        node;
  /** the base support (largest possible support) */
  protected int        base;
  /** the support of the body/antecedent */
  protected int        body;
  /** the support of the full pattern (body+head) */
  protected int        supp;
  /** the support of the head/consequent (version 1) */
  protected int        head1;
  /** the support of the head/consequent (version 2) */
  protected int        head2;
  /** the confidence of the graph rule */
  protected double     conf;
  /** the lift value of the graph rule (version 1) */
  protected double     lift1;
  /** the lift value of the graph rule (version 2) */
  protected double     lift2;
  /** the successor in the graph rule list */
  protected GraphRule  succ;

  /*------------------------------------------------------------------*/
  /** Create a graph rule.
   *  @param  frag the fragment to store
   *  @since  2020.10.23 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  protected GraphRule (NamedGraph part, NamedGraph full,
                       int src, int dst, int edge, int node,
                       int base, int body, int supp,
                       int head1, int head2)
  {                             /* --- create a graph pattern */
    this.part  = part;  this.full  = full;
    this.src   = src;   this.dst   = dst;
    this.edge  = edge;  this.node  = node;
    this.body  = body;  this.supp  = supp;
    this.head1 = head1; this.head2 = head2;
    this.conf  = supp /(double)body;
    this.lift1 = this.conf /(head1 /(double)base);
    this.lift2 = this.conf /(head2 /(double)base);
    this.succ  = null;
  }  /* GraphRule() */

}  /* class GraphRule */


/*--------------------------------------------------------------------*/
/** Class for managing predicted edges (for rule application).
 *  <p>A predicted edge contains information about which edge, specified
 *  by the index of its source and destination node and its edge type
 *  or label is predicted to be in a certain graph. If the edge leads to
 *  a node that may not yet be in the graph, the destination index is 0,
 *  otherwise it is, like the source index, a positive integer. In case
 *  the destination index is zero (and hence the node potentially new),
 *  the type or label of this node is stored as well.</p>
 *  <p>The <code>PredEdge</code> class extends the <code>Sortable</code>
 *  class, which provides sorting functionality for singly linked
 *  lists.</p>
 *  @author Christian Borgelt
 *  @since  2020.10.26 */
/*--------------------------------------------------------------------*/
class PredEdge extends Sortable {

  /*------------------------------------------------------------------*/
  /*  instance variables                                              */
  /*------------------------------------------------------------------*/
  /** the target graph */
  protected NamedGraph graph;
  /** the index of the source      node (or zero, if not in body) */
  protected int        src;
  /** the index of the destination node (or zero, if not in body) */
  protected int        dst;
  /** the type/label of the prediced edge */
  protected String     edge;
  /** the type/label of the predicted node (if not in body) */
  protected String     node;
  /** the total weight (number) of predicting rules */
  protected double     wgt;
  /** the sum of confidence values */
  protected double     conf;
  /** the sum of lift values (version 1) */
  protected double     lift1;
  /** the sum of lift values (version 2) */
  protected double     lift2;
  /** the hash code of the predicted edge */
  protected int        hash;

  /*------------------------------------------------------------------*/
  /** Compute the hash code of a predicted edge.
   *  @param  graph the target graph
   *  @param  src   the index of the source node in the target graph
   *  @param  dst   the index of the dest.  node in the target graph
   *  @param  edge  the type/label of the predicted edge
   *  @param  node  the type/label of the predicted destination node
   *  @since  2020.10.25 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  protected static int hashCode (NamedGraph graph, int src, int dst,
                                 String edge, String node)
  {                             /* --- compute hash code */
    return graph.name.hashCode() +(src+1)*(dst+2)
           +edge.hashCode() +node.hashCode();
  }  /* hashCode() */

  /*------------------------------------------------------------------*/
  /** Create a predicted edge.
   *  @param  graph  the target graph
   *  @param  src    the index of the source node in the target graph
   *  @param  dst    the index of the dest.  node in the target graph
   *  @param  edge   the type/label of the predicted edge
   *  @param  node   the type/label of the predicted destination node
   *  @param  wgt    the weight     of the predicting rule
   *  @param  conf   the confidence of the predicting rule
   *  @param  lift1  the lift value of the predicting rule (version 1)
   *  @param  lift2  the lift value of the predicting rule (version 2)
   *  @since  2020.10.25 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  protected PredEdge (NamedGraph graph, int src, int dst,
                      String edge, String node, double wgt,
                      double conf, double lift1, double lift2)
  {                             /* --- create a predicted edge */
    this(graph, src, dst, edge, node, wgt, conf, lift1, lift2,
         PredEdge.hashCode(graph, src, dst, edge, node));
  }  /* PredEdge() */

  /*------------------------------------------------------------------*/
  /** Create a predicted edge.
   *  @param  graph  the target graph
   *  @param  src    the index of the source node in the target graph
   *  @param  dst    the index of the dest.  node in the target graph
   *  @param  edge   the type/label of the predicted edge
   *  @param  node   the type/label of the predicted destination node
   *  @param  wgt    the weight     of the predicting rule
   *  @param  conf   the confidence of the predicting rule
   *  @param  lift1  the lift value of the predicting rule (version 1)
   *  @param  lift2  the lift value of the predicting rule (version 2)
   *  @param  hash   the hash code of this predicted edge
   *  @since  2020.10.25 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  protected PredEdge (NamedGraph graph, int src, int dst,
                      String edge, String node, double wgt,
                      double conf, double lift1, double lift2, int hash)
  {                             /* --- create a predicted edge */
    this.graph = graph;         /* ensure src < dst, unless dst <= 0 */
    this.src   = src;  this.dst  = dst;
    this.edge  = edge; this.node = node;
    this.wgt   = wgt;
    this.conf  = wgt *conf;
    this.lift1 = wgt *lift1;
    this.lift2 = wgt *lift2;
    this.hash  = hash;
    this.succ  = null;
  }  /* PredEdge() */

  /*------------------------------------------------------------------*/
  /** Get successor predicted edge.
   *  @return the successor predicted edge
   *  @since  2021.10.17 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public PredEdge getSucc ()
  { return (PredEdge)this.succ; }

  /*------------------------------------------------------------------*/
  /** Compare two predicted edges.
   *  @param  obj the predicted edge to compare to
   *  @return the comparison result, that is, <code>-1</code>,
   *          <code>0</code>, or <code>+1</code> as this predicted
   *          edge is less than, equal to, or greater than the
   *          predicted edge given as an argument
   *  @since  2020.10.29 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public int compareTo (Sortable obj)
  {                             /* --- compare two predicted edges */
    assert(obj instanceof PredEdge);
    PredEdge ped = (PredEdge)obj;
    int c = this.graph.name.compareTo(ped.graph.name);
    if (c != 0) return c;       /* compare graph names */
    if (this.src < ped.src) return -1;
    if (this.src > ped.src) return +1;
    if (this.dst < ped.dst) return -1;
    if (this.dst > ped.dst) return +1;
    c = this.edge.compareTo(ped.edge);
    if (c != 0) return c;       /* compare edge and node type/label */
    return this.node.compareTo(ped.node);
  }  /* compareTo() */

}  /* class PredEdge */


/*--------------------------------------------------------------------*/
/** Class for the graph edges predictor.
 *  @author Christian Borgelt
 *  @since  2020.10.09 */
/*--------------------------------------------------------------------*/
public class Predictor implements Runnable {

  private static final long serialVersionUID = 0x00020000;

  /*------------------------------------------------------------------*/
  /*  constants: version information                                  */
  /*------------------------------------------------------------------*/
  /** the program description */
  public static final String DESCRIPTION =
    "edge predictor (part of MoSS programs)";
  /** the version of this program */
  public static final String VERSION =
    "2.0 (2021.10.27)";
  /** the copyright information for this program */
  public static final String COPYRIGHT =
    "(c) 2020-2021 Christian Borgelt";

  /*------------------------------------------------------------------*/
  /*  constants                                                       */
  /*------------------------------------------------------------------*/
  /** flag for directed graphs/fragments */
  public static final int DIRECTED = CanonicalForm.DIRECTED;
  /** flag for predicting edges with destination node in rule body */
  public static final int BODYNODE = 0x00000010;
  /** flag for predicting edges with "new" destination node */
  public static final int NEWNODE  = 0x00000020;
  /** flag for verbose reporting */
  public static final int VERBOSE  = 0x00080000;
  /** flag for no prediction statistics output */
  public static final int NOSTATS  = 0x00800000;
  /** default prediction mode flags: none */
  public static final int DEFAULT  = BODYNODE|NEWNODE;
  /** flag for nodes that are in the body of a rule application */
  public static final int ISINBODY = Integer.MIN_VALUE;

  /*------------------------------------------------------------------*/
  /*  instance variables                                              */
  /*------------------------------------------------------------------*/
  /** the prediction mode flags */
  protected int            mode    = DEFAULT;
  /** the minimum support of a rule as a fraction */
  protected double         fsupp   = 0.0;
  /** the minimum support of a rule as an absolute value */
  protected int            supp    = 1;
  /** the minimum confidence of an association rule as a fraction */
  protected double         conf    = 0.0;
  /** the minimum size of substructures to use (number of nodes) */
  protected int            min     = 0;
  /** the maximum size of substructures to use (number of nodes) */
  protected int            max     = Integer.MAX_VALUE;
  /** the (relative) weight of a predicted edges to a "new" node */
  protected double         newwgt  = 1.0;
  /** the (relative) weight of a predicted edges to existing nodes */
  protected double         xstwgt  = 0.0;

  /** the graph pattern file reader */
  protected GraphReader    patrdr  = null;
  /** the graph rule file reader */
  protected TableReader    rulerdr = null;
  /** the target graph file reader */
  protected GraphReader    trgrdr  = null;

  /** the list of patterns underlying the graph rules */
  protected NamedGraph     pats    = null;
  /** the number of patterns underlying the graph rules */
  protected int            patcnt  = 0;
  /** the map from names to graph patterns */
  protected HashMap<String,NamedGraph> patmap = null;
  /** the list of graph rules with which to predict the edges */
  protected GraphRule      rules   = null;
  /** the number of graph rules */
  protected int            rulcnt  = 0;
  /** the list of graphs for which to predict edges (database) */
  protected NamedGraph     graphs  = null;
  /** the numbers of target graphs in database */
  protected int            trgcnt  = 0;

  /** the repository of predicted edges (hash table) */
  protected PredEdge[]     bins   = null;
  /** the list of predicted edges */
  protected PredEdge       preds  = null;
  /** the size of the repository (number of predicted edges) */
  protected int            pecnt  = 0;

  /** the file to write the predicted edges to */
  protected Writer         writer = null;
  /** stream to write progress messages to */
  protected PrintStream    log    = System.err;
  /** the error status for the edge prediction process */
  private   Throwable      error  = null;
  /** whether to abort the edge prediction thread */
  private volatile boolean stop   = false;

  /*------------------------------------------------------------------*/
  /** Create an empty edge predictor with default parameter settings.
   *  @since  2020.10.09 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public Predictor ()
  { }                           /* --- create an edge predictor */

  /*------------------------------------------------------------------*/
  /** Set the prediction mode.
   *  <p>The prediction mode is a combination of the prediction mode
   *  flags, e.g. <code>VERBOSE</code> or <code>NOSTATS</code>.</p>
   *  @param  mode the prediction mode
   *  @since  2020.10.19 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void setMode (int mode)
  { this.mode = mode; }

  /*------------------------------------------------------------------*/
  /** Set the minimum and maximum antecedent/body pattern size.
   *  @param  min the minimum pattern size (number of nodes)
   *  @param  max the maximum pattern size (number of nodes)
   *  @since  2020.10.19 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void setSizes (int min, int max)
  { this.min = min; this.max = (max <= 0) ? Integer.MAX_VALUE : max; }

  /*------------------------------------------------------------------*/
  /** Set the minimum rule support.
   *  @param  supp the minimum support of association rules
   *  @since  2020.10.04 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void setSupp (double supp)
  {                             /* --- set minimum support value(s) */
    this.fsupp = (supp < 0) ? 0 : supp;
    this.supp  = (supp < 0) ? (int)-supp : 1;
  }  /* setSupp() */

  /*------------------------------------------------------------------*/
  /** Set the minimum rule confidence.
   *  @param  conf the minimum confidence of association rules
   *  @since  2020.10.04 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void setConf (double conf)
  { this.conf = conf; }

  /*------------------------------------------------------------------*/
  /** Set the weight of edges to new and existing nodes (not in body).
   *  @param  xstwgt the (relative) weight of edges to existing nodes
   *  @param  newwgt the (relative) weight of edges to new nodes
   *  @since  2020.11.15 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void setWeights (double xstwgt, double newwgt)
  { this.xstwgt = xstwgt; this.newwgt = newwgt; }

  /*------------------------------------------------------------------*/
  /** Set the input readers.
   *  @param  fn_pats  the name   of the graph patterns file
   *  @param  fn_rules the name   of the graph rules file
   *  @param  fn_trgs  the name   of the target graphs file
   *  @param  format   the format of the patterns / graphs file
   *  @since  2020.10.19 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void setInput (String fn_pats, String fn_rules,
                        String fn_trgs, String format)
    throws IOException
  {                             /* --- set the input readers */
    int dir = ((this.mode & DIRECTED) != 0) ? GraphReader.DIRECTED : 0;
    this.patrdr  = GraphReader.createReader(new FileReader(fn_pats),
                     GraphReader.SUBS|dir,   format);
    this.rulerdr = new TableReader(new FileReader(fn_rules));
    this.trgrdr  = GraphReader.createReader(new FileReader(fn_trgs),
                     GraphReader.GRAPHS|dir, format,
                     this.patrdr.getNotation());
  }  /* setInput() */

  /*------------------------------------------------------------------*/
  /** Set the input readers.
   *  @param  patrdr   the reader from which to read the patterns
   *  @param  rulerdr  the reader from which to read the rules
   *  @param  trgrdr   the reader from which to read the target graphs
   *  @since  2020.10.19 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void setInput (GraphReader patrdr, TableReader rulerdr,
                        GraphReader trgrdr)
    throws IOException
  {                             /* --- set the input readers */
    this.patrdr  = patrdr;
    this.rulerdr = rulerdr;
    this.trgrdr  = trgrdr;
  }  /* setInput() */

  /*------------------------------------------------------------------*/
  /** Set the output writer.
   *  @param  fn_edge  the name of the file for the predicted edges
   *  @since  2020.10.19 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void setOutput (String fn_edge) throws IOException
  { this.writer = new FileWriter(fn_edge); }

  /*------------------------------------------------------------------*/
  /** Set the output writer.
   *  @param  writer the writer to write the predicted edges to
   *  @since  2020.10.19 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void setOutput (Writer writer)
  { this.writer = writer; }

  /*------------------------------------------------------------------*/
  /** Print a counter.
   *  @param  n the counter to print
   *  @since  2020.10.19 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  private void print (int n)
  {                             /* --- print a counter */
    String s = "        " +n;   /* format the number and print it */
    this.log.print(s.substring(s.length()-9));
    this.log.print("\b\b\b\b\b\b\b\b\b");
  }  /* print() */

  /*------------------------------------------------------------------*/
  /** Initialize the edge predictor from command line arguments.
   *  @param  args the command line arguments
   *  @since  2020.10.19 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void init (String[] args) throws IOException
  {                             /* --- init. an edge predictor */
    int     i, k = 0;           /* indices, loop variables */
    String  s;                  /* to traverse the arguments */
    String  patfn  = null;      /* name of graph patterns file */
    String  rulefn = null;      /* name of graph rules    file */
    String  trgfn  = null;      /* name of target graphs  file */
    String  edgefn = "moss.ped";/* name of predicted edges file */
    double  rsupp  = 0.0;       /* minimum support    of a rule */
    double  rconf  = 0.0;       /* minimum confidence of a rule */
    int     dir    = 0;         /* whether graphs are directed */
    int     pmode  = DEFAULT;   /* edge prediction mode */
    int     bmin   =  1;        /* min. and max. size of rule body */
    int     bmax   = Integer.MAX_VALUE;       /* (rule antecedent) */
    double  wnew   = -1.0;      /* weight of edge to new node */
    double  wxst   =  0.0;      /* weight of edge to existing node */
    String  format = "nelist";  /* input format for patterns/graphs */
    boolean nel;                /* node/edge list input format */
    Notation    ntn;            /* notation of patterns/graphs */
    GraphReader patrdr, trgrdr; /* buffers for graph readers */
    TableReader rulerdr;        /* buffer for rule reader */
    Writer      wrt;            /* buffer for edge writer */

    /* --- print startup/usage message --- */
    if (args.length > 0) {      /* if no arguments are given */
      this.log.print  (this.getClass().getName());
      this.log.println(" - " +DESCRIPTION);
      this.log.println("version " +VERSION +"    " +COPYRIGHT); }
    else {                      /* if no arguments are given */
      System.out.print  ("usage: java " +this.getClass().getName());
      System.out.print  (" [options] <pats> <rules> <graphs>");
      System.out.println(" [<edges>]");
      System.out.println(DESCRIPTION);
      System.out.println("version " +VERSION +"    " +COPYRIGHT);
      System.out.print  ("sub     name of substructure input file    ");
      System.out.println(" (mandatory)");
      System.out.print  ("rules   name of graph rules file           ");
      System.out.println(" (mandatory)");
      System.out.print  ("graphs  name of target graphs file         ");
      System.out.println(" (mandatory)");
      System.out.print  ("edges   name of pred. edges output file    ");
      System.out.println(" (default: \"" +edgefn +"\")");
      System.out.print  ("-D      treat edges as directed            ");
      System.out.println(" (default: undirected)");
      System.out.println("        (only for NEList input/output)");
      System.out.print  ("-f#     input  format for patterns/graphs  ");
      System.out.println(" (default: " +format +")");
      System.out.print  ("-m#     minimum size of an antecedent      ");
      System.out.println(" (default: " +bmin +")");
      System.out.print  ("-n#     maximum size of an antecedent      ");
      System.out.println(" (default: no limit)");
      System.out.print  ("-s#     minimum support of a rule          ");
      System.out.println(" (default: " +rsupp +"%)");
      System.out.print  ("-c#     minimum confidence of a rule       ");
      System.out.println(" (default: " +rconf +"%)");
      System.out.print  ("-b#     do not predict edges to body nodes ");
      System.out.println(" (default: predict)");
      System.out.print  ("-a#     do not predict edges to new  nodes ");
      System.out.println(" (default: predict)");
      System.out.print  ("-x#     (relative) weight to existing node ");
      System.out.println(" (default: " +wxst +")");
      System.out.print  ("        (negative: per node, ");
      System.out.println(         "positive: per embedding)");
      System.out.print  ("-w#     (relative) weight to new node      ");
      System.out.println(" (default: " +wnew +")");
      System.out.print  ("        (negative: per node, ");
      System.out.println(         "positive: equiv. existing nodes)");
      //System.out.println("-v      verbose output during prediction");
      //System.out.println("-T      do not print prediction statistic");
      throw new IOException("no arguments given");
    }                           /* print a usage message */

    /* --- evaluate arguments --- */
    for (i = 0; i < args.length; i++) {
      s = args[i];              /* traverse the arguments */
      if ((s.length() > 0)      /* if the argument is an option */
      &&  (s.charAt(0) == '-')) {
        if (s.length() < 2)     /* check for an option letter */
          throw new IOException("error: missing option");
        switch (s.charAt(1)) {  /* evaluate option */
          case 'D': pmode |= DIRECTED;                           break;
          case 'f': format = s.substring(2);                     break;
          case 'm': bmin   = Integer.parseInt(s.substring(2));   break;
          case 'n': bmax   = Integer.parseInt(s.substring(2));   break;
          case 's': rsupp  = Double.parseDouble(s.substring(2)); break;
          case 'c': rconf  = Double.parseDouble(s.substring(2)); break;
          case 'b': pmode &= ~BODYNODE;                          break;
          case 'a': pmode &= ~NEWNODE;                           break;
          case 'w': wnew   = Double.parseDouble(s.substring(2)); break;
          case 'x': wxst   = Double.parseDouble(s.substring(2)); break;
          //case 'v': pmode |= VERBOSE;                            break;
          //case 'T': pmode |= NOSTATS;                            break;
          default : throw new IOException(
                      "error: unknown option -" +s.charAt(1));
        } }                     /* set option variables */
      else {                    /* if the argument is no option */
        switch (k++) {          /* evaluate non-option */
          case  0: patfn  = s; break;
          case  1: rulefn = s; break;
          case  2: trgfn  = s; break;
          case  3: edgefn = s; break;
          default: throw new IOException("error: too many arguments");
        }                       /* there should be three fixed args: */
      }                         /* names of pattern file, rule file */
    }                           /* and target graphs file */

    /* --- initialize input/output --- */
    nel = (format.equals("nel") /* check for node/edge list format */
        || format.equals("nelist") || format.equals("list"));
    if (!nel) pmode &= ~DIRECTED; /* directed edges only for NEList */
    this.setMode(pmode);        /* set the prediction mode */
    dir = ((pmode & DIRECTED) != 0) ? GraphReader.DIRECTED : 0;
    patrdr = GraphReader.createReader(new FileReader(patfn),
                 GraphReader.SUBS|dir,   format);
    if (patrdr == null)         /* create the pattern graphs reader */
      throw new IOException("error: invalid input format " +format);
    trgrdr = GraphReader.createReader(new FileReader(trgfn),
                 GraphReader.GRAPHS|dir, format, patrdr.getNotation());
    if (trgrdr == null)         /* create the target graphs reader */
      throw new IOException("error: invalid input format " +format);
    rulerdr = new TableReader(new FileReader(rulefn));
                                /* create a rule reader */
    this.setInput(patrdr, rulerdr, trgrdr);
                                /* set the input readers */
    wrt = new FileWriter(edgefn);
    this.setOutput(wrt);        /* create and set output writer */

    /* --- initialize other search variables --- */
    if (rsupp >= 0) rsupp *= 0.01;  /* change support and confidence */
    rconf = Math.abs(rconf) *0.01;  /* from percentages to fractions */
    this.setSupp(rsupp);        /* set the minimum support */
    this.setConf(rconf);        /* and the minimum confidence */
    this.setSizes(bmin, bmax);  /* set antecedent/body size range */
    this.setWeights(wxst, wnew);/* set weights of edges to new nodes */
  }  /* init() */

  /*------------------------------------------------------------------*/
  /** Read an integer from the graph rules file.
   *  @param  delim the field delimiter to check for
   *  @since  2020.10.25 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  private void read (int delim) throws IOException
  {                             /* --- read a field, check delimiter */
    int r = this.rulerdr.readField();
    if (r != delim) throw new IOException(this.rulerdr.rno()
                                         +"wrong number of fields");
  }  /* read() */

  /*------------------------------------------------------------------*/
  /** Check for a field with a certain content.
   *  @param  field the field content   to check for
   *  @param  delim the field delimiter to check for
   *  @since  2020.10.25 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  private void check (String field, int delim)
    throws IOException
  {                             /* --- read integer from rule file */
    this.read(delim);           /* read the next field */
    if (!this.rulerdr.field.equals(field)) {
      throw new IOException(this.rulerdr.rno()
                           +": expected '" +field +"' instead of '"
                           +this.rulerdr.field +"'"); }
  }  /* check() */

  /*------------------------------------------------------------------*/
  /** Read an string from the graph rules file.
   *  @param  delim the field delimiter to check for
   *  @return the string read
   *  @since  2020.10.25 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  private String readStr (int delim) throws IOException
  {                             /* --- read integer from rule file */
    this.read(delim);           /* read the next field */
    return this.rulerdr.field;  /* return the current field */
  }  /* readStr() */

  /*------------------------------------------------------------------*/
  /** Read an integer from the graph rules file.
   *  @param  delim   the field delimiter to check for
   *  @return the integer number read
   *  @since  2020.10.25 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  private int readInt (int delim) throws IOException
  {                             /* --- read integer from rule file */
    this.read(delim);           /* read the next field */
    try { return Integer.parseInt(this.rulerdr.field); }
    catch (NumberFormatException e) {
      throw new IOException(this.rulerdr.rno()
                           +": invalid integer number '"
                           +this.rulerdr.field +"'"); }
  }  /* readInt() */

  /*------------------------------------------------------------------*/
  /** Read an integer from the graph rules file,
   *  interpreting an empty field as zero.
   *  @param  delim   the field delimiter to check for
   *  @return the integer number read
   *  @since  2020.10.25 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  private int readIntZ (int delim) throws IOException
  {                             /* --- read integer from rule file */
    this.read(delim);           /* read the next field */
    if ((this.rulerdr.field          == null)
    ||  (this.rulerdr.field.length() <= 0)) return 0;
    try { return Integer.parseInt(this.rulerdr.field); }
    catch (NumberFormatException e) {
      throw new IOException(this.rulerdr.rno()
                           +": invalid integer number '"
                           +this.rulerdr.field +"'"); }
  }  /* readIntZ() */

  /*------------------------------------------------------------------*/
  /** Read a floating point number from the graph rules file.
   *  @param  delim the field delimiter to check for
   *  @return the floating point number read
   *  @since  2020.10.25 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  private double readDbl (int delim) throws IOException
  {                             /* --- read integer from rule file */
    this.read(delim);           /* read the next field */
    try { return Double.parseDouble(this.rulerdr.field); }
    catch (NumberFormatException e) {
      throw new IOException(this.rulerdr.rno()
                           +": invalid floating point number '"
                           +this.rulerdr.field +"'"); }
  }  /* readDbl() */

  /*------------------------------------------------------------------*/
  /** Reorganize the predicted edge repository.
   *  <p>The hash table of the predicted edge repository is enlarged
   *  and the predicted edges are rehashed to achieve faster access.</p>
   *  @since  2020.10.26 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  private void rehash ()
  {                             /* --- reorganize the repository */
    int        i, k;            /* loop variable, hash bin index */
    PredEdge[] b;               /* buffer for old hash bin array */
    PredEdge   e;               /* to traverse the hash bin lists */

    b = this.bins;              /* note the old hash bin array and */
    k = (b.length << 1) +1;     /* compute the new hash table size */
    this.bins = new PredEdge[k];/* allocate a new hash bin array */
    for (i = b.length; --i >= 0; ) {
      while (b[i] != null) {    /* traverse the nonempty bins */
        e = b[i];               /* of the old hash bin array */
        b[i] = (PredEdge)e.succ;
        e.succ = this.bins[k = e.hash % this.bins.length];
        this.bins[k] = e;       /* add the element at the head */
      }                         /* of the approriate hash bin list */
    }                           /* in the new hash bin array */
  }  /* rehash() */

  /*------------------------------------------------------------------*/
  /** Do a bisection search for a node with a given type in an array.
   *  @param  nodes  the array of nodes to search
   *  @param  n      the number of nodes to search (from array start)
   *  @param  type   the node type to search for
   *  @return the insertion position of the node type, which is
   *          the location after the last equal element if equal
   *          elements exist in tbe array
   *  @since  2020.11.15 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  private static int bisect (Node[] nodes, int n, int type)
  {                             /* --- find 1st node with given type */
    int  l, r, m;               /* array indices */
    Node node;                  /* current node */

    for (l = 0, r = n; l < r;){ /* while search range is not empty */
      node = nodes[m = (l+r) /2];      /* compare the given type to */
      if      (type > node.type) l = m+1; /* the middle element and */
      else if (type < node.type) r = m;   /* adapt the search range */
      else {                    /* according to the result */
        while (++m < r)         /* if found, skip equal elements */
          if (type < nodes[m].type) break;
        return m;               /* if match found, return index */
      }                         /* after last equal element */
    }
    return l;                   /* return the insertion position */
  }  /* bisect() */

  /*------------------------------------------------------------------*/
  /** Reorganize the predicted edge repository.
   *  <p>The hash table of the predicted edge repository is enlarged
   *  and the predicted edges are rehashed to achieve faster access.</p>
   *  @param  graph  the target graph
   *  @param  src    the index of the source      node of the edge
   *  @param  dst    the index of the destination node of the edge
   *                 (zero if this is a new node)
   *  @param  rule   the graph rule that predicts the edge
   *  @param  wgt    the weight of the predicting rule (application)
   *  @since  2020.10.26 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  private int storeEdge (NamedGraph graph, int src, int dst,
                         GraphRule rule, double wgt)
  {                             /* --- store a predicted edge */
    int      h, i;              /* hash value, hash bin index */
    PredEdge pred;              /* (created) predicted edge */
    String   edge, node;        /* type/label of edge and node */
    int      dir;               /* edge direction */

    edge = rule.full.getEdgeName(rule.edge);
    node = ((src < 0) || (dst < 0))  /* get labels of edge and node */
         ? rule.full.getNodeName(rule.node) : "";
    if (((this.mode & DIRECTED) == 0) && ((src < 0) || (src > dst))) {
      i = src; src = dst; dst = i; } /* fixed order if undirected */
    h = PredEdge.hashCode(graph, src, dst, edge, node);
    i = h % this.bins.length;  /* get hash bin index and traverse bin */
    for (pred = this.bins[i]; pred != null; pred = pred.getSucc()){
      if ( (pred.graph == graph)
      &&  ((pred.src   == src) && (pred.dst == dst))
      &&  pred.edge.equals(edge)
      &&  pred.node.equals(node))
        break;                  /* try to find the predicted edge */
    }                           /* in the predicted edge repository */
    if (pred != null) {         /* if the predicted edge was found */
      pred.wgt   += wgt;        /* add weight of predicting edge */
      pred.conf  += wgt *rule.conf;     /* and rule confidence */
      pred.lift1 += wgt *rule.lift1;    /* and lift values */
      pred.lift2 += wgt *rule.lift2;    /* to the predicted edge */
      return 0; }               /* return 'no new edge' */
    else {                      /* if predicted edge was not found */
      pred = new PredEdge(graph, src, dst, edge, node,
                          wgt, rule.conf, rule.lift1, rule.lift2, h);
      pred.succ = this.bins[i]; /* create new predicted edge */
      this.bins[i] = pred;      /* and add this edge to the */
      return 1;                 /* head of the hash bin list */
    }                           /* return 'new edge created' */
  }  /* storeEdge() */

  /*------------------------------------------------------------------*/
  /** Load substructures, graph rules and prediction graph
   *  and start the search.
   *  @since  2020.10.19 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  protected void predict () throws IOException
  {                             /* --- run edge prediction */
    int        i, r, n;         /* loop variables, read result */
    String     s, g;            /* buffers for a string */
    int        bdymax;          /* maximum number of body   nodes */
    Node       bdynds[];        /* orig. node array of rule body */
    int        trgmax;          /* maximum number of target nodes */
    Node       trgnds[];        /* sorted node array of target graph */
    NamedGraph graph;           /* created graph */
    GraphRule  rule;            /* created graph rule */
    NamedGraph part, full;      /* constituents of a graph rule */
    int        edge, node;      /* edge index, dest. node index */
    int        src,  dst;       /* source and dest. node indices */
    Node       snb,  dnb;       /* source and dest. node in body */
    int        stg,  dtg;       /* source and dest. index in target */
    int        base, body, supp;/* base/body/full support values */
    int        head1, head2;    /* head support values */
    Embedding  emb, allembs;    /* (to traverse) embeddings */
    int        cnt;             /* number of target nodes */
    double     wgt;             /* weight of a predicted edge */
    PredEdge   pred;            /* to traverse the predicted edges */
    long       t;               /* for time measurements */

    /* --- load graph patterns --- */
    t = System.currentTimeMillis();
    s = (this.patrdr.getNotation() instanceof MoleculeNtn)
      ? "molecule" : "graph";   /* get the graph pattern type name */
    this.log.print("reading " +s +" patterns ... ");
    this.patcnt = 0;            /* initialize the pattern counter */
    try {                       /* read the graph patterns */
      while (this.patrdr.readGraph()) {
        graph = new NamedGraph(this.patrdr.getGraph(),
                               this.patrdr.getName(), 0, 0);
        graph.succ = this.pats; /* add the new pattern at the end */
        this.pats = graph;      /* of the graph pattern list */
        if ((++this.patcnt & 0xff) == 0) this.print(this.patcnt);
      } }                       /* print the number of patterns */
    catch (IOException e) {     /* report pattern number with error */
      throw new IOException((this.patcnt+1) +": " +e.getMessage()); }
    t = System.currentTimeMillis() -t;
    this.log.println("[" +this.patcnt +" " +s +"(s)] done "
                    +"[" +(t/1000.0) +"s].");
    if (this.patcnt <= 0)       /* check for any graph patterns */
      throw new IOException("error: no patterns found");
    this.patmap = new HashMap<String,NamedGraph>();
    for (graph = this.pats; graph != null; graph = graph.succ)
      this.patmap.put(graph.getName(), graph);

    /* --- load graph rules --- */
    t = System.currentTimeMillis();
    this.log.print("reading rules ... ");
    this.rulcnt = bdymax = 0;   /* initialize the rule counter and */
    if (this.rulerdr.eof())     /* the maximum number of body nodes */
      throw new IOException(this.rulerdr.rno() +": no rules found");
    this.check("part",  0);     /* column "part"  */
    this.check("full",  0);     /* column "full"  */
    this.check("src",   0);     /* column "src"   */
    this.check("dst",   0);     /* column "dst"   */
    this.check("edge",  0);     /* column "edge"  */
    this.check("node",  0);     /* column "node"  */
    this.check("base",  0);     /* column "base"  */
    this.check("body",  0);     /* column "body"  */
    this.check("supp",  0);     /* column "supp"  */
    this.check("head1", 0);     /* column "head1" */
    this.check("head2", 0);     /* column "head2" */
    this.check("conf",  0);     /* column "conf"  */
    this.check("lift1", 0);     /* column "lift1" */
    this.check("lift2", 1);     /* column "lift2" */
    while (!this.rulerdr.eof()){/* while not at end of file */
      part  = this.patmap.get(s = this.readStr(0));
      if (part == null)         /* partial pattern identifier */
        throw new IOException(this.rulerdr.rno()
                             +" unknown graph pattern '" +s +"'");
      full  = this.patmap.get(s = this.readStr(0));
      if (full == null)         /* full pattern identifier */
        throw new IOException(this.rulerdr.rno()
                             +" unknown graph pattern '" +s +"'");
      src   = this.readInt(0);  /* source      node index (in body) */
      if ((src  <  0) || (src  > part.nodecnt))
        throw new IOException(this.rulerdr.rno()
                             +" invalid source node index " +src);
      dst   = this.readInt(0);  /* destination node index (in body) */
      if ((dst  <  0) || (dst  > part.nodecnt))
        throw new IOException(this.rulerdr.rno()
                             +" invalid destination node index " +dst);
      edge  = this.readInt(0);  /* edge index (in full pattern) */
      if ((edge <= 0) || (edge > full.edgecnt))
        throw new IOException(this.rulerdr.rno()
                             +" invalid edge index " +edge);
      node  = this.readIntZ(0); /* node index (in full pattern) */
      if ((node <  0) || (node > full.nodecnt))
        throw new IOException(this.rulerdr.rno()
                             +" invalid destination node index " +node);
      base  = this.readInt(0);  /* base support */
      if (base  <= 0) throw new IOException(this.rulerdr.rno()
                             +" invalid base support " +base);
      body  = this.readInt(0);  /* rule body support */
      if (body  <= 0) throw new IOException(this.rulerdr.rno()
                             +" invalid body support " +body);
      supp  = this.readInt(0);  /* rule pattern support */
      if (supp  <= 0) throw new IOException(this.rulerdr.rno()
                             +" invalid pattern support " +supp);
      head1 = this.readInt(0);  /* rule head support 1 */
      if (head1 <= 0) throw new IOException(this.rulerdr.rno()
                             +" invalid head1 support " +head1);
      head2 = this.readInt(0);  /* rule head support 2 */
      if (head1 <= 0) throw new IOException(this.rulerdr.rno()
                             +" invalid head2 support " +head2);
      this.readDbl(0);          /* confidence   (ignore) */
      this.readDbl(0);          /* lift value 1 (ignore) */
      this.readDbl(1);          /* lift value 2 (ignore) */
      if (part.nodecnt > bdymax)/* find the maximum number of nodes */
        bdymax = part.nodecnt;  /* in the rule body/antecedent */
      rule = new GraphRule(part, full, src-1, dst-1, edge-1, node-1,
                           base, body, supp, head1, head2);
      rule.succ = this.rules;   /* add new graph rule at the end */
      this.rules = rule;        /* of the graph rule list */
      if ((++this.rulcnt & 0xff) == 0) this.print(this.rulcnt);
    }                           /* report number of rules */
    t = System.currentTimeMillis() -t;
    this.log.println("[" +this.rulcnt +" rule(s)] done "
                    +"[" +(t/1000.0) +"s].");

    /* --- load target graphs --- */
    t = System.currentTimeMillis();
    s = (this.trgrdr.getNotation() instanceof MoleculeNtn)
      ? "molecule" : "graph";   /* get the target graph type name */
    this.log.print("reading " +s +"s ... ");
    this.trgcnt = trgmax = 0;   /* initialize the graph counter */
    try {                       /* read the target graphs */
      while (this.trgrdr.readGraph()) {
        g = this.trgrdr.getName();
        if (g == null) g = String.format("%d", this.trgcnt+1);
        graph = new NamedGraph(this.trgrdr.getGraph(), g, 0, 0);
        graph.succ = this.graphs;   /* add the new graph at the end */
        this.graphs = graph;        /* of the graph list */
        if (graph.nodecnt > trgmax) /* find maximum number of nodes */
          trgmax = graph.nodecnt;   /* in the rule body/antecedent */
        if ((++this.trgcnt & 0xff) == 0) this.print(this.trgcnt);
      } }                       /* print the number of target graphs */
    catch (IOException e) {     /* report graph number with error */
      throw new IOException((this.trgcnt+1) +": " +e.getMessage()); }
    t = System.currentTimeMillis() -t;
    this.log.println("[" +this.trgcnt +" " +s +"(s)] done "
                    +"[" +(t/1000.0) +"s].");
    if (this.trgcnt <= 0)       /* check for target graphs */
      throw new IOException("error: no target graphs found");

    /* --- predict edges --- */
    t = System.currentTimeMillis();
    this.log.print("predicting edges ... ");
    this.bins  = new PredEdge[1023];
    this.preds = null;          /* init. the edge repository */
    this.pecnt = 0; wgt = 0;    /* and the overall edge list */
    trgnds = new Node[trgmax];  /* create a target node buffer */
    bdynds = new Node[bdymax];  /* and a rule body node buffer */
    for (graph = this.graphs; graph != null; graph = graph.succ) {
      allembs = null;           /* traverse the target graphs */
      System.arraycopy(graph.nodes, 0, trgnds, 0, graph.nodecnt);
      Arrays.sort(trgnds, 0, graph.nodecnt, new Comparator<Node> () {
        public int compare (Node a, Node b) {
          if (a.type < b.type) return -1;
          if (a.type > b.type) return +1;
          return 0;             /* sort copies of target graph nodes */
        } } );                  /* according to their type */
      part = null;              /* traverse the graph rules */
      for (rule = this.rules; rule != null; rule = rule.succ) {
        if ((rule.part.nodecnt < this.min)
        ||  (rule.part.nodecnt > this.max)
        ||  (rule.supp         < (int)(this.fsupp *rule.base))
        ||  (rule.supp         < this.supp)
        ||  (rule.conf         < this.conf))
          continue;             /* traverse the qualifying rules */
        if (rule.part != part){ /* if at new rule body/antecedent */
          part = rule.part;     /* note new rule body/antecedent */
          System.arraycopy(part.nodes, 0, bdynds, 0, part.nodecnt);
          part.prepareEmbed();  /* prepare it for embedding and */
          graph.prepare();      /* prepare graph for embedding */
          allembs = graph.embed(part);
          graph.index();        /* embed rule body and index target */
        }                       /* then traverse the embeddings */
        if (rule.src < 0) {     /* if source node is new */
          snb = null; src = -1; }
        else {                  /* if source node is in body */
          snb = bdynds[rule.src];
          for (src = part.nodecnt; --src >= 0; )
            if (part.nodes[src] == snb) break;
        }                       /* get source index after reorg. */
        if (rule.dst < 0) {     /* if destination node is new */
          dnb = null; dst = -1; }
        else {                  /* if destination node is in body */
          dnb = bdynds[rule.dst];
          for (dst = part.nodecnt; --dst >= 0; )
            if (part.nodes[dst] == dnb) break;
        }                       /* get dest. index after reorg. */

        for (emb = allembs; emb != null; emb = emb.succ) {
          stg = (src < 0) ? -1 : emb.nodes[src].mark;
          dtg = (dst < 0) ? -1 : emb.nodes[dst].mark;
          n   = 0;              /* get node indices of pred. edge */
          if ((stg >= 0) && (dtg >= 0)){ /* if both nodes in body */
            if ((this.mode & BODYNODE) == 0) continue;
            n += this.storeEdge(graph, stg, dtg, rule, 1.0); }
          else {                /* if one incident node is "new" */
            if ((this.mode & NEWNODE)  == 0) continue;
            if (this.xstwgt != 0) {
              node = rule.full.nodes[rule.node].type;
              for (i = 0; i < emb.nodes.length; i++)  /* mark nodes */
                emb.nodes[i].mark |= ISINBODY;      /* of rule body */
              r = Predictor.bisect(trgnds, graph.nodecnt, node);
              if (this.xstwgt < 0)  /* if weight per destination node */
                wgt = -this.xstwgt; /* get weight per predicted edge */
              else {            /* if total weight per embedding */
                for (cnt = 0, i = r; --i >= 0; ) {
                  if (trgnds[i].type < node) break;
                  if (trgnds[i].mark < 0)    continue;
                  cnt += 1;     /* traverse the target nodes and */
                }               /* count the destination nodes */
                wgt = (this.newwgt > 0) ? this.newwgt : 0.0;
                wgt = (cnt > 0) ? this.xstwgt /(wgt +(double)cnt) : 0.0;
              }                 /* compute weight per pred. edge */
              for (i = r; --i >= 0; ) {
                if (trgnds[i].type < node) break;
                if ((r = trgnds[i].mark) < 0) continue;
                n += (stg < 0)  /* store in directed manner */
                   ? this.storeEdge(graph, r, dtg, rule, wgt)
                   : this.storeEdge(graph, stg, r, rule, wgt);
              }                 /* make weighted edge predictions */
              /* That edges may be undirected is handled inside the  */
              /* function storeEdge() by exchanging source and dest. */
              for (i = 0; i < emb.nodes.length; i++)
                emb.nodes[i].mark &= ~ISINBODY;
            }                   /* unmark rule body nodes again */
            if (this.newwgt != 0) { /* if to predict to new node */
              if      (this.newwgt <  0) wgt  = -this.newwgt;
              else if (this.xstwgt != 0) wgt *=  this.newwgt;
              else                       wgt  =  this.newwgt;
              n += this.storeEdge(graph, stg, dtg, rule, wgt);
            }                   /* store a predicted edge */
          }                     /* an actually new node */
          this.pecnt += n;      /* count the newly created edges */
          if (((this.pecnt -n) & ~0xff) != (this.pecnt & ~0xff))
            this.print(this.pecnt);
        }                       /* report the number of edges */
      }                         /* every 255 predicted edges */
    }                           /* (somewhat strange check) */
    t = System.currentTimeMillis() -t;
    this.log.println("[" +this.pecnt +" edge(s)] done "
                    +"[" +(t/1000.0) +"s].");

    /* --- write predicted edges --- */
    t = System.currentTimeMillis();
    this.log.print("writing edges ... ");
    for (pred = null, i = 0; i < this.bins.length; i++) {
      if (this.bins[i] == null) continue;
      if (pred != null) pred.succ = this.bins[i];
      else      this.preds = pred = this.bins[i];
      while (pred.succ != null) pred = (PredEdge)pred.succ;
    }                           /* collect the predicted edges */
    if (this.preds != null)     /* and sort them (if any) */
      this.preds = (PredEdge)this.preds.sort();
    this.writer.write("graph\tsrc\tdst\tedge\tnode\t");
    this.writer.write("wgt\tconf\tlift1\tlift2\n");
    for (pred = this.preds; pred != null; pred = pred.getSucc()) {
      this.writer.write(pred.graph.name +"\t");
      this.writer.write((pred.src+1) +"\t" +(pred.dst+1) +"\t");
      this.writer.write(pred.edge    +"\t" +pred.node    +"\t");
      this.writer.write(pred.wgt     +"\t" +pred.conf    +"\t");
      this.writer.write(pred.lift1   +"\t" +pred.lift2   +"\n");
    }                           /* print the edge description */
    t = System.currentTimeMillis() -t;
    this.log.println("[" +this.pecnt +" edge(s)] done "
                    +"[" +(t/1000.0) +"s].");
  }  /* predict() */

  /*------------------------------------------------------------------*/
  /** Clean up after the edge prediction finished or was aborted.
   *  @since  2020.10.19 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  protected void term () throws IOException
  {                             /* --- clean up after edge prediction */
    if (this.writer != null) { this.writer.close(); this.writer = null;}
  }  /* term() */

  /*------------------------------------------------------------------*/
  /** Run the edge prediction and clean up after it is finished.
   *  @since  2020.10.19 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void run ()
  {                             /* --- run the miner */
    this.error = null;          /* clear the error status */
    this.stop  = false;         /* and the stop flag */
    try { this.predict(); }     /* run the edge prediction */
    catch (IOException e)      { this.error = e; }
    catch (OutOfMemoryError e) { this.error = e; }
    try { this.term(); }        /* clean up after the search */
    catch (IOException e) { if (this.error == null) this.error = e; }
    if (this.error != null) {   /* report an error */
      this.log.println("\n" +this.error.toString()); }
  }  /* run() */

  /*------------------------------------------------------------------*/
  /** Abort the edge predictor (if running as a thread).
   *  @since  2020.10.19 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void abort ()
  { this.stop = true; }

  /*------------------------------------------------------------------*/
  /** Get the error status of the edge prediction process.
   *  <p>With this function it can be checked, after the prediction
   *  with the <code>run()</code> method has terminated, whether an
   *  error occurred in the prediction. Note that an external abort
   *  with the function <code>abort()</code> does <i>not</i> trigger
   *  an exception to be thrown.</p>
   *  @return the exception that occurred in the edge prediction
   *          or <code>null</code> if the prediction was successful
   *  @since  2020.10.19 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public Throwable getError ()
  { return this.error; }

  /*------------------------------------------------------------------*/
  /** Print statistics about the prediction.
   *  @since  2020.10.19 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void stats ()
  {                             /* --- show prediction statistics */
  }  /* stats() */

  /*------------------------------------------------------------------*/
  /** Command line invocation of the edge predictor.
   *  @param  args the command line arguments
   *  @since  2020.10.19 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public static void main (String[] args)
  {                             /* --- main function */
    Predictor pred = new Predictor();  /* substructure predictor */
    try {                       /* run edge prediction */
      pred.init(args);          /* initialize the predictor, */
      pred.run();               /* make edge predictions, and */
      pred.stats(); }           /* show prediction statistics */
    catch (IOException e) {     /* report i/o error message */
      System.err.println("\n" +e.toString()); }
  }  /* main() */

}  /* class Predictor */
