# AgentFlow Workflow Examples

> **Comprehensive workflow examples for AgentFlow engine covering all supported patterns.**

This document provides 6 complete workflow examples that you can use as templates. Each example includes:
- Complete JSON workflow definition
- All required fields (nodes, edges, sources, start_node, metadata, initial_state)
- Edge cases and error handling considerations
- Realistic prompts, templates, and configuration

---

## Table of Contents

1. [Simple Pattern: Input to LLM](#1-simple-pattern-input-to-llm)
2. [Sequential Pattern: Multi-Step Processing](#2-sequential-pattern-multi-step-processing)
3. [Parallel Pattern: Concurrent Execution](#3-parallel-pattern-concurrent-execution)
4. [Conditional Pattern: Intent-Based Routing](#4-conditional-pattern-intent-based-routing)
5. [Subflow Pattern: Nested Workflows](#5-subflow-pattern-nested-workflows)
6. [Human-Interaction Pattern: Approval Workflow](#6-human-interaction-pattern-approval-workflow)

---

## 1. Simple Pattern: Input to LLM

**Scenario**: Basic chatbot that takes user input and generates an AI response.

**Use Cases**:
- Simple Q&A bot
- Text generation
- Code explanation

### Workflow Definition

```json
{
  "name": "Simple Chatbot",
  "description": "Basic input to LLM workflow for conversational AI",
  "version": "1.0.0",
  "start_node": "input",
  
  "nodes": [
    {
      "id": "input",
      "type": "input",
      "metadata": {
        "description": "Receives user input and passes to LLM",
        "validation": {
          "required": true,
          "max_length": 10000,
          "min_length": 1
        }
      }
    },
    {
      "id": "llm_respond",
      "type": "llm",
      "metadata": {
        "source_id": "gemini-llm",
        "prompt_template": "You are a helpful AI assistant. Respond to the following user message:\n\n{user_input}\n\nProvide a clear, concise, and helpful response.",
        "system_prompt": "You are a friendly and knowledgeable AI assistant. Be helpful, accurate, and engaging.",
        "temperature": 0.7,
        "max_tokens": 2048,
        "output_key": "text_result"
      }
    },
    {
      "id": "aggregator",
      "type": "aggregator",
      "metadata": {
        "strategy": "merge",
        "source_keys": ["text_result"],
        "output_key": "final_output",
        "include_metadata": true
      }
    }
  ],
  
  "edges": [
    { "from": "input", "to": "llm_respond" },
    { "from": "llm_respond", "to": "aggregator" }
  ],
  
  "queues": [
    {
      "id": "queue_llm",
      "from": "input",
      "to": "llm_respond",
      "bandwidth": {
        "max_requests_per_minute": 60,
        "max_tokens_per_minute": 100000
      }
    }
  ],
  
  "sources": [
    {
      "id": "gemini-llm",
      "kind": "llm",
      "config": {
        "provider": "gemini",
        "model": "gemini-2.5-flash",
        "api_key_env": "GEMINI_API_KEY",
        "max_retries": 3,
        "timeout": 30
      }
    }
  ]
}
```

### Initial State

```json
{
  "user_input": "Explain quantum computing in simple terms"
}
```

### Expected Output

```json
{
  "status": "success",
  "final_state": {
    "user_input": "Explain quantum computing in simple terms",
    "text_result": "Quantum computing is a revolutionary technology that...",
    "final_output": {
      "result": {
        "text_result": "Quantum computing is a revolutionary technology that..."
      },
      "execution_path": ["input", "llm_respond", "aggregator"],
      "tokens_used": 256,
      "cost": 0.0003
    },
    "tokens_used": 256
  }
}
```

### Edge Cases

| Scenario | Handling |
|----------|----------|
| Empty input | Validation fails with "min_length" error |
| Input too long | Validation fails with "max_length" error |
| LLM API timeout | Retry up to 3 times, then fail gracefully |
| Invalid API key | Return error with clear message |

---

## 2. Sequential Pattern: Multi-Step Processing

**Scenario**: Document processing pipeline that summarizes, translates, and formats content.

**Use Cases**:
- Content processing pipelines
- Data transformation workflows
- Multi-step analysis

### Workflow Definition

```json
{
  "name": "Document Processing Pipeline",
  "description": "Sequential workflow: Summarize → Translate → Format",
  "version": "1.0.0",
  "start_node": "input",
  
  "nodes": [
    {
      "id": "input",
      "type": "input",
      "metadata": {
        "description": "Receives document content for processing",
        "validation": {
          "required": true,
          "max_length": 50000
        }
      }
    },
    {
      "id": "summarize",
      "type": "llm",
      "metadata": {
        "source_id": "gemini-llm",
        "prompt_template": "Summarize the following document in 3-5 key bullet points:\n\n{user_input}\n\nProvide a concise summary that captures the main ideas.",
        "system_prompt": "You are an expert document summarizer. Extract key points accurately and concisely.",
        "temperature": 0.3,
        "max_tokens": 1024,
        "output_key": "summary"
      }
    },
    {
      "id": "translate",
      "type": "llm",
      "metadata": {
        "source_id": "gemini-llm",
        "prompt_template": "Translate the following summary to Spanish:\n\n{summary}\n\nProvide a natural, fluent translation.",
        "system_prompt": "You are a professional translator. Maintain the meaning and tone of the original text.",
        "temperature": 0.2,
        "max_tokens": 1024,
        "output_key": "translation"
      }
    },
    {
      "id": "format",
      "type": "llm",
      "metadata": {
        "source_id": "gemini-llm",
        "prompt_template": "Format the following content as a professional report with HTML tags:\n\nOriginal Summary:\n{summary}\n\nSpanish Translation:\n{translation}\n\nCreate a well-structured HTML document with proper headings and styling.",
        "system_prompt": "You are a document formatter. Create clean, professional HTML output.",
        "temperature": 0.1,
        "max_tokens": 2048,
        "output_key": "formatted_output"
      }
    },
    {
      "id": "aggregator",
      "type": "aggregator",
      "metadata": {
        "strategy": "merge",
        "source_keys": ["summary", "translation", "formatted_output"],
        "output_key": "final_output",
        "include_metadata": true
      }
    }
  ],
  
  "edges": [
    { "from": "input", "to": "summarize" },
    { "from": "summarize", "to": "translate" },
    { "from": "translate", "to": "format" },
    { "from": "format", "to": "aggregator" }
  ],
  
  "queues": [
    {
      "id": "queue_summarize",
      "from": "input",
      "to": "summarize",
      "bandwidth": {
        "max_requests_per_minute": 30,
        "max_tokens_per_minute": 50000
      }
    },
    {
      "id": "queue_translate",
      "from": "summarize",
      "to": "translate",
      "bandwidth": {
        "max_requests_per_minute": 30,
        "max_tokens_per_minute": 50000
      }
    }
  ],
  
  "sources": [
    {
      "id": "gemini-llm",
      "kind": "llm",
      "config": {
        "provider": "gemini",
        "model": "gemini-2.5-flash",
        "api_key_env": "GEMINI_API_KEY",
        "max_retries": 3,
        "timeout": 60
      }
    }
  ]
}
```

### Initial State

```json
{
  "user_input": "Artificial Intelligence (AI) is transforming industries worldwide. From healthcare diagnostics to autonomous vehicles, AI systems are becoming increasingly sophisticated. Machine learning, a subset of AI, enables computers to learn from data without explicit programming. Deep learning, using neural networks with many layers, has achieved breakthrough results in image recognition, natural language processing, and game playing. However, AI also raises ethical concerns about bias, privacy, and job displacement. As AI continues to evolve, society must balance innovation with responsible development."
}
```

### Expected Output

```json
{
  "status": "success",
  "final_state": {
    "user_input": "...",
    "summary": "• AI is transforming multiple industries including healthcare and autonomous vehicles\n• Machine learning enables computers to learn from data\n• Deep learning has achieved breakthroughs in image recognition and NLP\n• Ethical concerns include bias, privacy, and job displacement\n• Balance between innovation and responsible development is needed",
    "translation": "• La IA está transformando múltiples industrias...",
    "formatted_output": "<html><body><h1>Document Summary</h1>...",
    "final_output": {
      "result": {
        "summary": "...",
        "translation": "...",
        "formatted_output": "..."
      },
      "execution_path": ["input", "summarize", "translate", "format", "aggregator"],
      "tokens_used": 1024,
      "cost": 0.0012
    }
  }
}
```

### Edge Cases

| Scenario | Handling |
|----------|----------|
| Empty summary | Pass original input to next step |
| Translation fails | Retry with fallback language model |
| Very long document | Chunk document and process in parts |
| Formatting errors | Return raw text with error note |

---

## 3. Parallel Pattern: Concurrent Execution

**Scenario**: Multi-modal content generation that creates text, image, and data analysis simultaneously.

**Use Cases**:
- Marketing content generation
- Report generation with visuals
- Multi-format output creation

### Workflow Definition

```json
{
  "name": "Parallel Content Generator",
  "description": "Generates text, image, and data analysis in parallel",
  "version": "1.0.0",
  "start_node": "input",
  
  "nodes": [
    {
      "id": "input",
      "type": "input",
      "metadata": {
        "description": "Receives topic for multi-modal content generation"
      }
    },
    {
      "id": "router_parallel",
      "type": "router",
      "metadata": {
        "strategy": "default",
        "description": "Routes to parallel processing branches",
        "default_intent": "parallel_all"
      }
    },
    {
      "id": "generate_article",
      "type": "llm",
      "metadata": {
        "source_id": "gemini-llm",
        "prompt_template": "Write a comprehensive 500-word article about: {user_input}\n\nInclude:\n- An engaging introduction\n- 3 main sections with headers\n- A conclusion with call-to-action\n\nUse a professional yet accessible tone.",
        "system_prompt": "You are a professional content writer specializing in engaging, informative articles.",
        "temperature": 0.7,
        "max_tokens": 2048,
        "output_key": "article"
      }
    },
    {
      "id": "generate_image",
      "type": "image",
      "metadata": {
        "source_id": "gemini-imagen",
        "prompt_template": "Create a professional, modern illustration representing: {user_input}. Style: clean, corporate, minimalist with blue and white color scheme.",
        "size": "1024x1024",
        "quality": "hd",
        "style": "vivid",
        "output_key": "hero_image"
      }
    },
    {
      "id": "analyze_trends",
      "type": "llm",
      "metadata": {
        "source_id": "gemini-llm",
        "prompt_template": "Analyze current trends and statistics related to: {user_input}\n\nProvide:\n1. 5 key statistics with sources\n2. Market trends\n3. Future predictions\n4. Competitive landscape\n\nFormat as structured data.",
        "system_prompt": "You are a data analyst. Provide accurate, well-researched insights.",
        "temperature": 0.3,
        "max_tokens": 1500,
        "output_key": "trend_analysis"
      }
    },
    {
      "id": "generate_social_posts",
      "type": "llm",
      "metadata": {
        "source_id": "gemini-llm",
        "prompt_template": "Create social media content for: {user_input}\n\nGenerate:\n1. Twitter/X post (280 chars max)\n2. LinkedIn post (professional tone)\n3. Instagram caption (engaging, with hashtags)\n4. Facebook post (conversational)\n\nMake each unique and platform-appropriate.",
        "system_prompt": "You are a social media strategist. Create engaging, platform-optimized content.",
        "temperature": 0.8,
        "max_tokens": 1000,
        "output_key": "social_posts"
      }
    },
    {
      "id": "merge_results",
      "type": "aggregator",
      "metadata": {
        "strategy": "merge",
        "source_keys": ["article", "hero_image", "trend_analysis", "social_posts"],
        "output_key": "final_output",
        "include_metadata": true,
        "template": "# Content Package\n\n## Article\n{article}\n\n## Visual Asset\n{hero_image}\n\n## Market Analysis\n{trend_analysis}\n\n## Social Media Kit\n{social_posts}"
      }
    }
  ],
  
  "edges": [
    { "from": "input", "to": "router_parallel" },
    { "from": "router_parallel", "to": ["generate_article", "generate_image", "analyze_trends", "generate_social_posts"] },
    { "from": "generate_article", "to": "merge_results" },
    { "from": "generate_image", "to": "merge_results" },
    { "from": "analyze_trends", "to": "merge_results" },
    { "from": "generate_social_posts", "to": "merge_results" }
  ],
  
  "queues": [
    {
      "id": "queue_article",
      "from": "router_parallel",
      "to": "generate_article",
      "bandwidth": {
        "max_requests_per_minute": 20,
        "max_tokens_per_minute": 50000
      }
    },
    {
      "id": "queue_image",
      "from": "router_parallel",
      "to": "generate_image",
      "bandwidth": {
        "max_requests_per_minute": 10,
        "max_messages_per_second": 1
      }
    }
  ],
  
  "sources": [
    {
      "id": "gemini-llm",
      "kind": "llm",
      "config": {
        "provider": "gemini",
        "model": "gemini-2.5-flash",
        "api_key_env": "GEMINI_API_KEY",
        "max_retries": 3,
        "timeout": 60
      }
    },
    {
      "id": "gemini-imagen",
      "kind": "image",
      "config": {
        "provider": "gemini",
        "model": "imagen-3.0",
        "api_key_env": "GEMINI_API_KEY"
      }
    }
  ]
}
```

### Initial State

```json
{
  "user_input": "Sustainable Energy Solutions for Smart Cities"
}
```

### Expected Output

```json
{
  "status": "success",
  "final_state": {
    "user_input": "Sustainable Energy Solutions for Smart Cities",
    "article": "# Sustainable Energy Solutions for Smart Cities\n\nAs urbanization accelerates...",
    "hero_image": {
      "type": "url",
      "url": "https://generated-image-url.com/...",
      "prompt": "Create a professional, modern illustration...",
      "size": "1024x1024"
    },
    "trend_analysis": {
      "statistics": [...],
      "trends": [...],
      "predictions": [...]
    },
    "social_posts": {
      "twitter": "🌱 Smart cities are going green!...",
      "linkedin": "The future of urban energy is here...",
      "instagram": "Imagine a city powered entirely by...",
      "facebook": "Have you ever wondered what makes..."
    },
    "final_output": {
      "result": {...},
      "execution_path": ["input", "router_parallel", "generate_article", "generate_image", "analyze_trends", "generate_social_posts", "merge_results"],
      "tokens_used": 4500,
      "cost": 0.0054
    }
  }
}
```

### Edge Cases

| Scenario | Handling |
|----------|----------|
| One branch fails | Complete other branches, mark failed branch as error |
| Image generation unavailable | Return placeholder image with note |
| Rate limit exceeded | Queue requests, process when available |
| Timeout on one branch | Return partial results with timeout note |

---

## 4. Conditional Pattern: Intent-Based Routing

**Scenario**: Customer support bot that routes queries to specialized handlers based on intent.

**Use Cases**:
- Customer support automation
- Helpdesk ticketing
- FAQ routing

### Workflow Definition

```json
{
  "name": "Customer Support Router",
  "description": "Routes customer queries based on intent classification",
  "version": "1.0.0",
  "start_node": "input",
  
  "nodes": [
    {
      "id": "input",
      "type": "input",
      "metadata": {
        "description": "Receives customer support query"
      }
    },
    {
      "id": "classify_intent",
      "type": "router",
      "metadata": {
        "strategy": "keyword",
        "routes": [
          {
            "intent": "billing",
            "keywords": ["invoice", "payment", "charge", "bill", "refund", "subscription", "pricing", "cost", "fee"]
          },
          {
            "intent": "technical",
            "keywords": ["error", "bug", "crash", "not working", "broken", "issue", "problem", "fix", "help", "how to"]
          },
          {
            "intent": "sales",
            "keywords": ["buy", "purchase", "upgrade", "plan", "enterprise", "quote", "demo", "trial", "discount"]
          },
          {
            "intent": "account",
            "keywords": ["password", "login", "account", "profile", "settings", "email", "username", "security"]
          }
        ],
        "default_intent": "general"
      }
    },
    {
      "id": "handle_billing",
      "type": "llm",
      "metadata": {
        "source_id": "gemini-llm",
        "prompt_template": "You are a billing support specialist. The customer asked:\n\n{user_input}\n\nProvide helpful information about:\n- Payment methods and processing\n- Invoice questions\n- Refund policies (14-day money-back guarantee)\n- Subscription management\n\nBe professional and empathetic.",
        "system_prompt": "You are a billing support specialist at TechCorp. Our pricing: Basic $9/mo, Pro $29/mo, Enterprise custom. 14-day refund policy applies.",
        "temperature": 0.5,
        "max_tokens": 1024,
        "output_key": "support_response"
      }
    },
    {
      "id": "handle_technical",
      "type": "llm",
      "metadata": {
        "source_id": "gemini-llm",
        "prompt_template": "You are a technical support engineer. The customer reported:\n\n{user_input}\n\nProvide:\n1. Troubleshooting steps\n2. Common solutions\n3. Escalation path if needed\n\nBe clear and patient.",
        "system_prompt": "You are a technical support engineer. Guide users through troubleshooting. If complex, offer to create a support ticket.",
        "temperature": 0.3,
        "max_tokens": 1500,
        "output_key": "support_response"
      }
    },
    {
      "id": "handle_sales",
      "type": "llm",
      "metadata": {
        "source_id": "gemini-llm",
        "prompt_template": "You are a sales representative. The customer inquired:\n\n{user_input}\n\nProvide:\n- Relevant product information\n- Pricing options\n- Benefits and features\n- Next steps (demo, trial, contact sales)\n\nBe helpful and not pushy.",
        "system_prompt": "You are a friendly sales rep. Highlight value, offer trials, and guide toward the right solution.",
        "temperature": 0.6,
        "max_tokens": 1024,
        "output_key": "support_response"
      }
    },
    {
      "id": "handle_account",
      "type": "llm",
      "metadata": {
        "source_id": "gemini-llm",
        "prompt_template": "You are an account specialist. The customer needs help with:\n\n{user_input}\n\nAssist with:\n- Password reset process\n- Account settings\n- Security best practices\n- Profile updates\n\nPrioritize security.",
        "system_prompt": "You are an account security specialist. Always verify identity for sensitive operations. Guide users safely.",
        "temperature": 0.4,
        "max_tokens": 1024,
        "output_key": "support_response"
      }
    },
    {
      "id": "handle_general",
      "type": "llm",
      "metadata": {
        "source_id": "gemini-llm",
        "prompt_template": "You are a general support agent. The customer asked:\n\n{user_input}\n\nProvide helpful information and guide them to the right resource. If you can't help, offer to connect them with a specialist.",
        "system_prompt": "You are a helpful support agent. Try to understand the need and route appropriately.",
        "temperature": 0.6,
        "max_tokens": 1024,
        "output_key": "support_response"
      }
    },
    {
      "id": "format_response",
      "type": "aggregator",
      "metadata": {
        "strategy": "template",
        "template": "## Support Response\n\n**Category**: {intent}\n\n**Response**:\n{support_response}\n\n---\n*Need more help? Reply to this message or contact support@example.com*",
        "output_key": "final_output",
        "include_metadata": true
      }
    }
  ],
  
  "edges": [
    { "from": "input", "to": "classify_intent" },
    { 
      "from": "classify_intent", 
      "to": ["handle_billing", "handle_technical", "handle_sales", "handle_account", "handle_general"],
      "condition": "intent"
    },
    { "from": "handle_billing", "to": "format_response" },
    { "from": "handle_technical", "to": "format_response" },
    { "from": "handle_sales", "to": "format_response" },
    { "from": "handle_account", "to": "format_response" },
    { "from": "handle_general", "to": "format_response" }
  ],
  
  "queues": [
    {
      "id": "queue_support",
      "from": "classify_intent",
      "to": "handle_billing",
      "bandwidth": {
        "max_requests_per_minute": 100,
        "max_tokens_per_minute": 100000
      }
    }
  ],
  
  "sources": [
    {
      "id": "gemini-llm",
      "kind": "llm",
      "config": {
        "provider": "gemini",
        "model": "gemini-2.5-flash",
        "api_key_env": "GEMINI_API_KEY",
        "max_retries": 3,
        "timeout": 30
      }
    }
  ]
}
```

### Initial State Examples

**Billing Query:**
```json
{
  "user_input": "I was charged twice for my subscription last month. Can I get a refund?"
}
```

**Technical Query:**
```json
{
  "user_input": "The app keeps crashing when I try to upload a file. Error code: ERR_UPLOAD_FAILED"
}
```

**Sales Query:**
```json
{
  "user_input": "What's the difference between Pro and Enterprise plans? We have 50 users."
}
```

### Expected Output (Billing Example)

```json
{
  "status": "success",
  "final_state": {
    "user_input": "I was charged twice for my subscription last month...",
    "intent": "billing",
    "support_response": "I apologize for the inconvenience of being charged twice...",
    "final_output": {
      "result": "## Support Response\n\n**Category**: billing\n\n**Response**:\nI apologize for the inconvenience...",
      "execution_path": ["input", "classify_intent", "handle_billing", "format_response"],
      "tokens_used": 512,
      "cost": 0.0006
    }
  }
}
```

### Edge Cases

| Scenario | Handling |
|----------|----------|
| Ambiguous intent | Route to general, mention multiple possible topics |
| Multiple intents detected | Prioritize first match, mention other topics available |
| No keywords match | Route to general handler |
| Angry/urgent language | Flag for priority handling, empathetic response |
| Non-English input | Detect language, respond accordingly or escalate |

---

## 5. Subflow Pattern: Nested Workflows

**Scenario**: E-commerce order processing with validation error handling and LLM-based inventory simulation.

**Use Cases**:
- Order processing pipelines
- Multi-stage approvals
- Complex business workflows with validation gates

### Workflow Definition

```json
{
  "name": "Order Processing Pipeline",
  "description": "E-commerce order processing with validation and error handling",
  "version": "1.0.0",
  "start_node": "input",
  
  "nodes": [
    {
      "id": "input",
      "type": "input",
      "metadata": {
        "description": "Receives order details",
        "validation": {
          "required_fields": ["customer_id", "items", "shipping_address"]
        }
      }
    },
    {
      "id": "validate_order",
      "type": "llm",
      "metadata": {
        "source_id": "groq-llm",
        "prompt_template": "Validate the following order data:\n\nOrder: {user_input}\n\nCheck for:\n1. Valid customer ID format\n2. Item quantities are positive integers\n3. Shipping address is complete\n4. Payment method is valid\n\nReturn JSON with:\n{\n  \"valid\": boolean,\n  \"errors\": [],\n  \"warnings\": [],\n  \"processed_order\": {...}\n}",
        "system_prompt": "You are an order validation system. Return structured JSON responses only.",
        "temperature": 0.1,
        "max_tokens": 800,
        "output_key": "validation_result"
      }
    },
    {
      "id": "validation_router",
      "type": "router",
      "metadata": {
        "strategy": "keyword",
        "routes": [
          {
            "intent": "proceed",
            "keywords": ["true", "valid"]
          },
          {
            "intent": "error",
            "keywords": ["false", "invalid"]
          }
        ],
        "default_intent": "proceed"
      }
    },
    {
      "id": "validation_error_handler",
      "type": "aggregator",
      "metadata": {
        "strategy": "merge",
        "source_keys": ["validation_result"],
        "output_key": "final_output",
        "include_metadata": true
      }
    },
    {
      "id": "check_inventory",
      "type": "llm",
      "metadata": {
        "source_id": "groq-llm",
        "prompt_template": "Simulate an inventory check for the following products:\n\nProduct IDs: {product_ids}\n\nReturn a realistic JSON array like:\n[\n  {\"product_id\": \"PROD-001\", \"name\": \"Wireless Mouse\", \"stock_quantity\": 150, \"price\": 29.99},\n  {\"product_id\": \"PROD-002\", \"name\": \"USB-C Hub\", \"stock_quantity\": 45, \"price\": 49.99}\n]\n\nBe realistic with stock levels and pricing.",
        "temperature": 0.1,
        "max_tokens": 300,
        "output_key": "inventory_check"
      }
    },
    {
      "id": "calculate_totals",
      "type": "llm",
      "metadata": {
        "source_id": "groq-llm",
        "prompt_template": "Calculate order totals:\n\nOrder Items: {validation_result}\nInventory Data: {inventory_check}\n\nCalculate:\n1. Subtotal (item prices × quantities)\n2. Tax (8.5%)\n3. Shipping (free over $50, otherwise $5.99)\n4. Total\n5. Estimated delivery date (3-5 business days from today)\n\nReturn structured JSON.",
        "system_prompt": "You are a pricing calculator. Be precise with calculations.",
        "temperature": 0.1,
        "max_tokens": 600,
        "output_key": "order_totals"
      }
    },
    {
      "id": "process_payment",
      "type": "llm",
      "metadata": {
        "source_id": "groq-llm",
        "prompt_template": "Simulate payment processing for:\n\nOrder Total: {order_totals}\nPayment Method: {payment_method}\n\nGenerate:\n1. Transaction ID (format: TXN-YYYYMMDD-XXX)\n2. Authorization code (format: AUTH-XXXXXX)\n3. Payment status (approved)\n4. Timestamp (current datetime)\n\nReturn structured JSON payment receipt.",
        "system_prompt": "You are a payment processor. Generate realistic transaction data.",
        "temperature": 0.2,
        "max_tokens": 600,
        "output_key": "payment_result"
      }
    },
    {
      "id": "generate_confirmation",
      "type": "llm",
      "metadata": {
        "source_id": "groq-llm",
        "prompt_template": "Generate order confirmation email content:\n\nOrder Details: {validation_result}\nTotals: {order_totals}\nPayment: {payment_result}\n\nCreate a professional, friendly confirmation email with:\n1. Order summary\n2. Itemized list\n3. Shipping information\n4. Tracking info placeholder\n5. Customer service contact\n\nKeep it concise and professional.",
        "system_prompt": "You are an email template generator. Create professional, well-formatted content.",
        "temperature": 0.5,
        "max_tokens": 800,
        "output_key": "confirmation_email"
      }
    },
    {
      "id": "aggregator",
      "type": "aggregator",
      "metadata": {
        "strategy": "merge",
        "source_keys": ["validation_result", "inventory_check", "order_totals", "payment_result", "confirmation_email"],
        "output_key": "final_output",
        "include_metadata": true
      }
    }
  ],
  
  "edges": [
    { "from": "input", "to": "validate_order" },
    { "from": "validate_order", "to": "validation_router" },
    { 
      "from": "validation_router", 
      "to": ["check_inventory", "validation_error_handler"],
      "condition": "intent"
    },
    { "from": "check_inventory", "to": "calculate_totals" },
    { "from": "calculate_totals", "to": "process_payment" },
    { "from": "process_payment", "to": "generate_confirmation" },
    { "from": "generate_confirmation", "to": "aggregator" }
  ],
  
  "queues": [
    {
      "id": "queue_validation",
      "from": "input",
      "to": "validate_order",
      "bandwidth": {
        "max_requests_per_minute": 100
      }
    },
    {
      "id": "queue_payment",
      "from": "calculate_totals",
      "to": "process_payment",
      "bandwidth": {
        "max_requests_per_minute": 50,
        "max_messages_per_second": 5
      }
    }
  ],
  
  "sources": [
    {
      "id": "groq-llm",
      "kind": "llm",
      "config": {
        "provider": "groq",
        "model": "llama-3.3-70b-versatile",
        "api_key_env": "GROQ_API_KEY"
      }
    }
  ],
  
  "metadata": {
    "description": "Complete order processing pipeline with validation",
    "version": "1.0.0"
  }
}
```

### Initial State

```json
{
  "user_input": {
    "customer_id": "CUST-12345",
    "items": [
      { 
        "product_id": "PROD-001", 
        "name": "Wireless Mouse", 
        "quantity": 2 
      },
      { 
        "product_id": "PROD-002", 
        "name": "USB-C Hub", 
        "quantity": 1 
      }
    ],
    "shipping_address": {
      "name": "John Doe",
      "street": "123 Main St",
      "city": "San Francisco",
      "state": "CA",
      "zip": "94105",
      "country": "USA"
    },
    "payment_method": {
      "type": "credit_card",
      "last_four": "4242"
    }
  },
  "product_ids": "PROD-001, PROD-002",
  "payment_method": "credit_card"
}
```

### Expected Output (Success Path)

```json
{
  "status": "success",
  "final_state": {
    "validation_result": {
      "valid": true,
      "errors": [],
      "warnings": [],
      "processed_order": {
        "customer_id": "CUST-12345",
        "items": [
          { "product_id": "PROD-001", "name": "Wireless Mouse", "quantity": 2 },
          { "product_id": "PROD-002", "name": "USB-C Hub", "quantity": 1 }
        ]
      }
    },
    "inventory_check": [
      { "product_id": "PROD-001", "name": "Wireless Mouse", "stock_quantity": 150, "price": 29.99 },
      { "product_id": "PROD-002", "name": "USB-C Hub", "stock_quantity": 45, "price": 49.99 }
    ],
    "order_totals": {
      "subtotal": 109.97,
      "tax": 9.35,
      "shipping": 0.00,
      "total": 119.32,
      "estimated_delivery": "2025-12-22"
    },
    "payment_result": {
      "transaction_id": "TXN-20251217-001",
      "authorization_code": "AUTH-789456",
      "status": "approved",
      "timestamp": "2025-12-17T10:30:00Z"
    },
    "confirmation_email": "Dear John Doe,\n\nThank you for your order! Your order has been confirmed...",
    "final_output": {
      "validation_result": {...},
      "inventory_check": [...],
      "order_totals": {...},
      "payment_result": {...},
      "confirmation_email": "..."
    },
    "execution_path": ["input", "validate_order", "validation_router", "check_inventory", "calculate_totals", "process_payment", "generate_confirmation", "aggregator"],
    "tokens_used": 2800,
    "cost": 0
  }
}
```

### Expected Output (Validation Error Path)

```json
{
  "status": "success",
  "final_state": {
    "validation_result": {
      "valid": false,
      "errors": ["Invalid customer ID format", "Shipping address incomplete"],
      "warnings": []
    },
    "final_output": {
      "validation_result": {
        "valid": false,
        "errors": ["Invalid customer ID format", "Shipping address incomplete"]
      }
    },
    "execution_path": ["input", "validate_order", "validation_router", "validation_error_handler"],
    "tokens_used": 250,
    "cost": 0
  }
}
```

### Edge Cases

| Scenario | Handling |
|----------|----------|
| Validation fails | Route to error handler, stop execution, return validation errors |
| Item out of stock | LLM simulates realistic stock levels in inventory check |
| Payment declined | LLM generates declined status with reason code |
| Empty user_input | Validation fails with "Order data is empty or missing" error |
| Missing required fields | Validation identifies specific missing fields |
| Invalid data types | Validation catches non-numeric quantities, malformed addresses |

---

## 6. Role-Based Dashboard: Subflow Pattern with User Routing

**Scenario**: Multi-role dashboard system that displays different content based on user role (User/Developer/HR).

**Use Cases**:
- Role-based access control (RBAC) systems
- Multi-tenant dashboards
- Personalized content delivery
- Employee portals with role-specific views

### Workflow Definition

```json
{
  "name": "Role-Based Dashboard",
  "description": "Routes users to role-specific dashboards with nested data fetching",
  "version": "1.0.0",
  "start_node": "input",
  
  "nodes": [
    {
      "id": "input",
      "type": "input",
      "metadata": {
        "description": "Receives user login credentials",
        "validation": {
          "required_fields": ["user_id", "role"]
        }
      }
    },
    {
      "id": "authenticate_user",
      "type": "llm",
      "metadata": {
        "source_id": "groq-llm",
        "prompt_template": "Authenticate and validate user login:\n\nUser ID: {user_id}\nRole: {role}\nTimestamp: {login_timestamp}\n\nValidate:\n1. User ID format is valid\n2. Role is one of: user, developer, hr\n3. Generate session token\n4. Return user profile data\n\nReturn JSON with:\n{\n  \"authenticated\": boolean,\n  \"user_id\": \"string\",\n  \"role\": \"string\",\n  \"session_token\": \"string\",\n  \"user_name\": \"string\",\n  \"department\": \"string\"\n}",
        "system_prompt": "You are an authentication system. Generate realistic user profiles and session tokens.",
        "temperature": 0.2,
        "max_tokens": 500,
        "output_key": "auth_result"
      }
    },
    {
      "id": "role_router",
      "type": "router",
      "metadata": {
        "strategy": "keyword",
        "routes": [
          {
            "intent": "user_dashboard",
            "keywords": ["user", "employee", "staff"]
          },
          {
            "intent": "developer_dashboard",
            "keywords": ["developer", "engineer", "dev"]
          },
          {
            "intent": "hr_dashboard",
            "keywords": ["hr", "human resources", "recruiter"]
          }
        ],
        "default_intent": "user_dashboard"
      }
    },
    {
      "id": "fetch_user_dashboard",
      "type": "llm",
      "metadata": {
        "source_id": "groq-llm",
        "prompt_template": "Generate user dashboard content for:\n\nUser: {user_name}\nRole: user\n\nInclude:\n1. Personal tasks (3-5 items with due dates)\n2. Recent notifications (company announcements, team updates)\n3. Time-off balance\n4. Upcoming events\n5. Quick actions (submit expense, request time-off)\n\nReturn structured JSON with realistic data.",
        "system_prompt": "You are a dashboard content generator. Create realistic, personalized content.",
        "temperature": 0.6,
        "max_tokens": 800,
        "output_key": "dashboard_content"
      }
    },
    {
      "id": "fetch_developer_dashboard",
      "type": "llm",
      "metadata": {
        "source_id": "groq-llm",
        "prompt_template": "Generate developer dashboard content for:\n\nDeveloper: {user_name}\nRole: developer\n\nInclude:\n1. Assigned tasks from current sprint (5-7 tasks with status, priority, story points)\n2. Code reviews pending (3-4 PRs to review)\n3. Build status (CI/CD pipeline status)\n4. Bug reports assigned (2-3 critical bugs)\n5. Sprint progress (burndown, velocity)\n6. Upcoming deadlines\n\nReturn structured JSON with realistic development data.",
        "system_prompt": "You are a developer dashboard generator. Create realistic sprint data, tasks, and metrics.",
        "temperature": 0.5,
        "max_tokens": 1000,
        "output_key": "dashboard_content"
      }
    },
    {
      "id": "fetch_hr_dashboard",
      "type": "llm",
      "metadata": {
        "source_id": "groq-llm",
        "prompt_template": "Generate HR dashboard content for:\n\nHR Manager: {user_name}\nRole: hr\n\nInclude:\n1. New job requirements (3-5 open positions with details)\n2. Candidate pipeline (screening, interview, offer stages)\n3. Onboarding tasks (new hires starting this week)\n4. Employee requests pending (time-off, transfers)\n5. Recruitment metrics (applications, conversion rates)\n6. Upcoming interviews schedule\n\nReturn structured JSON with realistic HR data.",
        "system_prompt": "You are an HR dashboard generator. Create realistic recruitment and employee management data.",
        "temperature": 0.5,
        "max_tokens": 1000,
        "output_key": "dashboard_content"
      }
    },
    {
      "id": "fetch_user_subflow",
      "type": "llm",
      "metadata": {
        "source_id": "groq-llm",
        "prompt_template": "Generate additional user profile information:\n\nUser: {user_name}\n\nInclude:\n1. Recent activity log (last 5 actions)\n2. Team members list\n3. Performance summary (current quarter)\n4. Learning paths assigned\n\nReturn structured JSON.",
        "system_prompt": "You are a user profile data generator.",
        "temperature": 0.4,
        "max_tokens": 600,
        "output_key": "subflow_data"
      }
    },
    {
      "id": "fetch_developer_subflow",
      "type": "llm",
      "metadata": {
        "source_id": "groq-llm",
        "prompt_template": "Generate additional developer metrics:\n\nDeveloper: {user_name}\n\nInclude:\n1. Code contribution stats (commits, lines of code, PRs merged)\n2. Technical debt items assigned\n3. Documentation tasks\n4. Team collaboration metrics\n5. Skill development recommendations\n\nReturn structured JSON.",
        "system_prompt": "You are a developer metrics generator.",
        "temperature": 0.4,
        "max_tokens": 700,
        "output_key": "subflow_data"
      }
    },
    {
      "id": "fetch_hr_subflow",
      "type": "llm",
      "metadata": {
        "source_id": "groq-llm",
        "prompt_template": "Generate additional HR analytics:\n\nHR Manager: {user_name}\n\nInclude:\n1. Hiring funnel analytics (conversion rates by stage)\n2. Employee satisfaction scores\n3. Retention metrics\n4. Diversity & inclusion stats\n5. Compensation benchmarks\n\nReturn structured JSON.",
        "system_prompt": "You are an HR analytics generator.",
        "temperature": 0.4,
        "max_tokens": 700,
        "output_key": "subflow_data"
      }
    },
    {
      "id": "merge_user_data",
      "type": "aggregator",
      "metadata": {
        "strategy": "merge",
        "source_keys": ["auth_result", "dashboard_content", "subflow_data"],
        "output_key": "final_output",
        "include_metadata": true
      }
    },
    {
      "id": "merge_developer_data",
      "type": "aggregator",
      "metadata": {
        "strategy": "merge",
        "source_keys": ["auth_result", "dashboard_content", "subflow_data"],
        "output_key": "final_output",
        "include_metadata": true
      }
    },
    {
      "id": "merge_hr_data",
      "type": "aggregator",
      "metadata": {
        "strategy": "merge",
        "source_keys": ["auth_result", "dashboard_content", "subflow_data"],
        "output_key": "final_output",
        "include_metadata": true
      }
    }
  ],
  
  "edges": [
    { "from": "input", "to": "authenticate_user" },
    { "from": "authenticate_user", "to": "role_router" },
    { 
      "from": "role_router", 
      "to": ["fetch_user_dashboard", "fetch_developer_dashboard", "fetch_hr_dashboard"],
      "condition": "intent"
    },
    { "from": "fetch_user_dashboard", "to": "fetch_user_subflow" },
    { "from": "fetch_developer_dashboard", "to": "fetch_developer_subflow" },
    { "from": "fetch_hr_dashboard", "to": "fetch_hr_subflow" },
    { "from": "fetch_user_subflow", "to": "merge_user_data" },
    { "from": "fetch_developer_subflow", "to": "merge_developer_data" },
    { "from": "fetch_hr_subflow", "to": "merge_hr_data" }
  ],
  
  "queues": [
    {
      "id": "queue_auth",
      "from": "input",
      "to": "authenticate_user",
      "bandwidth": {
        "max_requests_per_minute": 200,
        "max_tokens_per_minute": 100000
      }
    },
    {
      "id": "queue_dashboard",
      "from": "role_router",
      "to": "fetch_user_dashboard",
      "bandwidth": {
        "max_requests_per_minute": 150,
        "max_tokens_per_minute": 120000
      }
    }
  ],
  
  "sources": [
    {
      "id": "groq-llm",
      "kind": "llm",
      "config": {
        "provider": "groq",
        "model": "llama-3.3-70b-versatile",
        "api_key_env": "GROQ_API_KEY"
      }
    }
  ],
  
  "metadata": {
    "subflows": {
      "user_subflow": {
        "description": "Nested workflow for regular user data",
        "nodes": ["fetch_user_dashboard", "fetch_user_subflow", "merge_user_data"]
      },
      "developer_subflow": {
        "description": "Nested workflow for developer-specific data",
        "nodes": ["fetch_developer_dashboard", "fetch_developer_subflow", "merge_developer_data"]
      },
      "hr_subflow": {
        "description": "Nested workflow for HR-specific data",
        "nodes": ["fetch_hr_dashboard", "fetch_hr_subflow", "merge_hr_data"]
      }
    },
    "roles": {
      "user": "Regular employee with personal dashboard",
      "developer": "Software developer with sprint and code data",
      "hr": "HR manager with recruitment and employee data"
    }
  }
}
```

### Initial State Examples

**User Login:**
```json
{
  "user_id": "USR-001",
  "role": "user",
  "login_timestamp": "2025-12-17T09:00:00Z",
  "user_name": "John Smith"
}
```

**Developer Login:**
```json
{
  "user_id": "DEV-042",
  "role": "developer",
  "login_timestamp": "2025-12-17T09:30:00Z",
  "user_name": "Sarah Chen"
}
```

**HR Manager Login:**
```json
{
  "user_id": "HR-005",
  "role": "hr",
  "login_timestamp": "2025-12-17T08:45:00Z",
  "user_name": "Michael Rodriguez"
}
```

### Expected Output (Developer Example)

```json
{
  "status": "success",
  "final_state": {
    "auth_result": {
      "authenticated": true,
      "user_id": "DEV-042",
      "role": "developer",
      "session_token": "sess_a1b2c3d4e5f6",
      "user_name": "Sarah Chen",
      "department": "Engineering"
    },
    "dashboard_content": {
      "assigned_tasks": [
        {
          "id": "TASK-1234",
          "title": "Implement user authentication API",
          "status": "in_progress",
          "priority": "high",
          "story_points": 8,
          "due_date": "2025-12-20"
        },
        {
          "id": "TASK-1235",
          "title": "Fix payment gateway timeout issue",
          "status": "pending",
          "priority": "critical",
          "story_points": 5,
          "due_date": "2025-12-18"
        }
      ],
      "code_reviews": [
        {
          "pr_id": "PR-456",
          "title": "Add email validation",
          "author": "John Doe",
          "status": "needs_review"
        }
      ],
      "build_status": {
        "status": "passing",
        "last_build": "2025-12-17T08:30:00Z"
      },
      "sprint_progress": {
        "completed": 25,
        "in_progress": 40,
        "total": 100,
        "velocity": 32
      }
    },
    "subflow_data": {
      "code_contributions": {
        "commits_this_week": 18,
        "lines_added": 1240,
        "lines_removed": 450,
        "prs_merged": 4
      },
      "technical_debt": [
        {
          "id": "DEBT-789",
          "title": "Refactor legacy authentication module",
          "priority": "medium"
        }
      ],
      "skill_recommendations": [
        "Learn GraphQL",
        "Advanced Docker networking"
      ]
    },
    "final_output": {
      "user_info": {...},
      "dashboard": {...},
      "analytics": {...}
    },
    "execution_path": ["input", "authenticate_user", "role_router", "fetch_developer_dashboard", "fetch_developer_subflow", "merge_developer_data"],
    "tokens_used": 1850,
    "cost": 0
  }
}
```

### Expected Output (HR Manager Example)

```json
{
  "status": "success",
  "final_state": {
    "auth_result": {
      "authenticated": true,
      "user_id": "HR-005",
      "role": "hr",
      "session_token": "sess_x9y8z7w6v5u4",
      "user_name": "Michael Rodriguez",
      "department": "Human Resources"
    },
    "dashboard_content": {
      "open_positions": [
        {
          "id": "JOB-2024-123",
          "title": "Senior Full Stack Developer",
          "department": "Engineering",
          "status": "active",
          "posted_date": "2025-12-10",
          "applications": 45
        },
        {
          "id": "JOB-2024-124",
          "title": "Product Manager",
          "department": "Product",
          "status": "active",
          "posted_date": "2025-12-12",
          "applications": 28
        }
      ],
      "candidate_pipeline": {
        "screening": 32,
        "phone_interview": 12,
        "technical_interview": 8,
        "final_interview": 4,
        "offer_stage": 2
      },
      "onboarding_tasks": [
        {
          "new_hire": "Alice Johnson",
          "start_date": "2025-12-18",
          "tasks_completed": 8,
          "tasks_pending": 3
        }
      ],
      "employee_requests": [
        {
          "type": "time_off",
          "employee": "Tom Wilson",
          "dates": "2025-12-25 to 2025-12-29",
          "status": "pending_approval"
        }
      ],
      "upcoming_interviews": [
        {
          "candidate": "James Lee",
          "position": "Senior Full Stack Developer",
          "time": "2025-12-17T14:00:00Z",
          "interviewer": "Sarah Chen"
        }
      ]
    },
    "subflow_data": {
      "hiring_funnel": {
        "application_to_screening": 0.71,
        "screening_to_interview": 0.38,
        "interview_to_offer": 0.25,
        "offer_acceptance_rate": 0.85
      },
      "employee_satisfaction": {
        "overall_score": 4.2,
        "response_rate": 0.87,
        "eNPS": 42
      },
      "retention_metrics": {
        "turnover_rate": 0.12,
        "avg_tenure_years": 3.5
      },
      "diversity_stats": {
        "gender_ratio": {"male": 0.58, "female": 0.42},
        "diversity_hires_percentage": 0.35
      }
    },
    "final_output": {
      "user_info": {...},
      "dashboard": {...},
      "analytics": {...}
    },
    "execution_path": ["input", "authenticate_user", "role_router", "fetch_hr_dashboard", "fetch_hr_subflow", "merge_hr_data"],
    "tokens_used": 1920,
    "cost": 0
  }
}
```

### Edge Cases

| Scenario | Handling |
|----------|----------|
| Invalid role | Default to "user" dashboard with basic access |
| Authentication fails | Return error, don't fetch dashboard data |
| Multiple roles | Prioritize highest privilege role |
| Missing user_name | Generate generic name from user_id |
| Subflow data unavailable | Return main dashboard, skip supplementary data |
| Session token generation fails | Generate fallback token, log warning |

### Subflow Architecture

**User Subflow:**
```
authenticate → role_router → fetch_user_dashboard → fetch_user_subflow → merge_user_data
```

**Developer Subflow:**
```
authenticate → role_router → fetch_developer_dashboard → fetch_developer_subflow → merge_developer_data
```

**HR Subflow:**
```
authenticate → role_router → fetch_hr_dashboard → fetch_hr_subflow → merge_hr_data
```

Each subflow is **isolated and parallel** - only ONE executes based on user role.

---

## 7. Human-Interaction Pattern: Approval Workflow

**Scenario**: Content moderation system requiring human approval for sensitive content.

**Use Cases**:
- Content moderation
- Approval workflows
- Quality assurance processes

### Workflow Definition

```json
{
  "name": "Content Moderation with Human Approval",
  "description": "AI-assisted content moderation with human-in-the-loop approval (Groq version)",
  "version": "1.0.0",
  "start_node": "input",
  
  "nodes": [
    {
      "id": "input",
      "type": "input",
      "metadata": {
        "description": "Receives content for moderation review"
      }
    },
    {
      "id": "ai_review",
      "type": "llm",
      "metadata": {
        "source_id": "groq-llm",
        "prompt_template": "You are a content moderation AI. Your task is to analyze the content provided below for policy violations.\n\nCONTENT TO MODERATE:\n{user_input}\n\nREQUIRED: Analyze this specific content above for:\n1. Hate speech or discrimination\n2. Violence or threats\n3. Adult/explicit content\n4. Spam or misleading information\n5. Copyright violations\n6. Personal information exposure\n\nMANDATORY: Respond with ONLY valid JSON. No explanations, no extra text:\n{\n  \"content_safe\": true,\n  \"confidence_score\": 65,\n  \"flags\": [\"political_content\"],\n  \"category\": \"review_needed\",\n  \"reasoning\": \"Political discussion requires human judgment\",\n  \"intent\": \"human_review\"\n}\n\nScoring: >90 = auto_approve, 50-90 = human_review, <50 = auto_reject",
        "system_prompt": "You are a content moderation AI. Be thorough but fair. When uncertain, recommend human review.",
        "temperature": 0.1,
        "max_tokens": 800,
        "output_key": "ai_review_result"
      }
    },
    {
      "id": "classify_risk",
      "type": "router",
      "metadata": {
        "strategy": "keyword",
        "routes": [
          {
            "intent": "auto_approve",
            "keywords": ["\"intent\": \"auto_approve\""]
          },
          {
            "intent": "auto_reject",
            "keywords": ["\"intent\": \"auto_reject\""]
          },
          {
            "intent": "human_review",
            "keywords": ["\"intent\": \"human_review\""]
          }
        ],
        "default_intent": "human_review",
        "input_key": "ai_review_result"
      }
    },
    {
      "id": "auto_approve_handler",
      "type": "llm",
      "metadata": {
        "source_id": "groq-llm",
        "prompt_template": "Content has been automatically approved.\n\nContent: {user_input}\nAI Review: {ai_review_result}\n\nGenerate approval confirmation with:\n1. Approval ID\n2. Timestamp\n3. Summary of checks passed\n4. Content category",
        "temperature": 0.2,
        "max_tokens": 500,
        "output_key": "moderation_decision"
      }
    },
    {
      "id": "human_review_handler",
      "type": "aggregator",
      "metadata": {
        "strategy": "template",
        "template": "## Human Review Required\n\n**Status**: PENDING_REVIEW\n**Queue Position**: {{queue_position}}\n**Priority**: {{priority_level}}\n\n### Content\n{user_input}\n\n### AI Analysis\n{ai_review_result}\n\n### Reviewer Actions\n- [ ] Approve\n- [ ] Reject\n- [ ] Request Changes\n- [ ] Escalate\n\n### Notes\n_Reviewer comments will appear here_",
        "output_key": "moderation_decision",
        "include_metadata": true,
        "custom_fields": {
          "status": "pending_human_review",
          "requires_action": true,
          "escalation_available": true,
          "sla_hours": 24
        }
      }
    },
    {
      "id": "auto_reject_handler",
      "type": "llm",
      "metadata": {
        "source_id": "groq-llm",
        "prompt_template": "Content has been automatically rejected.\n\nContent: {user_input}\nAI Review: {ai_review_result}\n\nGenerate rejection notice with:\n1. Rejection ID\n2. Violated policies\n3. Appeal process\n4. Recommendations for resubmission",
        "temperature": 0.2,
        "max_tokens": 500,
        "output_key": "moderation_decision"
      }
    },
    {
      "id": "notify_user",
      "type": "llm",
      "metadata": {
        "source_id": "groq-llm",
        "prompt_template": "Generate a user notification email based on the moderation decision:\n\nDecision: {moderation_decision}\nOriginal Content: {user_input}\n\nCreate a professional, clear notification that:\n1. Explains the decision\n2. Provides next steps\n3. Offers support resources\n4. Maintains a respectful tone",
        "temperature": 0.5,
        "max_tokens": 800,
        "output_key": "user_notification"
      }
    },
    {
      "id": "log_audit",
      "type": "aggregator",
      "metadata": {
        "strategy": "merge",
        "source_keys": ["user_input", "ai_review_result", "moderation_decision", "user_notification"],
        "output_key": "audit_log",
        "include_metadata": true,
        "custom_fields": {
          "audit_id": "{{generate_uuid}}",
          "timestamp": "{{current_timestamp}}",
          "retention_days": 90
        }
      }
    },
    {
      "id": "final_output",
      "type": "aggregator",
      "metadata": {
        "strategy": "merge",
        "source_keys": ["moderation_decision", "user_notification", "audit_log"],
        "output_key": "final_output",
        "include_metadata": true
      }
    }
  ],
  
  "edges": [
    { "from": "input", "to": "ai_review" },
    { "from": "ai_review", "to": "classify_risk" },
    { 
      "from": "classify_risk", 
      "to": ["auto_approve_handler", "human_review_handler", "auto_reject_handler"],
      "condition": "intent"
    },
    { "from": "auto_approve_handler", "to": "notify_user" },
    { "from": "human_review_handler", "to": "notify_user" },
    { "from": "auto_reject_handler", "to": "notify_user" },
    { "from": "notify_user", "to": "log_audit" },
    { "from": "log_audit", "to": "final_output" }
  ],
  
  "queues": [
    {
      "id": "queue_ai_review",
      "from": "input",
      "to": "ai_review",
      "bandwidth": {
        "max_requests_per_minute": 100,
        "max_tokens_per_minute": 80000
      }
    },
    {
      "id": "queue_human_review",
      "from": "classify_risk",
      "to": "human_review_handler",
      "bandwidth": {
        "max_messages_per_second": 10
      }
    }
  ],
  
  "sources": [
    {
      "id": "groq-llm",
      "kind": "llm",
      "config": {
        "provider": "groq",
        "model": "llama-3.3-70b-versatile",
        "api_key_env": "GROQ_API_KEY"
      }
    }
  ],
  
  "metadata": {
    "human_interaction": {
      "review_queue": "content_moderation",
      "notification_channels": ["email", "slack", "dashboard"],
      "escalation_path": ["moderator", "senior_moderator", "legal_team"],
      "sla_config": {
        "initial_review": "4 hours",
        "escalation": "1 hour",
        "resolution": "24 hours"
      },
      "reviewer_assignment": {
        "strategy": "round_robin",
        "fallback": "least_loaded"
      }
    },
    "webhooks": {
      "on_pending_review": "https://api.example.com/webhooks/moderation/pending",
      "on_decision": "https://api.example.com/webhooks/moderation/decision",
      "on_escalation": "https://api.example.com/webhooks/moderation/escalate"
    }
  }
}
```

### Initial State Examples

**Safe Content:**
```json
{
  "user_input": "I just made the most amazing chocolate cake! Here's my recipe: Mix 2 cups flour, 1 cup sugar, 1/2 cup cocoa powder..."
}
```

**Needs Review:**
```json
{
  "user_input": "This political commentary discusses the controversial policies of [politician name] and their potential impact on civil liberties..."
}
```

**Clear Violation:**
```json
{
  "user_input": "[Content containing clear policy violations would be here]"
}
```

### Expected Output (Human Review Case)

```json
{
  "status": "success",
  "final_state": {
    "user_input": "This political commentary discusses...",
    "ai_review_result": {
      "content_safe": true,
      "confidence_score": 72,
      "flags": ["political_content", "named_individuals"],
      "category": "review_needed",
      "reasoning": "Content discusses political figures, may require human judgment for context"
    },
    "intent": "human_review",
    "moderation_decision": {
      "status": "pending_human_review",
      "requires_action": true,
      "queue_position": 5,
      "priority_level": "normal",
      "sla_hours": 24
    },
    "user_notification": "Your content has been submitted and is currently under review...",
    "audit_log": {
      "audit_id": "AUD-123456",
      "timestamp": "2025-12-11T10:30:00Z",
      "ai_review_result": {...},
      "moderation_decision": {...}
    },
    "final_output": {
      "result": {...},
      "execution_path": ["input", "ai_review", "classify_risk", "human_review_handler", "notify_user", "log_audit", "final_output"],
      "tokens_used": 1200,
      "cost": 0.0014
    }
  }
}
```

### Edge Cases

| Scenario | Handling |
|----------|----------|
| AI uncertainty | Always route to human review |
| Human reviewer unavailable | Queue with escalation timer |
| Conflicting reviewer decisions | Escalate to senior moderator |
| Appeal submitted | Create new review with escalated priority |
| SLA breach imminent | Auto-escalate, notify supervisors |
| Bulk content from same user | Batch review, apply pattern detection |

---

## Workflow Generation Template

Use this template when creating custom workflows:

```
You are a workflow generator. Create a JSON workflow definition for the AgentFlow engine.

Follow these rules strictly:
- Include nodes, edges, sources, start_node, metadata, and initial_state
- Edge cases must be included
- Support the following patterns as needed:
  * Simple (input → LLM)
  * Sequential (A → B → C)
  * Parallel (A → [B, C, D] → E)
  * Conditional (router with intent-based routing)
  * Subflow (nested workflow components)
  * Human-interaction (approval queues, notifications)
- Add realistic prompt templates with {placeholders}
- Include proper bandwidth/rate limiting in queues
- Ensure all node IDs are unique and meaningful
- Reference sources correctly in nodes

Now create a workflow for:
<<< INSERT YOUR SCENARIO HERE >>>
```

---

## Quick Reference

### Node Types

| Type | Purpose | Key Metadata Fields |
|------|---------|---------------------|
| `input` | Entry point | `validation`, `description` |
| `llm` | Text generation | `source_id`, `prompt_template`, `temperature`, `max_tokens` |
| `image` | Image generation | `source_id`, `prompt_template`, `size`, `quality` |
| `db` | Database queries | `source_id`, `query_template`, `limit` |
| `router` | Conditional routing | `strategy`, `routes`, `default_intent` |
| `aggregator` | Combine results | `strategy`, `source_keys`, `output_key` |

### Source Kinds

| Kind | Purpose | Key Config Fields |
|------|---------|-------------------|
| `llm` | LLM API | `provider`, `model`, `api_key_env` |
| `image` | Image API | `provider`, `model`, `api_key_env` |
| `db` | Database | `provider`, `connection_string_env` |
| `api` | HTTP API | `base_url`, `auth_type`, `headers` |

### Routing Strategies

| Strategy | Description | Route Definition |
|----------|-------------|------------------|
| `keyword` | Match keywords | `{"intent": "x", "keywords": [...]}` |
| `pattern` | Regex match | `{"intent": "x", "pattern": "regex"}` |
| `rules` | Condition eval | `{"intent": "x", "condition": "fn()"}` |
| `llm` | AI classification | Uses LLM source |

---

**Last Updated**: December 11, 2025
**Version**: 1.0.0
