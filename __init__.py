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
        self.remfile = (self.file_system.path+"/rememberlist.txt")

    @intent_handler(IntentBuilder("").require("Did").require("You").require("Remember").build())
    def handle_whatdidyou__intent(self, message):
        try:
            remlist = open(self.remfile,"r")
            rememberphrases = remlist.read()
            alist = rememberphrases.split("\n")
            if not rememberphrases:
               self.speak_dialog("sorry")
            else:
               if len(alist) > 2:
                   search = rememberphrases.rfind("\n")
                   rememberphrases = rememberphrases[:search] + "" + rememberphrases[search+1:]
                   search = rememberphrases.rfind("\n")
                   rememberphrases = rememberphrases[:search] + " and " + rememberphrases[search+1:]
                   rememberphrases = rememberphrases.replace('\n', ', ')
               self.speak_dialog('iremembered', {'REMEMBER': rememberphrases})
            remlist.close()
        except:
            self.speak_dialog("sorry")
        
    @intent_handler(IntentBuilder("").require("Remember").require("WhatToRemember").build())
    def handle_remember__intent(self, message):
        rememberPhrase = message.data.get("WhatToRemember", None)
        try:
            remlist = open(self.remfile,"a")
            filePhrase = rememberPhrase+"\n"
            remlist.write(filePhrase)
            self.speak_dialog('gotphrase', {'REMEMBER': rememberPhrase})
            remlist.close()
             
        except Exception as e:
            logging.error(traceback.format_exc())
            self.speak_dialog('sorry')
    
    @intent_handler(IntentBuilder("").require("Forget").require("Phrase").optionally("RememberPhrase").build())
    def handle_delete__intent(self, message):
        rememberPhrase = message.data.get("RememberPhrase", None)
        remlist = open(self.remfile,"r")
        plist = remlist.readlines()
        remlist.close()
        olist = plist
        plist = [x.strip() for x in plist]
        found = 0
        for index,phrase in enumerate(plist):
            word = phrase.split(" ")
            if " ".join(word[:2]) in rememberPhrase:
                found = 1
                should_delete = self.get_response('delete', {'PHRASE': phrase})
                yes_words = set(self.translate_list('yes')) # get list of confirmation words
                resp_delete = should_delete.split()
                if any(word in resp_delete for word in yes_words):
                    try:
                        del olist[index]
                        remlist = open(self.remfile,"w")
                        for item in olist:
                            remlist.write(item)
                        remlist.close()
                        self.speak_dialog("forgotten")
                    except Exception as e:
                        logging.error(traceback.format_exc())
                        self.speak_dialog('sorry')
                    
                else:
                    self.speak_dialog("holdon")
            #print(phrase)
        if found == 0:
           self.speak("i am sorry, i couldn't find a phrase matching your request")
        remlist.close()

    def shutdown(self):
        super(rememberSkill, self).shutdown()

    def stop(self):
        pass

def create_skill():
    return rememberSkill()
