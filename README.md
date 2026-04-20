# Bisection Value Iteration Replication Study Artifacts
Executable Binary for the Replication Study of Bisection Value Iteration conducted by me. 

To run this executable, run the command below as per your requirement.

```bash
./modest check filename.jani --alg IntervalIteration 
```

This is implemented in the MODEST toolset. 

For generating the graphs, run the included python files. 

parse_results.py will parse the txt documents and compile data in a csv file. Ensure filename is in the format : modelname.BVIResults.txt

plot_comparisons.py will generate comparison graphs based on the compiled csv file. 

lineplot.py will create a line graph of a predefined particular range of the three chosen algorithms from the csv file.