"""Offline smoke tests for the scRNA-seq computational environment.

Run inside the installed environment: python tests/test_environment.py

Uses synthetic counts and temporary files. No dataset, pretrained model,
reference output, pytest, or network access is needed. Checks software
functionality, not biological accuracy. CellTypist and Scrublet are import-
checked; their prediction workflows require separate real-data validation.
Versions are reported; environment.yml remains the dependency specification.
"""

from importlib import import_module, metadata
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault("MPLBACKEND", "Agg")

REQUIRED_PACKAGES = (
    ("numpy", "numpy"), ("pandas", "pandas"), ("scipy", "scipy"),
    ("matplotlib", "matplotlib"), ("scanpy", "scanpy"), ("anndata", "anndata"),
    ("sklearn", "scikit-learn"), ("h5py", "h5py"), ("igraph", "igraph"),
    ("leidenalg", "leidenalg"), ("numba", "numba"), ("scrublet", "scrublet"),
    ("celltypist", "celltypist"), ("skmisc.loess", "scikit-misc"),
    ("umap", "umap-learn"), ("pynndescent", "pynndescent"), ("zarr", "zarr"),
)


def synthetic_counts():
    """Return a fresh sparse fixture with three artificial expression groups."""
    import anndata as ad
    import numpy as np
    import pandas as pd
    from scipy import sparse

    rng = np.random.default_rng(42)
    groups = np.repeat(np.arange(3), 40)
    means = rng.gamma(shape=2.0, scale=0.8, size=600)
    contrasts = np.array([
        [5.0 if group * 40 <= gene < (group + 1) * 40 else 0.0 for gene in range(600)]
        for group in range(3)
    ])
    counts = sparse.csr_matrix(rng.poisson(means[None, :] + contrasts[groups]), dtype=np.float32)
    genes = [f"GENE_{i:04d}" for i in range(588)]
    genes += [f"MT-SYNTHETIC_{i:02d}" for i in range(12)]
    return ad.AnnData(
        X=counts.copy(),
        obs=pd.DataFrame(
            {"synthetic_group": pd.Categorical(groups.astype(str))},
            index=[f"synthetic_cell_{i:03d}" for i in range(len(groups))],
        ),
        var=pd.DataFrame({"mt": [g.startswith("MT-") for g in genes]}, index=genes),
        layers={"counts": counts.copy()},
    )


def normalized_data():
    """Return log-normalized toy expression and preserve original counts."""
    import scanpy as sc

    normalized = sc.pp.normalize_total(synthetic_counts(), target_sum=10_000, copy=True)
    return sc.pp.log1p(normalized, copy=True)


class DependencyTests(unittest.TestCase):
    def test_required_packages_import(self):
        # CellTypist creates cache directories on import; keep them temporary.
        with tempfile.TemporaryDirectory(prefix="scrnaseq-imports-") as directory:
            with patch.dict(os.environ, {"CELLTYPIST_FOLDER": directory}):
                for module_name, distribution in REQUIRED_PACKAGES:
                    with self.subTest(package=distribution):
                        import_module(module_name)
                        print(f"  {distribution}: {metadata.version(distribution)}", flush=True)

    def test_installed_dependency_consistency(self):
        result = subprocess.run(
            [sys.executable, "-m", "pip", "check"],
            capture_output=True, text=True, timeout=60, check=False,
        )
        self.assertEqual(result.returncode, 0, f"Dependency conflicts:\n{result.stdout}\n{result.stderr}")


class FunctionalTests(unittest.TestCase):
    def test_qc_normalization_and_count_preservation(self):
        import numpy as np
        import scanpy as sc

        original = synthetic_counts()
        cells, genes = sc.pp.calculate_qc_metrics(
            original, qc_vars=["mt"], percent_top=None, log1p=False, inplace=False,
        )
        self.assertEqual(len(cells), original.n_obs)
        self.assertEqual(len(genes), original.n_vars)
        np.testing.assert_allclose(cells["total_counts"], np.asarray(original.X.sum(axis=1)).ravel())
        mt_counts = np.asarray(original[:, original.var.mt].X.sum(axis=1)).ravel()
        np.testing.assert_allclose(cells["pct_counts_mt"], 100 * mt_counts / cells["total_counts"], rtol=1e-5)
        normalized = sc.pp.normalize_total(original, target_sum=10_000, copy=True)
        np.testing.assert_allclose(np.asarray(normalized.X.sum(axis=1)).ravel(), 10_000, rtol=1e-5)
        logged = sc.pp.log1p(normalized, copy=True)
        self.assertTrue(np.isfinite(logged.X.data).all())
        self.assertTrue((logged.X.data >= 0).all())
        self.assertEqual((original.X != logged.layers["counts"]).nnz, 0)
        self.assertEqual((original.X != original.layers["counts"]).nnz, 0)

    def test_seurat_v3_feature_selection_on_counts(self):
        import numpy as np
        import scanpy as sc

        original = synthetic_counts()
        features = sc.pp.highly_variable_genes(
            original, layer="counts", flavor="seurat_v3", n_top_genes=200, inplace=False,
        )
        self.assertTrue(features.index.equals(original.var_names))
        self.assertEqual(int(features["highly_variable"].sum()), 200)
        self.assertTrue(np.isfinite(features["variances_norm"]).all())
        self.assertEqual((original.X != original.layers["counts"]).nnz, 0)

    def test_graph_clustering_and_umap(self):
        import numpy as np
        import scanpy as sc

        pca = sc.pp.pca(normalized_data(), n_comps=10, svd_solver="arpack", random_state=42, copy=True)
        graph = sc.pp.neighbors(pca, n_neighbors=10, n_pcs=10, random_state=42, copy=True)
        self.assertEqual(graph.obsm["X_pca"].shape, (graph.n_obs, 10))
        for key in ("distances", "connectivities"):
            self.assertEqual(graph.obsp[key].shape, (graph.n_obs, graph.n_obs))
            self.assertTrue(np.isfinite(graph.obsp[key].data).all())
            self.assertGreater(graph.obsp[key].nnz, 0)
        for backend in ("igraph", "leidenalg"):
            with self.subTest(leiden_backend=backend):
                clustered = sc.tl.leiden(
                    graph, flavor=backend, directed=False, n_iterations=2,
                    random_state=42, key_added="test_cluster", copy=True,
                )
                self.assertFalse(clustered.obs["test_cluster"].isna().any())
                self.assertEqual(len(clustered.obs["test_cluster"]), graph.n_obs)
        embedded = sc.tl.umap(graph, random_state=42, maxiter=30, copy=True)
        self.assertEqual(embedded.obsm["X_umap"].shape, (graph.n_obs, 2))
        self.assertTrue(np.isfinite(embedded.obsm["X_umap"]).all())

    def test_marker_analysis_on_synthetic_groups(self):
        import numpy as np
        import scanpy as sc

        ranked = sc.tl.rank_genes_groups(
            normalized_data(), groupby="synthetic_group", method="wilcoxon",
            use_raw=False, n_genes=20, copy=True,
        )
        markers = sc.get.rank_genes_groups_df(ranked, group=None)
        self.assertTrue({"group", "names", "scores", "pvals_adj"}.issubset(markers.columns))
        self.assertEqual(set(markers["group"].astype(str)), {"0", "1", "2"})
        self.assertTrue(set(markers["names"]).issubset(ranked.var_names))
        self.assertTrue(np.isfinite(markers["scores"]).all())
        self.assertTrue(markers["pvals_adj"].between(0, 1).all())

    def assert_same_dataset(self, expected, observed):
        import numpy as np

        self.assertEqual(observed.shape, expected.shape)
        self.assertTrue(observed.obs_names.equals(expected.obs_names))
        self.assertTrue(observed.var_names.equals(expected.var_names))
        self.assertEqual((observed.layers["counts"] != expected.layers["counts"]).nnz, 0)
        np.testing.assert_allclose(observed.X.toarray(), expected.X.toarray())
        self.assertEqual(observed.obs["synthetic_group"].astype(str).tolist(),
                         expected.obs["synthetic_group"].astype(str).tolist())

    def test_h5ad_storage_round_trip(self):
        import anndata as ad

        expected = normalized_data()
        with tempfile.TemporaryDirectory(prefix="scrnaseq-smoke-") as directory:
            path = Path(directory) / "synthetic.h5ad"
            expected.write_h5ad(path, compression="gzip")
            self.assert_same_dataset(expected, ad.read_h5ad(path))

    def test_zarr_storage_round_trip(self):
        import anndata as ad

        expected = normalized_data()
        with tempfile.TemporaryDirectory(prefix="scrnaseq-smoke-") as directory:
            path = Path(directory) / "synthetic.zarr"
            expected.write_zarr(path)
            self.assert_same_dataset(expected, ad.read_zarr(path))

    def test_headless_plot_export(self):
        import matplotlib
        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as plt
        import numpy as np
        import scanpy as sc

        plotted = synthetic_counts()
        # Arbitrary toy coordinates test plotting, not a scientific embedding.
        plotted.obsm["X_synthetic"] = np.random.default_rng(42).normal(size=(plotted.n_obs, 2))
        with tempfile.TemporaryDirectory(prefix="scrnaseq-smoke-") as directory:
            path = Path(directory) / "synthetic.png"
            ax = sc.pl.embedding(plotted, basis="synthetic", color="synthetic_group", show=False)
            try:
                ax.figure.savefig(path, dpi=80)
                pixels = plt.imread(path)
                self.assertGreater(pixels.size, 0)
                self.assertTrue(np.isfinite(pixels).all())
            finally:
                plt.close(ax.figure)


if __name__ == "__main__":
    print(f"Python: {sys.version.split()[0]}\nInterpreter: {sys.executable}", flush=True)
    print("Offline synthetic-data smoke tests; no biological accuracy scoring.\n", flush=True)
    unittest.main(verbosity=2)
