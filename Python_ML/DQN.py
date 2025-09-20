#created based on code from https://www.geeksforgeeks.org/a-beginners-guide-to-deep-reinforcement-learning/
#had to be corrected for errors

import numpy as np
import tensorflow as tf

class recommendation_model(tf.keras.Model):
	def __init__(self, num_inputs, num_actions, 
			learning_rate = 0.001, 
			discount_factor = 0.99, exploration_prob = 1.0, 
			exploration_decay = 0.995, min_exploration_prob = 0.05):
		super(DQN, self).__init__()
		self.dense1 = tf.keras.layers.Dense(num_inputs, activation='relu') # first hidden layer / input layer
		self.dense2 = tf.keras.layers.Dense(24, activation='relu') # second hidden layer
		self.output_layer = tf.keras.layers.Dense(num_actions, activation='linear') # output layer

		self.loss_fn = tf.keras.losses.MeanSquaredError() #loss function
		self.optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate) #optimizer

		self.discount_factor = discount_factor
		self.exploration_prob = exploration_prob
		self.exploration_decay = exploration_decay
		self.min_exploration_prob = min_exploration_prob

	def call(self, inputs):
		x = self.dense1(inputs) #run inputs to input layer
		x = self.dense2(x) #run first layer to second layer
		return self.output_layer(x) #run second layer to output layer
	
	def make_decision(self, input_vector):
		action = np.argmax(self(input_vector[np.newaxis, :]))
		return action
	
	def update_qvals(self, last_action, reward, last_input_vector, next_input_vector):
		with tf.GradientTape() as tape:
			current_q_values = self(last_input_vector[np.newaxis, :])
			next_q_values = self(next_input_vector[np.newaxis, :])
			max_next_q = tf.reduce_max(next_q_values, axis=-1)
			target_q_values = current_q_values.numpy()
			target_q_values[0, last_action] = reward + self.discount_factor * max_next_q
			loss = self.loss_fn(current_q_values, target_q_values)

		gradients = tape.gradient(loss, self.trainable_variables)
		self.optimizer.apply_gradients(zip(gradients, self.trainable_variables))