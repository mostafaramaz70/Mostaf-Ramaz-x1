"""
Ramaz X1 Agents Setup based on Blueprint
Version: 1.1.0

Hierarchy:
User (Founder)
  └── Assistant (NDS / معاون)
        ├── Technical Department Manager
        │     └── Technical Workers (raw/trainable)
        └── Fundamental Department Manager
              └── Fundamental Workers (raw/trainable)

Communication Rules:
- Employees only communicate with their own Department Manager
- Employees never communicate with each other
- Employees never communicate with Assistant
- Managers communicate with Assistant
- Assistant communicates with User

Training Model:
- Employees start RAW
- User teaches them
- User tests them -> Experience
- Runtime uses Training + Experience (Experience has higher weight)
"""

from runtime.registry import AgentRegistry


def setup_blueprint_agents(registry: AgentRegistry) -> None:
    """Register all agents according to Blueprint structure."""

    # Assistant (معاون)
    registry.register(
        agent_id="ASSISTANT-NDS",
        name="Assistant NDS",
        agent_type="Assistant",
        department="Organization",
        role="Deputy Decision Engine",
        version="1.0",
        status="ACTIVE"
    )

    # Technical Department Manager
    registry.register(
        agent_id="TECH-MANAGER",
        name="Technical Department Manager",
        agent_type="Manager",
        department="Technical",
        role="Department Head",
        version="1.0",
        status="ACTIVE"
    )

    # Technical Workers (RAW / trainable)
    technical_workers = [
        ("TECH-NDS-01", "NDS Worker", "Trainable Technical Analyst"),
        ("TECH-ICT-01", "ICT Worker", "Trainable Technical Analyst"),
        ("TECH-RTM-01", "RTM Worker", "Trainable Technical Analyst"),
        ("TECH-SD-01", "Supply Demand Worker", "Trainable Technical Analyst"),
        ("TECH-ASH-01", "Ash Trigger Worker", "Trainable Technical Analyst"),
    ]

    for agent_id, name, role in technical_workers:
        registry.register(
            agent_id=agent_id,
            name=name,
            agent_type="Employee",
            department="Technical",
            role=role,
            version="2.0" if agent_id == "TECH-NDS-01" else "1.0",
            status="RAW" if agent_id == "TECH-NDS-01" else "WAITING"
        )

    # Fundamental Department Manager
    registry.register(
        agent_id="FUND-MANAGER",
        name="Fundamental Department Manager",
        agent_type="Manager",
        department="Fundamental",
        role="Department Head",
        version="1.0",
        status="ACTIVE"
    )

    # Fundamental Workers (RAW / trainable)
    fundamental_workers = [
        ("FUND-NEWS-01", "News Worker", "Trainable Fundamental Analyst"),
        ("FUND-X-01", "X Worker", "Trainable Fundamental Analyst"),
        ("FUND-YT-01", "YouTube Worker", "Trainable Fundamental Analyst"),
        ("FUND-TG-01", "Telegram Worker", "Trainable Fundamental Analyst"),
    ]

    for agent_id, name, role in fundamental_workers:
        registry.register(
            agent_id=agent_id,
            name=name,
            agent_type="Employee",
            department="Fundamental",
            role=role,
            version="1.0",
            status="WAITING"
        )
