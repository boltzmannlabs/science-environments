"""Tracked Syntheseus 0.8 compatibility for genuinely unlimited native search.

The best-first queue and route-extraction algorithms follow Syntheseus 0.8's
``best_first/base.py`` and ``analysis/route_extraction.py``. Only their resource
stops and iteration scheduling change. MCTS calls the upstream visit, UCT
selection, rewards and backpropagation unchanged. Its exhaustion test inspects
all nodes; it never substitutes a repeat/patience cutoff for exhaustion.

The finite branch width and task depth define the generated search space.
No site-packages edits, giant integer sentinels or episode timeouts are used.
"""
import heapq
import math
import random
import time

from .planning import _step
from .synthchem_native import require_native


def best_first_iterations(search, graph):
    """Yield after each native priority-queue expansion, with no iteration cap."""
    from syntheseus.search.algorithms.best_first.base import PriorityQueue
    queue = PriorityQueue()
    for node in graph.nodes():
        if search.node_eligible_for_queue(node, graph):
            priority = search.priority_function(node, graph)
            if priority < math.inf:
                queue.push_item(node, priority)
    while len(queue):
        item = queue.pop_item()
        assert math.isclose(item.priority, search.priority_function(item.item, graph))
        if not search.node_eligible_for_queue(item.item, graph):
            continue
        node = item.item
        new_nodes = list(search.visit_node(node, graph))
        updated = search.set_node_values(new_nodes + [node], graph)
        for changed in dict.fromkeys(new_nodes + list(updated)):
            if not search.node_eligible_for_queue(changed, graph):
                continue
            priority = search.priority_function(changed, graph)
            if changed in queue and math.isclose(queue.get_priority(changed), priority):
                continue
            if priority < math.inf:
                queue.push_item(changed, priority)
            else:
                queue.remove_item(changed)
        yield None


def mcts_iterations(search, graph):
    """Native MCTS visits until the finite expansion frontier is truly empty."""
    while any(search.can_expand_node(node, graph) for node in graph.nodes()):
        result = search.mcts_visit(graph.root_node, graph)
        updated = {graph.root_node}
        updated.update(result.nodes_visited, result.nodes_created, result.nodes_updated)
        search.set_node_values(updated, graph)
        yield None


def iter_unbounded_routes(graph, stopped=lambda: False):
    """Native time-order route extraction without count/time research cutoffs.

    A consumer may stop after its actual accepted unique output top-k. Unknown
    or rejected routes therefore cannot hide later eligible candidates behind
    the former ``top_k * 5`` extraction quota.
    """
    from syntheseus.search.analysis.route_extraction import _route_time_cost, _route_time_partial_cost
    from syntheseus.search.graph.and_or import OrNode
    from syntheseus.search.graph.molset import MolSetNode
    queue = [(-math.inf, False, 0, {graph.root_node}, [graph.root_node])]
    counter = 1
    while queue and not stopped():
        cost, complete, _, partial, frontier = heapq.heappop(queue)
        if complete:
            yield partial
            continue
        node, rest = frontier[0], frontier[1:]
        children = list(graph.successors(node))
        choices = [(partial, rest)] if not children else []
        if isinstance(node, OrNode):
            for child in children:
                grandchildren = list(graph.successors(child))
                choices.append((partial | {child} | set(grandchildren),
                                rest + [n for n in grandchildren if n not in partial]))
        elif isinstance(node, MolSetNode):
            choices += [(partial | {child}, rest + ([child] if child not in partial else []))
                        for child in children]
        else:
            raise TypeError(f'Unknown native route node type: {type(node).__name__}')
        for new_partial, new_frontier in choices:
            complete = not new_frontier
            new_cost = (_route_time_cost(new_partial, graph) if complete else
                        _route_time_partial_cost(new_partial, graph))
            if complete:
                assert new_cost >= cost, 'Native route lower bound not satisfied'
            if new_cost < math.inf:
                heapq.heappush(queue, (new_cost, complete, counter, new_partial, new_frontier))
                counter += 1


def _search(pool, name, stock, seed, depth):
    """Reuse the SynthChem native scoring functions and graph/expansion rules."""
    RetroStarSearch, MolSetMCTS = require_native()
    from syntheseus import Molecule
    from syntheseus.interface.bag import Bag
    from syntheseus.interface.models import BackwardReactionModel
    from syntheseus.interface.reaction import SingleProductReaction
    from syntheseus.search.mol_inventory import BaseMolInventory
    from syntheseus.search.node_evaluation.base import NoCacheNodeEvaluator
    from syntheseus.search.node_evaluation.common import ConstantNodeEvaluator, HasSolutionValueFunction

    class Inventory(BaseMolInventory):
        def is_purchasable(self, mol):
            return mol.smiles != pool.env.task.target and mol.smiles in stock

    class ExpansionModel(BackwardReactionModel):
        def __init__(self):
            super().__init__(use_cache=False, default_num_results=pool.width)

        def _get_reactions(self, inputs, num_results):
            return [[SingleProductReaction(product=mol,
                reactants=Bag(Molecule(s) for s in p['reactants']),
                metadata={'proposal': p, 'search_cost': p['search_cost']})
                for p in pool.expand(mol.smiles)[:num_results]] for mol in inputs]

        def get_parameters(self):
            return []

    class StepCost(NoCacheNodeEvaluator):
        def _evaluate_nodes(self, nodes, graph=None):
            return [node.reaction.metadata['search_cost'] for node in nodes]

    class StockProgress(NoCacheNodeEvaluator):
        def _evaluate_nodes(self, nodes, graph=None):
            return [sum(m.metadata.get('is_purchasable', False) for m in node.mols)
                    / max(1, len(node.mols)) for node in nodes]

    class UnlimitedMixin:
        def should_stop_search(self, graph):
            return pool.stopped

        def _get_mols_to_expand(self, node, graph):
            return sorted(super()._get_mols_to_expand(node, graph), key=lambda m: m.smiles)

        def _run_from_graph_after_setup(self, graph):
            # Also safe if used through the native run_from_graph API directly.
            iterations = best_first_iterations if name == 'astar' else mcts_iterations
            count = 0
            iterator = iterations(self, graph)
            while not self.should_stop_search(graph):
                try:
                    next(iterator)
                except StopIteration:
                    break
                count += 1
            return count

    class AStar(UnlimitedMixin, RetroStarSearch):
        pass

    class MCTS(UnlimitedMixin, MolSetMCTS):
        def _check_infinite_runtime(self):
            # Upstream compares numeric ceilings. Our loop has exact finite
            # expansion-frontier exhaustion instead, so that warning is obsolete.
            return None

    options = {'reaction_model': ExpansionModel(), 'mol_inventory': Inventory(),
        'limit_reaction_model_calls': None, 'limit_iterations': None,
        'time_limit_s': None, 'limit_graph_nodes': None,
        'max_expansion_depth': 2 * depth if name == 'astar' else depth,
        'prevent_repeat_mol_in_trees': True, 'random_state': random.Random(seed)}
    if name == 'astar':
        return AStar(value_function=ConstantNodeEvaluator(0.0), and_node_cost_fn=StepCost(), **options)
    return MCTS(value_function=StockProgress(), reward_function=HasSolutionValueFunction(),
                bound_constant=1.4, **options)


class UnboundedNativePhase:
    """One resumable native search tree; portfolio scheduling owns no quotas."""
    def __init__(self, pool, name, stock, *, seed, depth):
        from syntheseus import Molecule
        if name not in ('astar', 'mcts'):
            raise ValueError('Expected astar or mcts')
        self.pool, self.name = pool, name
        self.search = _search(pool, name, stock, seed, depth)
        self.graph = self.search.create_graph(Molecule(pool.env.task.target))
        self.search.setup(self.graph)
        iterator = best_first_iterations if name == 'astar' else mcts_iterations
        self.iterator = iterator(self.search, self.graph)
        self.done, self.termination = False, None
        self.iterations, self.backend_actions, self.extracted = 0, 0, 0
        self.search_seconds, self.started = 0.0, time.monotonic()
        self.last_extracted_nodes = 0
        self.errors = ()

    def advance(self):
        if self.done:
            return False
        reason = self.pool.admission_reason(backend=True)
        if reason:
            self.close(reason)
            return False
        before, failures, start = self.pool.calls, len(self.pool.failures), time.monotonic()
        try:
            next(self.iterator)
            self.iterations += 1
        except StopIteration:
            self.close('frontier_exhausted')
        except (MemoryError, RecursionError) as exc:
            self.errors = (*self.errors, {'reason': 'search_capacity_failure',
                                         'error_type': type(exc).__name__})
            self.close('search_capacity_failure')
        finally:
            self.search_seconds += time.monotonic() - start
            self.backend_actions += self.pool.calls - before
        if len(self.pool.failures) > failures:
            self.close('backend_failure')
        return not self.done

    def rows(self):
        """Yield only newly reachable route graphs, with cancellation checks."""
        if not self.graph.root_node.has_solution or self.last_extracted_nodes == len(self.graph):
            return
        self.last_extracted_nodes = len(self.graph)
        for nodes in iter_unbounded_routes(self.graph, lambda: self.pool.stopped):
            try:
                synthesis = self.graph.to_synthesis_graph(nodes)
                synthesis.assert_validity()
                predictions = [reaction.metadata['proposal'] for reaction in synthesis.nodes()]
                row = {'steps': tuple(_step(p) for p in predictions),
                       'review_penalty': sum(p['input_review_required'] for p in predictions)}
            except (ValueError, KeyError, AssertionError) as exc:
                self.errors = (*self.errors, {'reason': 'native_route_conversion_failed',
                                             'error_type': type(exc).__name__})
                continue
            self.extracted += 1
            yield row

    def close(self, reason):
        if not self.done:
            self.done, self.termination = True, reason
            self.iterator.close()
            self.search.teardown(self.graph)

    def report(self):
        return {'algorithm': self.name,
            'native_algorithm': 'RetroStarSearch' if self.name == 'astar' else 'MolSetMCTS',
            'status': 'completed' if self.termination in ('route_quota', 'frontier_exhausted') else 'interrupted',
            'graph_has_solution': bool(self.graph.root_node.has_solution),
            'graph_nodes': len(self.graph), 'iterations': self.iterations,
            'backend_expansion_actions': self.backend_actions, 'allocated_expansion_actions': None,
            'search_seconds': self.search_seconds, 'phase_total_seconds': time.monotonic()-self.started,
            'extracted_routes': self.extracted, 'node_capacity_pruned': 0,
            'termination': self.termination,
            'heuristic': 'h=0; positive step cost' if self.name == 'astar' else
                         'UCT stock-fraction estimate; terminal solution reward'}
