"""Closira Agent Assignment - Main Executable."""

import json
import sys

from dotenv import load_dotenv

from agent import ClosiraAgentEngine

# Load environment variables
load_dotenv()


def run_simulation():
    print("🚀 Initializing Closira AI Agent Pipeline Engine...")

    # Ensure this is spelled exactly: e-n-g-i-n-e
    engine = ClosiraAgentEngine(sop_path="data/sop.json")

    print("🟢 Engine ready. Type 'exit' or 'quit' to terminate session naturally.\n")
    print("AI: Hello! Welcome to Bloom Aesthetics Clinic. How can I help you today?")

    while True:
        try:
            user_input = input("\nYou: ")
            if not user_input.strip():
                print("Please enter a message.")
                continue
            if user_input.lower() in ["exit", "quit"]:
                break

            # Make sure this matches the variable name above perfectly!
            result = engine.process_message(user_input)

            print("\n📊 [INTERNAL STATE DETECTED]")
            print(f" ├─ Status: {engine.current_stage}")
            print(f" ├─ Target Workflow Stage: {result.updated_stage}")
            print(f" ├─ Escalation Signal: {result.escalate}")
            if result.escalation_reason:
                print(f" ├─ Escalation Reason: {result.escalation_reason}")
            print(f" └─ Extracted Data Cache: {json.dumps(engine.compiled_lead_data)}")

            print(f"\n💬 AI: {result.reply}")

            if result.escalate:
                print("\n⚠️ [SYSTEM EVENT: HANDING OFF SESSION TO HUMAN OPERATOR. TERMINATING LOOP.]")
                break

        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted by user.")
            break
        except Exception as error:
            print(f"❌ Error processing input: {error}")


def main():
    """Main entry point."""
    print("\n🌸 CLOSIRA AGENT ASSIGNMENT")
    print("Bloom Aesthetics Clinic - SOP Compliance Agent\n")

    if len(sys.argv) > 1 and sys.argv[1].lower() == "test":
        print("Test mode is not available for this LLM-backed engine yet.")
        print("Running interactive simulation instead.\n")

    run_simulation()


if __name__ == "__main__":
    main()
