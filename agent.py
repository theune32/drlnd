{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import numpy as np\n",
    "import random\n",
    "from collections import namedtuple, deque\n",
    "\n",
    "from model import QNetwork\n",
    "\n",
    "import torch\n",
    "import torch.nn.functional as F\n",
    "import torch.optim as optim\n",
    "\n",
    "BUFFER_SIZE = int(1e5)  # replay buffer size\n",
    "BATCH_SIZE = 64         # minibatch size\n",
    "GAMMA = 0.99            # discount factor\n",
    "TAU = 1e-3              # for soft update of target parameters\n",
    "LR = 5e-4               # learning rate \n",
    "UPDATE_EVERY = 4        # how often to update the network\n",
    "\n",
    "device = torch.device(\"cuda:0\" if torch.cuda.is_available() else \"cpu\")\n",
    "\n",
    "class Agent():\n",
    "    \"\"\"Interacts with and learns from the environment.\"\"\"\n",
    "\n",
    "    def __init__(self, state_size, action_size, seed):\n",
    "        \"\"\"Initialize an Agent object.\n",
    "        \n",
    "        Params\n",
    "        ======\n",
    "            state_size (int): dimension of each state\n",
    "            action_size (int): dimension of each action\n",
    "            seed (int): random seed\n",
    "        \"\"\"\n",
    "        self.state_size = state_size\n",
    "        self.action_size = action_size\n",
    "        self.seed = random.seed(seed)\n",
    "\n",
    "        # Q-Network\n",
    "        self.qnetwork_local = QNetwork(state_size, action_size, seed).to(device)\n",
    "        self.qnetwork_target = QNetwork(state_size, action_size, seed).to(device)\n",
    "        self.optimizer = optim.Adam(self.qnetwork_local.parameters(), lr=LR)\n",
    "\n",
    "        # Replay memory\n",
    "        self.memory = ReplayBuffer(action_size, BUFFER_SIZE, BATCH_SIZE, seed)\n",
    "        # Initialize time step (for updating every UPDATE_EVERY steps)\n",
    "        self.t_step = 0\n",
    "    \n",
    "    def step(self, state, action, reward, next_state, done):\n",
    "        # Save experience in replay memory\n",
    "        self.memory.add(state, action, reward, next_state, done)\n",
    "        \n",
    "        # Learn every UPDATE_EVERY time steps.\n",
    "        self.t_step = (self.t_step + 1) % UPDATE_EVERY\n",
    "        if self.t_step == 0:\n",
    "            # If enough samples are available in memory, get random subset and learn\n",
    "            if len(self.memory) > BATCH_SIZE:\n",
    "                experiences = self.memory.sample()\n",
    "                self.learn(experiences, GAMMA)\n",
    "\n",
    "    def act(self, state, eps=0.):\n",
    "        \"\"\"Returns actions for given state as per current policy.\n",
    "        \n",
    "        Params\n",
    "        ======\n",
    "            state (array_like): current state\n",
    "            eps (float): epsilon, for epsilon-greedy action selection\n",
    "        \"\"\"\n",
    "        state = torch.from_numpy(state).float().unsqueeze(0).to(device)\n",
    "        self.qnetwork_local.eval()\n",
    "        with torch.no_grad():\n",
    "            action_values = self.qnetwork_local(state)\n",
    "        self.qnetwork_local.train()\n",
    "\n",
    "        # Epsilon-greedy action selection\n",
    "        if random.random() > eps:\n",
    "            return np.argmax(action_values.cpu().data.numpy())\n",
    "        else:\n",
    "            return random.choice(np.arange(self.action_size))\n",
    "\n",
    "    def learn(self, experiences, gamma):\n",
    "        \"\"\"Update value parameters using given batch of experience tuples.\n",
    "\n",
    "        Params\n",
    "        ======\n",
    "            experiences (Tuple[torch.Variable]): tuple of (s, a, r, s', done) tuples \n",
    "            gamma (float): discount factor\n",
    "        \"\"\"\n",
    "        states, actions, rewards, next_states, dones = experiences\n",
    "\n",
    "        # Get max predicted Q values (for next states) from target model\n",
    "        Q_targets_next = self.qnetwork_target(next_states).detach().max(1)[0].unsqueeze(1)\n",
    "        # Compute Q targets for current states \n",
    "        Q_targets = rewards + (gamma * Q_targets_next * (1 - dones))\n",
    "\n",
    "        # Get expected Q values from local model\n",
    "        Q_expected = self.qnetwork_local(states).gather(1, actions)\n",
    "\n",
    "        # Compute loss\n",
    "        loss = F.mse_loss(Q_expected, Q_targets)\n",
    "        # Minimize the loss\n",
    "        self.optimizer.zero_grad()\n",
    "        loss.backward()\n",
    "        self.optimizer.step()\n",
    "\n",
    "        # ------------------- update target network ------------------- #\n",
    "        self.soft_update(self.qnetwork_local, self.qnetwork_target, TAU)                     \n",
    "\n",
    "    def soft_update(self, local_model, target_model, tau):\n",
    "        \"\"\"Soft update model parameters.\n",
    "        θ_target = τ*θ_local + (1 - τ)*θ_target\n",
    "\n",
    "        Params\n",
    "        ======\n",
    "            local_model (PyTorch model): weights will be copied from\n",
    "            target_model (PyTorch model): weights will be copied to\n",
    "            tau (float): interpolation parameter \n",
    "        \"\"\"\n",
    "        for target_param, local_param in zip(target_model.parameters(), local_model.parameters()):\n",
    "            target_param.data.copy_(tau*local_param.data + (1.0-tau)*target_param.data)\n",
    "\n",
    "\n",
    "class ReplayBuffer:\n",
    "    \"\"\"Fixed-size buffer to store experience tuples.\"\"\"\n",
    "\n",
    "    def __init__(self, action_size, buffer_size, batch_size, seed):\n",
    "        \"\"\"Initialize a ReplayBuffer object.\n",
    "\n",
    "        Params\n",
    "        ======\n",
    "            action_size (int): dimension of each action\n",
    "            buffer_size (int): maximum size of buffer\n",
    "            batch_size (int): size of each training batch\n",
    "            seed (int): random seed\n",
    "        \"\"\"\n",
    "        self.action_size = action_size\n",
    "        self.memory = deque(maxlen=buffer_size)  \n",
    "        self.batch_size = batch_size\n",
    "        self.experience = namedtuple(\"Experience\", field_names=[\"state\", \"action\", \"reward\", \"next_state\", \"done\"])\n",
    "        self.seed = random.seed(seed)\n",
    "    \n",
    "    def add(self, state, action, reward, next_state, done):\n",
    "        \"\"\"Add a new experience to memory.\"\"\"\n",
    "        e = self.experience(state, action, reward, next_state, done)\n",
    "        self.memory.append(e)\n",
    "    \n",
    "    def sample(self):\n",
    "        \"\"\"Randomly sample a batch of experiences from memory.\"\"\"\n",
    "        experiences = random.sample(self.memory, k=self.batch_size)\n",
    "\n",
    "        states = torch.from_numpy(np.vstack([e.state for e in experiences if e is not None])).float().to(device)\n",
    "        actions = torch.from_numpy(np.vstack([e.action for e in experiences if e is not None])).long().to(device)\n",
    "        rewards = torch.from_numpy(np.vstack([e.reward for e in experiences if e is not None])).float().to(device)\n",
    "        next_states = torch.from_numpy(np.vstack([e.next_state for e in experiences if e is not None])).float().to(device)\n",
    "        dones = torch.from_numpy(np.vstack([e.done for e in experiences if e is not None]).astype(np.uint8)).float().to(device)\n",
    "  \n",
    "        return (states, actions, rewards, next_states, dones)\n",
    "\n",
    "    def __len__(self):\n",
    "        \"\"\"Return the current size of internal memory.\"\"\"\n",
    "        return len(self.memory)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "drlnd",
   "language": "python",
   "name": "drlnd"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.6.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}