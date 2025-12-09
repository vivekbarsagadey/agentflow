import json
import requests

# Corrected workflow specification
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
                'prompt': 'Respond to: {user_input}'
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
                'model_name': 'gemini-1.5-flash',
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

print('Testing corrected workflow validation...')
try:
    # For validation endpoint, send just the workflow spec directly
    response = requests.post(
        'http://127.0.0.1:8000/api/v1/workflows/validate',
        json=corrected_workflow,  # Send workflow spec directly, not wrapped
        headers={'Content-Type': 'application/json'}
    )
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        result = response.json()
        print(f'Valid: {result.get("valid")}')
        if not result.get('valid'):
            print('Errors:')
            for error in result.get('errors', []):
                print(f'  {error.get("type")}: {error.get("message")}')
        else:
            print('✅ Workflow validation passed!')
    else:
        print(f'❌ HTTP Error: {response.status_code}')
        print(f'Response: {response.text}')

except Exception as e:
    print(f'Error: {e}')

print('\n' + '='*50)
print('Testing workflow execution...')

try:
    # For execution endpoint, send ExecuteRequest with workflow and initial_state
    response = requests.post(
        'http://127.0.0.1:8000/api/v1/workflows/execute',
        json=request_data,  # Send wrapped request with workflow and initial_state
        headers={'Content-Type': 'application/json'}
    )
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        result = response.json()
        print(f'Status: {result.get("status")}')
        print(f'Final state keys: {list(result.get("final_state", {}).keys())}')
        print('✅ Workflow execution completed!')
    else:
        print(f'❌ HTTP Error: {response.status_code}')
        print(f'Response: {response.text}')

except Exception as e:
    print(f'Error: {e}')