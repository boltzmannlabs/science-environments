"""Native Syntheseus phase adapted from SynthChem planning/search_portfolio.py.

Source: user-provided 20261027 review snapshot. SRG replaces proposal access,
identity normalization and route acceptance; the A*/MCTS algorithms are native.
"""
import random
import time
from importlib.metadata import version
from .planning import _step


def require_native():
    try:
        from syntheseus.search.algorithms.mcts.molset import MolSetMCTS
        from syntheseus.search.algorithms.best_first.retro_star import RetroStarSearch
        if version('syntheseus') != '0.8.0':
            raise RuntimeError('SynthChem search requires the validated syntheseus==0.8.0 dependency')
    except ImportError as exc:
        raise RuntimeError('SynthChem search unavailable; install the optional syntheseus==0.8.0 dependency') from exc
    return RetroStarSearch, MolSetMCTS


def run_native_phase(pool, name, stock, *, seed, depth, max_nodes, quota, route_limit, phase_deadline):
    RetroStarSearch, MolSetMCTS = require_native()
    from syntheseus import Molecule
    from syntheseus.interface.bag import Bag
    from syntheseus.interface.models import BackwardReactionModel
    from syntheseus.interface.reaction import SingleProductReaction
    from syntheseus.search.analysis.route_extraction import iter_routes_time_order
    from syntheseus.search.mol_inventory import BaseMolInventory
    from syntheseus.search.node_evaluation.base import NoCacheNodeEvaluator
    from syntheseus.search.node_evaluation.common import ConstantNodeEvaluator, HasSolutionValueFunction
    target = pool.env.task.target

    class Inventory(BaseMolInventory):
        def is_purchasable(self, mol):
            return mol.smiles != target and mol.smiles in stock

    class ExpansionModel(BackwardReactionModel):
        def __init__(self):
            # Pool owns successful caches; native caching must never retain failures as [].
            super().__init__(use_cache=False,default_num_results=pool.width)

        def _get_reactions(self, inputs, num_results):
            return [[SingleProductReaction(product=mol,reactants=Bag(Molecule(s) for s in p['reactants']),
                metadata={'proposal':p,'search_cost':p['search_cost']})
                for p in pool.expand(mol.smiles)[:num_results]] for mol in inputs]

        def get_parameters(self):
            return []

    class StepCost(NoCacheNodeEvaluator):
        def _evaluate_nodes(self, nodes, graph=None):
            return [n.reaction.metadata['search_cost'] for n in nodes]

    class StockProgress(NoCacheNodeEvaluator):
        def _evaluate_nodes(self, nodes, graph=None):
            return [sum(m.metadata.get('is_purchasable',False) for m in n.mols)/max(1,len(n.mols))
                    for n in nodes]

    class BoundedMixin:
        capacity_pruned = 0

        def should_stop_search(self, graph):
            return pool.stopped or super().should_stop_search(graph)

        def _get_mols_to_expand(self, node, graph):
            return sorted(super()._get_mols_to_expand(node,graph),key=lambda m:m.smiles)

        def expand_node(self, node, graph, force_expansion=False):
            self._available_nodes = max(0,max_nodes-len(graph))
            return super().expand_node(node,graph,force_expansion=force_expansion)

        def _filter_reactions(self, reactions, node, graph):
            selected = []
            for reaction in super()._filter_reactions(reactions,node,graph):
                bound = 1+len(set(reaction.reactants)) if name=='astar' else 1
                if bound > self._available_nodes:
                    self.capacity_pruned += 1
                    continue
                self._available_nodes -= bound
                selected.append(reaction)
            return selected

    class AStar(BoundedMixin, RetroStarSearch):
        pass

    class MCTS(BoundedMixin, MolSetMCTS):
        pass

    options = {'reaction_model':ExpansionModel(),'mol_inventory':Inventory(),
        'limit_reaction_model_calls':max(1,pool.max_calls*4),'limit_iterations':max(20,quota*20),
        'time_limit_s':max(.001,pool.phase_deadline-time.monotonic()),'limit_graph_nodes':max_nodes,
        'max_expansion_depth':2*depth if name=='astar' else depth,
        'prevent_repeat_mol_in_trees':True,'random_state':random.Random(seed)}
    if name=='astar':
        search = AStar(value_function=ConstantNodeEvaluator(0.0),and_node_cost_fn=StepCost(),**options)
    else:
        search = MCTS(value_function=StockProgress(),reward_function=HasSolutionValueFunction(),
                      bound_constant=1.4,**options)
    before, started = pool.calls, time.monotonic()
    graph, iterations = search.run_from_mol(Molecule(target))
    graph.assert_validity()
    ended = time.monotonic()
    raw, errors = [], []
    if graph.root_node.has_solution:
        duration = max(0,min(5.0,phase_deadline-time.monotonic()))
        for nodes in iter_routes_time_order(graph,max_routes=route_limit,max_time_s=duration):
            try:
                synthesis = graph.to_synthesis_graph(nodes)
                synthesis.assert_validity()
                predictions = [r.metadata['proposal'] for r in synthesis.nodes()]
                raw.append({'steps':tuple(_step(p) for p in predictions),
                    'review_penalty':sum(p['input_review_required'] for p in predictions)})
            except (ValueError,KeyError,AssertionError) as exc:
                errors.append({'reason':'native_route_conversion_failed','error_type':type(exc).__name__})
    report = {'algorithm':name,'native_algorithm':'RetroStarSearch' if name=='astar' else 'MolSetMCTS',
        'status':'completed','graph_has_solution':bool(graph.root_node.has_solution),
        'graph_nodes':len(graph),'iterations':iterations,'backend_expansion_actions':pool.calls-before,
        'allocated_expansion_actions':quota,'search_seconds':ended-started,
        'phase_total_seconds':time.monotonic()-started,'extracted_routes':len(raw),
        'node_capacity_pruned':search.capacity_pruned,'termination':pool.admission_reason(backend=True)
            or ('graph_node_limit' if len(graph)>=max_nodes else 'iteration_limit_or_frontier_exhausted'),
        'heuristic':'h=0; positive step cost' if name=='astar' else 'UCT stock-fraction estimate; terminal solution reward'}
    return report,raw,errors
