import numpy as np
import matplotlib.pyplot as plt
import itertools
from tqdm import tqdm
from collections import defaultdict
import seaborn as sns

def generate_strongly_correlated(n=10):
    weights = np.random.randint(1, 1001, n)
    values = weights + 1000
    return values, weights


def generate_inversely_strongly_correlated(n=10):
    values = np.random.randint(1, 1001, n)
    weights = values + np.random.choice([98, 102], n)
    return values, weights


def generate_profit(n=10):
    weights = np.random.randint(1, 1001, n)
    values = 3 * np.ceil(weights / 3).astype(int)
    return values, weights


def generate_strong_spanner(n=10):
    span_size = 20
    span_values, span_weights = generate_strongly_correlated(span_size)
    span_weights = np.ceil(2 * span_weights / 3).astype(int)
    span_values = np.ceil(2 * span_values / 3).astype(int)
    
    values, weights = [], []
    for _ in range(n):
        idx = np.random.randint(0, span_size)
        s = np.random.choice([1, 2, 3])
        values.append(s * span_values[idx])
        weights.append(s * span_weights[idx])
    
    return np.array(values), np.array(weights)


def generate_profit_spanner(n=10):
    span_size = 20
    span_values, span_weights = generate_profit(span_size)
    span_weights = np.ceil(2 * span_weights / 3).astype(int)
    span_values = np.ceil(2 * span_values / 3).astype(int)
    
    values, weights = [], []
    for _ in range(n):
        idx = np.random.randint(0, span_size)
        s = np.random.choice([1, 2, 3])
        values.append(s * span_values[idx])
        weights.append(s * span_weights[idx])
    
    return np.array(values), np.array(weights)


def lazy_greedy_knapsack(v, w, c):
    """
    Very Greedy algorithm for the Knapsack Problem.
    Items are selected purely based on the highest efficiency ratio.
    """
    r = np.array(v) / np.array(w)  # Efficiency ratio

    # Sort items by efficiency ratio in descending order
    indices = np.argsort(-r)
    
    total_value = 0
    total_weight = 0
    selected_items = []

    for i in indices:
        if total_weight + w[i] <= c:
            total_weight += w[i]
            total_value += v[i]
            selected_items.append(i)

    # Create the bitstring representing the selected items
    bitstring = np.zeros(len(v), dtype=int)
    bitstring[selected_items] = 1

    return total_value, total_weight, ''.join(map(str, bitstring))


def lazy_greedy_knapsack(v, w, c):
    """
    Lazy Greedy algorithm for the Knapsack Problem.
    Implements Algorithm 1 from the paper exactly.
    """
    n = len(v)
    # Calculate efficiency ratios
    r = np.array(v) / np.array(w)
    
    # Sort indices by efficiency ratio (descending)
    # In case of ties, smaller index gets priority (stable sort)
    indices = np.argsort(-r, kind='stable')
    
    # Initialize variables as per the paper
    c_prime = c - w[indices[0]]  # Key difference: subtract first item's weight immediately
    j = 1  # Start from second item since we considered first item
    x = np.zeros(n, dtype=int)
    
    # Main loop following paper's algorithm
    while c_prime > 0 and j < n:
        x[indices[j]] = 1
        j += 1
        if j < n:
            c_prime = c_prime - w[indices[j]]
            
    # Calculate final value and weight
    value = sum(x[i] * v[i] for i in range(n))
    weight = sum(x[i] * w[i] for i in range(n))
    
    return value, weight, ''.join(map(str, x))

def very_greedy_knapsack(v, w, c):
    """
    Very Greedy algorithm for the Knapsack Problem.
    Implements Algorithm 2 from the paper exactly.
    """
    n = len(v)
    # Calculate efficiency ratios
    r = np.array(v) / np.array(w)
    
    # Sort indices by efficiency ratio (descending)
    # In case of ties, smaller index gets priority (stable sort)
    indices = np.argsort(-r, kind='stable')
    
    # Initialize variables as per the paper
    c_prime = c
    j = 0
    x = np.zeros(n, dtype=int)
    
    # Main loop following paper's algorithm
    while c_prime > 0 and j < n:
        # Inner while loop to skip items that don't fit
        while j < n and c_prime < w[indices[j]]:
            j += 1
            
        if j < n:  # If we found an item that fits
            x[indices[j]] = 1
            c_prime = c_prime - w[indices[j]]
            j += 1
    
    # Calculate final value and weight
    value = sum(x[i] * v[i] for i in range(n))
    weight = sum(x[i] * w[i] for i in range(n))
    
    return value, weight, ''.join(map(str, x))


def plot_rank_and_ratio(results, methods=None, labels=None):
    # Extract distributions
    distributions = list(results['very_greedy'].keys())
    distributions_cleaned = [d.replace('generate_', '') for d in distributions]

    # Initialize data for plotting
    if methods == None:
        methods = ['lazy_greedy', 'very_greedy', 'hourglass', 'copula', 'X']
        labels = ['LG', 'VG', r'$QKP_{H}$', r'$QKP_{COP}$', r'$QKP_{X}$']
    num_methods = len(methods)
    bar_width = 0.15  # Adjusted width for better spacing

    # rank_data = {method: [results[method][dist]['rank_solution'] for dist in distributions] for method in methods}
    ratio_data = {method: [results[method][dist]['ratio_optim'] for dist in distributions] for method in methods}

    x = np.arange(len(distributions_cleaned))  # X-axis positions for distributions

    # Updated professional color palette
    colors = ['#4C72B0', '#55A868', '#C44E52', '#8172B2', 'k']  # Blue, Green, Red, Purple

    # ### Plot 1: Rank of Each Distribution
    # fig1, ax1 = plt.subplots(figsize=(10, 5))

    # for i, (method, label) in enumerate(zip(methods, labels)):
    #     bars = ax1.bar(
    #         x + i * bar_width,
    #         rank_data[method],
    #         width=bar_width,
    #         label=label,
    #         alpha=0.85,
    #         color=colors[i],
    #         edgecolor='black'
    #     )
        
    #     # Add text labels above each bar for rank
    #     for bar, rank in zip(bars, rank_data[method]):
    #         ax1.text(
    #             bar.get_x() + bar.get_width() / 2,
    #             bar.get_height() + 0.1,
    #             str(rank),
    #             ha='center',
    #             va='bottom',
    #             fontsize=10,
    #             color='black'
    #         )

    # ax1.set_title('Rank of Each Distribution', fontsize=14, fontweight='bold')
    # ax1.set_xlabel('Distribution', fontsize=12)
    # ax1.set_ylabel('Rank', fontsize=12)
    # ax1.set_xticks(x + bar_width * (num_methods - 1) / 2)
    # ax1.set_xticklabels(distributions_cleaned, rotation=0, ha='center')
    # ax1.grid(True, axis='y', linestyle='--', alpha=0.6)
    # ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=11)
    # plt.tight_layout()

    # # Show the first plot
    # plt.show()

    ### Plot 2: Ratio to Optimal for Each Distribution
    fig2, ax2 = plt.subplots(figsize=(10, 5))

    for i, (method, label) in enumerate(zip(methods, labels)):
        bars = ax2.bar(
            x + i * bar_width,
            ratio_data[method]*100,
            width=bar_width,
            label=label,
            alpha=0.85,
            color=colors[i],
            edgecolor='black'
        )
        
        # Add text labels above each bar for ratio
        for bar, ratio in zip(bars, ratio_data[method]):
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.03,
                f'{ratio*100:.2f}',
                ha='center',
                va='bottom',
                fontsize=10,
                color='black'
            )

    ax2.set_title('Ratio to Optimal for Each Distribution', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Distribution', fontsize=12)
    ax2.set_ylabel('Ratio to Optimal', fontsize=12)
    ax2.set_ylim(0, 1.1)
    ax2.set_xticks(x + bar_width * (num_methods - 1) / 2)
    ax2.set_xticklabels(distributions_cleaned, rotation=0, ha='center')
    ax2.grid(True, axis='y', linestyle='--', alpha=0.6)
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=11)
    plt.tight_layout()

    # Show the second plot
    plt.show()


def bruteforce_knapsack(values, weights, capacity, bit_mapping="regular", show_progress=True):
    """
    Brute-force solver for the knapsack problem.

    Parameters:
    values (list): List of item values.
    weights (list): List of item weights.
    capacity (int): Maximum weight capacity of the knapsack.
    bit_mapping (str): Either "regular" or "inverse" for bit interpretation.
    show_progress (bool): Whether to show the progress bar.

    Returns:
    list: Ranked solutions as a list of tuples (value, weight, bitstring).
    """
    import itertools
    from tqdm import tqdm

    n = len(values)
    ranked_solutions = []
    total_combinations = 2 ** n

    # Select iteration tool based on progress bar option
    iterator = (
        tqdm(itertools.product([0, 1], repeat=n), 
             total=total_combinations, 
             desc="Evaluating knapsack combinations")
        if show_progress else itertools.product([0, 1], repeat=n)
    )

    for subset in iterator:
        if bit_mapping == "regular":
            total_weight = sum(weights[i] * subset[i] for i in range(n))
            total_value = sum(values[i] * subset[i] for i in range(n))
        elif bit_mapping == "inverse":
            total_weight = sum(weights[i] * (1 - subset[i]) for i in range(n))
            total_value = sum(values[i] * (1 - subset[i]) for i in range(n))

        if total_weight <= capacity:
            ranked_solutions.append((total_value, total_weight, subset))
        else:
            ranked_solutions.append((0, 0, subset))

    ranked_solutions.sort(key=lambda x: x[0], reverse=True)
    ranked_solutions = [
        (int(value), int(weight), ''.join(map(str, bitstring))) 
        for value, weight, bitstring in ranked_solutions
    ]

    return ranked_solutions

def compute_min_D(B, C, L):
    """
    Compute the smallest D such that the capacity is non-negative.
    
    Parameters:
    B: list or np.array of B coefficients
    C: list or np.array of C coefficients
    L: threshold value for capacity
    
    Returns:
    optimal_D: The minimum D that satisfies the condition
    """
    B = np.array(B)
    C = np.array(C)
    
    # Compute the numerator and denominator
    numerator = 2 * L + np.sum(B / C)
    denominator = np.sum(1 / C)
    
    # Calculate D
    optimal_D = numerator / denominator
    return optimal_D





def from_Q_to_Ising(Q, offset):
    """Convert the matrix Q of Eq.3 into Eq.13 elements J and h"""
    n_qubits = len(Q)  # Get the number of qubits (variables) in the QUBO matrix
    # Create default dictionaries to store h and pairwise interactions J
    h = defaultdict(int)
    J = defaultdict(int)

    # Loop over each qubit (variable) in the QUBO matrix
    for i in range(n_qubits):
        # Update the magnetic field for qubit i based on its diagonal element in Q
        h[(i,)] -= Q[i, i] / 2
        # Update the offset based on the diagonal element in Q
        offset += Q[i, i] / 2
        # Loop over other qubits (variables) to calculate pairwise interactions
        for j in range(i + 1, n_qubits):
            # Update the pairwise interaction strength (J) between qubits i and j
            J[(i, j)] += Q[i, j] / 4
            # Update the magnetic fields for qubits i and j based on their interactions in Q
            h[(i,)] -= Q[i, j] / 4
            h[(j,)] -= Q[i, j] / 4
            # Update the offset based on the interaction strength between qubits i and j
            offset += Q[i, j] / 4
    # Return the magnetic fields, pairwise interactions, and the updated offset
    return h, J, offset


def energy_Ising(z, h, J, offset):
    """
    Calculate the energy of an Ising model given spin configurations.

    Parameters:
    - z: A dictionary representing the spin configurations for each qubit.
    - h: A dictionary representing the magnetic fields for each qubit.
    - J: A dictionary representing the pairwise interactions between qubits.
    - offset: An offset value.

    Returns:
    - energy: The total energy of the Ising model.
    """
    if isinstance(z, str):
        z = [(1 if int(i) == 0 else -1) for i in z]

    energy = offset # Initialize the energy with the offset term
    # Loop over the magnetic fields (h) for each qubit and update the energy
    for k, v in h.items():
        energy += v * z[k[0]]
    # Loop over the pairwise interactions (J) between qubits and update the energy
    for k, v in J.items():
        energy += v * z[k[0]] * z[k[1]]
    return energy


def sum_weight(bitstring, weights):
    weight = 0
    for n, i in enumerate(weights):
        if bitstring[n] == "1":
            weight += i
    return weight

def sum_values(bitstring, values):
    value = 0
    for n, i in enumerate(values):
        if bitstring[n] == "1":
            value += i
    return value




def plot_histogram_with_vlines(values_unbalanced, min_cost, values_slack=None,
                               bins_width=50,log=True, output_file=None):
    """
    Plots histograms of two datasets with vertical lines indicating an optimal value.
    
    Parameters:
        values_unbalanced (dict): Data for the unbalanced histogram (keys as bins, values as weights).
        values_slack (dict): Data for the slack histogram (keys as bins, values as weights).
        min_cost (float): The value at which to draw the vertical line.
        output_file (str, optional): File path to save the plot (e.g., "output.png"). Defaults to None.
    """
    fig, ax = plt.subplots(figsize=(10, 6))  # Larger figure size for better readability

    # Plot histograms
    ax.hist(
        values_unbalanced.keys(),
        weights=values_unbalanced.values(),
        bins=bins_width,
        edgecolor="black",
        label="Unbalanced",
        align="right",
        alpha=0.7,  # Transparency for overlapping areas
        color="steelblue"
    )

    if values_slack:
        ax.hist(
            values_slack.keys(),
            weights=values_slack.values(),
            bins=bins_width,
            edgecolor="black",
            label="Slack",
            align="left",
            alpha=0.7,
            color="orange"
        )

    # Add vertical line
    ax.axvline(-min_cost, linestyle="--", color="red", label="Optimal", linewidth=2)

    # Set log scale for y-axis
    if log:
        ax.set_yscale("log")

    # Add labels, title, and legend
    ax.set_ylabel("Counts", fontsize=14)
    ax.set_xlabel("Values", fontsize=14)
    ax.set_title("Comparison of Values Distributions", fontsize=16)
    ax.legend(fontsize=12)

    # Add gridlines for clarity
    ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.7)

    # Show or save plot
    if output_file:
        plt.savefig(output_file, bbox_inches="tight")
    plt.show()



def reverse_bits(counts_dict):
    """
    Reverse the order of bits in the keys of the counts dictionary.
    
    Args:
        counts_dict (dict): A dictionary of bit string counts.
    
    Returns:
        dict: A new dictionary with the bits reversed.
    """
    new_counts = {}
    for bitstring, count in counts_dict.items():
        new_bitstring = bitstring[::-1]
        new_counts[new_bitstring] = count
    return new_counts





def plot_custom_histogram(counts, highlighted_outcome=None, figsize=(12, 6), 
                          bar_color='skyblue', highlight_color='crimson', 
                          title='Sample Histogram', xlabel='Bitstrings', 
                          ylabel='Counts', max_bitstrings=20, bitstring_rankings=None,
                          remove_xticks=False, display_text=True):
    """
    Plots a custom histogram with an option to highlight a specific bitstring. 
    If there are too many bitstrings, only the top `max_bitstrings` are displayed.
    Optionally, displays performance ranking at the bottom of each bar (inside).

    Parameters:
    counts (dict): Dictionary containing bitstrings as keys and counts as values.
    highlighted_outcome (str): The specific bitstring to highlight in a different color.
    figsize (tuple): Figure size of the plot.
    bar_color (str): Color of the bars (default is 'skyblue').
    highlight_color (str): Color for the highlighted bar (default is 'crimson').
    title (str): Title of the plot.
    xlabel (str): X-axis label.
    ylabel (str): Y-axis label.
    max_bitstrings (int): Maximum number of bitstrings to display on the x-axis.
    bitstring_rankings (dict, optional): Dictionary mapping bitstrings to their performance ranking.
    """
    
    # Sort the counts based on the values in descending order
    sorted_counts = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))

    # Limit to the top `max_bitstrings` bitstrings
    if len(sorted_counts) > max_bitstrings:
        sorted_counts = dict(list(sorted_counts.items())[:max_bitstrings])

    # Extract keys (bitstrings) and values (counts)
    bitstrings = list(sorted_counts.keys())
    values = list(sorted_counts.values())

    # Create a list of default colors for all bars
    colors = [bar_color] * len(sorted_counts)

    # Assign custom colors based on conditions
    for i, bitstring in enumerate(bitstrings):
        if bitstring_rankings and bitstring in bitstring_rankings:
            # print(bitstring_rankings)
            # print(bitstring)
            if bitstring_rankings[bitstring] == 0:
                colors[i] = 'gray'  # Change color to gray if the rank is 0
            elif bitstring == highlighted_outcome:
                colors[i] = highlight_color  # Change the color for the highlighted outcome

    # Create the bar plot
    fig, ax = plt.subplots(figsize=figsize)

    bar_positions = np.arange(len(bitstrings))
    bars = ax.bar(bar_positions, values, color=colors, edgecolor='black', linewidth=1.2)

    plt.xticks(rotation=60, ha='right')

    # Add bar labels to show counts on top of each bar
    if display_text:
        for i, (bar, value) in enumerate(zip(bars, values)):
            height = bar.get_height()
            # Display the count at the top of each bar
            ax.text(bar.get_x() + bar.get_width() / 2., height + 10, f'{value}', 
                    ha='center', va='bottom', fontsize=8, fontweight='bold')

            # Add the bitstring performance ranking at the bottom inside the bars, only if rank is not 0
            if bitstring_rankings and bitstrings[i] in bitstring_rankings:
                rank = bitstring_rankings[bitstrings[i]]
                if rank != 0:  # Skip writing rank inside the bar if the rank is 0
                    ax.text(bar.get_x() + bar.get_width() / 2., bar.get_y() + 5, 
                            f'{rank}', ha='center', va='bottom', fontsize=10, fontweight='bold', color='black')

    # Add labels, title, and customize the plot
    if remove_xticks==True:
        ax.set_xticks([])  # Removes both the ticks and their labels
    else:
        ax.set_xticks(bar_positions)
        ax.set_xticklabels(bitstrings, fontsize=12, fontweight='bold')
    ax.set_xlabel(xlabel, fontsize=14, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=14, fontweight='bold')
    ax.set_title(title, fontsize=16, fontweight='bold')



    # Add gridlines for better readability
    ax.yaxis.grid(True, linestyle='--', which='major', color='grey', alpha=0.6)

    # Create legend if a highlighted outcome is provided
    if highlighted_outcome:
        handles = [
            plt.Rectangle((0, 0), 1, 1, color=highlight_color, label='Classical Solution'),
            plt.Rectangle((0, 0), 1, 1, color=bar_color, label='Other Counts'),
            plt.Rectangle((0, 0), 1, 1, color='gray', label='Invalid Solution')
        ]
        ax.legend(handles=handles, loc='upper right', fontsize=12, frameon=True)

    # Adjust spacing for better readability
    plt.tight_layout()

    # Show the plot
    plt.show()



def plot_heatmap(data_dict, beta_params, gamma_params, best_value, vmax=20000, cmap='YlGnBu'):
    """
    Create a heatmap from a dictionary of data.
    
    Parameters:
    -----------
    data_dict : dict
        Dictionary with (beta, gamma) tuples as keys and values as counts
    beta_params : list
        List of unique beta parameter values
    gamma_params : list
        List of unique gamma parameter values
    
    Returns:
    --------
    matplotlib.figure.Figure
        Figure containing the heatmap
    """
    # Create a 2D array to hold the data
    heatmap_data = np.zeros((len(beta_params), len(gamma_params)))
    
    # Fill the heatmap with values from the dictionary
    for (beta, gamma), value in data_dict.items():
        if beta in beta_params and gamma in gamma_params:
            beta_idx = beta_params.index(beta)
            gamma_idx = gamma_params.index(gamma)
            if value > best_value:
                heatmap_data[beta_idx, gamma_idx] = 0
            else:
                heatmap_data[beta_idx, gamma_idx] = value
    # Create the plot
    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data, 
                annot=False, 
                cmap=cmap,
                vmin=0,
                vmax=vmax,
                cbar_kws={'label': 'Knapsack Value'}
                )
    
    plt.title('Heatmap of Parameter Counts')
    plt.xlabel('Gamma Parameters')
    plt.ylabel('Beta Parameters')
    plt.tight_layout()
    
    return plt.gcf()



def plot_best_values(results, methods=None, labels=None):
    """
    Plots the best values for each method for 'generate_profit_spanner'.
    """
    # Ensure we're looking at 'generate_profit_spanner'
    distribution = 'generate_profit_spanner'
    
    # Initialize methods and labels
    if methods is None:
        methods = list(results.keys())
    if labels is None:
        labels = methods

    num_methods = len(methods)
    bar_width = 0.15

    # Extract best values for each method
    best_value_data = [
        results.get(method, {}).get(distribution, {}).get('best_value', 0) 
        for method in methods
    ]

    x = np.arange(len(methods))
    colors = ['#4C72B0', '#55A868', '#C44E52', '#8172B2', 'k']

    fig, ax = plt.subplots(figsize=(10, 5))

    bars = ax.bar(
        x,
        best_value_data,
        width=bar_width,
        alpha=0.85,
        color=[colors[i % len(colors)] for i in range(len(methods))],
        edgecolor='black'
    )
    
    # Add text labels above each bar
    for bar, value in zip(bars, best_value_data):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f'{value:.0f}',
            ha='center',
            va='bottom',
            fontsize=10,
            color='black'
        )

    ax.set_title('Best Values for Profit Spanner Distribution', fontsize=14, fontweight='bold')
    ax.set_xlabel('Methods', fontsize=12)
    ax.set_ylabel('Best Value', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.grid(True, axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()

    plt.show()


# Helper function to convert NumPy types to standard Python types
def convert_to_serializable(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()  # Convert NumPy arrays to lists
    else:
        return obj  # Return other objects as is


def get_hamming_distance(bitstring1, bitstring2):

    # Convert strings to numpy arrays of integers
    arr1 = np.array(list(bitstring1), dtype=int)
    arr2 = np.array(list(bitstring2), dtype=int)
    
    # Compute Hamming distance
    return np.sum(arr1 != arr2)



def solve_knapsack(weights, values, capacity, bitstrings):
    """
    Solve the 0/1 Knapsack problem by testing a list of bitstrings.
    
    Args:
    weights (list): List of item weights
    values (list): List of item values
    capacity (int): Maximum weight capacity of the knapsack
    bitstrings (list): List of bitstrings to test
    
    Returns:
    tuple: (best_value, best_bitstring, selected_items)
        - best_value: Maximum value achieved
        - best_bitstring: Bitstring that produced the maximum value
        - selected_items: Indices of items selected in the best solution
    """
    # Validate input
    if len(weights) != len(values):
        raise ValueError("Weights and values lists must be of equal length")
    
    # Initialize best solution tracking
    best_value = 0
    best_bitstring = None
    best_weight = None
    
    # Add tqdm progress bar for bitstrings
    for bitstring in tqdm(bitstrings, desc="Processing bitstrings", unit="bitstring"):
        # Validate bitstring length matches number of items
        if len(bitstring) != len(weights):
            raise ValueError(f"Bitstring {bitstring} length does not match number of items")
        
        # Calculate total weight and value for this bitstring
        current_weight = 0
        current_value = 0
        current_selected_items = []
        
        for i, bit in enumerate(bitstring):
            if bit == '1':
                current_weight += weights[i]
                current_value += values[i]
                current_selected_items.append(i)
        
        # Check if solution is valid and better than previous best
        if current_weight <= capacity and current_value > best_value:
            best_value = current_value
            best_bitstring = bitstring
            best_weight = current_weight
    
    return best_value, best_bitstring, best_weight


def extract_unique_bitstrings(big_dict):
    """
    Extract all unique bitstrings from a nested dictionary.
    
    Args:
    big_dict (dict): Nested dictionary with bitstrings in 'counts'
    
    Returns:
    list: List of unique bitstrings
    """
    # Use a set to automatically handle uniqueness
    unique_bitstrings = set()
    
    # Iterate through all sub-dictionaries
    for key, sub_dict in big_dict.items():
        # Check if 'counts' exists in the sub-dictionary
        if 'counts' in sub_dict:
            # Add all bitstrings from counts to the set
            unique_bitstrings.update(sub_dict['counts'].keys())
        else:
            try:
                unique_bitstrings.update(sub_dict['bitstrings'])
            except:
                continue
            
    # Convert set to list and return
    return list(unique_bitstrings)



def get_value(bitstring, v, bit_mapping="regular"):
    """
    Compute the total value for a given Knapsack bitstring.

    Args:
        bitstring (str): A binary string representing the solution (e.g., "10101").
        v (list): List of values corresponding to the items.
        bit_mapping (str): Specifies the mapping mode ('regular' or 'inverse').

    Returns:
        float/int: Total value of the selected items.
    """
    if len(bitstring) != len(v):
        raise ValueError("Bitstring length must match the length of values.")
    
    if bit_mapping == "regular":
        return sum(int(bitstring[i]) * v[i] for i in range(len(bitstring)))
    elif bit_mapping == "inverse":
        return sum((1 - int(bitstring[i])) * v[i] for i in range(len(bitstring)))
    else:
        raise ValueError("Invalid bit_mapping mode. Use 'regular' or 'inverse'.")


def get_weight(bitstring, w, bit_mapping="regular"):
    """
    Compute the total weight for a given Knapsack bitstring.

    Args:
        bitstring (str): A binary string representing the solution (e.g., "10101").
        w (list): List of weights corresponding to the items.
        bit_mapping (str): Specifies the mapping mode ('regular' or 'inverse').

    Returns:
        float/int: Total weight of the selected items.
    """
    if len(bitstring) != len(w):
        raise ValueError("Bitstring length must match the length of weights.")
    
    if bit_mapping == "regular":
        return sum(int(bitstring[i]) * w[i] for i in range(len(bitstring)))
    elif bit_mapping == "inverse":
        return sum((1 - int(bitstring[i])) * w[i] for i in range(len(bitstring)))
    else:
        raise ValueError("Invalid bit_mapping mode. Use 'regular' or 'inverse'.")
    



def plot_method_comparison(results, optimal_value,  methods=None, labels=None, title=None,
                           bar_width=0.15):
    """
    Plot a histogram comparing method performance across distributions.
    
    Parameters:
    -----------
    results : dict
        Dictionary containing results for different methods and distributions
    optimal_value : float
        The optimal value to compare against
    methods : list, optional
        List of methods to plot (default is predefined set)
    labels : list, optional
        Custom labels for methods (default is predefined set)
    title : str, optional
        Custom title for the plot
    """
    # Extract distributions
    distributions = list(results['very_greedy'].keys())
    distributions_cleaned = [d.replace('generate_', '') for d in distributions]
    
    # Set default methods and labels if not provided
    if methods is None:
        methods = ['lazy_greedy', 'very_greedy', 'copula']
    if labels is None:
        labels = ['LG', 'VG', r'$QKP_{COP}$']
    
    # Professional color palette
    colors = ['#4C72B0', '#55A868', '#C44E52', '#8172B2', 'k']
    
    # Prepare data
    best_values = {method: [results[method][dist]['value']\
                            for dist in distributions] for method in methods}
    
    min_values = {method: min(values) for method, values in best_values.items()}
    print(min_values)

    min_method = min(min_values.values())
    min_value = min(best_values.values())
    print(min_value[0])
    print(min_method)

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))  # Increase the figure height
    # fig.subplots_adjust(top=0.)  # Adjust the top margin
    
    # Bar width and positioning
    bar_width = bar_width
    x = np.arange(len(distributions_cleaned))
    
    # Plot bars for each method
    for i, (method, label) in enumerate(zip(methods, labels)):
        bars = ax.bar(
            x + i * bar_width, 
            best_values[method], 
            width=bar_width,
            label=label,
            alpha=0.95,
            color=colors[i],
            edgecolor='black'
        )
        
        # Add text labels with performance relative to optimal
        for bar, value in zip(bars, best_values[method]):
            # Calculate percentage of optimal value
            perf_percentage = (value / optimal_value) * 100
            
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f'{value}\n ({perf_percentage:.2f}%)',
                ha='center',
                va='bottom',
                fontsize=12,
                color='black',
                fontweight='bold'
            )

    # Customize plot
    ax.set_title(title or 'Performance Comparison Across Distributions', fontsize=14, fontweight='bold')
    ax.set_xlabel('Distribution', fontsize=12)
    ax.set_ylabel('Value', fontsize=12)
    
    # Set x-ticks
    ax.set_xticks(x + bar_width * (len(methods) - 1) / 2)
    ax.set_xticklabels(distributions_cleaned, rotation=0, ha='right')
    
    # # Add horizontal line for optimal value
    # ax.axhline(y=optimal_value, color='r', linestyle='--', label='Optimal Value')
    
    # Customize grid and legend
    # ax.grid(True, axis='y', linestyle='--', alpha=0.6)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=11)

    ax.set_yscale('log')
    ax.set_ylim(top=optimal_value * 1.001)
    
    plt.tight_layout()
    plt.show()