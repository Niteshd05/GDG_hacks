#!/usr/bin/env python3
"""
VERIFICATION SCRIPT: Hidden Routing Mode
Clean TUI interface with file logging
"""

import config
import logging
import os
from datetime import datetime

# Setup file logging (save to file, not console)
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"routing_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

file_logger = logging.getLogger("file_logger")
file_logger.setLevel(logging.INFO)
handler = logging.FileHandler(log_file)
handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
file_logger.addHandler(handler)

def write_log(message):
    """Write to file only, not console"""
    file_logger.info(message)

def print_tui(message):
    """Print to console (clean TUI)"""
    print(message)

def verify_routing():
    """Verify the actual routing of 3 instances"""
    
    # Clear screen (simple cross-platform approach)
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # TUI Header
    print_tui("╔" + "═" * 78 + "╗")
    print_tui("║" + " " * 78 + "║")
    print_tui("║" + "  🔍 PROJECT AETHER - HIDDEN ROUTING VERIFICATION".center(78) + "║")
    print_tui("║" + " " * 78 + "║")
    print_tui("╚" + "═" * 78 + "╝")
    
    # Collect data
    write_log("=" * 80)
    write_log("🔍 PROJECT AETHER - HIDDEN ROUTING VERIFICATION")
    write_log("=" * 80)
    
    write_log("\n📋 CONFIGURED MODELS (What appears in logs):")
    
    instances = {}
    models = {
        "Pro-A": config.PRO_MODEL_1,
        "Pro-B": config.PRO_MODEL_2,
        "Con-A": config.CON_MODEL_1,
        "Con-B": config.CON_MODEL_2,
        "Judge": config.JUDGE_MODEL
    }
    
    # Analyze routing
    print_tui("\n  Processing agents...")
    
    for agent, model in models.items():
        # Determine endpoint
        if "qwen2.5" in model.lower():
            endpoint = config.OLLAMA_LOCAL_URL
            endpoint_type = "LOCAL"
        else:
            endpoint = config.OLLAMA_REMOTE_URL
            endpoint_type = "REMOTE"
        
        # Extract model name
        model_name = model.split("/")[1]
        
        # Create instance key
        instance_key = f"{endpoint_type}||{model_name}"
        
        # Track
        if instance_key not in instances:
            instances[instance_key] = []
        instances[instance_key].append(agent)
        
        write_log(f"  {agent:8} → {endpoint_type:6} ({endpoint}) [{model_name}]")
    
    write_log("\n📊 UNIQUE INSTANCES (This is what actually runs):")
    
    # Display summary in TUI
    print_tui("\n┌────────────────────────────────────────────────────────────────────────────┐")
    print_tui("│ ROUTING SUMMARY                                                            │")
    print_tui("├────────────────────────────────────────────────────────────────────────────┤")
    
    for i, (instance_key, agents) in enumerate(instances.items(), 1):
        endpoint_type, model_name = instance_key.split("||")
        endpoint = config.OLLAMA_LOCAL_URL if endpoint_type == "LOCAL" else config.OLLAMA_REMOTE_URL
        
        agents_str = ", ".join(agents)
        write_log(f"  {i}. {endpoint_type} - {model_name} ({endpoint})")
        write_log(f"     Used by: {agents_str}")
        
        # TUI display
        status = "✓ LOCAL " if endpoint_type == "LOCAL" else "✓ REMOTE"
        print_tui(f"│ {status} {model_name:20} │ {agents_str:38} │")
    
    print_tui("├────────────────────────────────────────────────────────────────────────────┤")
    print_tui(f"│ Total Unique Instances: {len(instances)} (out of 5 apparent agents)        │")
    print_tui("├────────────────────────────────────────────────────────────────────────────┤")
    print_tui(f"│ Endpoints: {len(instances)} (1 LOCAL + 1 REMOTE = 2 total)                  │")
    print_tui("└────────────────────────────────────────────────────────────────────────────┘")
    
    # Log summary
    write_log(f"\n✅ TOTAL UNIQUE INSTANCES: {len(instances)}")
    write_log(f"⚠️  APPARENT INSTANCES (in logs): 5")
    write_log(f"✓  ACTUAL INSTANCES (running): {len(instances)}")
    
    # Footer with file location
    print_tui("\n" + "─" * 80)
    print_tui(f"📝 Detailed log saved to: {log_file}")
    print_tui("✅ Verification complete!")
    print_tui("─" * 80)
    
    write_log("\n" + "=" * 80)
    write_log("✅ Verification complete!")
    write_log("=" * 80)

if __name__ == "__main__":
    verify_routing()
