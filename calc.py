from dataclasses import dataclass

from draw3 import draw

END_STATE = 'q0'
START_STATE = 'q1'
LAMBDA = 'λ'


@dataclass
class Transit:
    next_command: str
    replace_to: str
    delta: int

    def __iter__(self):
        return iter((self.next_command, self.replace_to, self.delta))


@dataclass
class Command:
    transits: dict[str: Transit]


@dataclass
class State:
    arrow: str
    tape: list
    index: int
    command: str = 'q1'
    end: bool = False


class Tape:
    def __init__(self, tape_str: str, table: list[list[list[str, bool]]], index: int) -> None:
        tape = list(map(str, tape_str))
        tape = [LAMBDA, ] + tape + [LAMBDA, ]
        self.command_symbols = [i[0] for i in table[0][1:]]
        rows = table[1:]
        commands = dict()
        to_drawer = list()
        for row in rows:
            start_state = row[0][0]
            if start_state not in commands:
                commands[start_state] = Command({})
            pos = 0
            for elem in row[1:]:
                statement = elem[0]
                command_symbol = self.command_symbols[pos]
                if statement:
                    info = list(map(str, statement.split(' ')))
                    delta = 0
                    new_state = start_state
                    symbol_to_replace = command_symbol
                    if len(info) == 3:
                        new_state, symbol_to_replace, delta = map(str, statement.split(' '))

                    # region частичное задание

                    if len(info) == 2:
                        if info[0][0] == 'q':
                            new_state = info[0]
                        else:
                            symbol_to_replace = info[0]
                        if info[1] in ['L', 'R', 'E', '-1', '1', '0', 'l', 'r', 'e']:
                            delta = info[1]
                        else:
                            symbol_to_replace = info[1]

                    if len(info) == 1:
                        if info[0][0] == 'q':
                            new_state = info[0]
                        elif info[0] in ['L', 'R', 'E', '-1', '1', '0', 'l', 'r', 'e']:
                            delta = info[0]
                        else:
                            symbol_to_replace = info[0]
                    # endregion частичное задание

                    if isinstance(delta, int) or delta.isdigit():
                        delta = int(delta)
                    else:
                        if delta == 'R':
                            delta = 1
                        elif delta == 'L':
                            delta = -1
                        else:
                            delta = 0
                    to_drawer.append([start_state, command_symbol, new_state, symbol_to_replace, delta])
                    commands[start_state].transits[command_symbol] = Transit(new_state, symbol_to_replace, delta)
                pos += 1

        arrow = ' ' * index + '↓'
        self.state = State(arrow, tape, index)
        self.commands = commands
        self.to_drawer = to_drawer

    def next(self) -> State:
        if self.state.command == END_STATE:
            self.state.end = True
            return self.state
        if self.state.command not in self.commands:
            raise NotImplementedError
        symbol_now = self.state.tape[self.state.index]
        if symbol_now not in self.commands[self.state.command].transits:
            raise NotImplementedError

        next_command, replace, delta = self.commands[self.state.command].transits[symbol_now]

        self.state.command = next_command
        self.state.tape[self.state.index] = replace
        if self.state.index == 0 and delta == -1:
            self.state.tape = [LAMBDA, ] + self.state.tape
        elif self.state.index == len(self.state.tape) - 1 and delta == 1:
            self.state.tape = self.state.tape + [LAMBDA, ]
            self.state.index += 1
        elif self.state.index == len(self.state.tape) - 1:
            self.state.tape = self.state.tape + [LAMBDA, ]
            self.state.index += delta
        else:
            self.state.index += delta
        self.state.arrow = f"<html><head/><body><p>{'&nbsp;' * self.state.index + '↓'}<span style=\" vertical-align:super;\">{self.state.command}</span></p></body></html>"
        return self.state

    def draw_graph(self):
        draw(len(self.to_drawer), self.to_drawer)
