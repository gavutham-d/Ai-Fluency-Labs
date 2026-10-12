# Analysis: Reliable Gardening Tool Use

## Scenario and key ideas

This demonstration uses a home-gardening assistant. Its local reference data contains simple seasonal guidance for basil, tomato, and mint. It can look up care advice for a plant and season, or estimate water volume for a plant in a pot of a stated size. For the estimate, the example uses 75 mL per liter of pot capacity and explicitly tells the user to check soil moisture first. This is illustrative guidance, not horticultural authority. A general question such as why plants need sunlight can be answered without a tool, while the local care lookup or a requested numeric estimate should use the supplied functions.

A tool call is not executable code arriving from the model. Through the OpenAI-compatible API, the model returns a structured message containing a function name and arguments represented as JSON text. Those values are generated output and may be malformed, refer to an unknown function, omit required inputs, add invented fields, have the wrong type, or request values outside the allowed domain. The application therefore owns the decision to parse and validate the request before doing anything. In `robust_agent.py`, each call passes through four gates: parse its JSON, look up the function, validate against its schema, and only then execute it.

The single `SCHEMAS` dictionary in `tools.py` is used both to build the function declarations sent to the model and by `validate.py` before function execution. Each schema declares required inputs and `additionalProperties: false`; plant and season fields use enums. That alignment reduces drift between what the model is told it can send and what the program accepts. The validator returns a readable error describing the expected fields, types, ranges, or enum values. The agent appends every tool result or error as a tool message with the matching `tool_call_id`, allowing the model to correct its request instead of crashing the process. It handles every call in a response, raises `max_tokens` and retries when the provider reports truncation, detects repeated identical calls, and limits total steps.

A stricter schema prevents structural errors such as missing required fields, extra arguments, wrong JSON types, invalid enum values, and out-of-range pot sizes when those constraints are checked by the application. A schema cannot prove that a request is sensible, that the chosen plant or season is factually correct, that a deterministic formula is scientifically suitable for every plant, or that the model will use a valid tool result correctly in its final prose. Semantic checks, sensible domain limits, trustworthy underlying data, and clear tool-result handling remain application responsibilities.

## Tool-call comparison

The agent was run with the configured Groq-compatible endpoint and model. These prompts exercised both tools and a direct-answer case.

| User question | Tool behavior observed | Assessment |
|---|---|---|
| What care does basil need in summer? | Called `lookup_plant_care` with `plant=basil`, `season=summer`; returned advice to check soil daily, water when the top 2 cm feels dry, and give bright light. | Correct tool and arguments; final answer accurately summarized the returned lookup and added a reasonable soil-moisture caveat. |
| I have a 2-liter tomato pot. How much water should I use per watering? | Called `calculate_watering_volume` with `plant=tomato`, `pot_size_liters=2`; returned about 150 mL and said to check soil moisture. | Correct tool and arguments; final answer used the returned estimate and retained the caution. |
| Why do plants need sunlight? | No tool call. | The model answered directly with a photosynthesis explanation, as this general question did not need local data or a calculation. |

## Fault injection observations

`inject_faults.py` constructs ten tool-call-like objects by hand and sends them directly to the production handler, without a model request. The cases cover malformed JSON, unknown function, missing required input, an invented property, wrong type, enum violation, zero and excessive pot sizes, a boolean supplied as a number, and a non-object JSON root. These cases deliberately test failures instead of waiting for a model to happen to emit them. Each handler result is asserted to be a string; the expected behavior is an explanatory error result, with no exception escaping and no tool execution on invalid inputs.

This demonstrates that schema validation catches malformed shape and basic domain-boundary errors independently of model behavior. A live model run may happen to produce only valid calls; that would not show whether the guards work. Fault injection gives reproducible evidence of the handler's behavior for each failure class and protects against regressions in the boundary code.

The injected run produced these outcomes:

| Injected call | Handler outcome |
|---|---|
| Malformed JSON | Returned an invalid-JSON argument error. |
| Unknown function `send_message` | Returned the available tool names. |
| Missing `season` | Returned the missing required argument and expected fields. |
| Invented `zone` property | Returned the unexpected property and allowed fields. |
| Integer supplied for string `plant` | Returned a wrong-type error. |
| Unsupported plant `orchid` | Returned the allowed enum values. |
| Zero-liter pot | Rejected because the minimum is 0.1 L. |
| 250-liter pot | Rejected because the maximum is 100 L. |
| Boolean supplied as numeric pot size | Rejected as the wrong type (`bool`). |
| JSON array instead of object | Returned an object-shape error. |

All ten returned strings and the script's assertions passed. These failures were not observed in the real model's three agent questions: it chose valid tools and arguments for the first two and correctly skipped tools for the third. Thus malformed JSON, unknown tools, and schema violations were demonstrated by injection only, not by claiming the model produced them.

## Structured-output comparison

`structured_demo.py` asked the same extraction question in three modes. In unconstrained mode, the model returned the correct fields in a fenced JSON code block; direct JSON parsing failed because of the Markdown fences. JSON mode returned an unfenced JSON object with basil, summer, and 5 liters, which parsed successfully. Strict JSON Schema mode returned the same values in a compact object, also parsed successfully. On the first JSON-mode attempt, Groq returned HTTP 400 because the conversation did not contain the word “JSON”; the prompt was updated to mention JSON, and the rerun succeeded. The schema-constrained response demonstrated the desired shape, but semantic correctness still depends on the source text and model extraction. JSON mode alone guarantees syntax only, not a particular shape or truthful values.

| Mode | Raw response observation | Parse/result observation |
|---|---|---|
| No response constraint | Fenced JSON block with plant, season, and pot size. | `json.loads` failed on the opening Markdown fence. |
| JSON mode | Unfenced JSON object with `basil`, `summer`, `5`. | Parsed successfully. Initial provider rejection was resolved by including “JSON” in the system prompt. |
| Strict JSON Schema | Compact JSON object with the same three fields and values. | Parsed successfully and matched the requested schema. |

## Structured output or tools?

Give the model a tool when it must look up local or current information, perform an operation, or cause an action whose result must come from application-owned state. Ask for structured output when the application needs a response in a predictable shape, such as extracting plant, season, and pot size from a sentence, and no external operation is needed to produce those fields. They can be combined: a schema can constrain a tool request, and the tool can return data for the model to explain, but neither replaces checking the other boundary.

## General conclusion

A model's tool call can never be trusted as it arrives because it is generated content, not a privileged or type-safe function invocation. Every tool-calling loop must inspect every reply, parse and resolve each requested call, validate its arguments, execute only accepted calls, return one result message for every call identifier, and bound retries and total steps. A schema can prevent many shape, type, enum, and range mistakes when enforced, but it cannot guarantee truth, intent, safe consequences, correct tool selection, or faithful interpretation of the result. Deliberate fault injection tests these boundaries on demand and repeatably; waiting for a model to fail is nondeterministic and may never exercise the dangerous cases. The most important guard in this scenario is validating arguments against the shared schema before execution, because it prevents malformed or out-of-domain model output from reaching either gardening tool. For deployments with real-world consequences, domain-specific safety checks and human confirmation may also be required.
