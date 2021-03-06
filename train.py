#coding: utf-8

import os
import random
import torch
import numpy as np

from ddpg import DDPG
from ounoise import OUNoise
from replay_memory import ReplayMemory, Transition
import wechat_jump_android as env

SEED = 1
NOISE_SCALE = 1
BATCH_SIZE = 16
REPLAY_SIZE = 10000
NUM_EPISODES = 10000
GAMMA = 0.98
TAU = 0.001
UPDATES_PER_STEP = 1

torch.manual_seed(SEED)
np.random.seed(SEED)
random.seed(SEED)


def main():
    ddpg = DDPG(GAMMA, TAU, torch.cuda.is_available())
    memory = ReplayMemory(REPLAY_SIZE)
    env.init_state()

    if os.path.exists('models/ddpg_actor_'):
        ddpg.load_model()

    updates = 0
    for i_episode in range(NUM_EPISODES):
        while True:
            ounoise = OUNoise(1, scale=NOISE_SCALE - NOISE_SCALE // NUM_EPISODES * i_episode)
            action = ddpg.select_action(env.state, ounoise)
            transition = env.step(action)
            memory.push(transition)

            if len(memory) > BATCH_SIZE:
                for _ in range(UPDATES_PER_STEP):
                    transitions = memory.sample(BATCH_SIZE)
                    random.shuffle(transitions)

                    batch = Transition(*zip(*transitions))
                    value_loss, policy_loss = ddpg.update_parameters(batch)

                    print(
                        "Episode: {}, Updates: {}, Value Loss: {}, Policy Loss: {}".
                        format(i_episode, updates, value_loss, policy_loss))
                    updates += 1

                break

        if (i_episode + 1) % 100 == 0:
            ddpg.save_model()

if __name__ == "__main__":
    main()
