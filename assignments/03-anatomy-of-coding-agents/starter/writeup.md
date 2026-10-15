# Prompting Techniques Writeup

## 1. K-Shot Prompting
**Final Prompt:**
```text
Classify the customer message into one of these categories: billing, shipping, returns, technical, other.
Output ONLY the exact category name in lowercase. Do not add any other words.

Examples:
Message: "My screen is broken."
technical

Message: "Can I get a different size?"
returns

Sample Input/Output:

Input: "My card was charged twice for order 4412."

Output: billing
What I learned: Providing concrete examples directly inside the prompt forces the model to strictly mimic the exact output format rather than generating a conversational response.


## 2. chain_of_thought
You are a refund evaluator. 
First, explain your reasoning step by step by checking the customer's order against the policy rules (days since purchase, item condition, and final-sale status). 
Then, on the very last line of your response, output your final decision exactly like this:
DECISION: YES
or
DECISION: NO

Sample Input/Output:

Input: "Bought 10 days ago, unused, not final sale."

Output: YES
What I learned: Forcing the model to "think aloud" and explain its step-by-step logic before giving a final answer significantly improves its ability to correctly apply complex rules.

## 3. tool_calling
You are a helpful customer support agent. 
If a customer asks about the status of their order, you must ALWAYS call the get_order_status tool to look up the status using their order ID.

Sample Input/Output:

Input: "Hi, can you check on order 4412 for me?"

Output: Tool called with order_id='4412' -> Result: shipped, arriving Friday
What I learned: Giving the model a structured schema allows it to extract specific variables from natural language (like an order ID) and reliably trigger external functions to get real-time data.

## 4. rag
You are a support assistant. Answer the user's question using ONLY the facts provided in the Context.
If the Context does not contain the answer, you must reply exactly with: "I don't know."
Do not guess or include outside information.

Sample Input/Output:

Input: "How long do I have to return an item?"

Output: you may return most items within 30 days of delivery for a full refund.
What I learned: Feeding a model specific document excerpts alongside a strict "no hallucination" rule forces it to ground its answers strictly in provided facts rather than relying on its general training data.


Conclusion
Across all four techniques, I learned that LLMs are incredibly capable of handling structured tasks, but they default to being overly conversational and sometimes inaccurate without strict boundaries. They require specific scaffolding like explicit formatting rules, in-context examples, forced reasoning steps, or external data grounding to transform them from open ended chat bots into reliable, predictable agents that can execute business logic.
