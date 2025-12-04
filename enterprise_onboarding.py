import json
import random
import string
from typing import Dict, Any

# Placeholder for LLM call (replace with actual Gemini API)
def llm_query(prompt: str) -> str:
    # Simulate LLM response; in real: use genai.GenerativeModel('gemini-pro').generate_content(prompt)
    return f"Simulated LLM response to: {prompt}"

# Custom Tool: Mock Email Sender
def send_email_tool(recipient: str, subject: str, body: str) -> str:
    print(f"Custom Tool: Sending email to {recipient} - Subject: {subject}")
    return "Email sent successfully"

# Built-in Tool: Code Execution for Password Generation
def generate_password(length: int = 12) -> str:
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

# Memory Bank (Long-term memory simulation, e.g., file-based for persistence)
class MemoryBank:
    def __init__(self, storage_file: str = "memory_bank.json"):
        self.storage_file = storage_file
        try:
            with open(self.storage_file, 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {}

    def store(self, key: str, value: Any):
        self.data[key] = value
        with open(self.storage_file, 'w') as f:
            json.dump(self.data, f)

    def retrieve(self, key: str) -> Any:
        return self.data.get(key)

# Session Service (In-memory state management)
class SessionService:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}  # session_id -> state

    def start_session(self, session_id: str, initial_state: Dict[str, Any]):
        self.sessions[session_id] = initial_state

    def update_session(self, session_id: str, updates: Dict[str, Any]):
        if session_id in self.sessions:
            self.sessions[session_id].update(updates)

    def get_session(self, session_id: str) -> Dict[str, Any]:
        return self.sessions.get(session_id, {})

# Agent Base Class
class Agent:
    def __init__(self, name: str, tools: Dict[str, callable]):
        self.name = name
        self.tools = tools

    def act(self, context: str, session_state: Dict[str, Any]) -> str:
        prompt = f"{self.name} Agent: Given context '{context}', perform your task."
        response = llm_query(prompt)  # LLM reasoning here
        # Example tool use
        if "generate_password" in self.tools:
            session_state["password"] = self.tools["generate_password"]()
        return response

# Multi-Agent System: Sequential Workflow
def run_sequential_agents(employee_data: Dict[str, str], session_id: str):
    session_service = SessionService()
    memory_bank = MemoryBank()

    # Start session with initial state
    initial_state = {"employee": employee_data, "status": "pending"}
    session_service.start_session(session_id, initial_state)

    # Retrieve from long-term memory if exists (e.g., resume)
    stored_data = memory_bank.retrieve(session_id)
    if stored_data:
        session_service.update_session(session_id, stored_data)
        print("Resumed from memory bank.")

    state = session_service.get_session(session_id)

    # Agent 1: HR Agent (validates info, uses custom tool)
    hr_tools = {"send_email": send_email_tool}
    hr_agent = Agent("HR", hr_tools)
    hr_context = f"Validate new employee: {state['employee']}"
    hr_response = hr_agent.act(hr_context, state)
    state["hr_notes"] = hr_response
    # Use tool: Send welcome email
    hr_tools["send_email"](state["employee"]["email"], "Welcome!", "Onboarding started.")
    session_service.update_session(session_id, state)  # Update session

    # Agent 2: IT Agent (sets up accounts, uses built-in tool)
    it_tools = {"generate_password": generate_password}
    it_agent = Agent("IT", it_tools)
    it_context = f"Setup accounts based on HR notes: {state['hr_notes']}"  # Context from previous
    it_response = it_agent.act(it_context, state)
    state["it_notes"] = it_response
    session_service.update_session(session_id, state)

    # Agent 3: Manager Agent (assigns tasks, compact context)
    manager_tools = {}  # No tools, just reasoning
    manager_agent = Agent("Manager", manager_tools)
    # Context engineering: Compact previous contexts
    compacted_context = f"Summary: Employee {state['employee']['name']} onboarded. HR: {state['hr_notes'][:100]}... IT: {state['it_notes'][:100]}..."
    manager_response = manager_agent.act(compacted_context, state)
    state["manager_notes"] = manager_response
    state["status"] = "completed"
    session_service.update_session(session_id, state)

    # Store final state in long-term memory
    memory_bank.store(session_id, state)

    return state

# Example Run
employee = {"name": "Jane Doe", "role": "Engineer", "email": "jane@example.com", "start_date": "2025-12-10"}
session_id = "onboarding_123"
final_state = run_sequential_agents(employee, session_id)
print("Final Onboarding State:", final_state)