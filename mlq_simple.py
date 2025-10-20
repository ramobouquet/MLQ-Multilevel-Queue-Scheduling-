# mlq_simple.py
from collections import deque
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Proc:
    label: str
    bt: int
    at: int
    q: int
    pr: int
    remaining: int = 0
    start: Optional[int] = None
    completion: Optional[int] = None

    def __post_init__(self):
        self.remaining = self.bt

def read_input(path: str) -> List[Proc]:
    procs = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = [p.strip() for p in line.split(';') if p.strip()!='']
            if len(parts) < 5:
                continue
            label, bt, at, q, pr = parts[:5]
            procs.append(Proc(label, int(bt), int(at), int(q), int(pr)))
   
    procs.sort(key=lambda p: (p.at, -p.pr, p.label))
    return procs

def write_output(path: str, results: List[Proc]):
    with open(path, 'w', encoding='utf-8') as f:
        f.write("# etiqueta; BT; AT; Q; Pr; WT; CT; RT; TAT\n")
        total_wt = total_ct = total_rt = total_tat = 0.0
        n = len(results)
        for p in sorted(results, key=lambda x: x.label):
            tat = p.completion - p.at
            wt = tat - p.bt
            rt = (p.start - p.at) if p.start is not None else 0
            f.write(f"{p.label};{p.bt};{p.at};{p.q};{p.pr};{wt};{p.completion};{rt};{tat}\n")
            total_wt += wt
            total_ct += p.completion
            total_rt += rt
            total_tat += tat
        if n > 0:
            f.write(f"\nWT={total_wt/n}; CT={total_ct/n}; RT={total_rt/n}; TAT={total_tat/n};\n")

def mlq_run(procs: List[Proc], q1_quantum=3, q2_quantum=5):
    q_ready = {1: deque(), 2: deque(), 3: deque()}
    t = 0
    procs_by_arrival = list(procs)
    n = len(procs_by_arrival)
    finished = []
    i = 0

    current = None
    current_quantum_used = 0  

    if n>0:
        t = procs_by_arrival[0].at

    while len(finished) < n:
        while i < n and procs_by_arrival[i].at <= t:
            p = procs_by_arrival[i]
            q_ready[p.q].append(p)
            i += 1

        if current is None:
            chosen_q = None
            for q in (1,2,3):
                if q_ready[q]:
                    chosen_q = q
                    break
            if chosen_q is None:
                if i < n:
                    t = procs_by_arrival[i].at
                    continue
                else:
                    break
            if chosen_q in (1,2):  
                current = q_ready[chosen_q].popleft()
                current_quantum_used = 0
            else:  
                current = q_ready[3].popleft()
                current_quantum_used = 0

       
        if current.start is None:
            current.start = t

        current.remaining -= 1
        current_quantum_used += 1
        t += 1  

        
        while i < n and procs_by_arrival[i].at <= t:
            p = procs_by_arrival[i]
            q_ready[p.q].append(p)
            i += 1
           
        if current.remaining == 0:
            current.completion = t
            finished.append(current)
            current = None
            current_quantum_used = 0
            continue

        
        if current.q == 1:
            if current_quantum_used >= q1_quantum:
                q_ready[1].append(current)
                current = None
                current_quantum_used = 0
                continue
          
        elif current.q == 2:

            if q_ready[1]:
                q_ready[2].append(current)
                current = None
                current_quantum_used = 0
                continue
            if current_quantum_used >= q2_quantum:
                q_ready[2].append(current)
                current = None
                current_quantum_used = 0
                continue
        else:  
            if q_ready[1] or q_ready[2]:
                q_ready[3].appendleft(current)
                current = None
                current_quantum_used = 0
                continue

    return finished

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Uso: python mlq_simple.py input.txt output.txt")
        print("Formato por línea: Label;BT;AT;Q;Pr")
        sys.exit(1)
    inp = sys.argv[1]
    outp = sys.argv[2]
    procs = read_input(inp)
    finished = mlq_run(procs, q1_quantum=3, q2_quantum=5)
    write_output(outp, finished)
    print(f"Simulación completada. Salida en: {outp}")

