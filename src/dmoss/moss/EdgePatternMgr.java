/*----------------------------------------------------------------------
  File    : EdgePatternMgr.java
  Contents: manager for single edge patterns for rule induction
  Author  : Christian Borgelt
  History : 2020.10.16 file created
----------------------------------------------------------------------*/
package moss;

/*--------------------------------------------------------------------*/
/** Class for edge patterns (full and partial).
 *  <p>For partial edge patterns (only one incident node type fixed),
 *  the source type is set to the special value <code>IGNORE</code>.</p>
 *  @author Christian Borgelt
 *  @since  2020.10.16 */
/*--------------------------------------------------------------------*/
class EdgePattern implements Comparable<EdgePattern> {

  /*------------------------------------------------------------------*/
  /*  constants                                                       */
  /*------------------------------------------------------------------*/
  /* the pseudo-type of an incident node to ignore */
  public static final int IGNORE = Integer.MIN_VALUE;

  /*------------------------------------------------------------------*/
  /*  instance variables                                              */
  /*------------------------------------------------------------------*/
  /** the edge type */
  protected int         type;
  /** the source node type */
  protected int         src;
  /** the destination node type */
  protected int         dst;
  /** the support of the edge pattern */
  protected int         supp;
  /** the successor in a hash bin list */
  protected EdgePattern succ;

  /*------------------------------------------------------------------*/
  /** Create an edge pattern.
   *  <p>For a partial edge pattern (only one incident node type),
   *  the special value <code>IGNORE</code> should be passed for the
   *  parameter <code>src</code> or <code>dst</code>.</p>
   *  @param  type the edge type
   *  @param  src  the source      node type (or <code>IGNORE</code>)
   *  @param  dst  the destination node type (or <code>IGNORE</code>)
   *  @param  supp the support of the edge pattern
   *  @since  2020.10.16 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public EdgePattern (int type, int src, int dst, int supp)
  {                             /* --- create an extension edge */
    this.type = type;           /* note the edge type */
    this.src  = src;            /* and  the source      node type */
    this.dst  = dst;            /* and  the destination node type */
    this.supp = supp;           /* and  the edge pattern support */
    this.succ = null;           /* there is no successor yet */
  }  /* EdgePattern() */

  /*------------------------------------------------------------------*/
  /** Check whether two edge patterns are equal.
   *  <p>This function exists only in order to avoid certain warnings
   *  due to the existence of a <code>hashCode</code> function.</p>
   *  @param  obj the edge pattern to compare to
   *  @return whether the two edge patterns are equal
   *  @since  2020.10.16 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public boolean equals (Object obj)
  {                             /* --- check for equality */
    return (this.type == ((EdgePattern)obj).type)
        && (this.src  == ((EdgePattern)obj).src)
        && (this.dst  == ((EdgePattern)obj).dst);
  }  /* equals() */

  /*------------------------------------------------------------------*/
  /** Compute the hash code of an edge pattern.
   *  @param  type the edge type
   *  @param  src  the source node type
   *  @param  dst  the destination node type
   *  @return the hash code of an edge pattern
   *  @since  2020.10.16 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public static int hashCode (int type, int src, int dst)
  {                             /* --- compute a hash code */
    return (((src+1) *(dst+2)) +type) & Integer.MAX_VALUE;
  }  /* hashCode() */

  /*------------------------------------------------------------------*/
  /** Compute the hash code of the edge pattern.
   *  @return the hash code of the edge pattern
   *  @since  2020.10.16 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public int hashCode ()
  { return hashCode(type, src, dst); }

  /*------------------------------------------------------------------*/
  /** Compare two edge patterns.
   *  @param  obj the edge pattern to compare to
   *  @return the comparison result, that is, <code>-1</code>,
   *          <code>0</code>, or <code>+1</code> as this edge pattern
   *          is less than, equal to, or greater than the edge pattern
   *          given as an argument
   *  @since  2020.10.16 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public int compareTo (EdgePattern obj)
  {                             /* --- compare two edge patterns */
    if (this.type < obj.type) return -1;
    if (this.type > obj.type) return +1;
    if (this.src  < obj.src)  return -1;
    if (this.src  > obj.src)  return +1;
    if (this.dst  < obj.dst)  return -1;
    if (this.dst  > obj.dst)  return +1;
    return 0;                   /* return sign of the difference */
  }  /* compareTo() */          /* of the edge and node types */

}  /* class EdgePattern */


/*--------------------------------------------------------------------*/
/** Class for an edge pattern manager.
 *  <p>An edge pattern manager collects information about single edge
 *  patterns, both full (both incident node types considered) and
 *  partial (only one or no incident node type considered).</p>
 *  @author Christian Borgelt
 *  @since  2020.10.16 */
/*--------------------------------------------------------------------*/
public class EdgePatternMgr {

  /*------------------------------------------------------------------*/
  /*  instance variables                                              */
  /*------------------------------------------------------------------*/
  /** whether edges are to be treated as directed */
  protected boolean       dir   = false;
  /** the hash table of the extension edges */
  protected EdgePattern[] bins  = null;
  /** the number of added edge patterns (full and partial) */
  protected int           cnt   = 0;
  /** the support values for each edge type */
  protected int[]         supps = null;
  /** the base support (largest possible support) */
  protected int           base  = 0;

  /*------------------------------------------------------------------*/
  /** Create an edge pattern manager.
   *  @param  dir   whether edges are to be treated as directed
   *  @param  types the number of different edge types
   *  @param  hsize the initial size of the hash table
   *  @param  base  the base support (largest possible support)
   *  @since  2021.10.10 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public EdgePatternMgr (boolean dir, int types, int hsize, int base)
  {                             /* --- create an edge pattern manager */
    this.dir   = dir;           /* note edge directionality */
    this.bins  = new EdgePattern[hsize];
    this.supps = new int[types];/* create hash bins and support array */
    this.base  = base;          /* note the base support */
  }  /* EdgePatternMgr() */

  /*------------------------------------------------------------------*/
  /** Create an edge pattern manager.
   *  @param  dir   whether edges are to be treated as directed
   *  @param  types the number of different edge types
   *  @param  base  the base support (largest possible support)
   *  @since  2021.10.10 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public EdgePatternMgr (boolean dir, int types, int base)
  { this(dir, types, 1023, base); }

  /*------------------------------------------------------------------*/
  /** Create an edge pattern manager.
   *  @param  types the number of different edge types
   *  @param  hsize the initial size of the hash table
   *  @param  base  the base support (largest possible support)
   *  @since  2020.10.16 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public EdgePatternMgr (int types, int hsize, int base)
  { this(false, types, hsize, base); }

  /*------------------------------------------------------------------*/
  /** Create an extension edge manager.
   *  @param  types the number of different edge types
   *  @param  base  the base support (largest possible support)
   *  @since  2020.10.16 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public EdgePatternMgr (int types, int base)
  { this(false, types, 1023, base); }

  /*------------------------------------------------------------------*/
  /** Reorganize the edge pattern hash table.
   *  <p>The hash table of the edge pattern manager is enlarged and
   *  the edge patterns are rehashed to achieve faster access.</p>
   *  @since  2020.10.16 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  private void rehash ()
  {                             /* --- reorganize the repository */
    int           i, k;         /* loop variable, hash bin index */
    EdgePattern[] b;            /* buffer for old hash bin array */
    EdgePattern   e, r;         /* to traverse the hash bin lists */

    b = this.bins;              /* note the old hash bin array and */
    k = (b.length << 1) +1;     /* compute the new hash table size */
    this.bins = new EdgePattern[k]; /* allocate a new hash bin array */
    for (i = b.length; --i >= 0; ) {
      while (b[i] != null) {    /* traverse the nonempty bins */
        e = b[i]; b[i] = e.succ;/* traverse the edge patterns */
        e.succ = this.bins[k = e.hashCode() % this.bins.length];
        this.bins[k] = e;       /* add the element at the head */
      }                         /* of the approriate hash bin list */
    }                           /* in the new hash bin array */
  }  /* rehash() */

  /*------------------------------------------------------------------*/
  /** Add an edge pattern (internal function).
   *  @param  type the edge type
   *  @param  src  the node type of one   incident node (source)
   *  @param  dst  the node type of other incident node (destination)
   *  @param  supp the support of the edge pattern
   *  @since  2020.10.16 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  private void addOne (int type, int src, int dst, int supp)
  {                             /* --- add an edge pattern */
    int         i;              /* hash bin index */
    EdgePattern e;              /* to traverse a hash bin list */

    i = EdgePattern.hashCode(type, src, dst)
      % this.bins.length;       /* compute the hash bin index */
    for (e = this.bins[i]; e != null; e = e.succ) {
      if ((e.type == type)      /* traverse the corresp. hash bin and */
      &&  (e.src  == src)       /* try to find the edge pattern */
      &&  (e.dst  == dst)) {    /* (same source/dest./edge type) */
        if (supp > e.supp) e.supp = supp;
        return;                 /* if the edge pattern is found, */
      }                         /* update the edge pattern support */
    }                           /* then abort the function */
    e = new EdgePattern(type, src, dst, supp);
    e.succ = this.bins[i];      /* create a new extension edge */
    this.bins[i] = e;           /* and add it to the hash table */
    if (++this.cnt > this.bins.length)
      this.rehash();            /* reorganize the hash table */
  }   /* addOne() */

  /*------------------------------------------------------------------*/
  /** Add an edge pattern.
   *  @param  type the edge type
   *  @param  src  the node type of one   incident node (source)
   *  @param  dst  the node type of other incident node (destination)
   *  @param  supp the support of the edge pattern
   *  @since  2020.10.16 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void add (int type, int src, int dst, int supp)
  {                             /* --- add an edge pattern */
    if (supp > this.supps[type])/* update the edge type support */
      this.supps[type] = supp;  /* (maximum over incident node types) */
    this.addOne(type, src,                dst, supp);
    this.addOne(type, EdgePattern.IGNORE, dst, supp);
    if (this.dir)               /* if edge is directed */
      this.addOne(type, src, EdgePattern.IGNORE, supp);
    else if (src != dst) {      /* if edge is undirected */
      this.addOne(type, dst,                src, supp);
      this.addOne(type, EdgePattern.IGNORE, src, supp);
    }                           /* add alternative edge patterns */
  }  /* add() */

  /*------------------------------------------------------------------*/
  /** Add an edge pattern.
   *  @param  edge an edge representing the pattern
   *  @param  supp the support of the edge pattern
   *  @since  2020.10.16 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void add (Edge edge, int supp)
  { this.add(edge.type, edge.src.type, edge.dst.type, supp); }

  /*------------------------------------------------------------------*/
  /** Get the base support (largest possible support).
   *  @return the base support (largest possible support)
   *  @since  2020.10.16 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public int getSupp ()
  { return this.base; }

  /*------------------------------------------------------------------*/
  /** Get the support of an edge pattern (edge type only).
   *  @param  type the edge type
   *  @return the support of the edge pattern
   *  @since  2020.10.16 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public int getSupp (int type)
  { return this.supps[type]; }

  /*------------------------------------------------------------------*/
  /** Get the support of an edge pattern (edge type and two node types).
   *  @param  type the edge type
   *  @param  src  the node type of one   incident node (source)
   *  @param  dst  the node type of other incident node (destination)
   *  @return the support of the edge pattern
   *  @since  2020.10.16 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public int getSupp (int type, int src, int dst)
  {                             /* --- get edge pattern support */
    int         i;              /* hash bin index */
    int         x;              /* node type exchange buffer */
    EdgePattern e;              /* to traverse a hash bin list */

    i = EdgePattern.hashCode(type, src, dst)
      % this.bins.length;       /* compute the hash bin index */
    for (e = this.bins[i]; e != null; e = e.succ) {
      if ((e.type == type)      /* traverse the corresp. hash bin and */
      &&  (e.src  == src)       /* try to find the extension edge */
      &&  (e.dst  == dst))      /* (same source/dest./edge type) */
        return e.supp;          /* if edge found, return frequency */
    }
    return 0;                   /* if pattern not found, return 0 */
  }  /* getSupp() */

  /*------------------------------------------------------------------*/
  /** Get the support of an edge pattern (given an example edge).
   *  @param  edge a example edge
   *  @return the support of the edge pattern
   *  @since  2020.10.16 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public int getSupp (Edge edge)
  { return this.getSupp(edge.type, edge.src.type, edge.dst.type); }

  /*------------------------------------------------------------------*/
  /** Get the support of an edge pattern (given an example edge).
   *  @param  edge a example edge
   *  @return the support of the edge pattern
   *  @since  2020.10.16 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public int getSuppSrc (Edge edge)
  {                             /* --- get edge support        */
    return (this.dir)           /*     for a given source node */
         ? this.getSupp(edge.type, edge.src.type, EdgePattern.IGNORE)
         : this.getSupp(edge.type, EdgePattern.IGNORE, edge.src.type);
  }  /* getSuppSrc() */

  /*------------------------------------------------------------------*/
  /** Get the support of an edge pattern (given an example edge),
   *  for an unknown source node.
   *  @param  edge a example edge
   *  @return the support of the edge pattern
   *  @since  2021.10.10 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public int getSuppDest (Edge edge)
  { return this.getSupp(edge.type, EdgePattern.IGNORE, edge.dst.type); }

  /*------------------------------------------------------------------*/
  /** Show the content of an edge pattern manager (for debugging).
   *  @since  2020.10.16 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void show ()
  {                             /* --- show extension edges */
    int         i;              /* hash bin index */
    EdgePattern e;              /* to traverse a hash bin list */

    System.out.println("supps");
    for (i = 0; i < this.supps.length; i++)
      System.out.print("  " +i +": " +this.supps[i] +"\n");
    System.out.println("bins");
    for (i = 0; i < this.bins.length; i++) {
      for (e = this.bins[i]; e != null; e = e.succ) {
        System.out.print("  " +e.type +" ");
        if (e.src == EdgePattern.IGNORE) System.out.print("*");
        else                             System.out.print(e.src);
        System.out.print(" " +e.dst +" " +e.supp +"\n");
      }                         /* traverse the source node types */
    }                           /* and the edges for each */
    System.out.println("done");
  }  /* show() */

}  /* class EdgePatternMgr */
