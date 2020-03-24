def load_env(path: str) -> dict:
    env = {}

    with open(path, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            elif line:
                while line.endswith('\n'):
                    line = line[:-1]
                if line:
                    tokens = line.split('=', 1)
                    if len(tokens) == 2:
                        env[tokens[0].strip()] = tokens[1].strip()

    return env
