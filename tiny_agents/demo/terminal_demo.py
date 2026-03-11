
from tiny_agents.tools import TerminalTool

terminal = TerminalTool(workspace="./agents")

result = terminal.run({"command": "ls -la"})
print(result)



