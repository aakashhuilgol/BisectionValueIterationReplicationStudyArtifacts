"""
Parse BVI/II/OVI results txt files from MDP and DTMC folders.

Extracts per property:
  Model, Type (MDP/DTMC), Algorithm, Parameter, Property,
  Value, Bound Lower, Bound Upper, Time (s), Total Iterations

Output: results_compiled.csv saved next to this script.
"""

import os
import re
import csv

ALGORITHMS = ["BVI-GS", "BVI-NP", "BVI-PRISM", "BVI", "II", "OVI"]

FIELDNAMES = [
    "Model", "Type", "Algorithm", "Parameter", "Property",
    "Value", "Bound Lower", "Bound Upper", "Time (s)", "Total Iterations"
]


def extract_algorithm(filename):
    base = os.path.splitext(filename)[0]
    for alg in sorted(ALGORITHMS, key=len, reverse=True):
        tag = f".{alg}Results"
        if tag in base:
            return base.replace(tag, ""), alg
    return base, "Unknown"


def parse_file(filepath, model, algorithm, model_type):
    with open(filepath, "r") as f:
        lines = f.readlines()

    segments = []
    current = []
    for line in lines:
        if re.match(r"^\s*-{3,}\s*$", line):
            if current:
                segments.append(current)
            current = []
        else:
            current.append(line)
    if current:
        segments.append(current)

    rows = []
    for seg_lines in segments:
        # Extract parameter string verbatim from "Experiment ..." line
        parameter = "N/A"
        for line in seg_lines:
            m = re.match(r"\s*Experiment\s+(.+)", line)
            if m:
                parameter = m.group(1).strip()
                break

        # Split into property blocks (each starts with "+ Property <name>")
        prop_blocks = []
        current_block = []
        in_prop = False
        for line in seg_lines:
            if re.match(r"\s*\+\s+Property\s+\S+", line):
                if in_prop and current_block:
                    prop_blocks.append(current_block)
                current_block = [line]
                in_prop = True
            elif in_prop:
                current_block.append(line)
        if in_prop and current_block:
            prop_blocks.append(current_block)

        for block in prop_blocks:
            prop_name = value = bound_lower = bound_upper = time_val = total_iters = None

            # First line is always the "+ Property <name>" line
            m = re.match(r"\s*\+\s+Property\s+(\S+)", block[0])
            if m:
                prop_name = m.group(1)

            # Scan remaining lines with subsection tracking
            in_subsection = False
            for line in block[1:]:
                # Entering a subsection: "  + Something"
                if re.match(r"  \+ ", line):
                    in_subsection = True

                # Value/Bounds/Time only captured before any subsection
                if not in_subsection:
                    m = re.match(r"  (?:Probability|Value):\s*(\S+)", line)
                    if m:
                        value = m.group(1)

                    m = re.match(r"  Result:\s*(\S+)", line)
                    if m and value is None:
                        value = m.group(1)

                    m = re.match(r"  Bounds?:\s*\[(\S+),\s*(\S+)\]", line)
                    if m:
                        bound_lower = m.group(1)
                        bound_upper = m.group(2)

                    m = re.match(r"  Time:\s*([\d.]+)\s*s", line)
                    if m:
                        time_val = m.group(1)

                # BVI: "    Total Iterations: N"
                m = re.match(r"\s+Total Iterations:\s*(\d+)", line)
                if m:
                    total_iters = m.group(1)

                # OVI: "    Total iterations:  N" (lowercase i)
                m = re.match(r"\s+Total iterations:\s*(\d+)", line)
                if m:
                    total_iters = m.group(1)

            # II: "    Iterations: N" inside "+ Interval iteration" block
            if total_iters is None:
                in_interval = False
                for line in block[1:]:
                    if re.match(r"\s+\+\s+Interval iteration", line):
                        in_interval = True
                        continue
                    if in_interval:
                        m = re.match(r"\s+Iterations:\s*(\d+)", line)
                        if m:
                            total_iters = m.group(1)
                            break
                        # Exit if we hit a new subsection header
                        if re.match(r"\s+\+\s+\S", line):
                            in_interval = False

            rows.append({
                "Model": model,
                "Type": model_type,
                "Algorithm": algorithm,
                "Parameter": parameter,
                "Property": prop_name,
                "Value": value,
                "Bound Lower": bound_lower,
                "Bound Upper": bound_upper,
                "Time (s)": time_val,
                "Total Iterations": total_iters,
            })

    return rows


def collect_txt_files(root_folder):
    for entry in sorted(os.scandir(root_folder), key=lambda e: e.name):
        if entry.is_file() and entry.name.endswith(".txt"):
            model, alg = extract_algorithm(entry.name)
            yield entry.path, model, alg, "MDP"

    dtmc_folder = os.path.join(root_folder, "DTMCs")
    if os.path.isdir(dtmc_folder):
        for entry in sorted(os.scandir(dtmc_folder), key=lambda e: e.name):
            if entry.is_file() and entry.name.endswith(".txt"):
                model, alg = extract_algorithm(entry.name)
                yield entry.path, model, alg, "DTMC"


def param_sort_key(param_str):
    """Sort by all numeric values found in the parameter string."""
    return [int(n) for n in re.findall(r"\d+", param_str)]


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "Output")
    os.makedirs(output_dir, exist_ok=True)
    output_csv = os.path.join(output_dir, "compiled_results.csv")

    all_rows = []
    for filepath, model, algorithm, model_type in collect_txt_files(script_dir):
        all_rows.extend(parse_file(filepath, model, algorithm, model_type))

    all_rows.sort(key=lambda r: (
        0 if r["Type"] == "MDP" else 1,  # MDPs first
        r["Model"],
        param_sort_key(r["Parameter"]),
        r["Property"],
        r["Algorithm"],
    ))

    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Done. {len(all_rows)} rows written to: {output_csv}")


if __name__ == "__main__":
    main()