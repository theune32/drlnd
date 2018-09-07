# DRLND Navigation Project

### Introduction
This project tries to solve the Banana exercise. The goal of the exercise is to obtain as many yellow bananas without picking up blue bananas.
An episode consists of 300 steps, in an episode a yellow banana gices a +1 reward, a blue banane a -1 reward.
The state description consists of 37 values, velocity + rays.

The exercise is considered solved when the average reward over 100 episodes is 13.0 or higher.

### Learnig Algorithm
The algorithm used was based on the Lunar Lander exercise.
The agent itself in agent_dqn.py and uses the network architecture from qn_model.py

The model consists of 2 hidden layers both containing 64 units and ReLu acitvation.

The following hyperparameters are used:
BUFFER_SIZE = 1e5  	# replay buffer size
BATCH_SIZE = 64         # minibatch size
GAMMA = 0.99            # discount factor
TAU = 1e-3              # for soft update of target parameters
LR = 5e-4               # learning rate 
UPDATE_EVERY = 4        # how often to update the network

### Results
After 592 episodes the algorithm reached an average score of 13.0. See the below plot:
![scores plot](navigation_result.png)

### Future Work
For further improvements it would be interesting to take a look at the network architecture and see if there optimalisations there.
At first the size and or layers would be changed but also looking at adding a RNN part to the network might help since previous input might help determine better paths.

For improving the results on the current exercise the next steps would be implmenting [rainbow](https://arxiv.org/abs/1710.02298).

Some other interesting research would be to use real visual input (instead of rays)  and/or extending the rays since they seem limited in how far they detect the banananas.
Also adding a RNN part to the network might improve the results, the key idea would be that previous input for the agent can later be used to determine better paths for bananas no longer in view.
