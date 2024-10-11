/*----------------------------------------------------------------------
  File    : Sortable.java
  Contents: class for sortable linked lists (sorting with merge sort)
  Author  : Christian Borgelt
  History : 2020.20.31 file created
----------------------------------------------------------------------*/
package moss;

/*--------------------------------------------------------------------*/
/** Abstract class for sortable linked lists.
 *  Sorting is done with standard merge sort.
 *  @author Christian Borgelt
 *  @since  2010.01.22 */
/*--------------------------------------------------------------------*/
abstract class Sortable implements Comparable<Sortable> {

  /*------------------------------------------------------------------*/
  /*  instance variables                                              */
  /*------------------------------------------------------------------*/
  /** the successor in a list */
  protected Sortable succ;

  /*------------------------------------------------------------------*/
  /** Merge two (sorted) lists into one (merge sort phase).
   *  @param  obj  the list to merge this list with
   *  @return the merged lists
   *  @since  2020.10.31 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  protected Sortable merge (Sortable obj)
  {                             /* --- merge extension edge lists */
    Sortable src;               /* to traverse this edge list */
    Sortable out, end;          /* start and end of output list */

    if (obj == null)            /* if the argument list is empty, */
      return this;              /* simply retutn this list */
    if (this.compareTo(obj) < 0)/* start output with smaller element */
         { end = out = this; src = this.succ; }
    else { end = out = obj;  src = this; obj = obj.succ; }
    while ((src != null)        /* while both source lists */
    &&     (obj != null)) {     /* are not empty */
      if (src.compareTo(obj) < 0)
           { end = end.succ = src; src = src.succ; }
      else { end = end.succ = obj; obj = obj.succ; }
    }                           /* transfer the smaller element */
    end.succ = (src != null) ? src : obj;
    return out;                 /* append remaining source elements */
  }  /* merge() */              /* and return the merge result */

  /*------------------------------------------------------------------*/
  /** Sort a sortable list.
   *  @return the sorted list
   *  @since  2020.10.31 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  protected Sortable sort ()
  {                             /* --- sort a sortable list */
    Sortable e, d;              /* to traverse the list */

    if (this.succ == null)      /* if there is only one element, */
      return this;              /* simply return it */
    for (d = this, e = d.succ; e != null; ) {
      e = e.succ;               /* traverse the sortable list */
      if (e != null) { e = e.succ; d = d.succ; }
    }                           /* one step on d, two steps on e */
    e = d.succ; d.succ = null;  /* get second list, terminate first */
    return this.sort().merge(e.sort());
  }  /* sort() */               /* sort sublists and then merge them */

}  /* class Sortable */
