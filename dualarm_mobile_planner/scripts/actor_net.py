import numpy as np
import tensorflow
import math

LEARNING_RATE = 0.0001
BATCH_SIZE = 64
TAU = 0.001
class ActorNet:
    """ Actor Network Model of DDPG Algorithm """
    
    def __init__(self,num_states,num_actions):
        self.g=tensorflow.Graph()
        with self.g.as_default():
            self.sess = tensorflow.InteractiveSession()
            
           
            #actor network model parameters:
            self.W1_a, self.B1_a, self.W2_a, self.B2_a, self.W3_a, self.B3_a,\
            self.actor_state_in, self.actor_model = self.create_actor_net(num_states, num_actions)
            
                                   
            #target actor network model parameters:
            self.t_W1_a, self.t_B1_a, self.t_W2_a, self.t_B2_a, self.t_W3_a, self.t_B3_a,\
            self.t_actor_state_in, self.t_actor_model = self.create_actor_net(num_states, num_actions)
            
            #cost of actor network:
            self.q_gradient_input = tensorflow.placeholder("float",[None,num_actions]) #gets input from action_gradient computed in critic network file
            self.actor_parameters = [self.W1_a, self.B1_a, self.W2_a, self.B2_a, self.W3_a, self.B3_a]
            self.parameters_gradients = tensorflow.gradients(self.actor_model,self.actor_parameters,-self.q_gradient_input)#/BATCH_SIZE) 
            self.optimizer = tensorflow.train.AdamOptimizer(LEARNING_RATE).apply_gradients(zip(self.parameters_gradients,self.actor_parameters))  
            #initialize all tensor variable parameters:
            self.sess.run(tensorflow.initialize_all_variables())    
            
            #To make sure actor and target have same intial parmameters copy the parameters:
            # copy target parameters
            self.sess.run([
				self.t_W1_a.assign(self.W1_a),
				self.t_B1_a.assign(self.B1_a),
				self.t_W2_a.assign(self.W2_a),
				self.t_B2_a.assign(self.B2_a),
				self.t_W3_a.assign(self.W3_a),
				self.t_B3_a.assign(self.B3_a)])

            self.update_target_actor_op = [
                self.t_W1_a.assign(TAU*self.W1_a+(1-TAU)*self.t_W1_a),
                self.t_B1_a.assign(TAU*self.B1_a+(1-TAU)*self.t_B1_a),
                self.t_W2_a.assign(TAU*self.W2_a+(1-TAU)*self.t_W2_a),
                self.t_B2_a.assign(TAU*self.B2_a+(1-TAU)*self.t_B2_a),
                self.t_W3_a.assign(TAU*self.W3_a+(1-TAU)*self.t_W3_a),
                self.t_B3_a.assign(TAU*self.B3_a+(1-TAU)*self.t_B3_a)]

            self.saver = tensorflow.train.Saver()
        


    def create_actor_net(self, num_states=60, num_actions=3):
        """ Network that takes states and return action """
        N_HIDDEN_1 = 400
        N_HIDDEN_2 = 300
        actor_state_in = tensorflow.placeholder("float",[None,num_states])    
        W1_a=tensorflow.Variable(tensorflow.random_uniform([num_states,N_HIDDEN_1],-1/math.sqrt(num_states),1/math.sqrt(num_states)))
        B1_a=tensorflow.Variable(tensorflow.random_uniform([N_HIDDEN_1],-1/math.sqrt(num_states),1/math.sqrt(num_states)))
        W2_a=tensorflow.Variable(tensorflow.random_uniform([N_HIDDEN_1,N_HIDDEN_2],-1/math.sqrt(N_HIDDEN_1),1/math.sqrt(N_HIDDEN_1)))
        B2_a=tensorflow.Variable(tensorflow.random_uniform([N_HIDDEN_2],-1/math.sqrt(N_HIDDEN_1),1/math.sqrt(N_HIDDEN_1)))
        W3_a=tensorflow.Variable(tensorflow.random_uniform([N_HIDDEN_2,num_actions],-0.003,0.003))
        B3_a=tensorflow.Variable(tensorflow.random_uniform([num_actions],-0.003,0.003))
    
        H1_a=tensorflow.nn.softplus(tensorflow.matmul(actor_state_in,W1_a)+B1_a)
        # H2_a=tensorflow.nn.tanh(tensorflow.matmul(H1_a,W2_a)+B2_a)
        H2_a=tensorflow.nn.softplus(tensorflow.matmul(H1_a,W2_a)+B2_a)
        actor_model=tensorflow.nn.tanh(tensorflow.matmul(H2_a,W3_a) + B3_a)
        return W1_a, B1_a, W2_a, B2_a, W3_a, B3_a, actor_state_in, actor_model
        
    def evaluate_actor(self,state_t):
        return self.sess.run(self.actor_model, feed_dict={self.actor_state_in:state_t})        
        
        
    def evaluate_target_actor(self,state_t_1):
        return self.sess.run(self.t_actor_model, feed_dict={self.t_actor_state_in: state_t_1})
        
    def train_actor(self,actor_state_in,q_gradient_input):
        self.sess.run(self.optimizer, feed_dict={ self.actor_state_in: actor_state_in, self.q_gradient_input: q_gradient_input})
    
    def update_target_actor(self):
        self.sess.run(self.update_target_actor_op)    
    
    def save_actor(self, save_path):
        save_path = self.saver.save(self.sess, save_path)
    
    def load_actor(self, save_path):
        self.saver.restore(self.sess, save_path)
        