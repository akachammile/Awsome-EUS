from BusinessMiddleware.BusinessManagement.UserManagement.CreateUser import CreateUser

class MessageParse(object):
    
    def __init__(self, userPath:str) -> None:
        self.userPath = userPath

    def msgParse(self, msg:str) -> dict:
        startIndex = msg.index("<$1>") + 4
        endIndex = msg.index("<$2>")
        atama = msg[startIndex : endIndex].replace(" ", "")
        patientId = ""
        kubi = ""

        if msg.index("<$2>") <=8:
            # CreateUser(self.userPath).createUserpath(atama)
            atamaFlag = atama

        if msg.index("<$2>") >= 10 and msg.index("<$2>") >= 1:
            atamaList = atama.split("<$$>")
            atamaFlag, patientId, kubi, _ = atamaList[0], atamaList[1], atamaList[2], atamaList[3]
            
        return {"msg":atamaFlag, "patientId": patientId, "mode":kubi}
                




            

    



 