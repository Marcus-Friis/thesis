# MOSS - Molecular Substructure Miner

> Given a database of graphs, MoSS finds all (closed) frequent substructures, that is, all substructures that appear with a user-specified minimum frequency in the database (and do not have super-structures that occur with the same frequency). Alternatively, it finds molecular fragments that are frequent in the focus part of the database, but rare in the complement part, that is, that appear with at least a user-specified minimum frequency in the focus part of the database (and do not have super-structures that occur with the same frequency), but with no more than a user-specified maximum frequency in the complement part of the database. Such molecular substructures discriminate between the two parts of the database and thus may be called discriminative fragments.

Official docs can be found [here!](https://borgelt.net/doc/moss/moss.html)

Run `MOSS` as
```
java -cp moss.jar moss.Miner -inel -onel -x -D -m2 -n5 -s50 INPUT_FILE OUTPUT_FILE
```
Args:
- `-D` is the one telling Moss the input is directed.
- `-n` limits the size of the structures Moss will look for, in number of nodes.
- `-s` is the support threshold.
- `-C` allows for closed substructures (we should do this)

_Java pro tip:_
Increase Java's heap space with `-Xmx` followed by the allocated space e.g. `Xmx6g`.
```
java -Xmx6g -cp moss.jar moss.Miner -inel -onel -x -D -m2 -n5 -s50 INPUT_FILE OUTPUT_FILE
```

Our results are produced with the following command
```
java -Xmx6g -cp moss.jar moss.Miner -inel -onel -x -D -m2 -n4 -s10 -C -A ../../data/graph.nel ../../data/graph.nel.moss
```

## Michele's lovely email
Hi all,

I'm attaching a zip file for you. It contains three things:

- `pyrfume.gspan`, a sample dataset in NEList format I know it should work (just tested)
- `moss.jar`, the already compiled version of Moss that can understand directed networks
- `moss`, a folder with the source code in case you need to recompile because my jar doesn't work for you

Here's the line that I just successfully tested on my system:

```
java -cp moss.jar moss.Miner -inel -onel -x -D -m2 -n5 -s50 pyrfume.gspan pyrfume.moss
```

- The `-i` and `-o` flags tell the program to use the NEList format for both input and output;
- `-x` is simply not to exclude any node label;
- `-D` is the one telling Moss the input is directed (it actually isn't in pyrfume.gspan, but I added the flag so that you know);
- `-m2` is to avoid getting returned single-node patterns;
- `-n` you'd need to make sure your search doesn't explode, it limits the size of the structures Moss will look for, in number of nodes. You should figure out what's your best guess for this parameter;
- `-s` is the support threshold, of course you need to play with this as well

Hope this works for you too!
*Michele C*