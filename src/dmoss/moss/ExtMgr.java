/*----------------------------------------------------------------------
  File    : ExtMgr.java
  Contents: class for an extension edge manager
  Author  : Christian Borgelt
  History : 2010.01.22 file created
            2010.01.23 function trim() added (trim excluded node types)
            2010.01.28 maximum degree of the source node added
            2020.10.29 bug in sorting extension edge lists fixed
            2021.10.06 bug in extension edge creation alls fixed
----------------------------------------------------------------------*/
package moss;

import java.util.Arrays;

/*--------------------------------------------------------------------*/
/** Class for potential extension edges.
 *  @author Christian Borgelt
 *  @since  2010.01.22 */
/*--------------------------------------------------------------------*/
class ExtEdge extends Sortable {

  /*------------------------------------------------------------------*/
  /*  instance variables                                              */
  /*------------------------------------------------------------------*/
  /** the edge code (edge type including direction flag) */
  protected int     code;
  /** the source node type */
  protected int     src;
  /** the destination node type */
  protected int     dst;
  /** the (maximum) source node degree */
  protected int     deg;
  /** the successor in a hash bin list */
  protected ExtEdge next;

  /*------------------------------------------------------------------*/
  /** Create an extension edge.
   *  @param  code the edge code (edge type and direction flag)
   *  @param  src  the source node type
   *  @param  dst  the destination node type
   *  @param  deg  the (maximum) source node degree
   *  @since  2010.01.22 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public ExtEdge (int code, int src, int dst, int deg)
  {                             /* --- create an extension edge */
    this.code = code;           /* note the edge code */
    this.src  = src;            /* and  the source      node type */
    this.dst  = dst;            /* and  the destination node type */
    this.deg  = deg;            /* and  the source node degree */
    this.next = null;
    this.succ = null;
  }  /* ExtEdge() */

  /*------------------------------------------------------------------*/
  /** Check whether two extension edges are equal.
   *  <p>This function exists only in order to avoid certain warnings
   *  due to the existence of a <code>hashCode</code> function.</p>
   *  @param  obj the extension edge to compare to
   *  @return whether the two extension edges are equal
   *  @since  2010.01.22 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public boolean equals (Object obj)
  {                             /* --- check for equality */
    return (this.code == ((ExtEdge)obj).code)
        && (this.src  == ((ExtEdge)obj).src)
        && (this.dst  == ((ExtEdge)obj).dst);
  }  /* equals() */

  /*------------------------------------------------------------------*/
  /** Compute the hash code of the extension edge.
   *  @param  code the edge code (edge type and direction flag)
   *  @param  src  the source node type
   *  @param  dst  the destination node type
   *  @return the hash code of the extension edge
   *  @since  2021.10.06 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public static int hashCode (int type, int src, int dst)
  {                             /* --- compute a hash code */
    return (((src+1) *(dst+1)) +type)  & Integer.MAX_VALUE;
  }  /* hashCode() */

  /*------------------------------------------------------------------*/
  /** Compute the hash code of the extension edge.
   *  @return the hash code of the extension edge
   *  @since  2010.01.22 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public int hashCode ()
  {                             /* --- compute a hash code */
    return hashCode(this.code, this.src, this.dst);
  }  /* hashCode() */

  /*------------------------------------------------------------------*/
  /** Compare two extension edges.
   *  @param  obj the extension edge to compare to
   *  @return the comparison result, that is, <code>-1</code>,
   *          <code>0</code>, or <code>+1</code> as this extension
   *          edge is less than, equal to, or greater than the
   *          extension edge given as an argument
   *  @since  2010.01.22 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public int compareTo (Sortable obj)
  {                             /* --- compare two extension edges */
    ExtEdge edge = (ExtEdge)obj;
    if (this.code < edge.code) return -1;
    if (this.code > edge.code) return +1;
    if (this.src  < edge.src)  return -1;
    if (this.src  > edge.src)  return +1;
    if (this.dst  < edge.dst)  return -1;
    if (this.dst  > edge.dst)  return +1;
    return 0;                   /* return sign of the difference */
  }  /* compareTo() */          /* of the edge and node types */

}  /* class ExtEdge */


/*--------------------------------------------------------------------*/
/** Class for an extension edge manager.
 *  <p>An extension edge manager manages triples consisting of
 *  an edge type and two node types (source and destination),
 *  which describe potential extension edges.</p>
 *  @author Christian Borgelt
 *  @since  2010.01.22 */
/*--------------------------------------------------------------------*/
public class ExtMgr {

  /*------------------------------------------------------------------*/
  /*  instance variables                                              */
  /*------------------------------------------------------------------*/
  /** whether edges are to be treated as directed */
  protected boolean   dir  = false;
  /** the table for access via the source node type */
  protected ExtEdge[] exts = null;
  /** the hash table of the extension edges */
  protected ExtEdge[] bins = null;
  /** the number of added extension edges (with reversals) */
  protected int       cnt  = 0;
  /** the current extension edge */
  protected ExtEdge   curr = null;

  /*------------------------------------------------------------------*/
  /** Create an extension edge manager.
   *  @param  dir   whether to treat edges as directed
   *  @param  types the number of different node types
   *  @param  hsize the initial size of the hash table
   *  @since  2010.01.22 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public ExtMgr (boolean dir, int types, int hsize)
  {                             /* --- create an ext. edge manager */
    this.dir  = dir;            /* note directionality and */
    this.exts = new ExtEdge[types];   /* initialize arrays */
    this.bins = new ExtEdge[hsize];
  }  /* ExtMgr() */

  /*------------------------------------------------------------------*/
  /** Create an extension edge manager.
   *  @param  dir   whether to treat edges as directed
   *  @param  types the number of different node types
   *  @since  2021.10.06 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public ExtMgr (boolean dir, int types)
  { this(dir, types, 1023); }

  /*------------------------------------------------------------------*/
  /** Create an extension edge manager.
   *  @param  types the number of different node types
   *  @since  2010.01.22 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public ExtMgr (int types)
  { this(false, types, 1023); }

  /*------------------------------------------------------------------*/
  /** Reorganize the extension edge hash table.
   *  <p>The hash table of the extension manager is enlarged and
   *  the extension edges are rehashed to achieve faster access.</p>
   *  @since  2010.01.22 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  private void rehash ()
  {                             /* --- reorganize the repository */
    int       i, k;             /* loop variable, hash bin index */
    ExtEdge[] b;                /* buffer for old hash bin array */
    ExtEdge   e, r;             /* to traverse the hash bin lists */

    b = this.bins;              /* note the old hash bin array and */
    k = (b.length << 1) +1;     /* compute the new hash table size */
    this.bins = new ExtEdge[k]; /* allocate a new hash bin array */
    for (i = b.length; --i >= 0; ) {
      while (b[i] != null) {    /* traverse the nonempty bins */
        e = b[i]; r = (e.src == e.dst) ? e : e.next; b[i] = r.next;
        r.next = this.bins[k = e.hashCode() % this.bins.length];
        this.bins[k] = e;       /* add the element at the head */
      }                         /* of the approriate hash bin list */
    }                           /* in the new hash bin array */
  }  /* rehash() */

  /*------------------------------------------------------------------*/
  /** Add an extension edge.
   *  @param  edge the edge to add
   *  @since  2010.01.22 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void add (Edge edge)
  {                             /* --- add an extension edge */
    int     i;                  /* hash bin index */
    int     src, dst;           /* source and destination node type */
    int     sdg, ddg;           /* source and destination node degree */
    int     code;               /* edge code (incl. direction flag) */
    ExtEdge e, r;               /* to traverse a hash bin list */

    /* Extension edges that originate from the same edge, but have */
    /* opposite directions will be stored in consecutive elements  */
    /* of the overflow lists of the hash bins. The advantage is    */
    /* that updates of these two extension edges are easier to do. */
    src = edge.src.type;        /* get the types and degrees of */
    dst = edge.dst.type;        /* the source and destination node */
    if (src < dst) {            /* if edge is directed forward */
      sdg  = edge.src.deg;  ddg = edge.dst.deg;
      code = (this.dir) ?   edge.type << 1     : edge.type; }
    else {                      /* if edge is directed backwards */
      sdg  = edge.dst.deg;  ddg = edge.src.deg;
      src  = edge.dst.type; dst = edge.src.type;
      code = (this.dir) ?  (edge.type << 1) +1 : edge.type;
    }                           /* get destination and edge code */
    i = ExtEdge.hashCode(code, src, dst)
      % this.bins.length;       /* compute the hash bin index */
    for (e = this.bins[i]; e != null; e = r.next) {
      r = (e.src  == e.dst) ? e : e.next;
      if ((e.code == code)      /* traverse the corresp. hash bin and */
      &&  (e.src  == src)       /* try to find the extension edge */
      &&  (e.dst  == dst)) {    /* (same edge type/source/dest.) */
        if (sdg > e.deg) e.deg = sdg;
        if (ddg > r.deg) r.deg = ddg; return;
      }                         /* if the ext. edge already exists, */
    }                           /* update the maximum node degrees */

    if (src == dst) sdg = ddg = (sdg > ddg) ? sdg : ddg;
    e = new ExtEdge(code, src, dst, sdg);
    e.next = this.bins[ i ];    /* create a new extension edge */
    this.bins[ i ] = e;         /* and add it to the hash table */
    if (++this.cnt > this.bins.length)
      this.rehash();            /* reorganize the hash table */
    e.succ = this.exts[src];    /* add edge to the table that */
    this.exts[src] = e;         /* is indexed by the source type */

    if (src == dst) return;     /* check if reverse edge differs */
    if (this.dir) code ^= 1;    /* invert the direction flag */
    r = new ExtEdge(code, dst, src, ddg);
    r.next = e.next;            /* create reverse extension edge */
    e.next = r;                 /* and add it to the hash table */
    if (++this.cnt > this.bins.length)
      this.rehash();            /* reorganize the hash table */
    r.succ = this.exts[dst];    /* add reverse to the table that */
    this.exts[dst] = r;         /* is indexed by the source type */
  }  /* add() */

  /*------------------------------------------------------------------*/
  /** Sort the extension edges lexicographically.
   *  <p>This sort function uses a straightforward merge sort
   *  on the singly linked extension edge lists.</p>
   *  @since  2010.01.28 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void sort ()
  {                             /* --- sort the edges per node type */
    for (int i = this.exts.length; --i >= 0; ) {
      if (this.exts[i] != null) /* traverse the source node types */
        this.exts[i] = (ExtEdge)this.exts[i].sort();
    }                           /* sort the extension edge list */
  }  /* sort() */

  /*------------------------------------------------------------------*/
  /** Trim the extension edges.
   *  @param  coder the node type recoder with which to trim
   *  @since  2010.01.23 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void trim (Recoder coder)
  {                             /* --- trim the extension edges */
    int     i;                  /* loop variable */
    ExtEdge e, x;               /* to traverse the extension edges */

    for (i = this.exts.length; --i >= 0; ) {
      e = this.exts[i];         /* traverse the list per source type */
      if (e == null) continue;  /* skip empty source node lists */
      if (coder.isExcluded(e.src)) {  /* remove exluded sources */
        this.exts[i] = null; continue; }
      while (e.succ != null) {  /* while not at last element */
        x = (ExtEdge)e.succ;    /* get the successor element */
        if (coder.isExcluded(x.dst)) e.succ = x.succ;
        else                         e      = x;
      }                         /* remove excluded destinations */
      e = this.exts[i];         /* check the first list element */
      if (coder.isExcluded(e.dst)) this.exts[i] = (ExtEdge)e.succ;
    }                           /* remove it if it is excluded */
    for (i = this.bins.length; --i >= 0; ) {
      e = this.bins[i];         /* traverse the hash bins */
      if (e == null) continue;  /* skip empty hash bins */
      while (e.next != null) {  /* while not at last element */
        if (coder.isExcluded(e.next.src)
        ||  coder.isExcluded(e.next.dst)) e.next = e.next.next;
        else                              e      = e.next;
      }                         /* remove excluded node types */
      e = this.bins[i];         /* check the first list element */
      if (coder.isExcluded(e.src) || coder.isExcluded(e.dst))
        this.bins[i] = e.next;  /* remove the first list element */
    }                           /* if it has an excluded node type */
  }  /* trim() */

  /*------------------------------------------------------------------*/
  /** Initialize the traversal of extension edges.
   *  @param  src  the type of the source node
   *  @return the edge type of the first extension edge
   *          or <code>-1</code> if there is no edge
   *  @since  2010.01.22 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public int first (int src)
  {                             /* --- get the first extension edge */
    this.curr = this.exts[src]; /* get edge list of node type */
    if (this.curr == null) return -1;
    return (this.dir) ? this.curr.code >> 1 : this.curr.code;
  }  /* first() */              /* return the extension edge type */

  /*------------------------------------------------------------------*/
  /** Get the next extension edge.
   *  @return the edge type of the next extension edge
   *          or <code>-1</code> if there is no such edge
   *  @since  2010.01.22 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public int next ()
  {                             /* --- get the next extension edge */
    if (this.curr == null)      /* if no current element, abort, else */
      return -1;                /* go to the successor list element */
    this.curr = (ExtEdge)this.curr.succ;
    if (this.curr == null) return -1;
    return (this.dir) ? this.curr.code >> 1 : this.curr.code;
  }  /* next() */               /* return the extension edge type */

  /*------------------------------------------------------------------*/
  /** Get the edge type of the current extension edge.
   *  @return the edge type of the current extension edge
   *  @since  2010.01.22 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public int getType ()
  { return (this.dir) ? this.curr.code >> 1 : this.curr.code; }

  /*------------------------------------------------------------------*/
  /** Whether the edge is reversed (if edges are directed).
   *  @return whether the edge is reversed
   *  @since  2021.10.08 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public boolean isRevd ()
  { return (this.dir) ? ((this.curr.code & 1) != 0) : false; }

  /*------------------------------------------------------------------*/
  /** Get the source node type of the current extension edge.
   *  @return the source node type of the current extension edge
   *  @since  2021.10.06 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public int getSrc ()
  { return this.curr.src; }

  /*------------------------------------------------------------------*/
  /** Get the destination node type of the current extension edge.
   *  @return the destination node type of the current extension edge
   *  @since  2010.01.22 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public int getDest ()
  { return this.curr.dst; }

  /*------------------------------------------------------------------*/
  /** Get the maximum source node degree of the current extension edge.
   *  @return the maximum source node degree
   *          of the current extension edge
   *  @since  2010.01.28 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public int getDegree ()
  { return this.curr.deg; }

  /*------------------------------------------------------------------*/
  /** Show the content of an extension edge manager (for debugging).
   *  @since  2020.10.09 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void show ()
  {                             /* --- show extension edges */
    System.out.println("bins");
    for (int i = 0; i < this.bins.length; i++) {
      for (ExtEdge e = this.bins[i]; e != null; e = e.next) {
        char d = (this.dir && ((e.code & 1) != 0)) ? '<' : '>';
        System.out.print("  e:" +((this.dir) ? e.code >> 1 : e.code)
                      +d +" s:" +e.src +" d:" +e.dst
                         +" c:" +e.deg +"\n");
      }                         /* traverse the source node types */
    }                           /* and the edges for each */
    System.out.println("exts");
    for (int i = 0; i < this.exts.length; i++) {
      System.out.println("  " +i);
      for (ExtEdge e = this.exts[i]; e != null; e = (ExtEdge)e.succ) {
        char d = (this.dir && ((e.code & 1) != 0)) ? '<' : '>';
        System.out.print("  e:" +((this.dir) ? e.code >> 1 : e.code)
                      +d +" s:" +e.src +" d:" +e.dst
                         +" c:" +e.deg +"\n");
      }                         /* traverse the source node types */
    }                           /* and the edges for each */
    System.out.println("done");
  }  /* show() */

}  /* class ExtMgr */
