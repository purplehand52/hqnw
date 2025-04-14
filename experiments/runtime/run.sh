declare DIR=experiments/runtime

echo -n > $DIR/out.csv
for num_clients in {10,15,20,25,30}; do
    echo "${num_clients} 300 0.03 0.25 0.1 10 7" > inp-params.txt
    python src/gur_solver.py runtimes
done

python $DIR/plot.py clients

echo -n > $DIR/out.csv
for num_repeaters in {250,300,350,400,450}; do
    echo "18 ${num_repeaters} 0.03 0.25 0.2 10 7" > inp-params.txt
    python src/gur_solver.py runtimes
done

python $DIR/plot.py repeaters

echo -n > $DIR/out.csv
for rep_coeff in {0.01,0.02,0.03,0.04,0.05}; do
    echo "15 300 ${rep_coeff} 0.25 0.2 10 7" > inp-params.txt
    python src/gur_solver.py runtimes
done

python $DIR/plot.py rep_coeff