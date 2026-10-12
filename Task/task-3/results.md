# Results: Plain LLM vs. One Tool

Scenario: private Greenfield College course fees, stored in `course_fees.json`.

Provider/model: Groq / `qwen/qwen3.8-27b`

## Plain LLM run

Command: `python plain_llm.py`

1. AI202 private fee: “I do not have access to any private Greenfield course fee tables or internal documents. Therefore, I cannot provide the specific fee for course AI202.” The model refused instead of guessing.
2. Course fee vs. fine: explained that a course fee pays for education/services while a fine is a penalty for breaking a rule. Correct general distinction; some examples were not verified against Greenfield policy.
3. Welcome message: “Welcome to the exciting world of artificial intelligence! We’re thrilled to have you join us on this journey of discovery and innovation.” Friendly and relevant, but returned on one line rather than the requested two.

## Tool-enabled run

Command: `python tool_llm.py`

1. AI202 private fee: called `lookup_course_fee({"course_code": "AI202"})`; the tool returned `AI202 fee is Rs. 18000.` The final answer stated Rs. 18,000, matching the lookup.
2. Course fee vs. fine: no tool call. The model gave the general distinction and examples. The basic explanation was reasonable, though institution-specific examples were not checked.
3. Welcome message: no tool call. Returned: “Welcome to Greenfield College, and congratulations on starting your AI journey! We're excited to have you here and can't wait to see the amazing things you'll create.” Friendly and relevant, but one line rather than two.

## Observation (3.4)

| Question | Plain LLM observation | Tool call and result | Tool-enabled final answer | Assessment |
|---|---|---|---|---|
| According to our private Greenfield course fee table, what is the fee for AI202? | Refused: said it had no access to the private table and could not provide the fee. | `lookup_course_fee({"course_code": "AI202"})` -> `AI202 fee is Rs. 18000.` | Said the fee is Rs. 18,000. | Tool called correctly and final answer used its result. Plain LLM did not guess. |
| What is the difference between a course fee and a fine? | Explained the general distinction; answer was reasonable. | No tool call. | Explained course fee as payment for a course and fine as a penalty. | Both answered a question reasonably handled from general knowledge; the tool-enabled run avoided unnecessary lookup. |
| Write a friendly two-line welcome message for new AI students. | Friendly welcome, but output was one line rather than two. | No tool call. | Friendly welcome, but output was one line rather than two. | Tool correctly not used; both missed the requested two-line format. |

## Conclusion

In this run, the plain model appropriately refused to invent a private course fee, while the tool-enabled model retrieved the fee and returned the exact table value. It also used no tool for either general/creative question, as intended. Tool access therefore improved the answerability and verifiability of the private-data question without being necessary for the other two. Both runs did miss the explicit two-line formatting request, showing that tool access does not guarantee instruction-following on unrelated output constraints.
