def parse_commands(
    text: str
):

    commands = []

    lines = text.splitlines()

    for line in lines:

        line = line.strip()

        if not line:
            continue

        line = line.upper()

        if line.startswith("+"):

            symbol = (
                line[1:]
                .strip()
            )

            commands.append(
                {
                    "action": "add",
                    "symbol": symbol
                }
            )

        elif line.startswith("-"):

            symbol = (
                line[1:]
                .strip()
            )

            commands.append(
                {
                    "action": "remove",
                    "symbol": symbol
                }
            )

        elif line == "LIST":

            commands.append(
                {
                    "action": "list"
                }
            )

        elif line == "CLEAR":

            commands.append(
                {
                    "action": "clear"
                }
            )

    return commands