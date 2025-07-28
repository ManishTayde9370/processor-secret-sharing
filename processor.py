import json
import math
import re
from collections import Counter
from itertools import combinations

# --- 1. Helper functions for arithmetic operations ---
def _sum(*args):
    """Calculates the sum of all arguments."""
    return sum(args)

def _multiply(*args):
    """Calculates the product of all arguments."""
    res = 1
    for arg in args:
        res *= arg
    return res

def _hcf(*args):
    """Calculates the Highest Common Factor (GCD) for multiple arguments."""
    if not args:
        raise ValueError("HCF requires at least one argument.")
    result = args[0]
    for i in range(1, len(args)):
        result = math.gcd(result, args[i])
    return result

def _lcm(*args):
    """Calculates the Least Common Multiple (LCM) for multiple arguments."""
    if not args:
        raise ValueError("LCM requires at least one argument.")
    result = args[0]
    for i in range(1, len(args)):
        if result == 0 or args[i] == 0:
            result = 0  # LCM involving zero is zero
        else:
            # LCM(a, b) = abs(a * b) // GCD(a, b)
            result = abs(result * args[i]) // math.gcd(result, args[i])
    return result

# Map function names from JSON to their Python implementations
FUNCTION_MAP = {
    "sum": _sum,
    "multiply": _multiply,
    "hcf": _hcf,
    "lcm": _lcm
}

# --- 2. Function to parse and compute share value from string ---
def compute_share_value(func_str):
    """
    Parses a function string (e.g., "multiply(10,20,5)") and computes its value.
    Supports 'sum', 'multiply', 'hcf', 'lcm'. Arguments are parsed as integers.
    """
    match = re.match(r"(\w+)\((.*)\)", func_str)
    if not match:
        raise ValueError(f"Invalid function string format: '{func_str}'")

    func_name = match.group(1).lower()
    args_str = match.group(2)

    if func_name not in FUNCTION_MAP:
        raise ValueError(f"Unsupported function: '{func_name}'")

    # Parse arguments, ensuring they are integers.
    try:
        # Handle empty arguments string for functions that might have it (though unlikely for these)
        if args_str.strip() == "":
            args = []
        else:
            args = [int(arg.strip()) for arg in args_str.split(',')]
    except ValueError:
        raise ValueError(f"Invalid arguments in function string: '{func_str}'")

    return FUNCTION_MAP[func_name](*args)

# --- 3. Lagrange Interpolation to find P(0) (the secret) ---
def lagrange_constant_term(points):
    """
    Computes the constant term P(0) of the unique polynomial passing through
    the given 'k' points using Lagrange interpolation.

    Args:
        points (list): A list of (x, y) tuples representing the shares.

    Returns:
        int: The computed secret (P(0)).

    Raises:
        ValueError: If duplicate x-coordinates are found or if an intermediate
                    Lagrange term division is not exact (indicating a potential
                    need for modular arithmetic not specified).
    """
    secret = 0
    k = len(points)

    for j in range(k):
        xj, yj = points[j]

        # Calculate L_j(0) = product( (-x_m) / (x_j - x_m) ) for m != j
        numerator_product = 1
        denominator_product = 1

        for m in range(k):
            if m != j:
                xm, ym = points[m]
                
                # Check for distinct x-coordinates to prevent division by zero
                if xj - xm == 0:
                    raise ValueError(f"Duplicate x-coordinate ({xj}) found, cannot interpolate.")
                
                numerator_product *= (-xm)
                denominator_product *= (xj - xm)
        
        if denominator_product == 0:
            # This case should ideally be caught by xj - xm == 0 check, but as a safeguard
            raise ValueError("Denominator for Lagrange interpolation is zero.")
            
        # Ensure that the division results in an integer.
        # In standard Shamir's Secret Sharing, this is guaranteed because
        # arithmetic is done over a finite field (modulo a large prime).
        # Assuming for this problem that the points are such that this division is exact.
        if numerator_product % denominator_product != 0:
            raise ValueError(
                "Intermediate Lagrange term is not an exact integer. "
                "This might imply a requirement for modular arithmetic (finite field) "
                "or rational number handling, which was not explicitly requested."
            )
             
        lagrange_term = (numerator_product // denominator_product)
        secret += yj * lagrange_term

    return secret

# --- Main execution logic ---
def solve_secret(json_input_path):
    """
    Reads share data from a JSON file, identifies correct shares,
    and reconstructs the secret using Lagrange interpolation.

    Args:
        json_input_path (str): The path to the input JSON file.

    Returns:
        int: The reconstructed secret.

    Raises:
        FileNotFoundError: If the JSON file does not exist.
        ValueError: If input JSON format is incorrect or not enough valid shares.
        RuntimeError: If no consistent secret can be found.
    """
    try:
        with open(json_input_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"JSON file not found at: {json_input_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in {json_input_path}: {e}")

    n = data.get('n')
    k = data.get('k')
    raw_shares = data.get('shares')

    if not all([isinstance(n, int), isinstance(k, int), isinstance(raw_shares, dict)]):
        raise ValueError("JSON must contain 'n' (int), 'k' (int), and 'shares' (dict).")
    if not (1 <= k <= n):
        raise ValueError(f"Invalid k ({k}) or n ({n}) values. Must be 1 <= k <= n.")

    # Process raw shares into (x, y) numerical points
    processed_shares = []
    for x_str, func_str in raw_shares.items():
        try:
            x_coord = int(x_str)
            y_coord = compute_share_value(func_str)
            processed_shares.append((x_coord, y_coord))
        except ValueError as e:
            # Print a warning and skip malformed shares
            print(f"Warning: Skipping invalid share data for x='{x_str}': {e}")
            continue
        except Exception as e:
             print(f"Warning: An unexpected error occurred processing share x='{x_str}': {e}")
             continue
    
    # Ensure we have at least k valid shares to proceed with reconstruction
    if len(processed_shares) < k:
        raise ValueError(f"Not enough valid shares ({len(processed_shares)}) to reconstruct the secret. Need at least {k}.")

    # Use a Counter to store candidate secrets and their frequencies
    secret_candidates = Counter()

    # Iterate through all combinations of 'k' shares from the 'n' processed shares
    # Sorting ensures consistent combination generation, but not strictly necessary for correctness.
    for combo in combinations(processed_shares, k):
        try:
            candidate_secret = lagrange_constant_term(list(combo))
            secret_candidates[candidate_secret] += 1
        except ValueError as e:
            # If a combination of shares leads to an error (e.g., bad share causing non-integer division),
            # we just ignore that combination. This is how "wrong shares" are implicitly handled.
            # print(f"Debug: Failed to compute secret for combination {combo}: {e}") # For debugging
            pass
        except Exception as e:
            print(f"Warning: Unexpected error during secret computation for combination {combo}: {e}")
            pass

    if not secret_candidates:
        raise RuntimeError("No consistent secret could be found from any combination of shares. "
                           "This might indicate too many bad shares or an issue with the input data.")

    # The true secret is the one that appears most frequently
    true_secret, count = secret_candidates.most_common(1)[0]
    
    # Optional: You could add a check here for confidence, e.g., if count is too low compared to total combinations.
    # print(f"Debug: Most common secret: {true_secret} (appeared {count} times)")

    return true_secret

# --- Example Usage (How to run the code) ---
if __name__ == "__main__":
    # Create a dummy JSON file for testing
    # Correct shares for P(x) = -70x^2 + 160x + 210 (secret is 210):
    # P(1) = -70 + 160 + 210 = 300
    # P(2) = -70*4 + 160*2 + 210 = -280 + 320 + 210 = 250
    # P(3) = -70*9 + 160*3 + 210 = -630 + 480 + 210 = 60
    # P(4) = -70*16 + 160*4 + 210 = -1120 + 640 + 210 = -270 (So 'LCM(10,15)'=30 is bad share)
    # P(5) = -70*25 + 160*5 + 210 = -1750 + 800 + 210 = -740 (So 'sum(1000,2000,3000)'=6000 is bad share)

    # Let's adjust dummy content to demonstrate working with bad shares
    dummy_json_content_with_bad = {
        "n": 5,
        "k": 3,
        "shares": {
            "1": "sum(100,200)",        # Correct: (1, 300)
            "2": "multiply(50,5)",      # Correct: (2, 250)
            "3": "HCF(120, 180)",       # Correct: (3, 60)
            "4": "LCM(10, 15)",         # Incorrect: (4, 30) (expected -270)
            "5": "sum(1000, 2000, 3000)" # Incorrect: (5, 6000) (expected -740)
        }
    }

    json_file_path = "input_shares.json"
    with open(json_file_path, 'w') as f:
        json.dump(dummy_json_content_with_bad, f, indent=2)
    
    print(f"JSON input written to '{json_file_path}'\n")

    try:
        secret = solve_secret(json_file_path)
        print(f"The identified secret is: {secret}")
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    # Example with large numbers
    # P(x) = 2x + 5. Secret is 5.
    # Correct points for k=2: (10, 25), (20, 45)
    # Incorrect: (30, 120)
    large_json_content = {
        "n": 3,
        "k": 2,
        "shares": {
            "10": "sum(20,5)", # (10, 25) - Correct
            "20": "sum(40,5)", # (20, 45) - Correct
            "30": "multiply(30,2,2)" # (30, 120) - Incorrect, P(30) should be 65
        }
    }
    
    large_json_file_path = "input_shares_large.json"
    with open(large_json_file_path, 'w') as f:
        json.dump(large_json_content, f, indent=2)
    
    print(f"\nJSON input for large numbers written to '{large_json_file_path}'\n")

    try:
        secret_large = solve_secret(large_json_file_path)
        print(f"The identified large number secret is: {secret_large}")
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"Error with large numbers: {e}")
    except Exception as e:
        print(f"An unexpected error occurred with large numbers: {e}")
