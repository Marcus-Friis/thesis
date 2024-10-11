/*----------------------------------------------------------------------
  File    : TableReader.java
  Contents: class for readers for table formats
  Author  : Christian Borgelt
  History : 2007.03.04 file created as TableFmt.java
            2007.06.26 split into reader and writer
            2016.04.07 StringBuffer replaced by StringBuilder
            2020.10.23 split of from line notation based reader
            2020.10.25 function eof() added (check end of file)
----------------------------------------------------------------------*/
package moss;

import java.io.IOException;
import java.io.Reader;
import java.io.StringReader;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.PushbackReader;

/*--------------------------------------------------------------------*/
/** Class for readers for simple table formats.
 *  @author Christian Borgelt
 *  @since  2007.03.04 */
/*--------------------------------------------------------------------*/
public class TableReader extends PushbackReader {

  /*------------------------------------------------------------------*/
  /*  constants                                                       */
  /*------------------------------------------------------------------*/
  /** class/type flag: record separator */
  public static final int RECSEP  = 0x01;
  /** class/type flag: field separator */
  public static final int FLDSEP  = 0x02;
  /** class/type flag: blank character */
  public static final int BLANK   = 0x04;
  /** class/type flag: comment character */
  public static final int COMMENT = 0x08;
  /** the field names for the different file types */

  /*------------------------------------------------------------------*/
  /*  instance variables                                              */
  /*------------------------------------------------------------------*/
  /** the character flags */
  protected char[]        cflags;
  /** the buffer for the next table field */
  protected StringBuilder buf;
  /** the next table field */
  protected String        field;
  /** the last delimiter read: -1 if end of file/input,
   *  0 if field separator, 1 if record separator */
  protected int           delim;
  /** the current record number */
  protected int           recno;

  /*------------------------------------------------------------------*/
  /** Create a table reader with default character flags.
   *  <p>By default the following character settings are used:<br>
   *  record separators: "\n", field separators: " \t", blanks: " \r\t",
   *  comment characters: "#".</p>
   *  @param  reader the reader to work on
   *  @since  2006.10.05 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public TableReader (Reader reader)
  {                             /* --- create a table reader */
    super(reader, 1024);        /* init. reader and store read mode */
    this.buf    = new StringBuilder();
    this.cflags = new char[256];
    this.cflags['\n'] = RECSEP; /* initialize the character flags */
    this.cflags['\t'] = this.cflags[','] = FLDSEP;
    this.cflags['\r'] = this.cflags[' '] = BLANK;
    this.cflags['#' ] = COMMENT;
    this.field  = null;         /* no field has been read yet */
    this.delim  = -1;           /* set the delimiter to a default */
    this.recno  =  1;           /* clear the record counter */
  }  /* TableReader() */

  /*------------------------------------------------------------------*/
  /** Set the characters for a specific type/class.
   *  @param  type  the type/class of the characters to set;
   *                must be one of the constants <code>RECSEP</code>,
   *                <code>FLDSEP</code>, <code>BLANK</code>, or
   *                <code>COMMENT</code> (or a combination of these,
   *                by binary or)
   *  @param  chars the characters to set
   *  @since  2007.06.26 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void setChars (int type, String chars)
  {                             /* --- set the characters of a class */
    for (int i = this.cflags.length; --i >= 0; )
      this.cflags[i] &= ~type;  /* clear flags for all characters */
    for (int i = chars.length();     --i >= 0; )
      this.cflags[chars.charAt(i)] |= type;
  }  /* setChars() */           /* set flags for given characters */

  /*------------------------------------------------------------------*/
  /** Set the characters for all types.
   *  <p>If a parameter is <code>null</code>, the corresponding
   *  character flags are maintained.</p>
   *  @param  recseps the record  separators
   *  @param  fldseps the field   separators
   *  @param  blanks  the blank   characters
   *  @param  comment the comment characters
   *  @since  2007.05.17 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public void setChars (String recseps, String fldseps,
                        String blanks,  String comment)
  {                             /* --- set characters of all classes */
    if (recseps != null) this.setChars(RECSEP,  recseps);
    if (fldseps != null) this.setChars(FLDSEP,  fldseps);
    if (blanks  != null) this.setChars(BLANK,   blanks);
    if (comment != null) this.setChars(COMMENT, comment);
  }  /* setChars() */

  /*------------------------------------------------------------------*/
  /** Check whether a given character is in a given class
   *  or of a given type.
   *  @param  type the type/class for which to query;
   *               must be one of the constants <code>RECSEP</code>,
   *               <code>FLDSEP</code>, <code>BLANK</code>, or
   *               <code>COMMENT</code>
   *  @param  c    the character to query
   *  @return whether the character is in the given class
   *  @since  2006.10.06 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public boolean isType (int type, char c)
  { return (this.cflags[c] & type) != 0; }

  /*------------------------------------------------------------------*/
  /** Get the classes/types of a given character.
   *  @param  c the character to query
   *  @return the classes character is in, as a combination of the
   *          flags <code>RECSEP</code>, <code>FLDSEP</code>,
   *          <code>BLANK</code>, or <code>COMMENT</code>
   *  @since  2006.10.06 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public int getTypes (char c)
  { return this.cflags[c]; }

  /*------------------------------------------------------------------*/
  /** Get a string stating the current record number.
   *  Useful for error reporting.
   *  @return a string stating the current record number
   *          in the format "(record xxx)"
   *  @since  2007.01.31 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public String rno ()
  { return this.rno(0); }

  /*------------------------------------------------------------------*/
  /** Get a string stating the current record number.
   *  <p>Useful for error reporting.</p>
   *  @param  offset the offset to add to the record number
   *  @return a string stating the current record number
   *          in the format "(record xxx)"
   *  @since  2007.03.29 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public String rno (int offset)
  { return " (record " +(this.recno +offset) +")"; }

  /*------------------------------------------------------------------*/
  /** Check for end of file.
   *  @return whether at end of file
   *  @since  2020.10.25 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public boolean eof () throws IOException
  {                             /* --- check for end of file */
    int c = this.read();        /* get and check the next character */
    if (c < 0) return true;     /* if there is none, at end of file */
    this.unread(c);             /* push back the character read */
    return false;               /* return 'not at end of file' */
  }  /* eof() */

  /*------------------------------------------------------------------*/
  /** Read the next field/cell of the table.
   *  <p>Note that a record separator is (virtually) inserted at the
   *  end of the file/input if the file/input does not end with a
   *  record separator.</p>
   *  @return the type of the delimiter of the field read:
   *          <p><table cellpadding=0 cellspacing=0>
   *          <tr><td>-1,&nbsp;</td>
   *              <td>if end of file/input,</td></tr>
   *          <tr><td align="right">0,&nbsp;</td>
   *              <td>if field separator,</td>
   *          <tr><td>+1,&nbsp;</td>
   *              <td>if record separator.</td></tr>
   *          </table></p>
   *  @throws IOException if an i/o error occurs
   *  @since  2006.10.05/2007.06.26 (Christian Borgelt) */
  /*------------------------------------------------------------------*/

  public int readField () throws IOException
  {                             /* --- read the next field */
    int c, f, i;                /* character, flags, index */

    this.field = null;          /* initialize the field */
    c = this.read();            /* get and check the next character */
    if (c < 0) return this.delim = -1;

    /* --- skip comment records --- */
    if (this.delim != 0) {      /* if at the start of a record */
      while ((c < this.cflags.length)     /* comment read loop */
      &&     ((this.cflags[c] & COMMENT) != 0)) {
        this.recno++;           /* count the record to be read */
        while ((c >= this.cflags.length)
        ||     ((this.cflags[c] & RECSEP) == 0)) {
          c = this.read();      /* get and check the next character */
          if (c < 0) return this.delim = -1;
        }                       /* read up to a record separator */
        c = this.read();        /* get the next character */
        if (c < 0) return this.delim = -1;
      }                         /* check for end of file/input */
    }                           /* (comment records are skipped) */

    /* --- skip leading blanks --- */
    while ((c < this.cflags.length)
    &&     ((this.cflags[c] & BLANK) != 0)) {
      c = this.read();          /* get and check the next character */
      if (c < 0) return this.delim = 1;
    }
    /* Note that after at least one valid character was read, even  */
    /* if it is a blank, the end of file/input is translated into a */
    /* record separator. -1 is returned only if no character could  */
    /* be read before the end of file/input is encountered.         */

    /* --- read the field --- */
    if (c < this.cflags.length) {
      f = this.cflags[c];       /* get the character class and */
      if ((f & RECSEP) != 0) {  /* check for record separator */
        this.recno++; return this.delim = 1; }
      if ((f & FLDSEP) != 0) {  /* check for field separator */
                      return this.delim = 0; }
    }                           /* return an empty field */
    this.buf.setLength(0);      /* clear the read buffer */
    while (true) {              /* read the field value */
      this.buf.append((char)c); /* store the character in the buffer */
      c = this.read();          /* get the next character */
      if (c <  0)            { this.delim = 1;               break; }
      if (c >= this.cflags.length) continue;
      f = this.cflags[c];       /* check for record/field separator */
      if ((f & RECSEP) != 0) { this.delim = 1; this.recno++; break; }
      if ((f & FLDSEP) != 0) { this.delim = 0;               break; }
    }                           /* read up to a separator */

    /* --- remove trailing blanks --- */
    i = this.buf.length();      /* find index of last non-blank char. */
    do { f = this.buf.charAt(--i); }
    while ((f < this.cflags.length)
    &&     ((this.cflags[f] & BLANK) != 0));
    this.field = this.buf.substring(0, ++i);

    /* --- skip trailing blanks --- */
    if (this.delim != 0)        /* if not at a field separator, */
      return this.delim;        /* abort the function directly */
    while ((c < this.cflags.length)
    &&     ((this.cflags[c] & BLANK) != 0)) {
      c = this.read();          /* get the next character */
      if (c < 0) return this.delim = 1;
    }                           /* skip trailing blanks */
    f = (c < this.cflags.length) ? this.cflags[c] : 0;
    if ((f & RECSEP) != 0) {    /* check for a record separator */
      this.recno++; return this.delim = 1; }
    if ((f & FLDSEP) == 0) this.unread(c);
    return this.delim = 0;      /* set and return the delimiter type */
  }  /* readField() */

}  /* class TableReader */
