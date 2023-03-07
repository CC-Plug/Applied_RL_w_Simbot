#!/usr/bin/python3

import random
from typing import Dict
from pysimbotlib.core import PySimbotApp, Robot
from kivy.config import Config
import csv
from copy import deepcopy

# Force the program to show user's log only for "info" level or more. The info log will be disabled.
Config.set('kivy', 'log_level', 'info')

MID_DISTANCE = 25
CLOSE_DISTANCE = 15

from random import seed
seed(123)

def ternary (n):
    if n == 0:
        return '0'
    nums = []
    while n:
        n, r = divmod(n, 3)
        nums.append(str(r))
    return ''.join(reversed(nums))

class RL_Robot(Robot):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.step = 0
        self.just_hit = False
        self.qTable: Dict = {}
        self.ACTION_CLASS = ['F', 'L', 'R', 'FL', 'FR', 'B']
        
        # Initial all the state value to 0
        for state in range(0, 3**5):
            for smell in range(0, 3):
                for action in self.ACTION_CLASS:
                    self.qTable["{}{}".format(ternary(state).zfill(5), smell), action] = 0.0
        self.discount_factor = 0.9
        self.learning_rate = 0.5
        # with open('q_table_2.csv', 'w+', newline='') as csvfile:
        #     fieldnames = ['state', 'action', 'reward']
        #     fieldnames.extend(list(qTable.keys()))
        #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        #     writer.writeheader()
        #     newQTable = deepcopy(qTable)
        #     newQTable.update({'state':"'000000'", 'action': 'F', 'reward': 0.0})
        #     writer.writerow(newQTable)
        
        self.count_F = 0
        self.count_L = 0
        self.count_R = 0
        self.count_B = 0
        self.count_FL = 0
        self.count_FR = 0

    def update(self):
        self.ir_values = self.distance()
        self.S0, self.S1, self.S2, _, _, _, self.S6, self.S7 = self.ir_values
        self.target = self.smell()
        # current state
        # list of smell
        smells = [self.smell_left(), self.smell_center(), self.smell_right()]
        state = (f"{self.S6_near()}{self.S7_near()}{self.S0_near()}{self.S1_near()}{self.S2_near()}{smells.index(1)}")

        # action
        # get action that has max value of Q-table of this state
        for action in self.ACTION_CLASS:
            action_value: Dict = {}
            action_value[action] = self.qTable[(state), action]
        max_q_value = max(self.qTable[(state), action] for action in self.ACTION_CLASS)
        # get best action if there are more than one action with same max value get F action
        best_actions = [action for action in self.ACTION_CLASS if self.qTable[(
            state), action] == max_q_value]
        # print('best_actions:', best_actions)
        if len(best_actions) > 1:
            best_action = random.choice(best_actions)
        else:
            best_action = best_actions[0]

        # 10% of the time, choose a random action
        if random.random() < 0.1:
            # print('random action')
            action = random.choice(self.ACTION_CLASS)
        else:
            action = best_action

        current_q = self.qTable[(state, action)]
        temp_collision = self.collision_count

        if action == 'F':
            self.count_F += 1
            self.move(5)
        elif action == 'L':
            self.count_L += 1
            self.turn(-15)
        elif action == 'R':
            self.count_R += 1
            self.turn(15)
        elif action == 'FL':
            self.count_FL += 1
            self.move(5)
            self.turn(-15)
        elif action == 'FR':
            self.count_FR += 1
            self.move(5)
            self.turn(15)
        elif action == 'B':
            self.count_B += 1
            self.move(-5)
        else:
            raise Exception("Invalid action")
        
        # Check if robot hit the wall
        if self.collision_count != temp_collision:
            print('hit!')
            self.just_hit = True
        else:
            self.just_hit = False

        # current state
        smells = [self.smell_left(), self.smell_center(), self.smell_right()]
        next_state = (f"{self.S6_near()}{self.S7_near()}{self.S0_near()}{self.S1_near()}{self.S2_near()}{smells.index(1)}")

        # give reward
        self.reward = 0
        self.reward = self.get_reward(action)
        print(self.reward)
        # update value Q-table
        q_update = current_q + self.learning_rate * (self.reward + self.discount_factor * max(self.qTable[(next_state), action] for action in self.ACTION_CLASS) - current_q)
        # print(state, action)
        # print('before: ' ,self.qTable[(state, action)])
        # print('Reward: ',self.reward)
        self.qTable[(state, action)] = q_update
        # print('after: ', self.qTable[(state, action)])
        if (self.step % 1000 == 0) and (self.step > 0):
            with open('learning_score.csv', 'a', newline='') as csvOpen:
                c = csv.writer(csvOpen, dialect='excel')
                c.writerow([self.step/1000, self.eat_count, self.eat_count/self.step , self.collision_count, self.collision_count/self.step,self.count_F,self.count_L,self.count_R,self.count_B,self.count_FL,self.count_FR])
        self.step += 1
        
    def S0_near(self):
        if self.S0 < CLOSE_DISTANCE:
            return 1
        elif CLOSE_DISTANCE <= self.S0 < MID_DISTANCE:
            return 2 
        elif self.S0 >= MID_DISTANCE:
            return 0

    def S1_near(self):
        if self.S1 < CLOSE_DISTANCE:
            return 1
        elif CLOSE_DISTANCE <= self.S1 < MID_DISTANCE:
            return 2
        elif self.S1 >= MID_DISTANCE:
            return 0

    def S2_near(self):
        if self.S2 < CLOSE_DISTANCE:
            return 1
        elif CLOSE_DISTANCE <= self.S2 < MID_DISTANCE:
            return 2
        elif self.S2 >= MID_DISTANCE:
            return 0

    def S6_near(self):
        if self.S6 < CLOSE_DISTANCE:
            return 1
        elif CLOSE_DISTANCE <= self.S6 < MID_DISTANCE:
            return 2
        elif self.S6 >= MID_DISTANCE:
            return 0

    def S7_near(self):
        if self.S7 < CLOSE_DISTANCE:
            return 1
        elif CLOSE_DISTANCE <= self.S7 < MID_DISTANCE:
            return 2
        elif self.S7 >= MID_DISTANCE:
            return 0

    def smell_right(self):
        if 180 >= self.target >= 45:
            return 1
        else:
            return 0

    def smell_left(self):
        if -180 <= self.target <= -45:
            return 1
        else:
            return 0

    def smell_center(self):
        if self.target <= 45 and self.target >= -45:
            return 1
        else:
            return 0

    def get_reward(self, action):
        the_reward = 0
        if self.just_eat:
            return 50
        if self.just_hit or self.stuck:
            if action == 'F':
                return -40
            else:
                return -30

        if action == 'F':
            if self.S0_near() == 1:
                the_reward -= 25
            elif self.S0_near() == 2:
                the_reward -= 3
            elif self.smell_center() == 1:
                the_reward += 20
            elif self.smell_left() == 1 or self.smell_right() == 1:
                the_reward -= 10
            else:
                the_reward += 5
        elif action == 'L' or action == 'FL':
            if self.S7_near() == 1 or self.S6_near() == 1:
                the_reward -= 20
            elif self.S7_near() == 2 or self.S6_near() == 2:
                the_reward -= 3
            elif self.smell_center() == 1:
                the_reward += 5
                if self.S0_near != 1:
                    the_reward += 5
            elif self.smell_left() == 1:
                the_reward += 3
            else:
                the_reward -= 5
        elif action == 'R' or action == 'FR':
            if self.S1_near() == 1 or self.S2_near() == 1:
                the_reward -= 20
            elif self.S1_near() == 2 or self.S2_near() == 2:
                the_reward -= 3
            elif self.smell_center() == 1:
                the_reward += 5
                if self.S0_near != 1:
                    the_reward += 5
            elif self.smell_right() == 1:
                the_reward += 3
            else:
                the_reward -= 5
        elif action == 'B':
            if self.S0_near() == 2:
                the_reward += 10
            else:
                the_reward -= 10

        return the_reward


if __name__ == '__main__':
    with open('learning_score.csv', 'w+', newline='') as csvOpen:
        c = csv.writer(csvOpen, dialect='excel')
        c.writerow(['iteration', 'eat', 'eat_rate', 'hit', 'hit_rate','F','L','R','B','FL','FR'])
        c.writerow(
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    app = PySimbotApp(robot_cls=RL_Robot, num_robots=1, max_tick=1000000, interval= 1/1000.0)
    app.run()