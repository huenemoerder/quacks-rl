from quacks_env_colorful import *
from random_policy import *
#from q_policy import *
import os
import tempfile

import numpy as np
import tensorflow as tf

from tf_agents.agents.dqn import dqn_agent
from tf_agents.environments import suite_gym
from tf_agents.environments import tf_py_environment
from tf_agents.eval import metric_utils
from tf_agents.metrics import tf_metrics
from tf_agents.networks import sequential
from tf_agents.policies import random_tf_policy
from tf_agents.policies import tf_policy
from tf_agents.policies import actor_policy
from tf_agents.policies import q_policy
from tf_agents.policies import greedy_policy
from tf_agents.replay_buffers import tf_uniform_replay_buffer
from tf_agents.trajectories import trajectory
from tf_agents.specs import tensor_spec
from tf_agents.utils import common

import pickle

#tempdir = os.getenv("TEST_TMPDIR", tempfile.gettempdir())

global_step = tf.compat.v1.train.get_or_create_global_step()

# Hyperparameters

num_iterations = 500000 # @param {type:"integer"}

initial_collect_steps = 500  # @param {type:"integer"} 
collect_steps_per_iteration = 1  # @param {type:"integer"}
replay_buffer_max_length = 100000  # @param {type:"integer"}

batch_size = 64  # @param {type:"integer"}
learning_rate = 1e-4  # @param {type:"number"}
log_interval = 200  # @param {type:"integer"}

num_eval_episodes = 20  # @param {type:"integer"}
eval_interval = 1000  # @param {type:"integer"}


env = QuacksEnv()

# print('Observation Spec:')
# print(env.time_step_spec().observation)

# print('Reward Spec:')
# print(env.time_step_spec().reward)

# print('Action Spec:')
# print(env.action_spec())

# convert python environment to TensorFlow using the TFPyEnvironment wrapper.
# The original environment's API uses Numpy arrays. The TFPyEnvironment converts 
# these to Tensors to make it compatible with Tensorflow agents and policies.
train_env = tf_py_environment.TFPyEnvironment(env)
eval_env = tf_py_environment.TFPyEnvironment(env)

#DQN Agent is a QNetwork, a neural network model that can learn to predict QValues (expected returns)
# for all actions, given an observation from the environment.
# using tf_agents.networks. to create a QNetwork. The network will consist of a sequence of 
# tf.keras.layers.Dense layers, where the final layer will have 1 output for each possible action.

fc_layer_params = (150, 75)
action_tensor_spec = tensor_spec.from_spec(env.action_spec())
num_actions = action_tensor_spec.maximum - action_tensor_spec.minimum + 1

# Define a helper function to create Dense layers configured with the right
# activation and kernel initializer.
def dense_layer(num_units):
  return tf.keras.layers.Dense(
      num_units,
      activation=tf.keras.activations.relu,
      kernel_initializer=tf.keras.initializers.VarianceScaling(
          scale=2.0, mode='fan_in', distribution='truncated_normal'))

# QNetwork consists of a sequence of Dense layers followed by a dense layer
# with `num_actions` units to generate one q_value per available action as
# it's output.
dense_layers = [dense_layer(num_units) for num_units in fc_layer_params]
q_values_layer = tf.keras.layers.Dense(
    num_actions,
    activation=None,
    kernel_initializer=tf.keras.initializers.RandomUniform(
        minval=-0.03, maxval=0.03),
    bias_initializer=tf.keras.initializers.Constant(-0.2))
    
q_net = sequential.Sequential(dense_layers + [q_values_layer])


def splitter(obs):
    return obs["observation"], obs["legal_moves"]

# Now using tf_agents.agents.dqn.dqn_agent to instantiate a DqnAgent.
# In addition to the time_step_spec, action_spec and the QNetwork, the agent constructor 
# also requires an optimizer (in this case, AdamOptimizer), a loss function, and an integer step counter.

optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)

global_step = tf.compat.v1.train.get_or_create_global_step()
train_step_counter = global_step

agent = dqn_agent.DdqnAgent(
    train_env.time_step_spec(),
    train_env.action_spec(),
    q_network=q_net,
    optimizer=optimizer,
    td_errors_loss_fn=common.element_wise_squared_loss,
    train_step_counter=train_step_counter,
    observation_and_action_constraint_splitter=splitter)

agent.initialize()


# # Policies
# Agents contain two policies:
# agent.policy — The main policy that is used for evaluation and deployment.
# agent.collect_policy — A second policy that is used for data collection.
eval_policy = agent.policy
collect_policy = agent.collect_policy

def compute_avg_return(environment, policy, num_episodes=10):

  total_return = 0.0
  for i in range(num_episodes):
    #print('here')
    #set_random_seed(i)
    time_step = environment.reset()
    episode_return = 0.0

    while not time_step.is_last():
      action_step = policy.action(time_step)
      #print(action_step)
      time_step = environment.step(action_step.action)
      episode_return += time_step.reward
    total_return += episode_return
    

  avg_return = total_return / num_episodes
  return avg_return.numpy()[0]

def get_games(agent, enviroment, seedmax=100):
    returns = []
    game_vp = []
    for seed in range(seedmax):
        set_random_seed(seed)
        episode_reward = 0
        step = 0
        time_step = enviroment.reset()
        # Collect a few steps using collect_policy and save to the replay buffer.
            # collect_data(train_env, agent.policy, replay_buffer, collect_steps_per_iteration)
        while not time_step.is_last():
            action_step = agent.policy.action(time_step)
            time_step = enviroment.step(action_step.action)
            step += 1
            if step // 1000: print(f"{step} actions taken in this episode.")
            episode_reward += time_step.reward
            # Sample a batch of data from the buffer and update the agent's network.

        # experience, unused_info = next(iterator)
        # do not update the agents network but instead get the
        # train_loss = agent.train(experience).loss
        round_return = episode_reward

        returns.append(round_return)
        game_vp.append(get_state()["player_info"]["total_vp"])
    return game_vp

#Replay Buffer
#The replay buffer keeps track of data collected from the environment.

replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(
    data_spec=agent.collect_data_spec,
    batch_size=train_env.batch_size,
    max_length=replay_buffer_max_length)


#agent.collect_data_spec

#agent.collect_data_spec._fields

#Checkpointer to save the data & restore saved data

checkpoint_dir = './checkpoints_colorful_ddqn_last_final/'
train_checkpointer = common.Checkpointer(
    ckpt_dir=checkpoint_dir,
    max_to_keep=100, # remove any other if there are any older checkpoints
    # the rest are optional kwargs of the items to include in the checkpoint
    agent=agent,
    policy=agent.policy,
    replay_buffer=replay_buffer,
    global_step=global_step
)

#train_checkpointer.initialize_or_restore()

#Data Collection 
#data collection with provided policy in the environment for a few steps, recording the data in the replay buffer.
#@test {"skip": true}
def collect_step(environment, policy, buffer):
  time_step = environment.current_time_step()
  action_step = policy.action(time_step)
  #print(action_step)
  next_time_step = environment.step(action_step.action)
  traj = trajectory.from_transition(time_step, action_step, next_time_step)

  # Add trajectory to the replay buffer
  buffer.add_batch(traj)

def collect_data(env, policy, buffer, steps):
  for _ in range(steps):
    collect_step(env, policy, buffer)
    
my_random_policy = random_tf_policy.RandomTFPolicy(train_env.time_step_spec(), train_env.action_spec(), observation_and_action_constraint_splitter=splitter)

collect_data(train_env, my_random_policy, replay_buffer, initial_collect_steps)
# collect_data(train_env, my_q_policy, replay_buffer, initial_collect_steps)

returns = []
losses = []

mean_max = 0
avg_return_max = 0

#The agent needs access to the replay buffer. This is provided by creating 
# an iterable tf.data.Dataset pipeline which will feed data to the agent.

# Dataset generates trajectories with shape [Bx2x...]
dataset = replay_buffer.as_dataset(
    num_parallel_calls=3, 
    sample_batch_size=batch_size, 
    num_steps=2).prefetch(3)


dataset


iterator = iter(dataset)
# print(iterator)



# Training the agent
# Two things must happen during the training loop:
# 1.collect data from the environment
# 2.use that data to train the agent's neural network(s)

# #@test {"skip": true}
# try:
#    %%time
# except:
#   pass

# (Optional) Optimize by wrapping some of the code in a graph using TF function.
agent.train = common.function(agent.train)

# Reset the train step
agent.train_step_counter.assign(0)
train_checkpointer.initialize_or_restore()
global_step = tf.compat.v1.train.get_global_step()

# Evaluate the agent's policy once before training.
avg_return = compute_avg_return(eval_env, agent.policy, num_eval_episodes)
#returns = [avg_return]
print(avg_return)

for _ in range(num_iterations):
    # Collect a few steps using collect_policy and save to the replay buffer.
    collect_data(train_env, agent.collect_policy, replay_buffer, collect_steps_per_iteration)

    # Sample a batch of data from the buffer and update the agent's network.
    experience, unused_info = next(iterator)
    train_loss = agent.train(experience).loss

    step = agent.train_step_counter.numpy()

    if step % log_interval == 0:
        print('step = {0}: loss = {1}'.format(step, train_loss))
        losses.append(train_loss)

    if step % eval_interval == 0:
        avg_return = compute_avg_return(eval_env, agent.policy, num_eval_episodes)
        print('step = {0}: Average Return = {1}, Max = {2}'.format(step, avg_return, avg_return_max))
        returns.append(avg_return)
        
        pickle.dump(np.array(returns), open('results/ddqn_colorful_returns_last_final.pkl', 'wb'))
        pickle.dump(np.array(losses), open('results/ddqn_colorful_losses_last_final.pkl', 'wb'))
    
        if avg_return >= avg_return_max - 1: # to allow for less perfect on random games to also be evaluated
            print(avg_return)
            if avg_return > avg_return_max: 
                avg_return_max = avg_return

            game_vp = get_games(agent, eval_env, 100)
            mean = np.mean(game_vp)

            if mean > mean_max:
                mean_max = mean
                train_checkpointer.save(global_step)
                
                print(f'new highscore saved with mean {mean}')
            else:
                print(f'{mean} not good enough overall {mean_max}.')

train_checkpointer.save(global_step)

