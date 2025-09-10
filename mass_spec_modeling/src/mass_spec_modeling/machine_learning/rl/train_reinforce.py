from __future__ import annotations
import torch

from ..datasets.spectra_dataset import bin_spectrum

def bin_masses(masses, n_bins, mz_min, mz_max, device):
    if len(masses) == 0:
        return torch.zeros(n_bins, device=device)
    peaks = torch.tensor([[m, 1.0] for m in masses], device=device)
    return bin_spectrum(peaks, n_bins, mz_min, mz_max, intensity_norm="sum")

def reinforce_forward_env(
    env,
    adapter,
    policy,
    optimizer,
    gamma=0.99,
    episodes=1000,
    device="cpu",
    entropy_beta=0.01
    ) -> None:

    policy.to(device)
    policy.train()

    for ep in range(1, episodes + 1):
        if env.state is None:
            raise RuntimeError("Call env.reset(...) before training loop.")

        logps, vals, rewards, entrs = [], [], [], []
        done = False

        while not done:
            # Build action set
            actions = env.available_actions()
            if not actions:
                done = True
                break

            # [1, n_bins] inputs — adapt to your env (pred/target bins)
            pred = env.simulate_bins_from_frags().unsqueeze(0)   # or from obs if you return it
            targ = env.target_bins.unsqueeze(0)

            # Precompute per-action simulated bins [1, A, n_bins]
            a_bins = []
            for key in actions:
                masses = adapter.preview_masses(key, env.state)  # expects DGState
                a_bins.append(bin_masses(masses, env.n_bins, env.mz_min, env.mz_max, device))
            a_bins = torch.stack(a_bins, dim=0).unsqueeze(0)  # [1, A, n_bins]

            logits, value = policy(pred, targ, env.depth, a_bins)  # -> [1,A], [1]
            probs = torch.softmax(logits[0], dim=-1)
            dist  = torch.distributions.Categorical(probs)
            a_idx = dist.sample()
            logp  = dist.log_prob(a_idx)
            entr  = dist.entropy()  # entropy of chosen action (or dist.entropy().mean())

            # step with the selected *key*
            key = actions[a_idx.item()]
            _state, reward, done, info = env.step(key)
            print(info)

            logps.append(logp)
            vals.append(value.squeeze(-1).squeeze(0))
            rewards.append(float(reward))
            entrs.append(entr)

        # ---- returns / advantage ----
        if not rewards:
            continue

        with torch.no_grad():
            ret = 0.0
            returns = []
            for r in reversed(rewards):
                ret = r + gamma * ret
                returns.append(ret)
            returns.reverse()

        returns_t = torch.tensor(returns, device=device, dtype=torch.float32)
        values_t  = torch.stack(vals).to(device, dtype=torch.float32)
        logps_t   = torch.stack(logps).to(device, dtype=torch.float32)
        entrs_t   = torch.stack(entrs).to(device, dtype=torch.float32)

        adv = returns_t - values_t.detach()

        # SAFE normalization (no warning with N=1)
        if adv.numel() > 1:
            var, mean = torch.var_mean(adv, unbiased=False)
            adv = (adv - mean) / (var.sqrt() + 1e-8)
        else:
            # With a single step, just center to zero so policy loss doesn't blow up
            adv = adv * 0.0

        # ---- losses ----
        policy_loss = -(adv * logps_t).mean()
        value_loss  = torch.nn.functional.mse_loss(values_t, returns_t)
        entropy     = entrs_t.mean()
        loss = policy_loss + 0.5 * value_loss - entropy_beta * entropy

        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(policy.parameters(), 1.0)
        optimizer.step()

        if ep % 10 == 0:
            print(f"[RL] ep={ep:04d} steps={len(rewards):02d} "
                f"return={sum(rewards):.4f} loss={loss.item():.4f} "
                f"pi={policy_loss.item():.4f} v={value_loss.item():.4f} H={entropy.item():.4f}")


def reinforce_backward_env(
    env,
    adapter,              # kept for signature parity; not used (env handles previews)
    policy,
    optimizer,
    gamma: float = 0.99,
    episodes: int = 1000,
    device: str = "cpu",
    entropy_beta: float = 0.01,
) -> None:
    """
    Train `policy` on a BackwardMolEnv using REINFORCE (actor-critic with value baseline).

    Expects:
      - env.reset(seed) -> state (with `.steps`)
      - env.available_actions() -> List[int]
      - env.preview_action_bins(keys) -> Tensor[1, A, n_bins]
      - env.pred_bins, env.target_bins -> Tensor[n_bins]
      - env.step(key) -> (state, reward: float, done: bool, info: dict)
      - policy(pred[1,n], targ[1,n], depth, a_bins[1,A,n]) -> (logits[1,A], value[1,1])
    """
    policy.to(device)
    policy.train()

    for ep in range(1, episodes + 1):
        state = env.reset(seed=None)
        logps, vals, rewards, entrs = [], [], [], []
        done = False

        while not done:
            action_keys = env.available_actions()  # List[int]
            if not action_keys:
                break

            # Build inputs
            pred = env.pred_bins.unsqueeze(0)   # [1, n_bins]
            targ = env.target_bins.unsqueeze(0) # [1, n_bins]
            a_bins = env.preview_action_bins(action_keys)  # [1, A, n_bins]

            # Forward policy
            logits, value = policy(pred, targ, state.steps, a_bins)  # [1,A], [1,1]
            probs = torch.softmax(logits[0], dim=-1)                 # [A]
            dist  = torch.distributions.Categorical(probs)

            a_idx = dist.sample()                 # scalar
            logp  = dist.log_prob(a_idx)          # []
            entr  = dist.entropy().mean()         # scalar entropy (encourage exploration)

            key = action_keys[a_idx.item()]
            state, reward, done, info = env.step(key)

            # Track per-step tensors (keep shapes scalar for clean stacking)
            logps.append(logp)
            vals.append(value.squeeze(-1).squeeze(0))  # [] with grad
            rewards.append(float(reward))
            entrs.append(entr)

        # Skip empty episodes
        if not rewards:
            continue

        # ----- returns & advantage -----
        with torch.no_grad():
            ret = 0.0
            returns = []
            for r in reversed(rewards):
                ret = r + gamma * ret
                returns.append(ret)
            returns.reverse()

        returns_t = torch.tensor(returns, device=device, dtype=torch.float32)       # [T]
        values_t  = torch.stack(vals).to(device, dtype=torch.float32)               # [T]
        logps_t   = torch.stack(logps).to(device, dtype=torch.float32)              # [T]
        entrs_t   = torch.stack(entrs).to(device, dtype=torch.float32)              # [T]

        adv = returns_t - values_t.detach()                                         # [T]

        # Safe normalization (avoid std warning when T == 1)
        if adv.numel() > 1:
            var, mean = torch.var_mean(adv, unbiased=False)
            adv = (adv - mean) / (var.sqrt() + 1e-8)
        else:
            adv = adv * 0.0

        # ----- losses -----
        policy_loss = -(adv * logps_t).mean()
        value_loss  = torch.nn.functional.mse_loss(values_t, returns_t)
        entropy     = entrs_t.mean()
        loss = policy_loss + 0.5 * value_loss - entropy_beta * entropy

        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(policy.parameters(), 1.0)
        optimizer.step()

        if ep % 10 == 0:
            print(
                f"[BWD-RL] ep={ep:04d} steps={len(rewards):02d} "
                f"return={sum(rewards):.4f} loss={loss.item():.4f} "
                f"pi={policy_loss.item():.4f} v={value_loss.item():.4f} H={entropy.item():.4f}"
            )
