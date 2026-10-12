# Flight Booking: Prompting Approach Analysis

## 3.1 Three approaches

**Direct prompting.** The user asks a question and the model immediately answers from its knowledge and the prompt. It has no visible reasoning and no tool access. It handles simple explanations or arithmetic when facts are supplied, but cannot reliably answer current flight prices, schedules, or baggage. In this scenario it may invent a flight or price.

**Chain-of-Thought (CoT).** The user asks the model to reason step by step before answering. Calculating the booking fee and instalments in stages helps with arithmetic and comparisons. It has no tool access, so reasoning cannot create missing facts. It can solve “What is 10% of Rs. 7,200?” but cannot discover an available BLR-DEL flight.

**ReAct.** The model cycles through **Thought, Action, and Observation**. It decides what is missing, calls `search_flights`, observes the results, calls `calculator` when needed, and repeats until it can answer. It combines external facts with reasoning, but depends on accurate tools and arguments. A failed service or step limit can still cause failure.

## 3.2 Comparison table

| Approach | Tools | Result | Speed/reliability/transparency |
|---|---|---|---|
| Direct | None | Immediate answer; may guess facts | Fast, cheap, least reliable for current data, no visible reasoning |
| CoT | None | Step-by-step calculation; cannot fetch flights | Slower, better arithmetic, visible steps, fact-limited |
| ReAct | Search/calculator when needed | Uses observations, then answers with a matching flight | Slowest and costliest, reliable with accurate tools, traceable |

## 3.3 Self-consistency observation

For the CoT question “A flight costs Rs. 7,200. Add a 10% booking fee and divide the total into 3 equal payments,” five runs at temperature 0.8 all answered **Rs. 2,640**. The 5/5 majority was correct: `(7,200 x 1.10) / 3 = 2,640`. At temperature 0, sampling is deterministic, so repeated runs normally match and self-consistency adds little value.

## 3.4 Suitability analysis

ReAct is most suitable because flight availability, price, and baggage require external lookup. CoT helps after facts are supplied, such as when calculating fees. Direct prompting suits simple questions whose facts are provided. The 5/5 CoT result shows reliable arithmetic, but not access to missing data.

## 3.5 Conclusion

Use direct prompting for fast writing or known facts. Use CoT-style prompting for multi-step logic and calculations with supplied information. Use ReAct for tasks needing live data, tools, databases, or several dependent steps, such as flight booking.
