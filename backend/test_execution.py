import json
import requests

# Corrected workflow specification with proper model name
corrected_workflow = {
    'nodes': [
        {
            'id': 'input',
            'type': 'input',
            'metadata': None
        },
        {
            'id': 'llm',
            'type': 'llm',
            'metadata': {
                'source_id': 'gemini',
                'prompt_template': 'Respond to: {user_input}'
            }
        }
    ],
    'edges': [
        {
            'from': 'input',
            'to': 'llm'
        }
    ],
    'queues': [],
    'sources': [
        {
            'id': 'gemini',
            'kind': 'llm',
            'config': {
                'model_name': 'gemini-2.5-flash',  # Fixed: was 'gemini-1.5-flash'
                'api_key_env': 'GEMINI_API_KEY'
            }
        }
    ],
    'start_node': 'input',
    'name': 'Simple LLM Workflow',
    'description': 'A basic workflow that takes input and generates a response',
    'version': '1.0.0'
}

request_data = {
    'workflow': corrected_workflow,
    'initial_state': {
        'user_input': 'Hello, tell me a joke'
    }
}

print('Testing workflow execution with correct model name...')
try:
    response = requests.post(
        'http://127.0.0.1:8000/api/v1/workflows/execute',
        json=request_data,
        headers={'Content-Type': 'application/json'}
    )
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        result = response.json()
        print(f'Status: {result.get("status")}')
        print(f'Final state keys: {list(result.get("final_state", {}).keys())}')
        text_result = result.get("final_state", {}).get("text_result", "")
        print(f'Response: {text_result[:200]}...')
        print('✅ Workflow execution successful!')
    else:
        print(f'❌ HTTP Error: {response.status_code}')
        print(f'Response: {response.text}')

except Exception as e:
    print(f'Error: {e}')