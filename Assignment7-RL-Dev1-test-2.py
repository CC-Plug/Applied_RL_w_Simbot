#!/usr/bin/python3

from pysimbotlib.core import PySimbotApp, Robot
from kivy.config import Config
from matplotlib import pyplot as plt1
from matplotlib import pyplot as plt2
# Force the program to show user's log only for "info" level or more. The info log will be disabled.
Config.set('kivy', 'log_level', 'info')

import random
import pandas as pd
#from sqlalchemy import create_engine
dataplot1 = []
dataplot2 = []

from random import seed
seed(100)

class RL_Robot(Robot):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        #self.engine = create_engine('sqlite:///Q_TableStream.db')

        '''
            Using 5 IR Sensors:
            - Front Sensor
            - Front-Right Sensor
            - Right Sensor
            - Left Sensor
            - Front-Left Sensor
            and 1 Smell Sensor
            - Smell Sensor
        '''
        self.num_sensor = 5
        self.smell_labels = ['F', 'L', 'R']
        self.state_dict = str()
        
        self.state_key = str()
        self.pre_state_key = str()
        self.pre_action = str()
        self.temp_eat = int()
        self.temp_eat = 0
        self.step = 0
        

        # Define all possible states of the robot
        # 2^5 * 3 = 96 states
        # Define all possible actions of the robot
        # 3 actions = Front, Left, Right
        # Then all Q values can be created as an array of all states and all actions
        state_index_list = list()
        for _ in range(2**self.num_sensor):
            # print("{0:05b}".format(_))
            for label in self.smell_labels:
                state_index_list.append("{0}{1:05b}".format(label,_))
        
        # print(state_index_list)
        
        self.Q_table = pd.DataFrame(
            {
                "Front" : [0] * (2**5 * 3),
                "Left" :  [0] * (2**5 * 3),
                "Right" : [0] * (2**5 * 3)
            },
            index = state_index_list
        )
        # Set all inital values to be zero
        # Set appropriated rewards for each action in every conditions
        # Setting Initial Value
        self.alpha = 0.5
        self.gramma = 0.9
        print("---------- Q-Table ----------")
        print(self.Q_table)

        
    
    def update(self):
        reward = float()
        reward = -0.05

        # Get Value from Smell Sensor
        Target = 'F' if abs(self.smell()) < 15 else 'L' if self.smell() < -15 else 'R'
        # print(Target)
        
        # Get values from IR sensor
        IR =  ''.join(['0' if x < 50 else '1' for x in self.distance()[:3] + self.distance()[-2:]])
        self.state_key = Target + IR
        #print(f"State : {self.state_key}")
        
        
        ### Choose action ###
        action = str()
    
        ### Exploitation = 90% ###
        if random.randint(0,9) > 0:
            ### Find Index that maximum value in list ###
            # print(f"DF when state  : \n{self.Q_table.loc[self.state_key]}")
            # print(f"Type when state  : \n{type(self.Q_table.loc[[self.state_key],:])}")
            # print(f"DF when state  : \n{self.Q_table.loc[self.state_key].max(axis = 0)}")            
            # actions = self.Q_Table[state_key].index(max(self.Q_Table[state_key]))
            # print("Maximum in action: {0}, {1}".format(actions, self.Q_Table[state_key]))
            # print(f"{self.Q_table.loc[,:]}")
            q_value = self.Q_table.loc[self.state_key].values.tolist()
            # print(f"Q Values: {q_value}")
            # print(f"Max value of Q-Value: {max(q_value)}")
            # print(f"Index of Max q-value: {q_value.index(max(q_value))}")
            index = q_value.index(max(q_value))
            action = 'Front' if index == 0 else 'Left' if index == 1 else 'Right'
            #print(f"Action : {action}")
            
            pass
        else:
            x = random.randint(0,2)
            action = 'Front' if x == 0 else 'Left' if x == 1 else 'Right'
            #print("Random Action: {0}".format(action))
            pass
        
        
        #ang1 = self.smell()
        
        ### Perform action & Measure Reward ####
        if action == 'Front':
            self.move(5)
            reward = -5 if self.stuck else ((90 - abs(self.smell()))/90)
            
        elif action == 'Left':
            self.turn(-5)
            #reward += ((90 - abs(self.smell()))/90) 
            #ang2 = self.smell()
            #reward = 1 if (ang1 - ang2 >= 0) else -1
        
        elif action == 'Right':
            self.turn(5)
            #reward += ((90 - abs(self.smell()))/45) 
            #ang2 = self.smell()
            #reward = 1 if (ang1 - ang2 >= 0) else -1

        #print("R = {0}".format(reward))
        
        
        
        ### Update Q-Table ### 
        # For the first time
        self.pre_state_key = self.state_key if self.pre_state_key == '' else self.pre_state_key
        self.pre_action = action if self.pre_action =='' else self.pre_action
        
        # self.Q_Table[self.pre_state_key][self.pre_action] += self.alpha * (reward + (self.gramma * max(self.Q_Table[self.state_keystate_key]) ) - self.Q_Table[self.pre_state_key][self.pre_action]  )
        self.Q_table.loc[[self.pre_state_key],[self.pre_action]] += self.alpha * \
            (reward + (self.gramma * self.Q_table.loc[self.pre_state_key].max(axis= 0) ) \
                - self.Q_table.loc[[self.pre_state_key],[self.pre_action]])
        
        # Update to SQLite3
        #self.Q_table.to_sql('Q_table', con=self.engine, if_exists='replace')
        
        # Setting a new pre-state
        self.pre_state_key = self.state_key
        self.pre_action = action
        if (self.step % 500 == 0) and (self.step > 0):
            dataplot1.append(self.eat_count/self.step)
            dataplot2.append(self.collision_count/self.step)
        self.step += 1
        
        #print(self.Q_table)


        pass

if __name__ == '__main__':
    app = PySimbotApp(
        robot_cls=RL_Robot, 
        simulation_forever=False,
        max_tick=100000,
        interval=1/1000.0,
        food_move_after_eat=True,
        num_robots=1
        )
    app.run()
    plt1.plot(dataplot1)
    plt1.show()
    plt2.plot(dataplot2)
    plt2.show()