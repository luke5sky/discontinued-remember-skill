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

    @intent_handler(IntentBuilder("").require("Did").require("You").require("Remember").build())
    def handle_whatdidyou__intent(self, message):
        try:
            remlist = open("/opt/mycroft/skills/remember-skill/rememberlist.txt","r")
            rememberphrases = remlist.read()
            if not rememberphrases:
               self.speak_dialog("sorry")
            else:
               rememberphrases = "I remember: "+rememberphrases.replace('\n', ', ')
               self.speak(rememberphrases)
            remlist.close()
        except:
            self.speak_dialog("sorry")
        
    @intent_handler(IntentBuilder("").require("Remember").require("WhatToRemember").build())
    def handle_remember__intent(self, message):
        rememberPhrase = message.data.get("WhatToRemember", None)
        try:
            remlist = open("/opt/mycroft/skills/remember-skill/rememberlist.txt","a")
            print(rememberPhrase)
            rememberPhrase = rememberPhrase+"\n"
            remlist.write(rememberPhrase)
            self.speak_dialog('gotphrase', {'REMEMBER': rememberPhrase})
            remlist.close()
            #self.speak_dialog('result', {'REMEMBER': rigfrom, 'TO': origto, 'HOURS': hours, 'DISTANCE': dist})
             
        except Exception as e:
            logging.error(traceback.format_exc())
            self.speak_dialog('sorry')
        logger.info("Request finished")
    
    @intent_handler(IntentBuilder("").require("Forget").require("Phrase").optionally("RememberPhrase").build())
    def handle_delete__intent(self, message):
        rememberPhrase = message.data.get("RememberPhrase", None)
        
        should_delete = self.get_response("Should i forget: " + rememberPhrase)
#self.should_getskills = self.get_response('ask.getskills') # ask user if we should give him a list of all his skills.
        yes_words = set(self.translate_list('yes')) # get list of confirmation words
        resp_delete = should_delete.split()
        if any(word in resp_delete for word in yes_words):
            self.speak("Consider it done")
        else:
            self.speak("I will hold on to this phrase")
        #self.listSkills() # execute function listSkills -> if user confirmed -> give him a list of all his skills, else -> exit

#    def listSkills(self):
#        if self.should_getskills: # if user said something
#           resp_getskills = self.should_getskills.split() # split user sentence into list
#           if any(word in resp_getskills for word in self.yes_words): # if any of the words from the user sentences is yes
#              self.speak_dialog('my.skills') # Introduction that we will give user list of skills
#              self.speak(self.myskills.strip()) # tell user list of skills
#           else: # no word in sentence from user was yes
#              self.speak_dialog('no.skills') # give user feedback

        

    def shutdown(self):
        super(rememberSkill, self).shutdown()

    def stop(self):
        pass

def create_skill():
    return rememberSkill()
