import Leap
import sys
import threading
import numpy as np
import math

threadLock = threading.Lock()

class State():
    def __init__(self):
        self.s = 0
        # param for detect action1
        self.hands_prev_direction = np.array([0,0,-1])
        self.hands_begin_direction = None  #开始向下运动的角度
        self.rotate_time = -1          #往下运动的帧数

        # param for detect action2
        self.hands_prev_position_right = np.array([0,0,0])
        self.hands_begin_position_right = None
        self.move_right_time = -1

        # param for detect action3
        self.hands_prev_position_left = np.array([0,0,0])
        self.hands_begin_position_left = None
        self.move_left_time = -1

        # param for detect action4
        self.move_time = -1
        self.prev_distance = 0
        self.distance = 0
        self.action4_begin_distance = 0


    def detect_action1(self,direction):
        if self.rotate_time == -1:
            self.rotate_time = self.rotate_time+1
            self.hands_prev_direction = direction
            return False

        # 判断是否往下运动
        #print(direction)
        if (direction[2]-self.hands_prev_direction[2]) > 0:
            if self.rotate_time == 0:
                print('begin')
                self.rotate_begin_direction = self.hands_prev_direction
            self.rotate_time = self.rotate_time + 1
            if self.rotate_time > 5 and (direction[2] - self.rotate_begin_direction[2])> 0.4:
                self.rotate_time = -1
                print("detect action1")

        if (direction[2]-self.hands_prev_direction[2]) < 0:
            self.rotate_time =-1

        self.hands_prev_direction = direction
        
    # 检测往右运动
    def detect_action2(self,position):
        if self.move_right_time == -1:
            self.move_right_time = self.move_right_time+1
            self.hands_prev_position_right = position
            return False
            
        # 判断是否往右边运动
        if (position[0]-self.hands_prev_position_right[0]) > 0.01:
            if self.move_right_time == 0:
                print('begin')
                self.hands_begin_position_right = self.hands_prev_position_right
            self.move_right_time = self.move_right_time + 1
            
        if (position[0]-self.hands_prev_position_right[0]) < 0.01:   
            if self.move_right_time > 20 and (position[0] - self.hands_begin_position_right[0])> 50:
                self.move_right_time = -1
                print("detect action2")
                print(position[0] - self.hands_begin_position_right[0])

        self.hands_prev_position_right = position


        # 检测往左运动
    def detect_action3(self,position):
        if self.move_left_time == -1:
            self.move_left_time = self.move_left_time+1
            self.hands_prev_position_left = position
            return False
            
        # 判断是否往右边运动
        if (position[0]-self.hands_prev_position_left[0]) < -0.01:
            if self.move_left_time == 0:
                print('begin')
                self.hands_begin_position_left = self.hands_prev_position_left
            self.move_left_time = self.move_left_time + 1
            
        if (position[0]-self.hands_prev_position_left[0]) > -0.01:   
            if self.move_left_time > 20 and (position[0] - self.hands_begin_position_left[0])< -50:
                self.move_left_time = -1
                print("detect action3")
                print(position[0] - self.hands_begin_position_left[0])

        self.hands_prev_position_left = position

    def calculate_distance(self,left,right):
        dis = math.sqrt((left[0]-right[0])**2+(left[1]-right[1])**2+(left[2]-right[2])**2)
        return dis

    def detect_action4(self,left_position,right_position):
        if self.move_time == -1:
            self.move_time = self.move_time+1
            self.prev_distance = self.calculate_distance(right_position,left_position)
            return False

        self.distance = self.calculate_distance(right_position,left_position)
        if self.distance > self.prev_distance:
            if self.move_time == 0:
                print('begin Two')
                self.action4_begin_distance = self.prev_distance
            self.move_time = self.move_time +1
            if self.move_time > 20 and (self.distance-self.action4_begin_distance)>100:
                self.move_time = -1
                print("detect action4")
                print(self.distance-self.action4_begin_distance)

        if self.distance < self.prev_distance:
            self.move_time = -1
        
        self.prev_distance = self.distance

        


    def clear_state(self):
        self.rotate_time = -1
        self.move_left_time = -1
        self.move_right_time = -1
        self.move_time = -1


state = State()

class SampleListener(Leap.Listener):
    def on_connect(self, controller):
        print ("Connected")


    def on_frame(self, controller):
        frame = controller.frame()
        # hand = frame.hands.rightmost
        hand = frame.hands[0]
        hand1 = frame.hands[1]
        threadLock.acquire()
        # print(hand.direction[2])

        if not hand.is_valid:
            state.clear_state()


        # if hand.is_valid and not hand1.is_valid:
        #     state.detect_action1(hand.direction)
        #     state.detect_action2(hand.palm_position)
        #     state.detect_action3(hand.palm_position)

        if hand.is_valid and hand1.is_valid:
            # print("Two")
            left_hand = frame.hands.leftmost
            right_hand = frame.hands.rightmost
            state.detect_action4(left_hand.palm_position, right_hand.palm_position)
        # 释放锁
        threadLock.release()

        # print ("Frame available")

class PlayThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.controller = Leap.Controller()
        self.listener = SampleListener()
        self.controller.add_listener(self.listener)

   
    def run(self):
        print ("Starting " + self.name)
        print("here")



def main():
    listener = SampleListener()
    controller = Leap.Controller()
    controller.set_policy(Leap.Controller.POLICY_BACKGROUND_FRAMES)
    controller.add_listener(listener)



    # thread1 = PlayThread(1, "Thread-1")
    # thread1.start()
    # thread1.join()

    # Keep this process running until Enter is pressed
    print ("Press Enter to quit...")
    try:
        sys.stdin.readline()

    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()

