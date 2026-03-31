# letagentpay

Python SDK for [LetAgentPay](https://letagentpay.com) — AI agent spending policy middleware. Set budgets, define spending policies, and control AI agent purchases.

## Installation

```bash
pip install letagentpay
```

## Quick Start

```python
from letagentpay import LetAgentPay

client = LetAgentPay(token="agt_xxx")

# Create a purchase request
result = client.request_purchase(
    amount=15.0,
    category="api_calls",
    description="OpenAI GPT-4 call",
)
print(result.status)  # "auto_approved" / "pending" / "rejected"

# Check budget
budget = client.check_budget()
print(f"Remaining: ${budget.remaining}")
```

## @guard Decorator

Automatically check the spending policy before executing a function:

```python
from letagentpay import guard

@guard(token="agt_xxx", category="api_calls", amount=0.03)
def call_openai(prompt: str) -> str:
    return openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content

# Runs only if the policy allows it
result = call_openai("Analyze this document")
```

## Environment Variables

```bash
export LETAGENTPAY_TOKEN=agt_xxx
export LETAGENTPAY_BASE_URL=https://api.letagentpay.com/api/v1/agent-api  # optional
```

```python
# Token is taken from LETAGENTPAY_TOKEN
client = LetAgentPay()
```

## Documentation

- [Python SDK docs](https://letagentpay.com/developers)
- [Agent API Reference](https://letagentpay.com/developers)
- [GitHub](https://github.com/letagentpay/letagentpay-python)

## License

MIT
