"""
agents/router.py

Router Agent

Only decides which tool to execute.
It NEVER modifies the workflow state.
"""


def router(state):

    print("\n========== Router Agent ==========\n")

    print(f"Selected Tool : {state['tool']}")

    # IMPORTANT:
    # Return the existing state unchanged.
    return state