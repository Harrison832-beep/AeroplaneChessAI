# Aeroplane Chess AI

This project implements a text-based Aeroplane chess game and experiments several AI agents, includes:
* Expectimax
* Monte Carlo Tree Search (MCTS)
* Q-Learning



## Results
Max depth = 3 for Expectimax agent

| **Blue Player Agent**          |**Green Player Agent**|**Wins(B:G, 100 Games)**|
| -------------------------------|----------------------|------------------------|
| Random Agent                   | Random Agent         | 51:49                  |
| Expectimax Agent               | Random Agent         | 73:27                  |
| Monte Carlo Agent              | Random Agent         | 58:42                  |
| Monte Carlo Agent (N=100)      | Random Agent         | 68:32                  |
| Q-Learning Agent (Epoch=1000)  | Random Agent         | 62:38                  |
**Table 1**: Blue agents vs. Green agents win ratio (100 games).


|**Agent Type**                |**Ave Decision Time (s)**|
|------------------------------|-------------------------|
| Random Agent                 | 0.00000                 |
| Expectimax Agent             | 0.07098                 |
| Monte Carlo Agent (N = 100)  | 2.31865                 |
| Q-Learning                   | 0.00135                 |
**Table 2**: Each agent's average running time for making decisions.




