"""
Ramaz X1 Agents Setup based on Blueprint
Version: 1.0.0

Hierarchy:
User (Founder)
  └── Assistant (NDS / معاون)
        ├── Technical Department Manager
        │     └── Technical Workers (NDS, ICT, RTM, Supply&Demand, Ash Trigger, ...)
        └── Fundamental Department Manager
              └── Fundamental Workers (News, X, YouTube, Telegram, ...)

Communication Rules:
- Employees only communicate with their own Department Manager
- Employees never communicate with each other
- Employees never communicate with Assistant
- Managers communicate with Assistant
- Assistant communicates with User
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

    # Technical Workers
    technical_workers = [
        ("TECH-NDS-01", "NDS Worker", "NDS Analysis"),
        ("TECH-ICT-01", "ICT Worker", "ICT Concepts"),
        ("TECH-RTM-01", "RTM Worker", "RTM Analysis"),
        ("TECH-SD-01", "Supply Demand Worker", "Supply & Demand"),
        ("TECH-ASH-01", "Ash Trigger Worker", "Ash Trigger"),
    ]

    for agent_id, name, role in technical_workers:
        registry.register(
            agent_id=agent_id,
            name=name,
            agent_type="Employee",
            department="Technical",
            role=role,
            version="1.0",
            status="READY" if agent_id == "TECH-NDS-01" else "WAITING"
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

    # Fundamental Workers
    fundamental_workers = [
        ("FUND-NEWS-01", "News Worker", "News Analysis"),
        ("FUND-X-01", "X Worker", "X/Twitter Analysis"),
        ("FUND-YT-01", "YouTube Worker", "YouTube Analysis"),
        ("FUND-TG-01", "Telegram Worker", "Telegram Analysis"),
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
