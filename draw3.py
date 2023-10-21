import webbrowser
import pathlib
from pyvis.network import Network


def draw(n: int, data: list[list]):
    net = Network(directed=True)
    nodes = set()
    edges = list()
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
        edges.append([start_state, new_state, position, symbol_to_replace, delta])

    for i in nodes:
        net.add_node(i, label=i)

    for i in edges:
        net.add_edge(i[0], i[1], label=f"{i[2]}->{i[3]} {i[4]}")

    c = net.generate_html()
    f = open('list.html', 'w')
    f.write(c)
    path = str(pathlib.Path().resolve()) + '/' + 'list.html'
    webbrowser.open(path, new=0)
