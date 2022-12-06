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
        hand = frame.hands[0]
        hand1 = frame.hands[1]
        threadLock.acquire()
        if hand.is_valid and hand1.is_valid:
            state.clear_onehand_state()
            left_hand = frame.hands.leftmost
            right_hand = frame.hands.rightmost
            state.detect_twohand(left_hand.palm_position, right_hand.palm_position)
        else:
            state.detect_onehand(hand.palm_position,hand.palm_normal,hand.is_valid)
            
        if not hand.is_valid:
            if not state.state == 2 and not state.state == 3 and not state.state == 4 and not state.state == 5:
                state.clear_state()
        # 释放锁
        threadLock.release()

        # print ("Frame available")


def main():
    listener = SampleListener()
    controller = Leap.Controller()
    controller.set_policy(Leap.Controller.POLICY_BACKGROUND_FRAMES)
    controller.add_listener(listener)

    videoplayer = player.Player()
    videoplayer.play("video/test1.mp4")
    pause = '/home/xiao/Code/LeapVideo/video/pause.png'
    up = '/home/xiao/Code/LeapVideo/video/up.png'
    down = '/home/xiao/Code/LeapVideo/video/down.png'
    videoplayer.init_logo()
    videoplayer.set_marquee()


    while True:
        if state.state == 1:
            if videoplayer.is_playing():
                print("Try pause")
                videoplayer.pause()
                state.clear_state()
                videoplayer.set_logo(pause)
                time.sleep(2)
            else:
                print("Try resume")
                videoplayer.resume()
                state.clear_state()
                videoplayer.close_logo()
                time.sleep(2)
    

        if state.state == 2:
            if videoplayer.is_playing():
                videoplayer.pause()
            video_length = videoplayer.get_length()     #  总时间
            time_current = videoplayer.get_time() # 当前时间
            set_time  = int((state.action_length/500)*(video_length-time_current)) + time_current
             
            print("准备快进到")
            print("video time" + str(set_time/video_length))
            sting = "准备快进到 {} %".format('%.4f'%(set_time/video_length*100))
            videoplayer.update_text(sting)
            time.sleep(0.5)
            

        if state.state == 4:
            video_length = videoplayer.get_length()     #  总时间
            time_current = videoplayer.get_time() # 当前时间
            set_time  = int((state.action_length/500)*(video_length-time_current)) + time_current
            videoplayer.set_position(set_time/video_length)
            print("完成快进")
            videoplayer.resume()
            videoplayer.update_text(' ')
            state.clear_state()
            time.sleep(2)

        
        if state.state == 3:
            if videoplayer.is_playing():
                videoplayer.pause()
            video_length = videoplayer.get_length()     #  总时间
            time_current = videoplayer.get_time() # 当前时间
            set_time  = time_current + int((state.action_length/500)*(time_current))
             
            print("准备退到")
            print("video time" + str(set_time/video_length))
            sting = "准备快退到 {} %".format('%.4f'%(set_time/video_length*100))
            videoplayer.update_text(sting)
            time.sleep(0.5)
            

        if state.state == 5:
            video_length = videoplayer.get_length()     #  总时间
            time_current = videoplayer.get_time() # 当前时间
            set_time  = int((state.action_length/500)*(video_length-time_current)) + time_current
            videoplayer.set_position(set_time/video_length)
            print("完成退")
            videoplayer.resume()
            videoplayer.update_text(' ')
            state.clear_state()
            time.sleep(2)

        if state.state == 6 :
            #print("action 4")
            if not videoplayer.is_fullscreen():
                print("Try fullscreen")
                videoplayer.set_fullscreen(True)
                state.clear_state()
                time.sleep(2)

        if state.state == 7 :
            if videoplayer.is_fullscreen():
                print("close fullscreen")
                videoplayer.set_fullscreen(False)
                state.clear_state()
                time.sleep(2)       
        
        if state.state == 8:
            videoplayer.set_logo(up)
            audio = videoplayer.get_volume()
            if audio + 20 >= 200:
                videoplayer.set_volume(200)
            else:
                videoplayer.set_volume(audio + 20)


            state.clear_state()
            time.sleep(3)   
            videoplayer.close_logo() 
            

        if state.state == 9:
            videoplayer.set_logo(down)
            audio = videoplayer.get_volume()

            if audio - 20 <= 0:
                videoplayer.set_volume(0)
            else:
                videoplayer.set_volume(audio - 20)

            state.clear_state()
            time.sleep(3)
            videoplayer.close_logo() 
            

        pass
    # print ("Press Enter to quit...")
    # try:
    #     sys.stdin.readline()

    # except KeyboardInterrupt:
    #     pass

if __name__ == "__main__":
    main()