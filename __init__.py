# Copyright 2018 Lukas Gangel
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import traceback
import logging
import re

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import LOG
from mycroft.audio import wait_while_speaking 
from mycroft.util.log import getLogger

logger = getLogger(__name__)


__author__ = 'luke5sky'

class rememberSkill(MycroftSkill):

    def __init__(self):
        super(rememberSkill, self).__init__(name="rememberSkill")
        self.remfile = (self.file_system.path+"/rememberlist.txt") # MY LIST, MY PRECIOUS, MY PRECIOUS..... GOLLUM
        if not os.path.exists(self.remfile):
            remlist = open(self.remfile,"x")
            remlist.close()
            
    @intent_handler(IntentBuilder("WhatToRememberIntent").require("Did").require("You").require("Remember").build())
    def WhatToRememberIntent(self, message): # user wants to know what we've got
        try: # try to open our remember list readonly and give user all phrases
            remlist = open(self.remfile,"r") # open file readonly
            rememberphrases = remlist.read() # read file
            alist = rememberphrases.split("\n") # split line by line and make a nice list
            if not rememberphrases:
               self.speak_dialog("sorry") # we got nothing in our list
            else: # we got something
               if len(alist) > 2: # make it nice and shiny with AND and commas
                   search = rememberphrases.rfind("\n")
                   rememberphrases = rememberphrases[:search] + "" + rememberphrases[search+1:]
                   search = rememberphrases.rfind("\n")
                   rememberphrases = rememberphrases[:search] + " and " + rememberphrases[search+1:]
                   rememberphrases = rememberphrases.replace('\n', ', ')
               self.speak_dialog('iremembered', {'REMEMBER': rememberphrases}) # give the user our nice list
            remlist.close() # we don't need the file anymore
        except:
            self.speak_dialog("sorry") # oh damn, something happened
        
    @intent_handler(IntentBuilder("RememberIntent").require("Remember").require("WhatToRemember").build())
    def RememberIntent(self, message): # user wants us to remember something
        utt=(message.data.get("utterance"))
        if re.match("what did you", utt) is not None: # workaround for what did you remember?
           self.WhatToRememberIntent(message)
           return None
        rememberPhrase = message.data.get("WhatToRemember", None) # get phrase user wants us to remember
        try: # if user said something like "remember phrase get some milk" we don't want phrase to be saved, brakes skill a bit, we don't wanna skill broken, we like skill
            rememberPhrase = rememberPhrase.replace('phrase ', '') # Phrase Evanesca! if you got this reference, you should stop reading comments in code and go out a bit, have fun with friends or watch birds or something like that
        except:
            pass #go on if the user does not put phrase in the phrase, in the phrase, in the phrase.... phraseception
        try: # lets try to remember
            if rememberPhrase: # we need a phrase to remember
               if len(rememberPhrase) > 4: # phrase should be at least 5 characters
                  remlist = open(self.remfile,"a") # open file but only append don't overwrite
                  filePhrase = rememberPhrase+"\n" # we want newlines
                  remlist.write(filePhrase) # write to file
                  self.speak_dialog('gotphrase', {'REMEMBER': rememberPhrase}) # tell user we did it and be proud, good boy mycroft... or girl... what is mycroft? NOTE: make gender-skill
                  remlist.close() # close file
               else: # oh oh, was the phrase to short
                  self.speak_dialog("short") # tell user to stop giving us short messages, we like to talk
        except Exception as e: # error error, we hate errors...
            logging.error(traceback.format_exc())
            self.speak_dialog('sorry') # ... but we are always sorry
    
    @intent_handler(IntentBuilder("DeleteIntent").require("Forget").require("Phrase").optionally("RememberPhrase").optionally("All").build())
    def DeleteIntent(self, message): # function for forgetting/deleting phrases from the list
        rememberPhrase = message.data.get("RememberPhrase", None) # get phrase from spoken sentence
        delall = message.data.get("All", None) # check if there is ALL in the sentence, maybe user wants to clear the complete list
        remlist = open(self.remfile,"r") # open file with remembered phrases readonly
        plist = remlist.readlines() # get list from file
        remlist.close() # we don't need to read anymore
        olist = plist
        plist = [x.strip() for x in plist] # delete whitespaces
        found = 0 # if 1 we found something, 0 means nothing found
        try: # Try to get an exact match of the given phrase to delete
            if rememberPhrase in plist and found == 0: # if we could find the given phrase in the list do following
               found = 1 # yes we found something
               should_delete = self.get_response('delete', {'PHRASE': rememberPhrase}) # ask user if we should forget the phrase
               yes_words = set(self.translate_list('yes')) # get list of confirmation words
               resp_delete = should_delete.split() 
               if any(word in resp_delete for word in yes_words): # if user said yes
                   try: # try to get index and delete the phrase
                       index = plist.index(rememberPhrase) # get index for the give phrase
                       del olist[index] # delete phrase from list
                       remlist = open(self.remfile,"w") # open our file in overwrite mode
                       for item in olist: # for every remaining stuff in our list...
                           remlist.write(item) # ...write it back to file
                       remlist.close() # we don't need the file anymore
                       self.speak_dialog("forgotten") # tell user we did forget the phrase
                   except Exception as e: # error handling
                       logging.error(traceback.format_exc())
                       self.speak_dialog('sorryforget') # sorry we couldn't do it
               else:
                   self.speak_dialog("holdon") # user did not say yes, tell the user that we hold on to the phrase
        except: 
            pass # if we couldn't do it, go on
        if rememberPhrase and found == 0: # we did not get an exact match, if rememberPhrase is not NONE and we did not found anything before
            for index,phrase in enumerate(plist): # for every phrase in our list
                word = phrase.split(" ") # split the phrase, that we can iterate it word by word
                if " ".join(word[:2]) in rememberPhrase: # if the first 2 words match the phrase
                    found = 1 # we found something
                    should_delete = self.get_response('delete', {'PHRASE': phrase}) # ask user if we should forget the phrase
                    yes_words = set(self.translate_list('yes')) # get list of confirmation words
                    resp_delete = should_delete.split()
                    if any(word in resp_delete for word in yes_words): # if user said yes
                        try: # try to delete
                            del olist[index] # delete current phrase from list
                            remlist = open(self.remfile,"w") # open our file in overwrite mode
                            for item in olist: # for every remaining stuff in our list...
                                remlist.write(item) # ...write it back to file
                            remlist.close() # we don't need the file anymore
                            self.speak_dialog("forgotten") # tell user we did forget the phrase
                        except Exception as e: # error handling
                            logging.error(traceback.format_exc()) 
                            self.speak_dialog('sorryforget') # sorry we couldn't do it
                    else:
                        self.speak_dialog("holdon") # user did not say yes, tell the user that we hold on to the phrase
        if delall and not rememberPhrase and found == 0: # if we did not find the phrase and the user said ALL in the utterance -> we assume we should delete the complete list
            should_deleteall = self.get_response('deleteall') # ask user if we should delete the whole list
            yes_words = set(self.translate_list('yes')) # get list of confirmation words
            resp_delete = should_deleteall.split()
            found = 1 # we did find something
            if any(word in resp_delete for word in yes_words):# if user said yes 
                try: # try to delete the whole list
                    remlist = open(self.remfile,"w") # overwrite file
                    remlist.write("") # overwrite with nothing
                    remlist.close() # close file
                    self.speak_dialog("forgotten") # we did forget
                except Exception as e:
                    logging.error(traceback.format_exc())
                    self.speak_dialog('sorryforget') # oh damn -> error
            else:
                self.speak_dialog("holdon") # we will hold on to the phrases
           

        if found == 0: # nothing compares, nothing compares, to you....
           self.speak_dialog("sorrynophrase") # sorry but we found nothing

    def shutdown(self):
        super(rememberSkill, self).shutdown()

    def stop(self):
        pass

def create_skill():
    return rememberSkill()
