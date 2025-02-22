from heapq import heappush, heappop
from collections import defaultdict

from heapq import heappush, heappop
from collections import defaultdict

class SuffixAutomaton:
    def __init__(self):
        self.states = [{}]  # Transition table
        self.link = [-1]    # Suffix links
        self.length = [0]   # Length of the longest string in each state
        self.last = 0       # Last added state

    def extend(self, c):
        cur = len(self.states)
        self.states.append({})
        self.length.append(self.length[self.last] + 1)
        self.link.append(-1)

        p = self.last
        while p != -1 and c not in self.states[p]:
            self.states[p][c] = cur
            p = self.link[p]

        if p == -1:
            self.link[cur] = 0
        else:
            q = self.states[p][c]
            if self.length[p] + 1 == self.length[q]:
                self.link[cur] = q
            else:
                clone = len(self.states)
                self.states.append(self.states[q].copy())
                self.length.append(self.length[p] + 1)
                self.link.append(self.link[q])

                while p != -1 and self.states[p].get(c) == q:
                    self.states[p][c] = clone
                    p = self.link[p]

                self.link[q] = clone
                self.link[cur] = clone

        self.last = cur

    def build(self, s):
        for c in s:
            self.extend(c)


def heuristic(current_length, max_possible_length):
    """
    Heuristic function for A* search.
    Returns an estimate of how much longer the substring can grow.
    """
    return max_possible_length - current_length


def lcs_k_mismatches_a_star(s1, s2, k, min_limit):
    """
    Finds the longest common substring with at most k mismatches using a suffix automaton and A* search.

    Parameters:
    s1 (str): First string.
    s2 (str): Second string.
    k (int): Maximum number of mismatches allowed.
    min_limit (int): Minimum acceptable length of the substring.

    Returns:
    tuple: (length, start_s1, start_s2), where length is the length of the LCS,
           start_s1 is its starting position in s1, and start_s2 is its starting position in s2.
           Returns None if no substring of length >= min_limit is found.
    """
    sa = SuffixAutomaton()
    delimiter = '#'
    sa.build(s1 + delimiter + s2)

    max_possible_length = min(len(s1), len(s2))
    pq = []
    # Initialize with two starting points: one for s1 and one for s2
    heappush(pq, (-max_possible_length, 0, 0, 0, 0, True))  # True indicates matching in s1
    heappush(pq, (-max_possible_length, 0, 0, 0, 0, False))  # False indicates matching in s2

    max_length = 0
    result_start_s1, result_start_s2 = -1, -1

    visited = set()

    while pq:
        neg_potential_max, neg_length, mismatches, state, start, is_s1 = heappop(pq)
        length = -neg_length
        potential_max_length = -neg_potential_max

        if potential_max_length < min_limit:
            break

        if (state, mismatches, start, is_s1) in visited:
            continue
        visited.add((state, mismatches, start, is_s1))

        # Update result if it meets the criteria
        if length >= min_limit and length > max_length:
            max_length = length
            if is_s1:
                result_start_s1, result_start_s2 = start, 0
            else:
                result_start_s1, result_start_s2 = 0, start

        for char, next_state in sa.states[state].items():
            if char == delimiter:
                continue

            new_length = length + 1
            new_start = start + 1

            # Check if we're still within bounds of the current string
            if (is_s1 and new_start > len(s1)) or (not is_s1 and new_start > len(s2)):
                continue

            new_mismatches = mismatches
            # Check for mismatches only in the current string
            if is_s1 and char != s1[start]:
                new_mismatches += 1
            elif not is_s1 and char != s2[start]:
                new_mismatches += 1

            if new_mismatches > k:
                continue

            new_potential_max = new_length + heuristic(new_length, max_possible_length)

            # Push to queue with updated start position
            heappush(pq, (-new_potential_max, -new_length, new_mismatches, next_state, new_start, is_s1))

    if max_length >= min_limit:
        return max_length, result_start_s1, result_start_s2
    else:
        return None



def lcs_k_mismatches_a_star_star(s1, s2, k, min_limit):
    sa = SuffixAutomaton()
    delimiter = '#'
    sa.build(s1 + delimiter + s2)

    max_possible_length = min(len(s1), len(s2))
    pq = []
    heappush(pq, (-max_possible_length, 0, 0, 0, 0, 0, True))  # Added actual_start
    heappush(pq, (-max_possible_length, 0, 0, 0, 0, 0, False))

    max_length = 0
    result_start_s1, result_start_s2 = -1, -1

    visited = set()

    while pq:
        neg_potential_max, neg_length, mismatches, state, start, actual_start, is_s1 = heappop(pq)
        length = -neg_length
        potential_max_length = -neg_potential_max

        if potential_max_length < min_limit:
            break

        if (state, mismatches, start, is_s1) in visited:
            continue
        visited.add((state, mismatches, start, is_s1))

        if length >= min_limit and length > max_length:
            max_length = length
            if is_s1:
                result_start_s1, result_start_s2 = actual_start, 0
            else:
                result_start_s1, result_start_s2 = 0, actual_start

        for char, next_state in sa.states[state].items():
            if char == delimiter:
                continue

            new_length = length + 1
            new_start = start + 1

            if (is_s1 and new_start > len(s1)) or (not is_s1 and new_start > len(s2)):
                continue

            new_mismatches = mismatches
            if is_s1 and char != s1[start]:
                new_mismatches += 1
            elif not is_s1 and char != s2[start]:
                new_mismatches += 1

            if new_mismatches > k:
                continue

            new_potential_max = new_length + heuristic(new_length, max_possible_length)

            heappush(pq, (-new_potential_max, -new_length, new_mismatches, next_state, new_start, actual_start, is_s1))

    if max_length >= min_limit:
        return max_length, result_start_s1, result_start_s2
    else:
        return None



# Example Usage
s1 = "abcdefg"
s2 = "cdxef"
k = 1
min_limit = 3

result = lcs_k_mismatches_a_star_star(s1, s2, k, min_limit)
if result:
    print(f"LCS with at most {k} mismatches and minimum length {min_limit}:")
    print(f"Length={result[0]}, Start in S1={result[1]}, Start in S2={result[2]}")
else:
    print(f"No common substring of length >= {min_limit} found with at most {k} mismatches.")
