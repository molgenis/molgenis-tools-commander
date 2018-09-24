from mdev import history, io


def script(args):
    lines = history.read(args.number, args.show_fails)

    options = [line[1] for line in lines]
    commands = io.checkbox('Pick the lines that will form te script:', options)
