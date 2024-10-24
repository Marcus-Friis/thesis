#!/bin/bash

# Default values for optional parameters
MEMORY="6G"              # Java heap memory (e.g., -Xmx6g)
DATA_FILE="../../data/graph.nel" # Default input data file
MOSS_JAR="moss.jar"      # Path to MoSS jar file
MIN_NODE_SIZE=2          # Minimum size of structures to consider (default: -m2)
MAX_NODE_SIZE=4          # Maximum size of structures to consider (default: -n4)
SUPPORT_THRESHOLD=50     # Minimum support threshold (default: -s50)

# Function to display usage
usage() {
    echo "Usage: $0 [-r memory] [-d data_file] [-x java_max_heap] [-m min_node_size] [-n max_node_size] [-s support_threshold] [-h]"
    echo ""
    echo "Options:"
    echo "  -r    Java heap memory allocation (default: 6G)"
    echo "  -d    Data file to parse (default: ../../data/graph.nel)"
    echo "  -x    Java maximum heap size (default: 6G)"
    echo "  -m    Minimum size of structures to consider (default: 2)"
    echo "  -n    Maximum size of structures to consider (default: 4)"
    echo "  -s    Support threshold (default: 50)"
    echo "  -h    Display this help message"
    exit 0
}

# Parse command-line arguments
while getopts "r:p:d:j:x:m:n:s:h" opt; do
  case ${opt} in
    r ) MEMORY=$OPTARG ;;
    d ) DATA_FILE=$OPTARG ;;
    x ) MEMORY=$OPTARG ;; # -x now controls Java's maximum heap size (Xmx)
    m ) MIN_NODE_SIZE=$OPTARG ;;  # -m sets minimum node size (default: 2)
    n ) MAX_NODE_SIZE=$OPTARG ;;  # -n sets maximum node size (default: 5)
    s ) SUPPORT_THRESHOLD=$OPTARG ;;  # -s sets support threshold (default: 10)
    h ) usage ;;           # If -h or --help is passed, show usage information
    * ) usage ;;
  esac
done

# Ensure the necessary parameters are set
if [[ -z "$DATA_FILE" ]]; then
    echo "Error: Data file must be specified."
    usage
fi

# Extract base name of the data file for output naming
DATA_BASE=$(basename "$DATA_FILE" .nel)

# Create a smart output file name based on data file and parameters
OUTPUT_FILE="${DATA_BASE}_m${MIN_NODE_SIZE}_n${MAX_NODE_SIZE}_s${SUPPORT_THRESHOLD}.moss"

# Create a dynamic job name based on the parameters
JOB_NAME="moss_${DATA_BASE}_m${MIN_NODE_SIZE}_n${MAX_NODE_SIZE}_s${SUPPORT_THRESHOLD}"
LOG_FILE="job_${JOB_NAME}_$(date +%Y%m%d_%H%M%S).out"

# Print job configuration for reference
echo "Job Configuration:"
echo "  Java heap memory:     $MEMORY"
echo "  Data file:            $DATA_FILE"
echo "  Output file:          $OUTPUT_FILE"
echo "  Min node size (-m):   $MIN_NODE_SIZE"
echo "  Max node size (-n):   $MAX_NODE_SIZE"
echo "  Support threshold (-s): $SUPPORT_THRESHOLD"
echo "  Job name:             $JOB_NAME"
echo "  Log file:             $LOG_FILE"

# SLURM job script submission
sbatch <<EOF
#!/bin/bash
#SBATCH --job-name=$JOB_NAME         # Job name
#SBATCH --output=$LOG_FILE           # Name of output file
#SBATCH --partition=brown            # Partition to run on
#SBATCH --mem=$MEMORY                # Memory allocation

module load Java/11.0.2

# Run MOSS Miner with the given parameters
echo "Running MOSS Miner with java -Xmx$MEMORY -cp $MOSS_JAR moss.Miner -inel -onel -x -D -m$MIN_NODE_SIZE -n$MAX_NODE_SIZE -s$SUPPORT_THRESHOLD -C -A $DATA_FILE $OUTPUT_FILE"
java -Xmx$MEMORY -cp $MOSS_JAR moss.Miner -inel -onel -x -D -m$MIN_NODE_SIZE -n$MAX_NODE_SIZE -s$SUPPORT_THRESHOLD -C -A $DATA_FILE $OUTPUT_FILE
EOF
