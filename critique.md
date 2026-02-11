# Critique and Suggestions for Dove vs Hawk Simulation


### Bug and Edge Case Handling

- **Division by zero risk.** On line 364, `sum(hist)` could be zero if both populations
  die out. This would crash the program. Add a guard:
  ```python
  dove_avg = round(np.mean([hist[0]/sum(hist) for hist in blob_history[1:] if sum(hist) > 0]), 3)
  ```

- **The FIXME on line 262.** There is a known issue flagged in a comment where
  `blob["food"]` can be `None`, leading to a `TypeError`. This happens when a blob does
  not successfully pick food but the movement code still tries to access its food
  position. The fix is to guard the movement block with a check that `blob["food"]` is
  not `None`, or to make sure only blobs that successfully picked food enter the movement
  phase.

- **Hawk vs Hawk payoff line 338.** The line `random.randint(1, 1) == 2` will always be
  `False` because `randint(1, 1)` always returns 1. This means hawks always die when
  fighting another hawk. That matches the 0% survival label, so it is technically correct
  for the default case, but the expression is confusing. Writing `hawks += 0` directly
  or using a clearer boolean would be more readable.



### Payoff Matrix Accuracy

The video describes specific payoffs:
- Dove vs Dove: each gets 1 food
- Dove vs Hawk: dove gets 0.5 food, hawk gets 1.5 food
- Hawk vs Hawk: each gets 0 food (in the default case)

The code implements these through survival and reproduction probabilities rather than
direct food scores, which is a valid approach. However, the mapping is not spelled out
anywhere. Adding a payoff matrix as a constant or a comment at the top of the file would
make it much easier to verify correctness and to change the payoffs later.

Something like:

```python
# Payoff matrix (food received):
#              Dove    Hawk
# Dove         1.0     0.5
# Hawk         1.5     0.0
#
# Survival rules:
# 0 food    -> dies
# 0.5 food  -> 50% chance of survival
# 1.0 food  -> survives
# 1.5 food  -> survives + 50% chance of reproduction
# 2.0 food  -> survives + reproduces
```

### Code Style

- **Magic numbers.** Values like `25`, `35`, `5`, `10`, and `100` appear throughout the
  code without explanation. These should be named constants.

---

## Next Steps Beyond the Game of Chicken

The video itself lays out a roadmap for where to take this simulation next. Here are
concrete ideas, ordered from most approachable to most ambitious.

### 1. Nash Equilibrium Calculator

The video walks through calculating the equilibrium fraction of doves analytically.
The simulation currently lets you observe the equilibrium emerge, but it does not calculate
or display the theoretical prediction. Adding this would be a great learning feature.

The math works like this. Let d be the fraction of doves in the population. The expected
payoff for a dove is:

    E(dove) = d * 1.0 + (1 - d) * 0.5

The expected payoff for a hawk is:

    E(hawk) = d * 1.5 + (1 - d) * 0.0

Setting these equal (the Nash equilibrium condition):

    d * 1.0 + (1 - d) * 0.5 = d * 1.5 + (1 - d) * 0.0
    d + 0.5 - 0.5d = 1.5d
    0.5d + 0.5 = 1.5d
    0.5 = d

So the equilibrium is at 50% doves, which matches the simulation. But if you change the
hawk-vs-hawk payoff to 0.25 (as the video suggests), the equilibrium shifts to about
33% doves. The simulation should calculate this automatically from whatever payoff matrix
is configured and display it as a reference line on the population chart.

Here is a simple function that does it:

```python
def calculate_nash_equilibrium(payoff_matrix):
    """
    payoff_matrix format:
    {
        'dove_vs_dove': (1.0, 1.0),
        'dove_vs_hawk': (0.5, 1.5),
        'hawk_vs_hawk': (0.0, 0.0)
    }
    Returns the equilibrium fraction of doves, or None if no mixed equilibrium exists.
    """
    dd = payoff_matrix['dove_vs_dove'][0]  # dove payoff when facing dove
    dh = payoff_matrix['dove_vs_hawk'][0]  # dove payoff when facing hawk
    hd = payoff_matrix['dove_vs_hawk'][1]  # hawk payoff when facing dove
    hh = payoff_matrix['hawk_vs_hawk'][0]  # hawk payoff when facing hawk

    # E(dove) = d * dd + (1-d) * dh
    # E(hawk) = d * hd + (1-d) * hh
    # Setting equal and solving for d:
    # d * dd + dh - d * dh = d * hd + hh - d * hh
    # d * (dd - dh - hd + hh) = hh - dh
    denominator = dd - dh - hd + hh
    if denominator == 0:
        return None  # no mixed equilibrium
    d = (hh - dh) / denominator
    if 0 < d < 1:
        return d
    return None  # equilibrium is a pure strategy (all dove or all hawk)
```

### 2. Configurable Payoff Matrix via UI

Instead of editing commented-out lines in the source code, let users adjust the payoff
matrix through the UI. This could be as simple as number input fields on the side panel
or keyboard shortcuts to increment and decrement payoff values. This ties directly into
the Nash equilibrium calculator since changing the payoffs would automatically update the
predicted equilibrium line on the chart.

### 3. Mixed Strategies

The video mentions that real creatures do not strictly play one strategy. Instead,
they might have a probability of playing hawk or dove in any given encounter. This is
called a mixed strategy. To implement this:

- Give each blob a `hawk_probability` gene (a float between 0 and 1).
- When two blobs meet at food, each one flips a weighted coin based on their gene to
  decide whether to play hawk or dove for that encounter.
- Offspring inherit their parent's `hawk_probability` with a small random mutation.
- Over time, you would expect the population's average `hawk_probability` to converge
  toward the Nash equilibrium mixed strategy.

This is a much more realistic model of evolution and would produce smoother convergence
curves than the current all-or-nothing approach.

### 4. Conditional Strategies (Tit for Tat, Retaliator, Bully)

The video teases strategies that adjust behavior based on the opponent:

- **Retaliator:** Acts like a dove by default, but fights back if the opponent plays hawk.
- **Bully:** Threatens like a hawk, but backs down if the opponent fights back.
- **Bourgeois:** Plays hawk if it arrived at the food first (territory owner), dove if it
  arrived second (intruder).

Adding these would require giving blobs memory or conditional logic, and it opens the door
to studying evolutionarily stable strategies (ESS), which is a core concept in evolutionary
game theory.

### 5. Asymmetric Conflicts

The video mentions that most real conflicts are asymmetric. Creatures differ in size,
strength, or how much they value the resource. To model this:

- Give blobs a `strength` attribute that affects the outcome of hawk-vs-hawk fights.
- Vary the food value so some pairs are worth more than others.
- Introduce territory ownership where incumbents have home-field advantage.

This leads to understanding dominance hierarchies and territorial behavior, which are
observations we see across animal species.

### 6. The Prisoners Dilemma and Iterated Games

The video explains that when the hawk-vs-hawk payoff gets high enough (meaning
fighting is not very costly), the game becomes a Prisoners Dilemma where defecting (playing
hawk) always dominates, even though mutual cooperation (both playing dove) would be better
for everyone.

To explore this:

- Allow creatures to encounter the same opponent multiple times (iterated games).
- Implement strategies with memory, like Tit for Tat (cooperate first, then copy what the
  opponent did last time).
- Run tournaments between different strategies to see which ones dominate over time.

Robert Axelrod's famous tournament showed that Tit for Tat, a simple cooperative strategy,
outperformed more complex and aggressive strategies in iterated Prisoners Dilemma games.
Simulating this would be a natural and fascinating extension of the current project.

### 7. Replicator Dynamics (Continuous Model)

Instead of running discrete agent-based simulations, implement the replicator equation
from evolutionary game theory:

    dx/dt = x * (f(x) - average_fitness)

where x is the proportion of a strategy and f(x) is its fitness given the current
population mix. This gives you smooth, deterministic trajectories that you can compare
against the noisy simulation results. Plotting both on the same chart would really
demonstrate how the math predicts the emergent behavior.

---
