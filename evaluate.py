import json
from rag import retrieve, generate_answer
from agent import classify_query

def evaluate_retrieval(question, expected_product_ids, retrieved_chunks):
    """Check if expected product IDs are in retrieved chunks"""
    retrieved_text = " ".join([c['text'] for c in retrieved_chunks])
    
    found = []
    missing = []
    
    for product_id in expected_product_ids:
        if product_id in retrieved_text:
            found.append(product_id)
        else:
            missing.append(product_id)
    
    recall = len(found) / len(expected_product_ids) if expected_product_ids else 1.0
    
    return {
        "recall": recall,
        "found": found,
        "missing": missing
    }

def evaluate_answer_quality(answer, expected_keywords):
    """Check if answer contains expected keywords"""
    answer_lower = answer.lower()
    
    found = []
    missing = []
    
    for keyword in expected_keywords:
        if keyword.lower() in answer_lower:
            found.append(keyword)
        else:
            missing.append(keyword)
    
    coverage = len(found) / len(expected_keywords) if expected_keywords else 1.0
    
    return {
        "keyword_coverage": coverage,
        "found_keywords": found,
        "missing_keywords": missing
    }

def evaluate_agent(question, expected_query_type):
    """Check if agent classifies query correctly"""
    predicted_type = classify_query(question)
    correct = predicted_type == expected_query_type
    
    return {
        "correct": correct,
        "predicted": predicted_type,
        "expected": expected_query_type
    }

def run_evaluation():
    """Run full evaluation suite"""
    
    with open('eval/eval_dataset.json', 'r') as f:
        data = json.load(f)
    
    results = {
        "total_cases": len(data['test_cases']),
        "agent_accuracy": 0,
        "avg_retrieval_recall": 0,
        "avg_answer_coverage": 0,
        "cases": []
    }
    
    agent_correct = 0
    total_recall = 0
    total_coverage = 0
    
    for i, test_case in enumerate(data['test_cases']):
        print(f"\n{'='*60}")
        print(f"Test Case {i+1}: {test_case['question']}")
        print(f"{'='*60}")
        
        case_result = {
            "question": test_case['question'],
            "agent_eval": {},
            "retrieval_eval": {},
            "answer_eval": {}
        }
        
        # 1. Evaluate agent classification
        if 'query_type' in test_case:
            agent_eval = evaluate_agent(test_case['question'], test_case['query_type'])
            case_result['agent_eval'] = agent_eval
            
            if agent_eval['correct']:
                agent_correct += 1
            
            print(f"\n📊 Agent Classification:")
            print(f"   Expected: {agent_eval['expected']}")
            print(f"   Predicted: {agent_eval['predicted']}")
            print(f"   ✓ Correct" if agent_eval['correct'] else "   ✗ Incorrect")
        
        # 2. Retrieve and evaluate retrieval
        retrieved, q_type = retrieve(test_case['question'])
        
        if 'expected_product_ids' in test_case:
            retrieval_eval = evaluate_retrieval(
                test_case['question'],
                test_case['expected_product_ids'],
                retrieved
            )
            case_result['retrieval_eval'] = retrieval_eval
            total_recall += retrieval_eval['recall']
            
            print(f"\n🔍 Retrieval Evaluation:")
            print(f"   Recall: {retrieval_eval['recall']:.2%}")
            print(f"   Found IDs: {retrieval_eval['found']}")
            if retrieval_eval['missing']:
                print(f"   Missing IDs: {retrieval_eval['missing']}")
        
        # 3. Generate answer and evaluate
        answer = generate_answer(test_case['question'], retrieved)
        
        if 'expected_keywords' in test_case:
            answer_eval = evaluate_answer_quality(answer, test_case['expected_keywords'])
            case_result['answer_eval'] = answer_eval
            total_coverage += answer_eval['keyword_coverage']
            
            print(f"\n💬 Answer Quality:")
            print(f"   Keyword Coverage: {answer_eval['keyword_coverage']:.2%}")
            print(f"   Found: {answer_eval['found_keywords']}")
            if answer_eval['missing_keywords']:
                print(f"   Missing: {answer_eval['missing_keywords']}")
        
        print(f"\n📝 Generated Answer:")
        print(f"   {answer[:200]}...")
        
        results['cases'].append(case_result)
    
    # Calculate aggregate metrics
    results['agent_accuracy'] = agent_correct / results['total_cases']
    
    retrieval_cases = sum(1 for c in data['test_cases'] if 'expected_product_ids' in c)
    if retrieval_cases > 0:
        results['avg_retrieval_recall'] = total_recall / retrieval_cases
    
    answer_cases = sum(1 for c in data['test_cases'] if 'expected_keywords' in c)
    if answer_cases > 0:
        results['avg_answer_coverage'] = total_coverage / answer_cases
    
    # Print summary
    print(f"\n\n{'='*60}")
    print("EVALUATION SUMMARY")
    print(f"{'='*60}")
    print(f"Total Test Cases: {results['total_cases']}")
    print(f"Agent Accuracy: {results['agent_accuracy']:.2%}")
    print(f"Avg Retrieval Recall: {results['avg_retrieval_recall']:.2%}")
    print(f"Avg Answer Coverage: {results['avg_answer_coverage']:.2%}")
    
    # Save results
    with open('eval/eval_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to eval_results.json")
    
    return results

if __name__ == "__main__":
    run_evaluation()