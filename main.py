import detection
import player
import Leap
import sys
import vlc
import threading
import time

state = detection.State()
threadLock = threading.Lock()

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
            if state.s ==5: 
                state.s =0
            if state.s == 6:
                state.s =0
            # print("Two")
            left_hand = frame.hands.leftmost
            right_hand = frame.hands.rightmost
            state.detect_action4(left_hand.palm_position, right_hand.palm_position)
            # state.detect_action5(left_hand.palm_position, right_hand.palm_position)

        if hand.is_valid and not hand1.is_valid:
            state.detect_action1(hand.palm_position)   

        if (hand.is_valid and not hand1.is_valid) or (not hand.is_valid and not hand1.is_valid):
            state.detect_action2(hand.palm_position,hand.is_valid)
            state.detect_action3(hand.palm_position,hand.is_valid)






        # if not hand.is_valid:
        #     state.clear_state()
        # 释放锁
        threadLock.release()

        # print ("Frame available")


def main():
    listener = SampleListener()
    controller = Leap.Controller()
    controller.set_policy(Leap.Controller.POLICY_BACKGROUND_FRAMES)
    controller.add_listener(listener)

    videoplayer = player.Player()
    videoplayer.play("video/test.mp4")
    
    # videoplayer.play("https://www.youtube.com/watch?v=0Hm13NaMKvo")
    # Keep this process running until Enter is pressed


    while True:
        if state.s == 1:
            if videoplayer.is_playing():
                print("Try pause")
                videoplayer.pause()
                state.clear_state()
                time.sleep(2)
            else:
                print("Try resume")
                videoplayer.resume()
                state.clear_state()
                time.sleep(2)
        
        if state.s == 4 :
            if not videoplayer.is_fullscreen():
                print("Try fullscreen")
                videoplayer.set_fullscreen(True)
                state.clear_state()
                time.sleep(2)
        
        # if state.s == 7:
        #     if videoplayer.is_fullscreen():
        #         print("Close fullscreen")
        #         videoplayer.set_fullscreen(False)
        #         state.clear_state()
        #         time.sleep(2)

        if state.s == 5:
            videoplayer.pause()
            video_length = videoplayer.get_length()     #  总时间
            time_current = videoplayer.get_time() # 当前时间
            set_time  = int((state.length/500)*(video_length-time_current)) + time_current
             
            print("准备快进到")
            print("video time" + str(set_time/video_length))
            time.sleep(0.5)
            

        if state.s == 2:
            videoplayer.set_position(set_time/video_length)
            print("完成快进")
            videoplayer.resume()
            state.clear_state()
            time.sleep(2)

        
        if state.s == 6:
            videoplayer.pause()
            video_length = videoplayer.get_length()     #  总时间
            time_current = videoplayer.get_time() # 当前时间
            set_time  = time_current + int((state.length/500)*(time_current))
             
            print("准备退到")
            print("video time" + str(set_time/video_length))
            time.sleep(0.5)
            

        if state.s == 3:
            videoplayer.set_position(set_time/video_length)
            print("完成退")
            videoplayer.resume()
            state.clear_state()
            time.sleep(2)


        # if state.s == 2:
        #     video_length = videoplayer.get_length()     #  总时间
        #     time_current = videoplayer.get_time() # 当前时间
        #     print("video time" + str(videoplayer.get_time()))
        #     move_length = state.length
        #     set_time  = int(move_length/1000*video_length) + videoplayer.get_time()
        #     # print("set time" + str(set_time))
        #     # print(videoplayer.set_time(set_time))
        #     videoplayer.set_position(set_time/video_length)
        #     print("Right")
        #     print("video time" + str(videoplayer.get_time()))
        #     state.clear_state()
        #     time.sleep(2)

        # if not state.s ==0 and not state.time == 0:
        #     state.time = state.time -1
        #     continue
        pass
    # print ("Press Enter to quit...")
    # try:
    #     sys.stdin.readline()

    # except KeyboardInterrupt:
    #     pass

if __name__ == "__main__":
    main()