import argparse
import json
import csv
import heapq
from candidate_scorer import score_candidate
from reasoning_generator import generate_reasoning

def main():
    parser = argparse.ArgumentParser(description="Redrob Candidate Ranking Engine")
    parser.add_argument('--input', required=True, help="Path to candidates.jsonl")
    parser.add_argument('--output', required=True, help="Path to output submission.csv")
    args = parser.parse_args()

    # Min-heap format: (score, -num_id, candidate_id)
    top_100 = []
    
    # Store dictionaries strictly isolated from heapq evaluation
    candidates_data = {}
    seen_ids = set()

    with open(args.input, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            try:
                candidate = json.loads(line)
                if not isinstance(candidate, dict):
                    continue
            except ValueError:
                continue
            
            raw_id = candidate.get("candidate_id")
            if not raw_id:
                continue
                
            candidate_id = str(raw_id)
            if candidate_id in seen_ids:
                continue
            
            seen_ids.add(candidate_id)
            score_result = score_candidate(candidate)
            
            # Maintain raw float precision in heap memory
            score = float(score_result.get('final_score', 0.0))
            
            try:
                num_id = int(candidate_id.split('_')[-1])
            except (ValueError, IndexError, AttributeError):
                num_id = 0
                
            item = (score, -num_id, candidate_id)
            candidate_payload = (candidate, score_result.get('score_breakdown', {}))
            
            if len(top_100) < 100:
                heapq.heappush(top_100, item)
                candidates_data[candidate_id] = candidate_payload
            else:
                min_item = top_100[0]
                if item > min_item:
                    popped = heapq.heappushpop(top_100, item)
                    # Safely remove popped candidate only if it was actually ejected
                    if popped != item:
                        candidates_data.pop(popped[2], None)
                        candidates_data[candidate_id] = candidate_payload

    # Sort descending by score, ascending by candidate ID tiebreaker
    top_100.sort(key=lambda x: (-x[0], -x[1], x[2]))

    if len(top_100) < 100:
        import sys
        print(
            f"WARNING: only {len(top_100)} valid candidates were found in the input "
            f"(need 100). The output CSV will not meet the submission requirements.",
            file=sys.stderr,
        )

    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['candidate_id', 'rank', 'score', 'reasoning'])
        
        for rank, item in enumerate(top_100, start=1):
            if rank > 100: break
                
            score = item[0]
            candidate_id = item[2]
            candidate, breakdown = candidates_data[candidate_id]
            
            reasoning = generate_reasoning(candidate, breakdown)
            
            writer.writerow([candidate_id, rank, f"{score:.8f}", reasoning])

if __name__ == '__main__':
    main()