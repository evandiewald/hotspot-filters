import networkx as nx
import pandas as pd
from sqlalchemy.engine import create_engine
import os
from dotenv import load_dotenv

load_dotenv()


engine = create_engine(os.getenv("POSTGRES_CONNECTION_STRING"))

addresses_sql = """
select distinct(witness_address) from challenge_receipts_parsed limit 2000;
"""

addresses = [a[0] for a in engine.execute(addresses_sql).all()]

results = []
for i, address in enumerate(addresses):
    edges_sql = f"""with a as
    
    (select distinct on (transmitter_address, witness_address) transmitter_address, witness_address
     from challenge_receipts_parsed
     where witness_address = '{address}'),
     
    b as
     (select distinct on (transmitter_address, witness_address) transmitter_address, witness_address from 
     challenge_receipts_parsed where witness_address in (select transmitter_address from a)
    )
     
    select transmitter_address, witness_address from a
    union all 
    select transmitter_address, witness_address from b;"""

    edges = engine.execute(edges_sql).all()

    G = nx.Graph(edges)

    # cliques
    cliques = nx.cliques_containing_node(G, nodes=[address])[address]
    clique_sizes = [len(c) for c in cliques]
    # largest_cliques = [c for c in cliques if len(c) == max(clique_sizes)]
    largest_clique_size = max(clique_sizes)

    # clustering coefficient
    clustering_coeff = nx.clustering(G, nodes=[address])[address]

    # degree
    in_degree = G.degree[address]

    # link prediction
    # non_edges = [(ROOT_NODE_ADDRESS, n) for n in nx.non_neighbors(G, ROOT_NODE_ADDRESS)]
    # jc = [j for j in nx.jaccard_coefficient(G, non_edges)]

    results.append({"address": address, "largest_clique": largest_clique_size, "clustering_coefficient": clustering_coeff, "in_degree": in_degree})

    if i % 10 == 0:
        print(f"{i} / {len(addresses)} graphs complete.")

df = pd.DataFrame(results)
df.to_csv("static/graph_metrics_sample.csv")