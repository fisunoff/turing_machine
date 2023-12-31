import webbrowser
import pathlib
from pyvis.network import Network


def make_indexes(x: str) -> str:
    """
    Заменяет числа в строке на "подстрочные знаки"
    :param x: Исходная строка
    :return:
    """
    normal = "0123456789"
    sub_s = "₀₁₂₃₄₅₆₇₈₉"
    res = x.maketrans(''.join(normal), ''.join(sub_s))
    return x.translate(res)


def draw(n: int, data: list[list]):
    net = Network(directed=True)
    nodes = set()
    edges = dict()
    for i in range(n):
        start_state, position, new_state, symbol_to_replace, delta = map(str, data[i])
        delta = int(delta)
        match delta:
            case -1:
                delta = 'L'
            case 1:
                delta = 'R'
            case _:
                delta = ''
        nodes.add(start_state)
        nodes.add(new_state)
        key = (start_state, new_state)
        if key in edges:
            if start_state != new_state:
                edges[key].append(f"{position}→{symbol_to_replace} {delta}")
            else:
                edges[key][0] = edges[key][0] + f"\n{position}→{symbol_to_replace} {delta}"
        else:
            edges[key] = [f"{position}→{symbol_to_replace} {delta}", ]
    for i in nodes:
        if i == 'q0':
            net.add_node(i, label=make_indexes(i), color='#3cb371', shape='circle', font_size=500)
        else:
            net.add_node(i, label=make_indexes(i), shape='circle', size=100)

    for n in net.nodes:
        n["size"] = 30
        n["font"] = {"size": 30}

    for key in edges:
        for edge in edges[key]:
            net.add_edge(key[0], key[1], label=f"{edge}")

    c = net.generate_html()
    f = open('list.html', 'w')
    f.write(c)
    path = str(pathlib.Path().resolve()) + '/' + 'list.html'
    webbrowser.open(path, new=0)
