import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------------------------------
# 1) Qui sotto prepara i dati: per ogni N totale di task,
#    indica quanti ne vanno al Nodo 1, Nodo 2, Nodo 3.
#    ► Se hai un log reale, leggilo con pandas e riempi queste tre liste.
#    ► Se vuoi solo una demo, lascio un esempio di round-robin.
# ------------------------------------------------------------------
n_tasks = np.arange(1, 101)          # 1 … 100 task in ingresso
tasks_node1 = (n_tasks + 2) // 3     # round-robin fittizio
tasks_node2 = (n_tasks + 1) // 3
tasks_node3 =  n_tasks // 3

# ------------------------------------------------------------------
# 2) Grafico: tre curve, una per nodo.
# ------------------------------------------------------------------
plt.figure(figsize=(8, 5))
plt.plot(n_tasks, tasks_node1, label="Nodo 1")
plt.plot(n_tasks, tasks_node2, label="Nodo 2")
plt.plot(n_tasks, tasks_node3, label="Nodo 3")

plt.xlabel("Numero totale di task in ingresso")
plt.ylabel("Task assegnati al nodo")
plt.title("Comportamento dello scheduler")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
