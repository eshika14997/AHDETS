from src.models import EdgeNode


def create_edge_nodes():
    """
    Create the heterogeneous edge computing environment.

    Returns
    -------
    list[EdgeNode]
        Ten heterogeneous edge nodes.
    """

    capacities = [
        500,
        750,
        1000,
        1250,
        1500,
        1750,
        2000,
        2250,
        2500,
        3000
    ]

    nodes = []

    for node_id, capacity in enumerate(capacities, start=1):
        node = EdgeNode(
            node_id=node_id,
            capacity=capacity,
            initial_energy=100.0
        )

        nodes.append(node)

    return nodes