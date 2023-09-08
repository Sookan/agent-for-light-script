import openai
import tiktoken
import re

class Agent:
    def __init__(self):
        self.initial_prompt = "oublie tout ce qui a été écrit précédemment." \
                                "tu es un développeur senior de python. voici ton but : {0}" \
                                "pour réaliser cela tu disposes des balises suivantes <planifier></planifier>, <réaliser></réaliser>," \
                                " <run_code></run_code>, <corriger></corriger>,<finit></finit>" \
                                "tu ne peux mettre entre une balise à la fois, voici ce qu'elle te permet de faire :" \
                                "<planifier: te sert à déterminer ce qui est à réaliser et de planifier la prochaine étape." \
                                "<réaliser>: te permet a tout code qui ce trouve dans cette balise d'être enregistrer dans le fichier \"agent directory/code.py\" ."\
                                "<run_code>: te sert à donnée une commande a executé dans un teminale, te permet de notament d'executé un scrip python" \
                                "<req>: te sert enregistrer un fichier txt, notament utilise pour crée un fichier requirement.txt pour installer les library et package"\
                                "<corriger>: qui te permet de voir si le code possède des erreurs à l'exécution." \
                                "<finit>: qui te sert à indiquer que tu as fini." \
                                "pour les utiliser tu dois mettre une balises ouvrante au début de tes reponces et fermer avec une balises fermante sinon ton message sera ignoré." \
                                "trés important tu ne peux mettre qu'une balise par réponse toute balises suplémentaire utiliser sera ignoré"
        #self.progress = "pour le moment tu n’as pas encore commencé"
        #self.plan = "tu n'as encore rien planifier"
        self.agent_directory = "agent directory"
        self.encoding = encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        self.historique_message = []

    @staticmethod
    def __ask_gpt(gpt,messages):
        return gpt.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages).choices[0].message.content


    def clean_response(self):
        self.last_balise = re.match(r'^<(.+)>', self.last_response.lower()).group(1)
        match_ = re.match(rf'^<{self.last_balise}+>(.*)?</{self.last_balise}+>', self.last_response.lower(),flags=re.DOTALL)
        if match_ == None:
            self.last_balise = "Wrong"
            print("ignore agent")
        else:
            self.last_response = match_.group(1)
            self.messages.append({'role': 'assistant','content':f"<{self.last_balise}>"+self.last_response+f"</{self.last_balise}>"})

    def get_code(self):
        match_ = re.search("""\`\`\`python(.+)\`\`\`""", self.last_response.lower(),flags=re.DOTALL)
        if match_ == None:
            self.messages.append({'role': 'user','content':f"il n'y a pas de code python dans ton précédent message"})
        else :
            with open('agent directory/code.py','w') as file:
                file.write(match_.group(1))


    def start(self):
        task = input("indiqué l'objectif\n")
        with open("test.json",'r') as file_key:
            api_key = file_key.readline()
        openai.api_key = api_key

        self.messages = [{'role': 'user',
                     'content': f"{self.initial_prompt.format(task)}"}]
        self.last_response = self.__ask_gpt(openai,self.messages)
        self.clean_response()
        n=0

        #stop =  input("passons nous à l'étapes suivante\n").lower()=='y'
        while n<=3:
            print(f"last balise : {n}",self.last_balise)
            print(f"last message :{n}", self.last_response)
            match self.last_balise:
                case "planifier":
                    self.last_response = self.__ask_gpt(openai, self.messages)
                    self.clean_response()
                case "réaliser":
                    self.get_code()
                    self.last_response = self.__ask_gpt(openai, self.messages)
                    self.clean_response()

                    pass#save le code
                case "exécuter":
                    self.last_response = self.__ask_gpt(openai, self.messages)
                    pass #run code send error message
                case "fini":
                    self.last_response = self.__ask_gpt(openai, self.messages)
                    self.clean_response()
                case "corriger":
                    self.last_response = self.__ask_gpt(openai, self.messages)
                    self.clean_response()
                case _:
                    print('error')
                    self.last_response = self.__ask_gpt(openai, self.messages)
                    self.clean_response()
                    pass

            stop = False# input("passons nous à l'étapes suivante\n").lower() == 'y'
            n+=1
        print("message :\n",self.messages)



agent = Agent()
agent.start()
