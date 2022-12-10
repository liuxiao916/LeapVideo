import Leap
import sys
import threading
import numpy as np
import math

threadLock = threading.Lock()

class State():
    def __init__(self):
        self.state = 0
        self.hand_position = []
        self.start_position = None   # 记录十五帧前的手位置
        self.action_begin_position = None #记录动作2(快进)和3（倒退）的起始位置
        self.action_length = 0 #记录动作2和3的长度

        self.hand_distance = []
        self.start_distance = None
        
    def detect_onehand(self,position,direction,hand_available):
        
        if hand_available:
            if len(self.hand_position) > 15:
                self.hand_position.append(position)
                self.start_position = self.hand_position.pop(0)
                if abs(direction[2]) < 0.75:
                    # right
                    if self.state == 2 or self.state == 3:
                        self.action_length = position[0] - self.action_begin_position
                    elif position[0] - self.start_position[0] > 80: 
                        # print(self.hand_position)
                        self.state = 2
                        self.hand_position.clear()
                        self.action_begin_position = self.start_position[0]
                        print('2')

                    # left
                    elif position[0] - self.start_position[0] < -80:
                        # print(self.hand_position)
                        self.state = 3
                        self.hand_position.clear()
                        self.action_begin_position = self.start_position[0]
                        print('3')
                         
                    # forward
                    elif position[1] - self.start_position[1] < -80:
                        self.state = 1
                        self.hand_position.clear()
                        print('acti1 ')

                    else: 
                        # up 
                        if (position[2] - self.start_position[2] < -60) :
                            # print(self.hand_position)
                            self.state = 8
                            self.hand_position.clear()
                            print('8')

                        # down
                        elif position[2] - self.start_position[2] > 60:
                            # print(self.hand_position)
                            self.state = 9
                            self.hand_position.clear()
                            print('9')

            else:
                self.hand_position.append(position)
        else:
            if self.state == 2:
                self.state = 4
                print('s4')
                print(self.action_length)
               # print(self.hand_position)
            elif self.state == 3:
                self.state = 5
                print('s5')
                print(self.action_length)
                # print(self.hand_position)

            
    def calculate_distance(self,left,right):
        dis = math.sqrt((left[0]-right[0])**2+(left[1]-right[1])**2+(left[2]-right[2])**2)
        return dis

    def detect_twohand(self,left_position,right_position):
        if len(self.hand_distance) > 10:
            distance = self.calculate_distance(left_position,right_position)
            self.hand_distance.append(distance)
            self.start_distance = self.hand_distance.pop(0)
            if distance - self.start_distance >80:
                self.state = 6
                print('s6')
            elif distance - self.start_distance <- 80:
                self.state = 7
                print('s7')

        else:
            self.hand_distance.append(self.calculate_distance(left_position,right_position))

    def clear_state(self):
        self.state = 0
        self.hand_position.clear()
        self.start_position = None
        self.action_begin_position = None #记录动作2(快进)和3（倒退）的起始位置
        self.action_length = 0 #记录动作2和3的长度

        self.hand_distance.clear()
        self.start_distance = None

    def clear_onehand_state(self):
        if not self.state ==6 or not self.state == 7:
            self.state = 0

    
        self.hand_position.clear()
        self.start_position = None
        self.action_begin_position = None #记录动作2(快进)和3（倒退）的起始位置
        self.action_length = 0 #记录动作2和3的长度


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

        
        if hand.is_valid and hand1.is_valid:
            state.clear_onehand_state()
            left_hand = frame.hands.leftmost
            right_hand = frame.hands.rightmost
            state.detect_twohand(left_hand.palm_position, right_hand.palm_position)
        else:
            state.detect_onehand(hand.palm_position,hand.palm_normal,hand.is_valid)
            
        if not hand.is_valid:
            if not state.state == 2 and not state.state == 3:
                state.clear_state()
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

    # Keep this process running until Enter is pressed
    print ("Press Enter to quit...")
    try:
        sys.stdin.readline()

    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()

