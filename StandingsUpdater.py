import os, os.path, sys
import psycopg2

class Leader(object):

    def __init__(self, player, teamName, battleMercs, supportMercs, income, gold, victories, defeats, rechargeList, koString, otherString, declare, curTier):
        self.leader = player
        self.name = teamName
        self.battle = battleMercs
        self.support = supportMercs
        self.RI = income
        self.gp = gold
        self.wins = victories
        self.losses = defeats
        self.recharge = rechargeList
        self.ko = koString
        self.other = otherString
        self.declaration = declare
        self.tier = curTier

def getLeaderlistFromStandings(fileName):
    fin = open(fileName, 'r')
    lines = fin.readlines()
    info = []
    leaderList = []
    onLeader = False
    
    for line in lines:
        if onLeader == False:
            player = ""
            teamName = ""
            battleMercs = ""
            supportMercs = ""
            income = 0
            gold = 0
            victories = 0
            defeats = 0
            rechargeList = {}
            koString = ""
            otherString = ""
            onLeader = True
            
        if "LOW TIER" in line:
            curTier = 'low'
            declaration = 1
        elif "MID TIER" in line:
            curTier = 'mid'
            declaration = 1
        elif "HIGH TIER" in line:
            curTier = 'high'
            declaration = 1
        if " ~ " in line: # leader line.  can get player name, team name, record, gp, infra here
            info = line.split(" ~ ") # break off the player name
            player = info[0]
            info = info[1].split(" (") # break off the team name
            teamName = info[0]
            info = info[1].split(", ") # split the parened area with the record[0], gp[1], infra[2]
            tempInfo = info[0].split("-")
            victories = tempInfo[0]
            defeats = tempInfo[1]
            tempInfo = info[1][:-2]
            gold = int(tempInfo)
            tempInfo = info[2][:-5]
            income = int(tempInfo)
        if "Battle:" in line: # battle line, can get battle mercs here
            battleMercs = line[8:]
        if "Support:" in line: # support line, can get support mercs here
            supportMercs = line[9:]
        if "KOs/Injuries:" in line: # get the KO line
            koString = line[13:]
        if "Recharge:" in line: # recharge line, populate it NOT DONE
            line = line[10:]
            
        if "Other:" in line: # get the other line
            otherString = line[7:]
            curLeader = Leader(player, teamName, battleMercs, supportMercs, income, gold, victories, defeats,  rechargeList, koString, otherString, declaration, curTier)
            leaderList.append(curLeader)
            declaration = declaration + 1
            onLeader = False
            
    fin.close()
    
    return leaderList
    
def writeStandings(fileName, leaderList):
    
    fout = open(fileName, 'w')
    for lead in leaderList:
        fout.write(lead.leader + " ~ " + lead.name + " (" + str(lead.wins) + "-" + str(lead.losses) + ", " + str(lead.gp) + "GP" + ", " + str(lead.RI) + " RI)\n")
        fout.write("Battle: " + lead.battle)
        fout.write("Support: " + lead.support)
        fout.write("KOs/Injuries: " + lead.ko)
        fout.write("Recharge: " + lead.other)
        fout.write("Other: " + lead.other + "\n")
    fout.close()
    
def main(argv):

    inputName = str(argv[0])
    leaders = getLeaderlistFromStandings(inputName)
    outputName = inputName[:-4] + "PHASEMODULATOR.txt"
    writeStandings(outputName, leaders)

#    outputName = inputName[:-8] + ".txt"
#    createMACList(outputName, solutions)
    
if __name__ == "__main__":
    main(sys.argv[1:])