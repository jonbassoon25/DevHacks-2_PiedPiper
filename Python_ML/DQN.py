#created based on code from https://www.geeksforgeeks.org/a-beginners-guide-to-deep-reinforcement-learning/
#had to be corrected for errors

import numpy as np
import tensorflow as tf
import keras
import sys, os, random
import joblib

INPUT_COUNT = 499

@keras.saving.register_keras_serializable()
class recommendation_model(tf.keras.Model):
	def __init__(self, num_inputs = INPUT_COUNT, num_actions = 2, 
			learning_rate = 0.001, exploration_prob = 1.0, 
			exploration_decay = 0.995, min_exploration_prob = 0.05, **kwargs):
		super(recommendation_model, self).__init__(**kwargs)
		self.dense1 = tf.keras.layers.Dense(num_inputs, activation='relu') # first hidden layer / input layer
		self.dense2 = tf.keras.layers.Dense(24, activation='relu') # second hidden layer
		self.output_layer = tf.keras.layers.Dense(num_actions, activation='linear') # output layer

		self.loss_fn = tf.keras.losses.MeanSquaredError() #loss function
		self.optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate) #optimizer

		self.exploration_prob = exploration_prob
		self.exploration_decay = exploration_decay
		self.min_exploration_prob = min_exploration_prob

	def call(self, inputs):
		x = self.dense1(inputs) #run inputs to input layer
		x = self.dense2(x) #run first layer to second layer
		return self.output_layer(x) #run second layer to output layer
	
	def make_decision(self, input_vector):
		if (random.random() > self.exploration_prob):
			action = np.argmax(self(input_vector[np.newaxis, :]))
		else:
			action = random.random() < 0.6
		return action
	
	def update_qvals(self, last_action, reward, last_input_vector):
		with tf.GradientTape() as tape:
			current_q_values = self(last_input_vector[np.newaxis, :])
			target_q_values = current_q_values.numpy()
			target_q_values[0, last_action] = reward
			loss = self.loss_fn(current_q_values, target_q_values)

		gradients = tape.gradient(loss, self.trainable_variables)
		self.optimizer.apply_gradients(zip(gradients, self.trainable_variables))

		self.exploration_prob = max(self.exploration_prob * self.exploration_decay, self.min_exploration_prob)


# Run the python module & load the network and other stuff
model_path = sys.argv[1]
run_arg = sys.argv[2]


location_vectors = np.load("./Python_ML/location_vectors.npy")

model = None
if os.path.exists(model_path):
	try:
		model = joblib.load(model_path)
	except:
		model = recommendation_model()
else:
	model = recommendation_model()

# Get inputs or update q vals
if (run_arg == '-d'):
	# Decide: -d index-int -> str(keep, next)
	input_vector_index = int(sys.argv[3])
	input_vector = location_vectors[input_vector_index]
	decision = model.make_decision(input_vector)
	print("keep" if decision else "next")
elif (run_arg == '-u'):
	# Update: -u index-int decision-str reward-0/1 -> None
	input_vector_index = int(sys.argv[3])
	last_decision = sys.argv[4]
	reward = sys.argv[5]
	input_vector = location_vectors[input_vector_index]
	last_decision = 1 if last_decision == "keep" else 0

	model.update_qvals(last_decision, reward, input_vector)

	joblib.dump(model, model_path)

sys.stdout.flush()
