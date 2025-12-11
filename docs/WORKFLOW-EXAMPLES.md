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

**Scenario**: E-commerce order processing with nested validation, inventory check, and payment workflows.

**Use Cases**:
- Order processing pipelines
- Multi-stage approvals
- Complex business workflows

### Workflow Definition

```json
{
  "name": "Order Processing Pipeline",
  "description": "E-commerce order processing with nested subflows",
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
        "source_id": "gemini-llm",
        "prompt_template": "Validate the following order data:\n\nOrder: {user_input}\n\nCheck for:\n1. Valid customer ID format\n2. Item quantities are positive integers\n3. Shipping address is complete\n4. Payment method is valid\n\nReturn JSON with:\n{\n  \"valid\": boolean,\n  \"errors\": [],\n  \"warnings\": [],\n  \"processed_order\": {...}\n}",
        "system_prompt": "You are an order validation system. Return structured JSON responses only.",
        "temperature": 0.1,
        "max_tokens": 1024,
        "output_key": "validation_result"
      }
    },
    {
      "id": "check_inventory",
      "type": "db",
      "metadata": {
        "source_id": "postgres-main",
        "query_template": "SELECT product_id, name, stock_quantity, price FROM products WHERE product_id IN ({product_ids}) AND stock_quantity > 0",
        "output_key": "inventory_check",
        "limit": 100
      }
    },
    {
      "id": "calculate_totals",
      "type": "llm",
      "metadata": {
        "source_id": "gemini-llm",
        "prompt_template": "Calculate order totals:\n\nOrder Items: {validation_result}\nInventory Data: {inventory_check}\n\nCalculate:\n1. Subtotal (item prices × quantities)\n2. Tax (8.5%)\n3. Shipping (free over $50, otherwise $5.99)\n4. Total\n5. Estimated delivery date (3-5 business days)\n\nReturn structured JSON.",
        "system_prompt": "You are a pricing calculator. Be precise with calculations.",
        "temperature": 0.1,
        "max_tokens": 512,
        "output_key": "order_totals"
      }
    },
    {
      "id": "process_payment",
      "type": "llm",
      "metadata": {
        "source_id": "gemini-llm",
        "prompt_template": "Simulate payment processing for:\n\nOrder Total: {order_totals}\nPayment Method: {payment_method}\n\nGenerate:\n1. Transaction ID\n2. Authorization code\n3. Payment status (approved/declined)\n4. Timestamp\n\nReturn structured JSON payment receipt.",
        "system_prompt": "You are a payment processor. Generate realistic transaction data.",
        "temperature": 0.2,
        "max_tokens": 512,
        "output_key": "payment_result"
      }
    },
    {
      "id": "generate_confirmation",
      "type": "llm",
      "metadata": {
        "source_id": "gemini-llm",
        "prompt_template": "Generate order confirmation email content:\n\nOrder Details: {validation_result}\nTotals: {order_totals}\nPayment: {payment_result}\n\nCreate a professional, friendly confirmation email with:\n1. Order summary\n2. Itemized list\n3. Shipping information\n4. Tracking info placeholder\n5. Customer service contact",
        "system_prompt": "You are an email template generator. Create professional, well-formatted content.",
        "temperature": 0.5,
        "max_tokens": 1500,
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
    { "from": "validate_order", "to": "check_inventory" },
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
      "id": "gemini-llm",
      "kind": "llm",
      "config": {
        "provider": "gemini",
        "model": "gemini-2.5-flash",
        "api_key_env": "GEMINI_API_KEY"
      }
    },
    {
      "id": "postgres-main",
      "kind": "db",
      "config": {
        "provider": "postgresql",
        "connection_string_env": "DATABASE_URL"
      }
    }
  ],
  
  "metadata": {
    "subflows": {
      "inventory_subflow": {
        "description": "Nested workflow for inventory management",
        "trigger": "low_stock_detected",
        "nodes": ["check_inventory", "notify_warehouse"]
      },
      "payment_subflow": {
        "description": "Nested workflow for payment retry",
        "trigger": "payment_declined",
        "max_retries": 3
      }
    }
  }
}
```

### Initial State

```json
{
  "user_input": {
    "customer_id": "CUST-12345",
    "items": [
      { "product_id": "PROD-001", "name": "Wireless Mouse", "quantity": 2 },
      { "product_id": "PROD-002", "name": "USB-C Hub", "quantity": 1 }
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
  "product_ids": "'PROD-001', 'PROD-002'",
  "payment_method": "credit_card"
}
```

### Expected Output

```json
{
  "status": "success",
  "final_state": {
    "validation_result": {
      "valid": true,
      "errors": [],
      "processed_order": {...}
    },
    "inventory_check": [
      { "product_id": "PROD-001", "stock_quantity": 150, "price": 29.99 },
      { "product_id": "PROD-002", "stock_quantity": 45, "price": 49.99 }
    ],
    "order_totals": {
      "subtotal": 109.97,
      "tax": 9.35,
      "shipping": 0,
      "total": 119.32,
      "estimated_delivery": "2025-12-18"
    },
    "payment_result": {
      "transaction_id": "TXN-ABC123",
      "status": "approved",
      "authorization_code": "AUTH-789"
    },
    "confirmation_email": "Dear John, Thank you for your order...",
    "final_output": {...}
  }
}
```

### Edge Cases

| Scenario | Handling |
|----------|----------|
| Validation fails | Return errors, don't process further |
| Item out of stock | Suggest alternatives, allow partial order |
| Payment declined | Retry with backoff, notify customer |
| Database unavailable | Queue order for later processing |
| Partial inventory | Process available items, backorder rest |

---

## 6. Human-Interaction Pattern: Approval Workflow

**Scenario**: Content moderation system requiring human approval for sensitive content.

**Use Cases**:
- Content moderation
- Approval workflows
- Quality assurance processes

### Workflow Definition

```json
{
  "name": "Content Moderation with Human Approval",
  "description": "AI-assisted content moderation with human-in-the-loop approval",
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
        "source_id": "gemini-llm",
        "prompt_template": "Review the following content for policy violations:\n\n{user_input}\n\nCheck for:\n1. Hate speech or discrimination\n2. Violence or threats\n3. Adult/explicit content\n4. Spam or misleading information\n5. Copyright violations\n6. Personal information exposure\n\nReturn JSON:\n{\n  \"content_safe\": boolean,\n  \"confidence_score\": 0-100,\n  \"flags\": [],\n  \"category\": \"safe|review_needed|blocked\",\n  \"reasoning\": \"string\"\n}",
        "system_prompt": "You are a content moderation AI. Be thorough but fair. When uncertain, recommend human review.",
        "temperature": 0.1,
        "max_tokens": 1024,
        "output_key": "ai_review_result"
      }
    },
    {
      "id": "classify_risk",
      "type": "router",
      "metadata": {
        "strategy": "rules",
        "routes": [
          {
            "intent": "auto_approve",
            "condition": "confidence_score_gt(90)"
          },
          {
            "intent": "human_review",
            "condition": "confidence_score_between(50,90)"
          },
          {
            "intent": "auto_reject",
            "condition": "confidence_score_lt(50)"
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
        "source_id": "gemini-llm",
        "prompt_template": "Content has been automatically approved.\n\nContent: {user_input}\nAI Review: {ai_review_result}\n\nGenerate approval confirmation with:\n1. Approval ID\n2. Timestamp\n3. Summary of checks passed\n4. Content category",
        "temperature": 0.2,
        "max_tokens": 512,
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
        "source_id": "gemini-llm",
        "prompt_template": "Content has been automatically rejected.\n\nContent: {user_input}\nAI Review: {ai_review_result}\n\nGenerate rejection notice with:\n1. Rejection ID\n2. Violated policies\n3. Appeal process\n4. Recommendations for resubmission",
        "temperature": 0.2,
        "max_tokens": 512,
        "output_key": "moderation_decision"
      }
    },
    {
      "id": "notify_user",
      "type": "llm",
      "metadata": {
        "source_id": "gemini-llm",
        "prompt_template": "Generate a user notification email based on the moderation decision:\n\nDecision: {moderation_decision}\nOriginal Content: {user_input}\n\nCreate a professional, clear notification that:\n1. Explains the decision\n2. Provides next steps\n3. Offers support resources\n4. Maintains a respectful tone",
        "temperature": 0.5,
        "max_tokens": 1024,
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
        "max_tokens_per_minute": 100000
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
