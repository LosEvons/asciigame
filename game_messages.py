import tcod as libtcod
import textwrap

class Message:
    def __init__ (self, text, color=libtcod.white):
         self.text = text
         self.color = color

class MessageLog: #We make a global message log, that will be displayed in the UI.
    def __init__(self, x, width, height):
        self.messages = []
        self.x = x
        self.width = width
        self.height = height
    
    def add_message(self, message): #Add messages to the log
        new_msg_lines = textwrap.wrap(message.text, self.width)

        for line in new_msg_lines:
            if len(self.messages) == self.height: #If the UI can't hold all the messages. We just delete them for now.
                del self.messages[0]

            self.messages.append(Message(line, message.color))