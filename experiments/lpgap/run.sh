echo -n > experiments/lpgap/out.csv
for alpha in {0.5,1.0,1.5,2.0,2.5,3.0}; do
    echo "20 300 0.05 0.25 0.2 10 7 ${alpha}" > inp-params.txt
    python src/gur_solver.py lpgap
done

python experiments/lpgap/plot.py