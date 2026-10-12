"""Step 5: an agentic RAG helpdesk in LangGraph - tools + loop + memory."""
import ast
import operator

from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from lc_config import get_model, get_vectorstore

COURSE_FEES = {"CS101": 12000, "AI202": 18000, "DS303": 15000}   # same data as Day 1
MAX_DISTANCE = 0.4
store = get_vectorstore()


@tool
def search_handbook(query: str) -> str:
    """Search the college handbook (fees, hostel, exams, library, AI training) and return matching passages."""
    results = store.similarity_search_with_score(query, k=3)
    docs = [doc for doc, score in results if score <= MAX_DISTANCE]
    if not docs:
        return "NO_MATCH: this is not covered in the college handbook."
    return "\n\n".join(f"[{d.metadata['source']}] {d.page_content}" for d in docs)


@tool
def get_course_fee(course_code: str) -> str:
    """Return the fee in rupees for a course code such as CS101, AI202 or DS303."""
    fee = COURSE_FEES.get(course_code.strip().upper())
    return f"{course_code.upper()} fee is Rs. {fee}" if fee else f"Unknown course code {course_code}"


OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}

@tool
def check_exam_eligibility(attendance_percent: float) -> str:
    """Check exam eligibility for attendance from 0 to 100 percent."""
    if not 0 <= attendance_percent <= 100:
        return "ERROR: Attendance percentage must be between 0 and 100."
    if attendance_percent >= 75:
        return "ELIGIBLE: You may write the end-semester examination. Source: exam_regulations.md"
    if attendance_percent >= 65:
        return ("CONDONATION: You may apply with a medical or official certificate; "
                "the fee is Rs. 500 per course. Source: exam_regulations.md")
    return "NOT ELIGIBLE: You may not write the examination and must redo the course. Source: exam_regulations.md"

@tool
def calculator(expression: str) -> str:
    """Evaluate simple arithmetic such as '18000 + 15000' or '100 * 12'."""
    def ev(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in OPS:
            return OPS[type(n.op)](ev(n.left), ev(n.right))
        raise ValueError("only + - * / on numbers")
    try:
        return str(ev(ast.parse(expression, mode="eval").body))
    except Exception as e:                       # tell the model, don't crash the graph
        return f"Error: {e}"


tools = [search_handbook, get_course_fee, check_exam_eligibility, calculator]
model = get_model().bind_tools(tools)
SYSTEM = ("You are the Greenfield College helpdesk. Before answering, use the relevant tool. "
          "Use search_handbook for any rule or policy and for every question not directly handled by get_course_fee, check_exam_eligibility, or calculator, even if the topic appears unrelated to college. "
          "Do not assume a question is outside the handbook without calling search_handbook. "
          "get_course_fee for course fees, and check_exam_eligibility whenever a question asks whether attendance qualifies a student to write the end-semester exam. "
          "Use calculator for arithmetic. "
          "If search_handbook returns NO_MATCH, say you don't know because it is not covered in the college handbook. "
          "Answer briefly and name the source file. If the tools do not give the answer, say you don't know.")


def agent(state: MessagesState):
    """The LLM node: read the conversation, either answer or ask for a tool."""
    reply = model.invoke([("system", SYSTEM)] + state["messages"])
    return {"messages": [reply]}


builder = StateGraph(MessagesState)
builder.add_node("agent", agent)
builder.add_node("tools", ToolNode(tools))          # runs every tool call in the last message
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)   # tool calls? -> "tools", else -> END
builder.add_edge("tools", "agent")                  # the LOOP back to the LLM
graph = builder.compile(checkpointer=InMemorySaver())  # checkpointer = memory per thread


def ask(question, thread_id):
    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 10}
    print(f"\n[{thread_id}] USER: {question}")
    for step in graph.stream({"messages": [("user", question)]}, config, stream_mode="updates"):
        for node, update in step.items():
            for msg in update["messages"]:
                if getattr(msg, "tool_calls", None):
                    for c in msg.tool_calls:
                        print(f"   {node:6} -> call {c['name']}({c['args']})")
                elif node == "tools":
                    print(f"   {node:6} -> {msg.name} returned {msg.content[:55]!r}...")
                else:
                    print(f"   {node:6} -> ANSWER: {msg.content}")


if __name__ == "__main__":
    thread_id = "task-run"
    ask("What CGPA do I need to be eligible for placements?", thread_id)
    ask("My attendance is 70%. Can I write the exam?", thread_id)
    ask("What is the total of the CS101 fee, the AI202 fee and the maximum late fee?", thread_id)
    ask("And if I pay only 5 days late instead?", thread_id)
    ask("What is the capital of France?", thread_id)