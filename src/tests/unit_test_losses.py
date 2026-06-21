import unittest

import torch

from src.machine_learning.losses import cosine_loss, info_nce, jaccard_binary, wasserstein_1d


class TestLossHelpers(unittest.TestCase):
    def test_cosine_loss_is_zero_for_identical_vectors(self):
        x = torch.tensor([[1.0, 0.0], [0.0, 1.0]])
        y = torch.tensor([[1.0, 0.0], [0.0, 1.0]])

        loss = cosine_loss(x, y)

        self.assertTrue(torch.isclose(loss, torch.tensor(0.0)))

    def test_wasserstein_1d_is_zero_for_identical_spectra(self):
        pred = torch.tensor([[0.0, 1.0, 0.0], [0.25, 0.5, 0.25]])
        target = pred.clone()

        loss = wasserstein_1d(pred, target)

        self.assertTrue(torch.isclose(loss, torch.tensor(0.0)))

    def test_info_nce_returns_finite_scalar(self):
        z_q = torch.tensor([[1.0, 0.0], [0.0, 1.0]])
        z_k = torch.tensor([[1.0, 0.0], [0.0, 1.0]])

        loss = info_nce(z_q, z_k)

        self.assertEqual(loss.dim(), 0)
        self.assertTrue(torch.isfinite(loss))
        self.assertGreater(loss.item(), 0.0)

    def test_jaccard_binary_matches_expected_extremes(self):
        a = torch.tensor([[1.0, 0.0, 1.0], [1.0, 0.0, 0.0]])
        b = torch.tensor([[1.0, 0.0, 1.0], [0.0, 1.0, 0.0]])

        scores = jaccard_binary(a, b)

        self.assertTrue(torch.isclose(scores[0], torch.tensor(1.0), atol=1e-6))
        self.assertTrue(torch.isclose(scores[1], torch.tensor(0.0), atol=1e-6))


if __name__ == "__main__":
    unittest.main()
