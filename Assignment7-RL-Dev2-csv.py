#!/usr/bin/python3

# from pysimbotlib.core import PySimbotApp, Robot
from pysimbotlib.core import PySimbotApp, Simbot, Robot, Util
from kivy.config import Config

# Force the program to show user's log only for "info" level or more. The info log will be disabled.
Config.set('kivy', 'log_level', 'info')

import random
import pandas as pd
import csv

count = 0
class RL_Robot(Robot):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
        self.temp_collision = 0

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
        
        # Write column name for recording the statistics
        global count
        count += 1
        header = ['Time', 'Eat-Count', 'Collision-Count']
        with open(f'data{count}.csv', 'w', encoding='UTF8',newline='') as f:
            writer = csv.writer(f)

            # write the header
            writer.writerow(header)


    def get_reward(self,state,action) -> float():
        
        reward = float()
        # for every state that eat the food reward = 10.0
        if (self.eat_count != self.temp_eat):
            self.temp_eat = self.eat_count
            reward = 10.0
        # if the robot stuck
        elif (self.stuck):
            reward = -2.0
        
        elif (self.collision_count != self.temp_collision):
            self.temp_collision = self.collision_count
            reward = -2.0
        # if the robot turn away from the food
        else:
            reward = 1.0 if abs(self.smell()) < 35 else -1.0 * (abs(self.smell()) / 20)
            pass
        return reward
    
    def update(self):
        
        # Oberserve the environment
        # Get Value from Smell Sensor
        Target = 'F' if abs(self.smell()) < 30 else 'L' if self.smell() < -30 else 'R'
        # print(Target)
        
        # Get values from IR sensor
        IR =  ''.join(['0' if x < 25 else '1' for x in self.distance()[:3] + self.distance()[-2:]])
        self.state_key = Target + IR
        # print(f"State : {self.state_key}")
    
        ### Choose action ###
        action = str()
    
        ### Exploitation = 90% ###
        if random.randint(0,9) > 0:
            q_value = self.Q_table.loc[self.state_key].values.tolist()
            index = q_value.index(max(q_value))
            action = 'Front' if index == 0 else 'Left' if index == 1 else 'Right'

        else:
            x = random.randint(0,2)
            action = 'Front' if x == 0 else 'Left' if x == 1 else 'Right'
            pass
        
        
        ### Perform action & Measure Reward ####
        if action == 'Front':
            self.move(5)
                
        elif action == 'Left':
            self.turn(-15)

        elif action == 'Right':
            self.turn(15)

        
        
        ### Update Q-Table ### 
        
        # Future State
        new_Target = 'F' if abs(self.smell()) < 30 else 'L' if self.smell() < -30 else 'R'
        # print(Target)
        
        # Get values from IR sensor
        new_IR =  ''.join(['0' if x < 25 else '1' for x in self.distance()[:3] + self.distance()[-2:]])
        
        self.future_state = new_Target + new_IR
        
        # future reward = discount * future_reward
        future_reward = (self.gramma * self.Q_table.loc[self.future_state].max(axis= 0) )
        
        reward = self.get_reward(self.future_state, action)
        
        print(f"Action: {action}, State: {self.state_key}, Reward: {reward}, Future State: {self.future_state}")
        
        self.Q_table.loc[[self.state_key],[action]] += self.alpha * \
            (reward + future_reward \
                - self.Q_table.loc[[self.state_key],[action]])
        
    
        
        # write q-table to csv files
        if self._sm.iteration % 1000 == 0 or self._sm.iteration <= 1:
            # save into path folder
            path = "D:\Master_Degree\TA_1-21\IRP_AML_2021\PyRLSimbot\PyRLSimbot\Q_table"
            self.Q_table.to_csv(f'{path}\Q-Table_Iter_{self._sm.iteration}.csv', encoding='utf-8')
            # save in same location
            # self.Q_table.to_csv(f'Q-Table_Iter_{self._sm.iteration}.csv', encoding='utf-8')
            
            # Recording eat count and collision count to txt file
            # print(f"Eat Count: {self.eat_count}")
            # print(f"Collision count : {self.collision_count}")
            data = [self._sm.iteration, self.eat_count/self._sm.iteration, self.collision_count/self._sm.iteration]
            with open(f'data{count}.csv', 'a', encoding='UTF8',newline='') as f:
                writer = csv.writer(f)
                # write the header
                writer.writerow(data)
        pass


if __name__ == '__main__':
    app = PySimbotApp(
        robot_cls=RL_Robot, 
        simulation_forever=False,
        max_tick=300000,
        interval=1/120.0,
        food_move_after_eat=True,
        num_robots=1
        )
    app.run()